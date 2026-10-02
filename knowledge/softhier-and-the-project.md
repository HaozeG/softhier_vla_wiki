---
type: entity
tags: [softhier, project, scope, start-here]
sources: [session:parent-readme, https://github.com/pulp-platform/softhier-sdk]
---
# SoftHier and the SoftHier-VLA project

## Summary
The project wants to map VLA applications for physical AI onto a tile-based many-PE chip like [SoftHier](https://github.com/pulp-platform/softhier-sdk): it is a repository for exploring that mapping (the project README). Its three goals, listed below, are an MLIR-based deployment toolchain, workload analysis, and aiming for high utilization with a scheduling layer in software. A PE (processing element) is one compute unit, so a many-PE chip has many of them, and tile-based says the chip is organised in tiles. The README states no compute or latency target. This note records only what the README states; the rest of the wiki covers the VLA side, starting with [one VLA call](one-vla-call.md).

## Goals
The README lists three goals:
1. MLIR-based deployment toolchain. MLIR is a compiler framework (standard meaning, not spelled out in the README).
2. Workload analysis: what a VLA application asks of a chip. The [VLA edge serving overview](vla-edge-serving-overview.md) and the notes it lists collect what the sources report about this.
3. Aim for MFU, with a scheduling layer in software (the README line is unfinished). MFU is the share of the chip's peak arithmetic rate that a model's work actually uses (standard meaning, not spelled out in the README).

## Terms
- **SoftHier:** the tile-based many-PE chip the project maps VLA applications to; the SDK is at https://github.com/pulp-platform/softhier-sdk.
- **PE (processing element):** one compute unit of a many-PE chip.
- **Tile (of a tile-based chip):** the unit the chip is organised in.
- **SRAM:** static random-access memory, the fast memory on a chip itself (standard meaning, not from the README).
