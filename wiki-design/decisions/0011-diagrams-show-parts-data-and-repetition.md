---
type: decision
tags: [schema, diagrams, quality, ascii]
sources: [wiki-design/decisions/0007-ascii-diagrams-as-logic-check.md, resources/models/smolvla.md, session:diagram-review]
---
# 0011: A diagram must show the parts, the data between them, and what repeats

## Context
[0007](0007-ascii-diagrams-as-logic-check.md) required a diagram that matches the text. Reviewing the first SmolVLA diagram showed that matching the text is not enough: the three input lines joined at different columns, the arrow from the model to the action expert was labelled only "features from the N layers", the expert's inputs and outputs were missing, and the 10 flow steps were a sentence, not a loop. A reader still had to rebuild the structure from the paragraph, which is what the diagram is for. Redrawing it also sent the author back to the first-party code, which showed things the paper text left out (the expert's self-attention layers also see the cached prefix; the expert's key and value projections are recomputed in every step).

## Decision
A diagram must let a reader answer three questions without reading the paragraph: **what are the parts, what data passes between them and how big is it, and what repeats or happens in what order.**
```text
parts       boxes (components); mechanisms inside the box they belong to
data        arrows labelled with what moves and its size
            ("241 prefix tokens", "keys + values per LLM layer", "50 tokens")
repeats     a drawn loop marked xN, and a visible split between work done
            once per call and work done per step
direction   one flow direction, top to bottom or left to right
```
- Every number in a diagram also appears in the note's text, with its source. If the diagram needs a fact the text lacks, add it to the text first (from the source note) and cite it.
- If a question cannot be answered from the diagram, the text is probably missing that fact too: find it in the source (paper, first-party code) and add it to both.
- Level of detail: structure and data flow in the diagram; configuration details (padding, resolutions) stay in the text.
- Build boxed diagrams in code: `tools/diagram.py` places boxes and text by column and row, so edges line up. `check` reports a `DIAGRAM` error when the side edges of a box do not line up between its top and bottom edge.
- Every diagram is built this way, not only flows: number lines, bar charts, timelines, trees and column layouts use `Canvas` too (`table`, `bar`, `tree`, `lines`), so columns and ticks are computed, not typed. The data and repetition rules apply wherever something flows or repeats. Ordinary markdown tables stay tables.

## Why
The purpose of a diagram is to cut the effort of inferring the logical structure from a block of text. A box-and-arrow picture that omits the data on the arrows, or the repetition, only restates the part list. Requiring the data and the loop also exposes missing facts in the text (what actually crosses between two components), which is the second purpose from 0007: drawing as a check on the prose. Generated layout removes hand-spacing drift, and a lint keeps it from coming back.

Refines [0007](0007-ascii-diagrams-as-logic-check.md); example: the SmolVLA diagram in `knowledge/smolvla.md`.
