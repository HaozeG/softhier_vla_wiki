---
type: decision
tags: [schema, glossary, plugin]
sources: [wiki-design/decisions/0003-claude-code-plugin.md, wiki-design/decisions/0009-separate-project-knowledge-from-wiki-design.md, session:glossary-design]
---
# 0012: A grouped glossary, with project terms loaded by the plugin

## Context
A newcomer test showed the wiki used terms (memory-bound, KV cache, flow matching) before defining them, so a first glossary note was added. That fixes newcomers but not a second problem: as the project designs its own mappings and schedules it will define its own words, and the wiki already uses some terms in a local sense (for example "balance point" for what papers call the ridge point, and L for two different counts). A model working in the parent repo that has not read those definitions will fall back on general knowledge and mislead. The glossary must therefore be part of the design, and the parts that must not be guessed must reach the model without it having to look.

## Decision
```text
glossary/                    project side, one file per group
  robot-and-control-loop  model-and-attention  action-generation
  hardware-and-performance  compression  evaluation-and-models
  symbols-and-conventions  project-terms
        |
        | every term row has a scope
        v
  field        standard meaning, for newcomers: looked up on demand
  convention   the wiki's own meaning of a field term or symbol
  project      defined by a SoftHier-VLA decision
        |
        | convention + project rows only
        v
  plugin SessionStart hook: injected as `term: meaning [defined in]`
```
- **Definitions only.** A row is a concise, accurate, conceptual definition. It carries no measured or derived numbers, worked examples, findings or model catalogs; those belong in `knowledge/` and `resources/`, and the row links to them. `check` reports a `GLOSSARY` error when a meaning contains a number.
- Each group file is a `glossary` note: `## Summary`, then `## Terms` with a table `Term | Meaning | Scope | Defined in`, then optional explanations. `Defined in` links to the note or decision that defines the term; `check` reports a `GLOSSARY` error for a missing scope or a link that does not resolve.
- The plugin hook injects the convention and project rows before the recent-changes list, and the instruction that they override general knowledge. When the context budget is tight the recent changes are cut, never the glossary. `check` reports `GLOSSARYSIZE` when those rows exceed 3000 characters, so they cannot be truncated silently: keep meanings to one line, and give standard terms scope `field`.
- `tools/wiki.py glossary "<term>"` looks a term up; `glossary --loaded` prints what the hook injects.
- **Defining a term is part of the design.** Project terms go in [project-terms](../../glossary/project-terms.md). A decision that introduces or redefines a term lists it in its `defines:` frontmatter and adds a project row to `glossary/project-terms.md` in the same commit; `check` reports `DEFINES` if the row is missing. A source that brings a new field term adds a `field` row to the right group.
- The sessions that read the wiki are told to check the glossary before designing and to add rows when they define something (`CLAUDE.md`, plugin skill, runbooks).
- Claude's own personal memory is not a place for these definitions; they live in the committed wiki.

## Why
Putting the load-bearing definitions in front of the model removes the failure where a new local meaning loses to a familiar general one, and keeping the loaded set small and checked keeps it from crowding out the rest of the session context. Grouping and scoping let newcomers have the full vocabulary while projects load only what could mislead. Revisit if the loaded set approaches the budget (move or shorten terms) or if sessions still misuse a term (add a hook-side nudge).

Builds on [0003](0003-claude-code-plugin.md) and [0009](0009-separate-project-knowledge-from-wiki-design.md).
