---
type: entity
tags: [softhier, project, scope, start-here]
sources: [session:parent-readme, https://github.com/pulp-platform/softhier-sdk, https://github.com/gvsoc/gvsoc/tree/soft_hier_release]
---
# SoftHier and the SoftHier-VLA project

## Summary
The project wants to map VLA applications for physical AI onto a tile-based many-PE chip like [SoftHier](https://github.com/pulp-platform/softhier-sdk): it is a repository for exploring that mapping (the project README). Its three goals, listed below, are an MLIR-based deployment toolchain, workload analysis, and aiming for high utilization with a scheduling layer in software. A PE (processing element) is one compute unit, so a many-PE chip has many of them, and tile-based says the chip is organised in tiles. The README states no compute or latency target. This note records only what the README states; the rest of the wiki covers the VLA side, starting with [one VLA call](one-vla-call.md).

## Goals
The README lists three goals:
1. MLIR-based deployment toolchain. MLIR is a compiler framework (standard meaning, not spelled out in the README).
2. Workload analysis: what a VLA application asks of a chip. The [VLA architecture overview](vla-architecture-overview.md) and [one VLA call](one-vla-call.md) are the current starting points.
3. Aim for MFU, with a scheduling layer in software (the README line is unfinished). MFU is the share of the chip's peak arithmetic rate that a model's work actually uses (standard meaning, not spelled out in the README).

## Hardware overview (current status)
From the architecture figure of the SoftHier model on the `soft_hier_release` branch of GVSoC (`docs/figures/SoftHier_Arch.png`); the figure's labels only.
```text
HBM (top)
 +-----+-----+-----+-----+
 | R+T | R+T | R+T | R+T |   R = router of the data NoC and sync NoC
 +-----+-----+-----+-----+   T = tile (one TE cluster)
 | R+T | R+T | R+T | R+T |
 +-----+-----+-----+-----+   HBM on all four edges (left, right,
 | R+T | R+T | R+T | R+T |   top, bottom), reached through the
 +-----+-----+-----+-----+   edge routers
 | R+T | R+T | R+T | R+T |
 +-----+-----+-----+-----+

TE cluster (inside each tile)
 I$ (instruction cache)
 [Vector Engine | Core 0..n | Matrix Engine | DMA]
 Interconnect --- to SYNC NoC router; DMA --- to DATA NoC router
 L1 local memory
```
- **Chip:** a 2D grid of tiles (the figure draws 4 by 4), each with one router; neighbouring routers are linked in a mesh.
- **Two networks:** a data NoC (orange arrows) and a separate sync NoC (green dashed arrows); each router has a data part and a sync part.
- **Off-chip memory:** HBM blocks along all four edges of the grid.
- **Inside a tile (TE cluster):** an instruction cache, a vector engine, several cores (Core 0 to Core n), a matrix engine, a DMA engine, an interconnect, and an L1 local memory.
- **Memory hierarchy as drawn:** L1 local memory per tile, then HBM at the edge; no other level is shown. The DMA connects to the data NoC; the cluster interconnect connects to the sync NoC.
- **Not in the figure:** sizes, bandwidths, number of cores per tile, engine throughput and the routing scheme.

## Terms
- **SoftHier:** the tile-based many-PE chip the project maps VLA applications to; the SDK is at https://github.com/pulp-platform/softhier-sdk.
- **PE (processing element):** one compute unit of a many-PE chip.
- **Tile (of a tile-based chip):** the unit the chip is organised in.
- **SRAM:** static random-access memory, the fast memory on a chip itself (standard meaning, not from the README).
