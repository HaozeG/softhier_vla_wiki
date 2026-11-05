# knowledge/

Synthesis of what the sources say about physical AI; VLA models are the first covered area (further areas get their own notes), with a focus on how they are built. Each note cites `resources/` notes. Start with the frame notes below (SoftHier, VLA, WAM), with the glossary (`../glossary/_overview.md`) open for new words.

## Frame

- [Physical AI map](physical-ai-map.md) — the areas of physical AI (from the Embodied-AI-Guide), where each wiki note sits, and areas with no note yet
- [SoftHier and the project](softhier-and-the-project.md) — what the project README says: mapping VLA applications to a tile-based many-PE chip; goals
- [One VLA call, step by step](one-vla-call.md) — start here: plain-language walkthrough of one call, with one picture
- [VLA architecture overview](vla-architecture-overview.md) — components, action heads, reference models
- [Paper map: tile-based dataflow hardware, compilers and mapping](dataflow-hw-paper-map.md) — ISCA/ASPLOS/MICRO/HPCA themes and verified anchors for the SoftHier side; reading tracker
- [World action models (WAM)](wam-overview.md) — definition, taxonomy and cost model from one survey; other WAM definitions open

## Reference

- [Imitation learning and behaviour cloning](imitation-learning-and-behaviour-cloning.md) — BC, compounding error, multimodal demos; why chunking and generative heads
- [Action representation and chunking](action-representation-and-chunking.md) — tokens vs regression and CVAE vs diffusion and flow; chunk size, ensembling
- [SmolVLA](smolvla.md) — the reference small VLA, its data flow and sizes
- [Dual-system VLA](dual-system-vla.md) — System 1 and System 2 as separate networks at different rates; contrast with SmolVLA; the full chain down to System 0 (IK or OSC on arms, a learned tracker on humanoids) and how the interface affects latency
- [Fast policy trained by RL](fast-policy-trained-by-rl.md) — RL Token, Real-Time EXPO-FT and π*0.6: where RL enters a VLA
- [Simulation benchmarks](simulation-benchmarks.md) — task-success benchmarks (LIBERO, CALVIN, Meta-World, VLABench): what each tests and reports; VLABench's knowledge and long-horizon tasks where fine-tuned VLAs score low
- [Benchmark workloads](vla-benchmark-workloads.md) — five VLAs profiled at batch 1 on one stack: stage latency, memory- vs compute-bound, Jetson sensitivity, closed-loop overlap; compared with VLA-HWBench (18 models, Jetson Thor and AMD, seven stages, staged optimizations)
- [Low-level policy loop](low-level-policy-loop.md) — a 50 Hz one-action-per-call joint policy (microduck): inputs, tick, CPU vs NPU, camera placement
