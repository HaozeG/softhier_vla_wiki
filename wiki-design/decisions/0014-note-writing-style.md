---
type: decision
tags: [schema, style, tables, evidence]
sources: [wiki-design/decisions/0006-rename-folder-summary-files-and-plain-language.md, wiki-design/decisions/0007-ascii-diagrams-as-logic-check.md, wiki-design/decisions/0008-obsidian-padded-tables.md, session:paper-research-dataflow]
---
# 0014: Note writing style: structure first, tables, evidence labels

## Context
In a paper-research session the maintainer asked that wiki notes follow the same style as the replies they prefer in chat. That style puts the structure first, uses tables and one ASCII diagram, says plainly what was checked, and leaves open questions explicit. The chat replies also mix Chinese and English. The search index embeds notes with `BAAI/bge-small-en-v1.5`, an English-only model, so Chinese text in notes would weaken `find`. The maintainer chose to adopt the structure in notes and keep note text in English.

## Decision
| Rule                             | What it means in a note                                                                                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Structure before detail          | `## Summary` gives the claim and the layout of the note; the diagram follows it; details come after                                                                      |
| Tables for items with attributes | Lists of papers, options, choices or comparisons go in a table, not prose; padded per [0008](0008-obsidian-padded-tables.md)                                             |
| One diagram for structure        | As in [0007](0007-ascii-diagrams-as-logic-check.md) and 0011                                                                                                             |
| Evidence labels                  | Say what was checked and against what (for example "venue seen in the program page"); mark unchecked items as such; no "iff", "always" or "only" unless a source says it |
| Short sections                   | Short paragraphs and lists; headings that say what the section holds                                                                                                     |
| Open questions explicit          | Unresolved points go in `## Open questions`, not mixed into claims                                                                                                       |
| English text                     | Note text stays English so the English embedding model indexes it; Chinese stays in chat replies                                                                         |

The rules are listed in `CLAUDE.md` (note format) and in the plugin's `wiki` skill (file back), so parent-repo sessions see them.

## Why
Notes written in the style the maintainer reads fastest are easier to review. Evidence labels keep a reader from mistaking an unchecked item for a sourced one, which [0013](0013-scope-and-no-derived-content.md) also requires. Keeping note text English avoids a model swap and a re-index; a multilingual model would be needed before notes could mix languages.
