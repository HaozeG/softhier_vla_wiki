# memories/status/

**Current state.** SmolVLA runs end to end on simulated SoftHier (GVSoC with a ten-patch series, compiled by softhier-mlir) and matches its golden reference in the published one-camera configuration; the LIBERO two-camera latency exists only as an estimate from partial runs, and the LIBERO checkpoint's success rate was measured on a GPU. Details and labels: [Basic integration of components](basic-integration-of-components.md). The model's needs are now stated (operator graph, compiler walk-through, four research questions), ([Analyzing the needs of one model: SmolVLA](analyzing-the-needs-of-one-model-smolvla.md)). Stage 1 fixed its hardware (H1, an 8 x 8 mesh) and workload (W1, SmolVLA on three VLABench cameras), measured every operator as a checked hand-written kernel on H1, and composed 29.0 ms per call at 22.0 % MFU (estimate); vision takes half the time and the action expert has the lowest MFU: [Stage-1 kernel baseline on H1: SmolVLA](stage-1-kernel-baseline-on-h1-smolvla.md).

**Rules** ([status and patch logs](../../wiki-design/decisions/2026-11-12-status-and-patch-logs.md)):
- One entry (note type `status`) per theme of work. Title it by theme, never by date or pull-request number, for example "Basic integration of components" or "Analyzing the needs of one model: SmolVLA".
- The order of the catalog below is the sequence: a new entry goes at the end. Frontmatter `follows:` names the previous entry and `superseded_by:` the entry that replaces it (file names in this folder).
- Every claim sits in the entry's `## Evidence` table with its label (`measured`, `estimate` or `inference`, as the [glossary](../../glossary/evidence.md) defines them) and its source: a commit-pinned permalink into the code repository, or a wiki note.
- An outdated entry is not deleted: set `superseded_by:`, say so in its first summary line, and keep it in the catalog.
- No dates in entries: git gives them (`tools/wiki.py history <entry>`).
- Update the current-state paragraph above whenever an entry is added or superseded.

**Catalog (in sequence)**
- [Basic integration of components](basic-integration-of-components.md) — simulator, compiler, golden reference and LIBERO evaluation joined; SmolVLA latency on simulated SoftHier (published configuration measured, LIBERO estimated) and LIBERO success rate on GPU.
- [Analyzing the needs of one model: SmolVLA](analyzing-the-needs-of-one-model-smolvla.md) — operator graph with compute and bytes per operator, compiler walk-through, research questions, and a composed baseline from hand-written kernels (79.2 ms, estimate; baseline superseded).
- [Stage-1 kernel baseline on H1: SmolVLA](stage-1-kernel-baseline-on-h1-smolvla.md) — H1 hardware and W1 workload fixed, every kernel measured on H1 with outputs checked, composed 29.0 ms per call at 22.0 % MFU (estimate).
