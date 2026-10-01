---
type: decision
tags: [naming, schema, plain-language]
sources: [wiki-design/decisions/0001-wiki-layout-and-search.md, wiki-design/decisions/0002-lint-and-git-as-log.md, session:sidecar-rename]
---
# 0006: Rename folder summary files; prefer plain words

## Context
[0001](0001-wiki-layout-and-search.md) and [0002](0002-lint-and-git-as-log.md) called each folder's two companion files "sidecars" and named them `.abstract.md` and `.overview.md`. The maintainer asked what "sidecar" meant and asked for a more straightforward name. Problems with the old names: the word is jargon, and the leading dot hides the files from `ls` and file trees.

## Decision
- The files are `_abstract.md` (short summary) and `_overview.md` (summary plus catalog of the folder's notes). The prefix `_` keeps them visible and sorted first, and cannot collide with a real note name.
- In prose and messages they are called "folder summary files", not "sidecars".
- Plain words are preferred over jargon in file names, tool messages, notes and replies; an unavoidable term is defined where it first appears. This rule is in `CLAUDE.md` so that sessions started in the parent repo follow it too.
- 0001 and 0002 stay as written (they are history); their file names and the word "sidecar" there are superseded by this note.

## Why
Names that say what a file is are easier for people and agents to find and use. `_abstract.md` and `_overview.md` reuse plain words that were already in use, so `stamp`, `check`, `ls`, `find` and the plugin hook only needed the name changed in one constant.
