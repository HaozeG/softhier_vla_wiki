#!/usr/bin/env python3
"""Local search + browsing for the wiki (OpenViking-style layers, zvec index).

Layers (per directory, like OpenViking):
  L0  _abstract.md   <=256 chars, one-glance summary of the directory
  L1  _overview.md   <=4000 chars, what is inside and where to look
  L2  *.md           the actual notes (indexed per heading chunk)

Folder summary files carry `covers: <hash>` in frontmatter: a hash of the directory's direct
children (file contents + child abstracts). `check` flags a summary file stale when it
no longer matches; after rewriting one, run `stamp` to record the new hash.

Notes (L2) carry frontmatter (`type`, `tags`, `sources`) and per-type required sections;
no dates live in files: git is the log (`commit` writes structured messages, `log` reads them).

Commands:
  index | find | related | ls | tree            search & browse (zvec hybrid / nearest-neighbour)
  new | check | health | stamp                  create from template, lint, semantic health, summary-file stamp
  commit | log | history | install-hooks        git-as-log
  setup                                         one-time environment setup
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ensure_venv():
    """Re-exec inside <wiki>/.venv so the tool works from any cwd (e.g. the parent repo) without activation."""
    py = ROOT / ".venv" / "bin" / "python"
    if py.exists() and not os.environ.get("WIKI_REEXEC") and Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        os.environ["WIKI_REEXEC"] = "1"
        os.execv(str(py), [str(py), *sys.argv])


_ensure_venv()
INDEX = ROOT / ".index"
DB = INDEX / "zvec"
MANIFEST = INDEX / "manifest.json"
MODEL = "BAAI/bge-small-en-v1.5"
DIM = 384
SCHEMA_VERSION = 1
SKIP_DIRS = {"tools", "node_modules", "__pycache__"}  # plus any dot-dir
ROOT_SKIP_FILES = {"README.md", "CLAUDE.md"}
L0_MAX, L1_MAX, CHUNK_MAX = 256, 4000, 1500
SUMMARY_FILES = {"_abstract.md": "L0", "_overview.md": "L1"}
# note type -> required "## " sections
TYPES = {
    "concept": ["Summary"],
    "entity": ["Summary"],
    "paper": ["Summary", "Key claims"],
    "decision": ["Context", "Decision", "Why"],
    "runbook": ["Steps"],
    "comparison": ["Summary", "Comparison"],
}
NEED_SOURCES = {"concept", "entity", "paper"}
OPS = ["ingest", "update", "delete", "lint", "refactor", "init"]
DUP_THRESHOLD = 0.93  # bge-small, chunk-level: a lightly reworded copy scores ~1.0; related-but-distinct notes in one narrow topic reach ~0.90-0.92 (see decision 0005); unrelated <0.65


# ---------- filesystem model ----------
def sha(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def split_fm(text: str):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, text
    fm = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    return {k.strip(): v.strip() for k, v in fm.items()}, text[m.end():]


def parse_list(v: str):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def note_title(body: str):
    for line in body.splitlines():
        if line.strip():
            return line[2:].strip() if line.startswith("# ") else None
    return None


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)|(wiki://[\w./-]+\.md)")


def note_links(f: Path, body: str):
    """-> (existing target rel paths, broken raw targets)."""
    ok, broken = set(), []
    body = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", body, flags=re.S))  # ignore code
    for m in LINK_RE.finditer(body):
        t = (m.group(1) or m.group(2)).split("#")[0]
        if not t or re.match(r"(https?:|mailto:)", t) or not t.endswith(".md"):
            continue
        tp = ROOT / t[len("wiki://"):] if t.startswith("wiki://") else (f.parent / t)
        tp = tp.resolve()
        if tp.exists():
            ok.add(tp.relative_to(ROOT).as_posix())
        else:
            broken.append(t)
    return ok, broken


def link_graph():
    out = {}
    for d in all_dirs():
        for f in notes(d):
            out[f.relative_to(ROOT).as_posix()] = note_links(f, split_fm(f.read_text())[1])[0]
    inbound = {k: set() for k in out}
    for src, tgts in out.items():
        for t in tgts:
            if t in inbound and t != src:
                inbound[t].add(src)
    return out, inbound


def uri(p: Path) -> str:
    rel = p.relative_to(ROOT).as_posix()
    return "wiki://" + ("" if rel == "." else rel)


def resolve(arg: str) -> Path:
    p = Path(arg[len("wiki://"):] if arg.startswith("wiki://") else arg)
    if not p.is_absolute():
        p = ROOT / p if (ROOT / p).exists() or not (Path.cwd() / p).exists() else Path.cwd() / p
    return p.resolve()


def dirs(base: Path):
    for d in sorted(base.iterdir()):
        if d.is_dir() and not d.name.startswith(".") and d.name not in SKIP_DIRS:
            yield d


def notes(d: Path):
    for f in sorted(d.glob("*.md")):
        if f.name in SUMMARY_FILES or (d == ROOT and f.name in ROOT_SKIP_FILES):
            continue
        yield f


def all_dirs():
    stack = [ROOT]
    while stack:
        d = stack.pop()
        yield d
        stack.extend(reversed(list(dirs(d))))


def summary_body(d: Path, name: str):
    f = d / name
    return split_fm(f.read_text())[1].strip() if f.exists() else None


def covers_hash(d: Path) -> str:
    parts = [f"{f.name}:{sha(f.read_text())}" for f in notes(d)]
    parts += [f"{c.name}/:{sha(summary_body(c, '_abstract.md') or '')}" for c in dirs(d)]
    return sha("\n".join(parts))[:12]


# ---------- chunking ----------
def chunks(text: str, title: str):
    """Split markdown by heading, then by paragraph to <= CHUNK_MAX chars."""
    sections, path, buf = [], [], []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((" > ".join(path), body))
        buf.clear()

    for line in text.splitlines():
        m = re.match(r"(#{1,4})\s+(.*)", line)
        if m:
            flush()
            path[:] = path[: len(m.group(1)) - 1] + [m.group(2).strip()]
        else:
            buf.append(line)
    flush()
    for head, body in sections:
        cur = ""
        for para in re.split(r"\n\s*\n", body):
            if cur and len(cur) + len(para) > CHUNK_MAX:
                yield head, cur
                cur = ""
            cur = f"{cur}\n\n{para}" if cur else para
        if cur:
            yield head, cur


def build_docs(f: Path):
    """-> list of (chunk_id, fields) for one file."""
    fm, body = split_fm(f.read_text())
    layer = SUMMARY_FILES.get(f.name, "L2")
    body = body.strip()
    meta = ""
    if layer == "L2":
        meta = f"[{fm.get('type', 'note')}] tags: {', '.join(parse_list(fm.get('tags')))}\n"
    rel = f.relative_to(ROOT).as_posix()
    if layer != "L2":
        pieces = [(f"summary of {uri(f.parent)}", body)]
    else:
        pieces = list(chunks(body, f.stem)) or [(f.stem, body)]
    out = []
    for i, (head, text) in enumerate(pieces):
        out.append((sha(f"{rel}#{i}"), {
            "uri": uri(f), "layer": layer, "heading": head or f.stem,
            "text": meta + (f"{head}\n{text}" if head else text),
        }))
    return out


def indexable():
    for d in all_dirs():
        for f in notes(d):
            yield f
        for name in SUMMARY_FILES:
            if (d / name).exists():
                yield d / name


# ---------- zvec ----------
def zv():
    try:
        import zvec
    except ImportError:
        sys.exit(f"zvec is not installed. Run once: {Path(__file__).resolve()} setup")
    return zvec


def open_db(create=False):
    zvec = zv()
    if DB.exists():
        return zvec.open(str(DB))
    if not create:
        sys.exit("no index yet: run `tools/wiki.py index`")
    INDEX.mkdir(exist_ok=True)
    schema = zvec.CollectionSchema(
        name="wiki_chunks",
        fields=[
            zvec.FieldSchema("text", zvec.DataType.STRING, index_param=zvec.FtsIndexParam()),
            zvec.FieldSchema("layer", zvec.DataType.STRING, index_param=zvec.InvertIndexParam()),
            zvec.FieldSchema("uri", zvec.DataType.STRING),
            zvec.FieldSchema("heading", zvec.DataType.STRING),
        ],
        vectors=zvec.VectorSchema(
            "emb", zvec.DataType.VECTOR_FP32, DIM,
            index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE)),
    )
    return zvec.create_and_open(path=str(DB), schema=schema)


_model = None


def embedder():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding(MODEL)
    return _model


def load_manifest():
    if MANIFEST.exists():
        m = json.loads(MANIFEST.read_text())
        if m.get("version") == SCHEMA_VERSION and m.get("model") == MODEL:
            return m
    return {"version": SCHEMA_VERSION, "model": MODEL, "files": {}}


# ---------- commands ----------
def sync_index():
    zvec = zv()
    man = load_manifest()
    if not man["files"] and DB.exists():  # fresh/invalid manifest -> rebuild from scratch
        import shutil
        shutil.rmtree(DB)
    db = open_db(create=True)
    current = {f.relative_to(ROOT).as_posix(): f for f in indexable()}
    stale = [p for p in man["files"] if p not in current]
    for p in stale:
        db.delete(man["files"].pop(p)["ids"])
    changed = 0
    for rel, f in current.items():
        h = sha(f.read_text())
        old = man["files"].get(rel)
        if old and old["hash"] == h:
            continue
        if old:
            db.delete(old["ids"])
        docs = build_docs(f)
        vecs = list(embedder().embed([d[1]["text"] for d in docs]))
        db.upsert([zvec.Doc(id=i, vectors={"emb": [float(x) for x in v]}, fields=fl)
                   for (i, fl), v in zip(docs, vecs)])
        man["files"][rel] = {"hash": h, "ids": [d[0] for d in docs]}
        changed += 1
    db.flush()
    MANIFEST.write_text(json.dumps(man, indent=1))
    return f"indexed {changed} changed, {len(stale)} removed, {len(man['files'])} files total"


def cmd_index(a):
    print(sync_index())


def cmd_find(a):
    zvec = zv()
    db = open_db()
    qv = [float(x) for x in next(embedder().query_embed([a.query]))]
    qs = [zvec.Query("emb", vector=qv),
          zvec.Query("text", fts=zvec.Fts(match_string=a.query))]
    flt = f"layer = '{a.layer}'" if a.layer else None
    if a.under:
        pre = uri(resolve(a.under))
        flt = " AND ".join(x for x in [flt, f"uri LIKE '{pre}%'"] if x)
    res = db.query(queries=qs, topk=a.n, filter=flt, reranker=zvec.RrfReRanker())
    for d in res:
        f = d.fields
        snippet = re.sub(r"\s+", " ", f["text"].split("\n", 1)[-1])[:a.width]
        print(f"{d.score:.4f} [{f['layer']}] {f['uri']}  # {f['heading']}\n    {snippet}")
    if not len(res):
        print("(no results)")


def first_line(f: Path):
    body = split_fm(f.read_text())[1]
    m = re.search(r"^#\s+(.*)", body, re.M)
    return m.group(1) if m else ""


def show_dir(d: Path, depth: int, indent=""):
    for c in dirs(d):
        ab = summary_body(c, "_abstract.md")
        print(f"{indent}{c.name}/  — {re.sub(chr(10), ' ', ab) if ab else '(no abstract)'}")
        if depth > 1:
            show_dir(c, depth - 1, indent + "  ")
    for f in notes(d):
        print(f"{indent}{f.name}  — {first_line(f)}")


def cmd_ls(a):
    d = resolve(a.path)
    print(uri(d) if d == ROOT else uri(d) + "/")
    ab = summary_body(d, "_abstract.md")
    if ab:
        print(f"  {ab}")
    show_dir(d, a.depth)


def structural_issues():
    """Model-free lint. -> list of (severity, code, path, message)."""
    out = []
    add = lambda sev, code, path, msg: out.append((sev, code, path, msg))
    _, inbound = link_graph()
    titles, bodies = {}, {}
    for d in all_dirs():
        rel = d.relative_to(ROOT).as_posix()
        for name, cap in (("_abstract.md", L0_MAX), ("_overview.md", L1_MAX)):
            f = d / name
            if not f.exists():
                if any(True for _ in notes(d)) or any(True for _ in dirs(d)):
                    add("ERROR", "MISSING", f"{rel}/{name}", "folder summary file missing")
                continue
            fm, body = split_fm(f.read_text())
            if not body.strip():
                add("ERROR", "EMPTY", f"{rel}/{name}", "summary file has no body text; write the summary, then `stamp`")
            if len(body.strip()) > cap:
                add("ERROR", "TOO LONG", f"{rel}/{name}", f"{len(body.strip())} > {cap} chars")
            if fm.get("covers") != covers_hash(d):
                add("ERROR", "STALE", f"{rel}/{name}", "children changed; review/rewrite then `stamp`")
        overview = summary_body(d, "_overview.md") or ""
        for f in notes(d):
            frel = f.relative_to(ROOT).as_posix()
            fm, body = split_fm(f.read_text())
            typ = fm.get("type")
            if not re.search(r"\]\(" + re.escape(f.name) + r"\)", overview):
                add("ERROR", "UNCATALOGUED", frel, f"needs a link `[title]({f.name})` + one-line summary in {rel}/_overview.md")
            for key in ("type", "tags", "sources"):
                if key not in fm:
                    add("ERROR", "FRONTMATTER", frel, f"missing `{key}:`")
            if typ is not None and typ not in TYPES:
                add("ERROR", "BADTYPE", frel, f"type `{typ}` not in {sorted(TYPES)}")
            if "tags" in fm and not parse_list(fm["tags"]):
                add("WARN", "NOTAGS", frel, "empty tags")
            if typ in NEED_SOURCES and "sources" in fm and not parse_list(fm["sources"]):
                add("WARN", "NOSOURCES", frel, f"`{typ}` note cites no sources")
            title = note_title(body)
            if title is None:
                add("ERROR", "NOTITLE", frel, "first content line must be `# Title`")
            else:
                titles.setdefault(title.lower(), []).append(frel)
            heads = {h.lower() for h in re.findall(r"^##\s+(.*?)\s*$", body, re.M)}
            for need in TYPES.get(typ, []):
                if need.lower() not in heads:
                    add("ERROR", "NOSECTION", frel, f"`{typ}` note needs `## {need}`")
            _, broken = note_links(f, body)
            for t in broken:
                add("ERROR", "BROKENLINK", frel, t)
            if "<!--" in body:
                add("ERROR", "UNFILLED", frel, "template guidance comment (`<!-- ... -->`) still present; replace with real content")
            if re.search(r"\bTODO\b", body):
                add("WARN", "PLACEHOLDER", frel, "contains TODO")
            if not inbound.get(frel):
                add("WARN", "ORPHAN", frel, "no other note links here (use `related` to find where to link it)")
            bodies.setdefault(sha(re.sub(r"\s+", " ", body).strip()), []).append(frel)
    for group in list(titles.values()) + list(bodies.values()):
        if len(group) > 1:
            add("WARN", "DUPLICATE", group[0], "same title/content as " + ", ".join(group[1:]))
    return out


def report(issues, strict=False):
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for sev, code, path, msg in sorted(issues, key=lambda x: (order[x[0]], x[2], x[1])):
        print(f"{sev:5} {code:12} {path}  {msg}")
    errs = sum(1 for i in issues if i[0] == "ERROR")
    warns = sum(1 for i in issues if i[0] == "WARN")
    infos = len(issues) - errs - warns
    print("ok" if not (errs or warns) else f"{errs} error(s), {warns} warning(s)" + (f", {infos} to review" if infos else ""))
    return 1 if errs or (strict and warns) else 0


def cmd_check(a):
    sys.exit(report(structural_issues(), a.strict))


def neighbours(db, cid, topk=10):
    zvec = zv()
    return db.query(zvec.Query("emb", id=cid), topk=topk, filter="layer = 'L2'")


def semantic_pairs(db, man, floor):
    pairs = {}
    for rel, info in man["files"].items():
        if Path(rel).name in SUMMARY_FILES:
            continue
        for cid in info["ids"]:
            for r in neighbours(db, cid, 6):
                other = r.fields["uri"][len("wiki://"):]
                sim = 1 - r.score
                if r.id != cid and other != rel and sim >= floor:
                    key = tuple(sorted((rel, other)))
                    if sim > pairs.get(key, (0, ""))[0]:
                        pairs[key] = (sim, r.fields["heading"])
    return pairs


def cmd_health(a):
    print(sync_index())
    issues = structural_issues()
    pairs = semantic_pairs(open_db(), load_manifest(), a.review_floor)
    out, _ = link_graph()
    for (x, y), (sim, head) in sorted(pairs.items(), key=lambda kv: -kv[1][0]):
        linked = y in out.get(x, ()) or x in out.get(y, ())
        if sim >= a.dup_threshold and not linked:  # linked pairs are acknowledged as distinct
            issues.append(("WARN", "NEARDUP", x, f"{sim:.2f} similar to {y} (# {head}); merge, or cross-link with a sentence on how they differ"))
        elif sim < a.dup_threshold and a.candidates:
            issues.append(("INFO", "REVIEW", x, f"{sim:.2f} related to {y} (# {head}); read both for conflicting claims"))
    sys.exit(report(issues, a.strict))


def cmd_related(a):
    db = open_db()
    rel = resolve(a.path).relative_to(ROOT).as_posix()
    info = load_manifest()["files"].get(rel)
    if not info:
        sys.exit(f"{rel} is not indexed (run `index`; only .md notes are indexed)")
    out, inbound = link_graph()
    linked = out.get(rel, set()) | inbound.get(rel, set())
    best = {}
    for cid in info["ids"]:
        for r in neighbours(db, cid, 12):
            other = r.fields["uri"][len("wiki://"):]
            if other != rel and (1 - r.score) > best.get(other, (0, ""))[0]:
                best[other] = (1 - r.score, r.fields["heading"])
    for other, (sim, head) in sorted(best.items(), key=lambda kv: -kv[1][0])[: a.n]:
        tag = "linked    " if other in linked else "NOT LINKED"
        print(f"{sim:.2f} {tag} {other}  # {head}")
    if not best:
        print("(no related notes)")


def cmd_new(a):
    tpl = ROOT / "tools" / "templates" / f"{a.type}.md"
    if not tpl.exists():
        sys.exit(f"unknown type {a.type}; choose from {sorted(TYPES)}")
    dest = (ROOT / a.path).resolve()
    if dest.suffix != ".md" or ROOT not in dest.parents:
        sys.exit("path must be a .md file inside the wiki")
    if dest.exists():
        sys.exit(f"{a.path} already exists")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(tpl.read_text().replace("{{title}}", a.title))
    rel = dest.relative_to(ROOT)
    print(f"created {rel}\nnext: replace every `<!-- ... -->` guidance comment with real content, list it in {rel.parent}/_overview.md, "
          f"`related {rel}` to cross-link, then `stamp`, `index`, `health`")


# ---------- git as the log ----------
def git(*args, check=True):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def cmd_commit(a):
    issues = [i for i in structural_issues() if i[0] == "ERROR"]
    if issues and not a.force:
        report(issues)
        sys.exit("refusing to commit: fix errors (or --force)")
    pre_staged = bool(git("diff", "--cached", "--name-only").strip())
    git("add", "-A")
    changes = [l.split("\t") for l in git("diff", "--cached", "--name-status").splitlines()]
    if not changes:
        sys.exit("nothing to commit")
    pages = [f"{c[0][0]} {c[-1]}" for c in changes if Path(c[-1]).name not in SUMMARY_FILES]
    n_side = len(changes) - len(pages)
    date = a.date or datetime.date.today().isoformat()
    trailers = [f"Date: {date}", f"Op: {a.op}", f"Pages: {'; '.join(pages) or '(summary files only)'}"]
    if n_side:
        trailers.append(f"Summary-files: {n_side}")
    if a.source:
        trailers.append(f"Sources: {'; '.join(a.source)}")
    body = (a.body.strip() + "\n\n") if a.body else ""
    msg = f"wiki({a.op}): {a.subject}\n\n{body}" + "\n".join(trailers) + "\n"
    if a.dry_run:
        print(msg)
        if not pre_staged:
            git("reset", "-q")
        return
    git("commit", "-q", "-m", msg)
    print(git("log", "-1", "--format=%h %s"), end="")


def cmd_log(a):
    fmt = "%h%x1f%as%x1f%s%x1f%(trailers:key=Date,valueonly,unfold)%x1f%(trailers:key=Pages,valueonly,unfold)%x1e"
    args = ["log", f"-{a.n}", f"--format={fmt}"]
    if a.op:
        args += ["--grep", f"^wiki({a.op}):"]
    if a.path:
        args += ["--follow", "--", a.path]
    for rec in git(*args).split("\x1e"):
        if not rec.strip():
            continue
        h, adate, subj, date, pages = ([x.strip() for x in rec.split("\x1f")] + [""] * 5)[:5]  # older commits lack trailers
        print(f"{date or adate}  {h}  {subj}" + (f"\n{'':12}{pages}" if pages and a.pages else ""))


def cmd_history(a):
    rel = resolve(a.path).relative_to(ROOT).as_posix()
    a.op, a.path, a.n, a.pages = None, rel, a.n, False
    cmd_log(a)


def cmd_hook(a):
    """Claude Code hook entry points (stdin JSON -> stdout JSON). Never fails: hooks must not block the session."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        payload = {}
    try:
        if a.event == "session-start":
            text = session_context(Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or Path.cwd()))
            event = "SessionStart"
        else:
            return
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))
    except Exception as e:  # noqa: BLE001
        print(f"wiki hook error: {e}", file=sys.stderr)


def session_context(project: Path) -> str:
    """Stdlib-only orientation for a session: where the wiki is, what it holds, what changed lately."""
    tool = os.path.relpath(Path(__file__).resolve(), project)
    lines = [f"A project wiki (LLM-maintained, git submodule) lives at `{os.path.relpath(ROOT, project)}/`.",
             f"Consult it before design/architecture/planning work and when past decisions or project knowledge could matter: "
             f"`{tool} find \"<question>\"` (semantic+keyword search), `{tool} ls <dir>`; cite `wiki://` URIs. "
             f"File durable outcomes back (decisions, syntheses) using the workflow in `{os.path.relpath(ROOT, project)}/CLAUDE.md` "
             f"or the `softhier-wiki:wiki` skill; commit only inside the submodule and only when asked."]
    if not (ROOT / ".venv").exists() or not INDEX.exists():
        lines.append(f"Not set up on this machine yet: run `{tool} setup` once before using it.")
    ab, ov = summary_body(ROOT, "_abstract.md"), summary_body(ROOT, "_overview.md")
    if ab:
        lines.append(f"\nWiki abstract: {ab}")
    if ov:
        lines.append(f"\nWiki overview:\n{ov}")
    for d in dirs(ROOT):
        a0 = summary_body(d, "_abstract.md")
        lines.append(f"- {d.name}/: {a0 or '(no abstract)'}")
    try:
        recent = git("log", "-5", "--format=%as %s", check=False).strip()
    except Exception:  # noqa: BLE001
        recent = ""
    if recent:
        lines.append("\nRecent wiki changes:\n" + recent)
    return "\n".join(lines)[:9000]


def cmd_setup(a):
    """Create .venv, install requirements, build the index, enable the commit hook (stdlib only until the venv exists)."""
    venv = ROOT / ".venv"
    if not (venv / "bin" / "python").exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
    py = str(venv / "bin" / "python")
    subprocess.check_call([py, "-m", "pip", "install", "-q", "-r", str(ROOT / "requirements.txt")])
    subprocess.check_call([py, str(Path(__file__).resolve()), "index"])
    if (ROOT / ".git").exists():
        subprocess.check_call([py, str(Path(__file__).resolve()), "install-hooks"])
    print("setup complete")


def cmd_install_hooks(a):
    hook = ROOT / "tools" / "hooks" / "commit-msg"
    hook.chmod(0o755)
    git("config", "core.hooksPath", "tools/hooks")
    print("git core.hooksPath -> tools/hooks (commit-msg enforces `wiki(<op>): subject` + `Date:` trailer)")


def cmd_stamp(a):
    targets = [resolve(p) for p in a.paths] if a.paths else list(all_dirs())
    # bottom-up so parents hash the freshly-stamped child abstracts... abstracts' bodies
    # don't change on stamp, so order only matters for the printed output.
    for d in sorted(targets, key=lambda p: -len(p.parts)):
        for name in SUMMARY_FILES:
            f = d / name
            if f.exists():
                body = split_fm(f.read_text())[1].lstrip("\n")
                f.write_text(f"---\ncovers: {covers_hash(d)}\n---\n{body}")
                print(f"stamped {f.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index", help="incrementally (re)index changed files").set_defaults(fn=cmd_index)
    p = sub.add_parser("find", help="hybrid semantic + keyword search")
    p.add_argument("query")
    p.add_argument("-n", type=int, default=8)
    p.add_argument("--layer", choices=["L0", "L1", "L2"])
    p.add_argument("--under", help="restrict to a directory, e.g. knowledge/")
    p.add_argument("--width", type=int, default=160)
    p.set_defaults(fn=cmd_find)
    p = sub.add_parser("ls", help="list a directory with abstracts")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("-d", "--depth", type=int, default=1)
    p.set_defaults(fn=cmd_ls)
    p = sub.add_parser("tree", help="recursive ls")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("-d", "--depth", type=int, default=4)
    p.set_defaults(fn=cmd_ls)
    p = sub.add_parser("check", help="fast structural lint (no model): folder summary files, frontmatter, sections, links, catalog")
    p.add_argument("--strict", action="store_true", help="warnings also fail")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("health", help="sync index, run check, add semantic near-duplicate detection (zvec)")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--dup-threshold", type=float, default=DUP_THRESHOLD)
    p.add_argument("--candidates", action="store_true", help="also list related-but-distinct pairs (0.65..threshold) to review for contradictions")
    p.add_argument("--review-floor", type=float, default=0.65)
    p.set_defaults(fn=cmd_health)
    p = sub.add_parser("related", help="nearest-neighbour notes for a note, flagged if not yet linked")
    p.add_argument("path")
    p.add_argument("-n", type=int, default=8)
    p.set_defaults(fn=cmd_related)
    p = sub.add_parser("new", help="scaffold a note from tools/templates/<type>.md")
    p.add_argument("type", choices=sorted(TYPES))
    p.add_argument("path")
    p.add_argument("title")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("commit", help="lint-gated git commit with structured message")
    p.add_argument("op", choices=OPS)
    p.add_argument("subject")
    p.add_argument("--body")
    p.add_argument("--source", action="append", help="repeatable; recorded in Sources: trailer")
    p.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_commit)
    p = sub.add_parser("log", help="wiki change log from git history")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--op", choices=OPS)
    p.add_argument("--path")
    p.add_argument("--pages", action="store_true", help="also show pages touched")
    p.set_defaults(fn=cmd_log)
    p = sub.add_parser("history", help="git history of one note")
    p.add_argument("path")
    p.add_argument("-n", type=int, default=20)
    p.set_defaults(fn=cmd_history)
    p = sub.add_parser("hook", help="Claude Code hook entry point (used by the softhier-wiki plugin)")
    p.add_argument("event", choices=["session-start"])
    p.set_defaults(fn=cmd_hook)
    sub.add_parser("setup", help="one-time: create .venv, install deps, build index, enable hook").set_defaults(fn=cmd_setup)
    sub.add_parser("install-hooks", help="enable the commit-msg hook").set_defaults(fn=cmd_install_hooks)
    p = sub.add_parser("stamp", help="record current children hash in summary files")
    p.add_argument("paths", nargs="*")
    p.set_defaults(fn=cmd_stamp)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
