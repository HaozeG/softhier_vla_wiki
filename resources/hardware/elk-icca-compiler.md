---
type: paper
tags: [compiler, inter-core-connected, dataflow, hbm, scheduling, mesh, recent]
sources: [arxiv:2507.11506, https://arxiv.org/abs/2507.11506, https://doi.org/10.1145/3725843.3756064, https://github.com/platformxlab/elk]
---
# Elk: Exploring the Efficiency of Inter-core Connected AI Chips with Deep Learning Compiler Techniques

Liu, Xue, Crawford, Xue, Huang (UIUC and Microsoft Research). MICRO 2025 (venue seen in the MICRO 2025 program and on the paper's ACM reference line). arXiv 2507.11506 v2. Code: github.com/platformxlab/elk.

## Summary
Draft in progress (in-depth reading); filled after the last section.

## Key claims

### Problem and approach (Abstract, §1, Fig. 1)
- **ICCA chip (inter-core connected AI chip):** many cores, each with a local SRAM scratchpad; inter-core links let a core read another core's SRAM directly, so all local SRAMs form one software-managed distributed memory. HBM controllers attach to the same on-chip interconnect (Fig. 1).
- **Example given (§1):** Graphcore IPU, 1472 cores × 624 KB = 896 MB on-chip SRAM; each core reads another core's SRAM at 5.5 GB/s, about 8 TB/s all-to-all in aggregate. The paper contrasts this with an A100 (60 MB total cache, 2 TB/s HBM). Other chips it lists as having inter-core interconnect: SambaNova SN40, Cerebras WSE, Meta MTIA, NVIDIA H100.
- **Why HBM is needed (§1):** on-chip SRAM is limited, so large models keep parameters in off-chip HBM, whose bandwidth scales more slowly than compute.
- **Contrast with chips without inter-core links (§1):** there, cores work independently and a separate global SRAM handles all off-chip loading. On an ICCA chip software shares data between cores without a global SRAM, and the distributed SRAM can hold several operators, so the chip can preload future operators' data while executing the current one. This needs each core's SRAM to be split for double buffering, which costs memory footprint.
- **Three performance factors (Abstract, §1):** compute (per-core execution), communication (inter-core data exchange) and I/O (off-chip loading). The abstract calls their interaction "a fundamental tussle"; §1 names three resource contentions (Fig. 2): SRAM capacity, interconnect bandwidth, SRAM access.
- **Gap claimed (§1):** compilers that tune tile size optimize compute and off-chip access volume but ignore inter-core communication; ICCA compilers such as T10 optimize per-core execution and inter-core communication but not off-chip memory access.
- **Key insight (§1):** each factor maps to a compiler parameter: execution-space size ↔ per-core speed; number of preloaded operators ↔ HBM bandwidth utilization; per-operator preload space ↔ inter-core exchange overhead (shared data can be duplicated on cores in advance instead of fetched on demand).
- **Method outline (§1):** a two-level search, exhaustive over the number of preloaded operators, then an iterative greedy memory allocation; preload reordering delays large operators and avoids interconnect "rush hours", with the reorder search bounded by edit distance.
- **Evaluation outline (Abstract, §1):** an emulator built on a real IPU-POD4 and a simulator covering several inter-core topologies; LLMs and diffusion models; 94% of ideal roofline performance on average. Contributions include what the authors call the first ICCA chip simulator and an open-source release.

## Related
