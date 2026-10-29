---
type: glossary
tags: [glossary, devices, softhier, performance]
sources: [session:parent-readme, https://github.com/pulp-platform/softhier-sdk, resources/models/rt-2.md]
---
# Deployment hardware

## Summary
Words for the chips a policy runs on and how well it uses them: tile, PE, SRAM, many-PE chip, MLIR, TPU, MFU. All terms are standard (scope field); the SoftHier chip terms come from the project README. This branch is outside the robot-side map of the field ([physical AI map](../knowledge/physical-ai-map.md)).

## Terms
| Term                          | Meaning                                                                                                                                | Scope | Defined in                                                           |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------------------------- |
| tile                          | One tile of a tile-based many-PE chip: a group of processing elements with their local memory, repeated across the chip.               | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| PE (processing element)       | One small compute unit of a many-PE chip.                                                                                              | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| SRAM                          | Static random-access memory: fast memory on the chip itself.                                                                           | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| many-PE chip, tile-based chip | A chip built from many processing elements grouped in tiles.                                                                           | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| MLIR                          | A compiler framework for building toolchains that translate a model into code for a chip. Standard gloss; the project README names it. | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| TPU                           | Tensor processing unit: Google's accelerator chip for models; the cloud service of an early VLA ran on several of them.                | field | [RT-2](../resources/models/rt-2.md)                                  |
| MFU (model FLOPs utilization) | The share of a chip's peak arithmetic rate that a model's work actually uses. Standard gloss; the project README names it as an aim.   | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
