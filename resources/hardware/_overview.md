# resources/hardware/

Sources on tile-based, inter-core connected and dataflow AI chips: their architecture, the compilers that target them and how workloads are mapped onto them, as opposed to measurements of VLA models on existing hardware (`serving/`).

- [Elk (Liu et al., UIUC and MSR)](elk-icca-compiler.md) — compiler for inter-core connected AI chips with HBM: trades per-core compute, inter-core traffic and off-chip loading; 94.84% of an ideal roofline on an IPU-POD4 emulator; MICRO 2025
