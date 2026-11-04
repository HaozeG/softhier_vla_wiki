---
type: concept
tags: [paper-map, reading-tracker, dataflow, tile-based, compiler, mapping, softhier]
sources: [session:paper-research-dataflow, softhier-and-the-project.md, https://www.iscaconf.org/isca2025/program/, https://www.iscaconf.org/isca2026/program/, https://microarch.org/micro58/program/, https://microarch.org/micro59/program/, https://2026.hpca-conf.org/program/program-hpca-2026/, https://www.asplos-conference.org/asplos2026/program/]
---
# Paper map: tile-based dataflow hardware, compilers and mapping

## Summary
A reading map and tracker for architecture-venue papers (ISCA, ASPLOS, MICRO, HPCA; window 2023 to 2026) on three topics the user set: tile-based or dataflow hardware, compilation for it, and mapping workloads onto it. The map is kept here because the project targets [SoftHier](softhier-and-the-project.md), a tile-based many-PE chip. Each topic splits into themes; each theme lists anchor papers. A paper's venue counts as verified only when it was seen in that conference's published program (URLs in `sources:`). Status moves from `candidate` to `read` when a `resources/` note exists for it. The "Working ideas" section is the user's request (a file to track ideas while reading) and is the only place in this note for opinion or project implications.

```text
                    tile-based / dataflow AI chips
                                 |
       +-------------------------+-------------------------+
       |                         |                         |
  [A] Hardware             [B] Compilation           [C] Workload mapping
  A1 tile/mesh arrays      B1 tile-level IR,         C1 intra-op: GEMM,
     + local SRAM             dataflow planning         attention on a mesh
  A2 NoC + collectives     B2 fusion across          C2 inter-layer and
  A3 wafer / chiplet          ops and cores             pipeline scheduling
  A4 CGRA / reconfig.      B3 cost models,           C3 LLM serving:
  A5 memory-centric           mappers, simulators       prefill/decode, MoE
     (3D DRAM, PIM)        B4 MLIR flows (AIE,       C4 embodied / VLA
                              wafer, CGRA)              on accelerators
       |                         |                         |
       +---- recurring across all three: on-chip network, -+
             no shared cache level, sync, data movement
```

## Details

### Scope (set by the user)
| Choice     | Setting                                                    |
| ---------- | ---------------------------------------------------------- |
| Venues     | ISCA, ASPLOS, MICRO, HPCA only; no second tier             |
| Window     | 2023 to 2026, trend first, then deep reads of a few papers |
| Chip scale | Single chip, wafer-scale and chiplet all included          |
| Workload   | Inference only for now                                     |
| CGRA       | Lower priority; read for ideas                             |

### Verified anchors by theme
Venue and year below come from the conference program pages. "arXiv" marks adjacent work outside the four venues, kept because it targets SoftHier-like chips directly.

| Theme | Paper                                                                                                   | Venue       |
| ----- | ------------------------------------------------------------------------------------------------------- | ----------- |
| A1    | M100: An Orchestrated Dataflow Architecture Powering General AI Computing                               | ISCA 2026   |
| A1    | NUPEA: Optimizing Critical Loads on Spatial Dataflow Architectures via Non-Uniform PE Access            | ISCA 2025   |
| A1    | RAIL: A Reconfigurable Spatial Accelerator for Linear-Time Sequence Model Inference                     | MICRO 2026  |
| A2    | Evaluating Ruche Networks: Physically Scalable, Cost-Effective, Bandwidth-Flexible NoCs                 | ISCA 2025   |
| A2    | Hermes: Architecting Congestion Management for Large-Scale NoCs                                         | MICRO 2026  |
| A2    | Software Prefetch Multicast: Sharer-Exposed Prefetching for Bandwidth Efficiency in Manycore Processors | MICRO 2025  |
| A3    | WSC-LLM: Efficient LLM Service and Architecture Co-exploration for Wafer-scale Chips                    | ISCA 2025   |
| A3    | FRED: A Wafer-scale Fabric for 3D Parallel DNN Training                                                 | ISCA 2025   |
| A3    | Mapping and Communication Optimizations with Fault Tolerance for Wafer-Scale LLM Inference              | ISCA 2026   |
| A3    | TEMP: A Memory Efficient Physical-aware Tensor Partition-Mapping Framework on Wafer-scale Chips         | HPCA 2026   |
| A3    | MoEntwine: Unleashing the Potential of Wafer-scale Chips for Large-scale Expert Parallel Inference      | HPCA 2026   |
| A3    | COMET: Communication and Memory Co-Design for Fine-Grained AI Inference in MCM Accelerators             | HPCA 2026   |
| A4    | Neura: A Unified Framework for Hierarchical and Adaptive CGRAs                                          | ASPLOS 2026 |
| A4    | FexMo: Enabling Fuse Execution Mode for Multi-task CGRAs                                                | MICRO 2025  |
| A4    | Capstone: Power-Capped Pipelining for CGRA Compilers                                                    | MICRO 2026  |
| A5    | H2-LLM: Hardware-Dataflow Co-Exploration for Hybrid-Bonding-based Low-Batch LLM Inference               | ISCA 2025   |
| B1    | CODO: An Automated Compiler for Comprehensive Dataflow Optimization                                     | ISCA 2026   |
| B1    | ELK: Exploring the Efficiency of Inter-core Connected AI Chips with DL Compiler Techniques              | MICRO 2025  |
| B1    | StreamTensor: Make Tensors Stream in Dataflow Accelerators for LLMs                                     | MICRO 2025  |
| B1    | Trinity: Three-Dimensional Tensor Program Optimization via Tile-level Equality Saturation               | ASPLOS 2026 |
| B1    | Dynamic Scheduling for AI Accelerators via TISA                                                         | ISCA 2026   |
| B2    | FuseFlow: A Fusion-Centric Compilation Framework for Sparse DL on Streaming Dataflow                    | ASPLOS 2026 |
| B2    | RedFuser: Automatic Operator Fusion for Cascaded Reductions on AI Accelerators                          | ASPLOS 2026 |
| B2    | TransFusion: End-to-End Transformer Acceleration via Graph Fusion and Pipelining                        | MICRO 2025  |
| B2    | SFD: Towards Segment Fusion Dataflow for Spatial Accelerators                                           | HPCA 2026   |
| B3    | LLMulator: Generalizable Cost Modeling for Dataflow Accelerators                                        | MICRO 2025  |
| B3    | The Turbo-Charged Mapper: Fast and Optimal Mapping for Accelerator Design                               | MICRO 2026  |
| B3    | Lotus: A Task Dataflow Architecture for Cycle-Level Simulation                                          | ISCA 2026   |
| B4    | An MLIR Lowering Pipeline for Stencils at Wafer-Scale                                                   | ASPLOS 2026 |
| C1    | SystolicAttention: Fusing FlashAttention within a Single Systolic Array                                 | MICRO 2026  |
| C1    | SNECKO: Efficient GEMM Mapping on Versal ACAP Heterogeneous Spatial Architecture                        | MICRO 2026  |
| C1    | MeshSlice: Efficient 2D Tensor Parallelism for Distributed DNN Training                                 | ISCA 2025   |
| C2    | Crane: Inter-Layer Scheduling Framework for DNN Inference and Training on Tiled Architecture            | MICRO 2025  |
| C2    | MLX: Multi-Layer Execution for Structured LLM Workload Acceleration on Spatial Architectures            | ISCA 2026   |
| C3    | FACE: Fully PD Overlapped Scheduling and Multi-Level Architecture Co-Exploration on Wafer               | HPCA 2026   |
| C3    | Topology-Aware Virtualization over Inter-Core Connected Neural Processing Units                         | ISCA 2025   |
| C4    | Deltoris: Real-time VLA Inference via Bit-level Sparsity and Speculative Inference                      | MICRO 2026  |
| C4    | SpecVLA: Efficient Robotic Manipulation via Speculative VLA Inference and Verification                  | MICRO 2026  |
| C4    | VQVLA: Motion-Aware Vector Quantization with Computation Fusion for VLA Acceleration                    | MICRO 2026  |
| C4    | DiTPA: A DiT-based Action Planner Accelerator for Embodied AI                                           | ISCA 2026   |
| C4    | Dadu-Corki: Algorithm-Architecture Co-Design for Embodied AI-powered Robotic Manipulation               | ISCA 2025   |
| C4    | HiPER: Hierarchically-Composed Processing for Efficient Robot Learning-Based Control                    | ISCA 2025   |

Adjacent work on SoftHier-like chips, venue not verified here: FlatAttention (arXiv 2505.18824, extended as 2604.02110, which describes the SoftHier simulator on GVSoC), Design in Tiles, GEMM on tile-based many-PE chips (arXiv 2512.13638), WaferLLM (OSDI 2025), TileLoom (arXiv 2512.22168), Loom, "Schedules Are Solvable Symbols" (arXiv 2609.29219), and a collective-capable NoC paper (arXiv 2603.26438, MLSys 2026 proceedings).

### Earlier anchors (2023 to 2025)
| Theme | Paper                                                                                                       | Venue      |
| ----- | ----------------------------------------------------------------------------------------------------------- | ---------- |
| A1    | SambaNova SN40L: Scaling the AI Memory Wall with Dataflow and Composition of Experts                        | MICRO 2024 |
| A1    | Stellar: An Automated Design Framework for Dense and Sparse Spatial Accelerators                            | MICRO 2024 |
| A1    | Si-Kintsugi: Recovering Golden-Like Performance of Defective Many-Core Spatial Architectures for AI         | MICRO 2023 |
| A1    | SPD: Open-Source RISC-V Manycore with Scalable Resource Organization                                        | ISCA 2024  |
| A1    | LEGO: Spatial Accelerator Generation and Optimization for Tensor Applications                               | HPCA 2025  |
| A2    | Ring Road: A Scalable Polar-Coordinate-based 2D Network-on-Chip Architecture                                | MICRO 2024 |
| A2    | Push Multicast: A Speculative and Coherent Interconnect for Manycore CPU Communication                      | HPCA 2025  |
| A3    | Waferscale Network Switches                                                                                 | ISCA 2024  |
| A4    | MapZero: Mapping for CGRAs with Reinforcement Learning and Monte-Carlo Tree Search                          | ISCA 2023  |
| A4    | Pipestitch: An Energy-Minimal Dataflow Architecture with Lightweight Threads                                | MICRO 2023 |
| A4    | Tyr: Taming Dataflow Parallelism for Better Locality                                                        | MICRO 2024 |
| B2    | TileFlow: A Framework for Modeling Fusion Dataflow via Tree-based Analysis                                  | MICRO 2023 |
| B2    | FuseMax: Leveraging Extended Einsums to Optimize Attention Accelerator Design                               | MICRO 2024 |
| B3    | Mind the Gap: Attainable Data Movement and Operational Intensity Bounds for Tensor Algorithms               | ISCA 2024  |
| B3    | Soter: Analytical Tensor-Architecture Modeling and Automatic Tensor Program Tuning for Spatial Accelerators | ISCA 2024  |
| B3    | The Dataflow Abstract Machine Simulator Framework                                                           | ISCA 2024  |
| B3    | LLMCompass: Enabling Efficient Hardware Design for Large Language Model Inference                           | ISCA 2024  |
| B3    | SoMA: DRAM Communication Scheduling Space for DNN Accelerators                                              | HPCA 2025  |
| C2    | Inter-layer Scheduling Space Definition and Exploration for Tiled Accelerators                              | ISCA 2023  |
| C2    | EDA: Energy-Efficient Inter-Layer Model Compilation for Edge DNN Inference Acceleration                     | HPCA 2025  |
| C3    | SCAR: Scheduling Multi-Model AI Workloads on Heterogeneous Multi-Chiplet Module Accelerators                | MICRO 2024 |
| C3    | Hardware-Assisted Virtualization of Neural Processing Units for Cloud Platforms                             | MICRO 2024 |
| C4    | Tartan: Microarchitecting a Robotic Processor                                                               | ISCA 2024  |
| C4    | RoboShape: Using Topology Patterns to Scalably and Flexibly Deploy Accelerators Across Robots               | ISCA 2023  |
| C4    | Dadu-RBD: Robot Rigid Body Dynamics Accelerator with Multifunctional Pipelines                              | MICRO 2023 |

Programs not obtained (page missing, blocked, or redirected to the 2026 program): ASPLOS 2023 to 2025, HPCA 2023 and 2024. Titles from those are not in either table.

### What the program titles show, by year
Read off the titles above; a title count, not a reading of the papers.

| Year | Visible in titles                                                                                                                                                        |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2023 | Scheduling and mapping for tiled and CGRA accelerators (inter-layer scheduling, MapZero); robot-specific accelerators (RoboShape, Dadu-RBD)                              |
| 2024 | Models and bounds for data movement (Mind the Gap, Soter, LLMCompass); a commercial dataflow chip (SN40L); fusion modelled for attention (FuseMax)                       |
| 2025 | LLM work dominates; wafer-scale appears (three ISCA papers); compilers for inter-core connected chips (ELK, StreamTensor); inter-layer scheduling continues (Crane, EDA) |
| 2026 | Wafer-scale is a cluster (about six HPCA papers); fusion across operators and cores (FuseFlow, RedFuser, SFD); VLA accelerators appear (MICRO, ISCA)                     |

### Trends (working summary, user-requested, revised in place)
Each trend lists the papers it rests on, so it can be checked and revised. "Basis" says how far the evidence goes: `titles` means program titles only; it becomes `read` once a supporting paper has a `resources/` note. Revise rows in place; git history keeps earlier versions.

| ID  | Trend                                                                                                   | Evidence (paper, venue)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Basis  |
| --- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| T1  | Wafer-scale chips become a main target for mapping and scheduling, mostly for LLMs                      | Waferscale Network Switches (ISCA 2024); WSC-LLM, FRED, PD Constraint-aware Topology Co-Design for Network on Wafer, Cramming a Data Center into One Cabinet (ISCA 2025); Mapping and Communication Optimizations with Fault Tolerance for Wafer-Scale LLM Inference, ConBin (ISCA 2026); WATOS, FACE, TEMP, MoEntwine, ReThermal, HDPAT (HPCA 2026); Ouroboros, MLIR Lowering Pipeline for Stencils at Wafer-Scale (ASPLOS 2026); Beyond Linear Scaling for LLM Training on Wafer-Scale GPUs (MICRO 2026) | titles |
| T2  | 2023 to 2024 work models and bounds data movement on spatial accelerators                               | TileFlow (MICRO 2023); Mind the Gap, Soter, Dataflow Abstract Machine Simulator, LLMCompass (ISCA 2024); FuseMax (MICRO 2024)                                                                                                                                                                                                                                                                                                                                                                              | titles |
| T3  | From 2025, compilers target inter-core connected and dataflow chips and fuse across operators and cores | ELK, StreamTensor, TransFusion (MICRO 2025); CODO, Dynamic Scheduling via TISA (ISCA 2026); FuseFlow, RedFuser, Trinity (ASPLOS 2026); SFD (HPCA 2026)                                                                                                                                                                                                                                                                                                                                                     | titles |
| T4  | Scheduling across layers on tiled arrays continues through the whole window                             | Inter-layer Scheduling Space for Tiled Accelerators (ISCA 2023); EDA (HPCA 2025); Crane (MICRO 2025); MLX (ISCA 2026); SFD (HPCA 2026)                                                                                                                                                                                                                                                                                                                                                                     | titles |
| T5  | On-chip network traffic, multicast in particular, becomes a design target                               | Ring Road (MICRO 2024); Push Multicast (HPCA 2025); Ruche Networks (ISCA 2025); Software Prefetch Multicast (MICRO 2025); Hermes (MICRO 2026)                                                                                                                                                                                                                                                                                                                                                              | titles |
| T6  | Robot accelerators move from kinematics and planning kernels to learned policies and VLA models         | RoboShape, RoSE, Energy-Efficient Realtime Motion Planning (ISCA 2023); Dadu-RBD (MICRO 2023); Tartan (ISCA 2024); Dadu-Corki, HiPER (ISCA 2025); DiTPA, Accelerator Polymorphism with Robotics (ISCA 2026); Deltoris, SpecVLA, VQVLA, UDYR, Arborist (MICRO 2026)                                                                                                                                                                                                                                         | titles |
| G1  | Gap: no title in the checked programs maps a VLA model onto a tile-based dataflow chip                  | Absence across all checked programs; no T6 title names a tile-based dataflow target                                                                                                                                                                                                                                                                                                                                                                                                                        | titles |

### Reading tracker
| Paper | Venue (verified?) | Theme | Status | Notes |
| ----- | ----------------- | ----- | ------ | ----- |
| -     | -                 | -     | -      | -     |

## Working ideas (user-requested)
Ideas and project links noted while reading; not source claims.

- The user's working view: the core concern for VLA on SoftHier is latency.
- The user's working view: the compiler IR is likely tile-level (open; compare tile-level and stream-level IRs while reading).

## Open questions
- Which papers form the first deep-read batch.
