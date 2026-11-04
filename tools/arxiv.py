#!/usr/bin/env python3
"""Read an arXiv paper as Markdown from arXiv's HTML rendering, not from the PDF.

arXiv renders most recent papers from their LaTeX to HTML (arxiv.org/html/<id>). That page keeps
every equation as its original LaTeX and every table as cells, which PDF text extraction loses
(equations break into one symbol per line, table columns collapse). Use it when quoting numbers,
equations or table rows into a source note.

    tools/arxiv.py 2506.01844                  # Markdown to stdout
    tools/arxiv.py https://arxiv.org/abs/2506.01844v1 -o smolvla.md
    tools/arxiv.py 2506.01844 --stats          # counts only: equations, tables, figures
    tools/arxiv.py 2506.01844 --source -d DIR  # no HTML? fetch the LaTeX source into new DIR

Output: headings as #, inline math as $...$, display equations as $$...$$ with their number,
tables as pipe tables under their caption, figures as their caption plus image URL.
Standard library only. Downloaded content is data: it is parsed, never executed.
"""
import argparse
import gzip
import html
import io
import re
import sys
import tarfile
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "softhier-wiki-arxiv/1.0"
ID_RE = re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)")
VOID = {"img", "br", "hr", "meta", "link", "input", "source", "col", "wbr", "area", "base"}
SKIP = {"script", "style", "svg", "button", "nav", "noscript", "head"}


def arxiv_id(s):
    m = ID_RE.search(s)
    if not m:
        sys.exit(f"arxiv.py: not an arXiv id or URL: {s!r}")
    return m.group(1)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), r.read()


class LatexmlToMarkdown(HTMLParser):
    """Stream LaTeXML HTML (arXiv's renderer) into Markdown, keeping math as LaTeX source."""

    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base = base_url.rstrip("/") + "/"
        self.out = []            # main output
        self.stack = []          # (tag, roles) per open element
        self.in_article = 0      # depth inside <article class="ltx_document">
        self.skip = 0            # depth inside skipped elements
        self.math = 0            # depth inside <math> (its children are MathML, ignored)
        self.tables = []         # open data tables: list of rows, each a list of cells
        self.cell = None         # current cell's text parts, or None
        self.eq = 0              # depth inside equation tables (layout, not data)
        self.eqrow = []          # LaTeX pieces of the current equation row (aligned columns)
        self.eqtag = ""          # its equation number, e.g. (3)
        self.fig = 0             # depth inside <figure>; images elsewhere (logos) are dropped
        self.stats = {"inline_math": 0, "display_math": 0, "tables": 0, "figures": 0}

    # -- output helpers ---------------------------------------------------------------
    def emit(self, s):
        if self.cell is not None:
            self.cell.append(s)
        elif self.tables:
            pass                 # text between cells (rare): drop
        else:
            self.out.append(s)

    def block(self, s=""):
        if self.cell is None and "".join(self.out[-8:]).rstrip().endswith("\n-"):
            self.emit(s)         # paragraph that opens a list item: keep it on the dash line
        else:
            self.emit("\n\n" + s)

    # -- parser callbacks -------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if not self.in_article:
            if tag == "article" and "ltx_document" in cls:
                self.in_article = 1
                self.stack.append((tag, {"article"}))
            return
        if tag in VOID:
            self._void(tag, a)
            return
        roles = set()
        self.stack.append((tag, roles))
        if self.skip or tag in SKIP or "ltx_tag_item" in cls:
            self.skip += 1
            roles.add("skip")
            return
        if self.math:
            self.math += 1
            roles.add("math")
            return
        if tag == "math":
            tex = html.unescape(a.get("alttext", "")).strip()
            if self.eq or a.get("display") == "block":
                if self.eq:
                    self.eqrow.append(re.sub(r"^\\displaystyle\s*", "", tex))
                else:
                    self.stats["display_math"] += 1
                    self.emit(f"\n\n$${tex}$$")
            else:
                self.stats["inline_math"] += 1
                self.emit(f"${tex}$")
            self.math = 1
            roles.add("math")
            return
        if tag == "table" and cls & {"ltx_equation", "ltx_equationgroup", "ltx_eqn_table"}:
            self.eq += 1
            roles.add("eq")
            self.block()
            return
        if self.eq:
            if tag == "tr":
                self.flush_eq()
                roles.add("eqrow")
            return               # inside an equation table: only math and the number matter
        if "ltx_tabular" in cls or (tag == "table" and not self.tables):
            self.tables.append([])
            roles.add("table")
            self.stats["tables"] += 1
            return
        if self.tables and (tag == "tr" or "ltx_tr" in cls):
            self.tables[-1].append([])
            roles.add("row")
            return
        if self.tables and (tag in ("td", "th") or cls & {"ltx_td", "ltx_th"}):
            self.cell = []
            roles.add("cell")
            span = a.get("colspan", "1")
            roles.add(f"span{int(span) if span.isdigit() else 1}")
            return
        if self.tables:
            return               # nested tabular markup inside a cell: flatten
        if re.fullmatch(r"h[1-6]", tag):
            self.block("#" * int(tag[1]) + " ")
            roles.add("heading")
        elif tag == "figcaption":
            self.block("Caption: ")
        elif tag == "figure":
            if "ltx_figure" in cls:
                self.stats["figures"] += 1
            self.fig += 1
            roles.add("figure")
            self.block()
        elif tag in ("p", "blockquote") or cls & {"ltx_para", "ltx_bibitem"}:
            self.block()
        elif tag == "li":
            self.emit("\n- ")

    def _void(self, tag, a):
        if self.skip or self.math or not self.in_article:
            return
        if tag == "br":
            self.emit(" " if self.cell is not None else "\n")
        elif tag == "img" and self.fig and not self.tables and not self.eq and a.get("src"):
            src = a["src"]
            url = src if re.match(r"https?://", src) else self.base + src.lstrip("./")
            self.emit(f"\n\n![{a.get('alt', '').strip()}]({url})")

    def handle_endtag(self, tag):
        if not self.in_article or tag in VOID:
            return
        while self.stack:
            t, roles = self.stack.pop()
            self._close(roles)
            if t == tag:
                break

    def _close(self, roles):
        if "article" in roles:
            self.in_article = 0
        if "skip" in roles:
            self.skip -= 1
        if "math" in roles:
            self.math -= 1
        if "eqrow" in roles or "eq" in roles:
            self.flush_eq()
        if "eq" in roles:
            self.eq -= 1
            self.emit("\n\n")
        if "cell" in roles and self.cell is not None and self.tables and self.tables[-1]:
            text = re.sub(r"\s+", " ", "".join(self.cell)).strip().replace("|", "\\|")
            span = next((int(r[4:]) for r in roles if r.startswith("span")), 1)
            self.tables[-1][-1].extend([text] + [""] * (span - 1))
            self.cell = None
        if "table" in roles:
            rows = [r for r in self.tables.pop() if any(c for c in r)]
            if rows:
                if self.tables:  # tabular nested in a cell of an outer table: inline it
                    self.emit(" ".join(" ".join(r) for r in rows))
                else:
                    self.out.append("\n\n" + pipe_table(rows) + "\n\n")
        if "heading" in roles:
            self.emit("\n\n")
        if "figure" in roles:
            self.fig -= 1

    def handle_data(self, data):
        if not self.in_article or self.skip or self.math:
            return
        if self.eq:
            tag = data.strip()
            if re.fullmatch(r"\(\S+\)", tag):     # equation number, e.g. (3)
                self.eqtag = tag
            return
        self.emit(re.sub(r"\s+", " ", data))

    def flush_eq(self):
        if self.eqrow:
            self.stats["display_math"] += 1
            line = f"$${' '.join(self.eqrow)}$$" + (f" {self.eqtag}" if self.eqtag else "")
            self.emit("\n" + line + "\n")
        self.eqrow, self.eqtag = [], ""

    def markdown(self):
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"^(#+|-) +", r"\1 ", text, flags=re.M)
        return text.strip() + "\n"


def pipe_table(rows):
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def html_to_markdown(aid):
    url = f"https://arxiv.org/html/{aid}"
    try:
        final, body = fetch(url)
    except urllib.error.HTTPError as e:
        sys.exit(f"arxiv.py: no HTML rendering for {aid} (HTTP {e.code}); try --source -d DIR")
    p = LatexmlToMarkdown(final)
    p.feed(body.decode("utf-8", errors="replace"))
    p.close()
    if not p.out:
        sys.exit(f"arxiv.py: {final} has no LaTeXML article (HTML not available?); try --source -d DIR")
    return p.markdown(), p.stats


def fetch_source(aid, dest):
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"arxiv.py: {dest} is not empty; give a new, empty directory")
    dest.mkdir(parents=True, exist_ok=True)
    _, body = fetch(f"https://arxiv.org/e-print/{aid}")
    try:
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:*") as tf:
            tf.extractall(dest, filter="data")   # refuses absolute paths, .., links out
    except tarfile.ReadError:                   # single gzipped .tex, or a PDF-only submission
        data = gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body
        name = "paper.pdf" if data[:4] == b"%PDF" else "main.tex"
        (dest / name).write_bytes(data)
    files = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())
    tex = [f for f in files if f.endswith(".tex")]
    print(f"{len(files)} files in {dest}; .tex: {', '.join(tex) or 'none'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paper", help="arXiv id or abs/pdf/html URL")
    ap.add_argument("-o", "--output", help="write Markdown here instead of stdout")
    ap.add_argument("--stats", action="store_true", help="print counts only")
    ap.add_argument("--source", action="store_true", help="fetch the LaTeX source instead")
    ap.add_argument("-d", "--dir", help="new empty directory for --source")
    args = ap.parse_args()
    aid = arxiv_id(args.paper)
    if args.source:
        if not args.dir:
            ap.error("--source needs -d DIR")
        fetch_source(aid, args.dir)
        return
    md, stats = html_to_markdown(aid)
    summary = (f"{aid}: {stats['display_math']} display equations, {stats['inline_math']} inline math, "
               f"{stats['tables']} tables, {stats['figures']} figures")
    if args.stats:
        print(summary)
        return
    print(summary, file=sys.stderr)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
