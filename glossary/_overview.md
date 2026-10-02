---
covers: 04924d0eea31
---
# glossary/

Read this right after the README if terms are new; next comes [one VLA call](../knowledge/one-vla-call.md), then the [overview](../knowledge/vla-edge-serving-overview.md). Terms of physical AI so far come mostly from VLA models. Each file has a terms table (Term, Meaning, Scope, Defined in) and explanations below it. Scope `field` is a standard meaning, for newcomers; `convention` is this wiki's own meaning of a field term or symbol, and `project` is defined by a SoftHier-VLA decision; both override general knowledge, and their names are listed at the start of project sessions (look up a definition with `tools/wiki.py glossary "<term>"`) ([wiki-design decision 0012](../wiki-design/decisions/0012-glossary-with-on-demand-lookup.md)).

- [Robot and control loop](robot-and-control-loop.md) — control step, chunk, latency, async, stale and lagged actions
- [Model and attention](model-and-attention.md) — VLA, VLM, action head, tokens, prefix, KV cache, keys and values, decoding, attention kinds
- [Action generation](action-generation.md) — discrete tokens, regression, flow matching, flow steps
- [Hardware and performance](hardware-and-performance.md) — memory-bound versus compute-bound, TOPS, devices, toolchains, batch size, tile, PE, SRAM
- [Compression](compression.md) — quantization names, pruning, distillation, token and step reduction
- [Evaluation and models](evaluation-and-models.md) — benchmarks, GPUs used as reference, one-line identities of the models (no sizes or speeds), evidence tags
- [Symbols and conventions](symbols-and-conventions.md) — H, n, K, T, l, dt, Δ, g, L, N, Hz, and the grouped D, d, f_c, P, E
- [Project terms](project-terms.md) — terms specific to SoftHier-VLA (SoftHier so far; no decisions define terms yet)
