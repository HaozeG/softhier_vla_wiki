---
type: glossary
tags: [glossary, devices, softhier]
sources: [session:parent-readme, https://github.com/pulp-platform/softhier-sdk]
---
# Devices and toolchains

## Summary
Chip terms the notes use: tile, PE, SRAM, many-PE chip, MLIR, TPU. All terms are standard (scope field); the SoftHier chip terms come from the project README.

## Terms
| Term                          | Meaning                                                                                                                                                                                                                                                                                                   | Scope | Defined in                                                           |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------------------------- |
| tile                          | A block handled as a unit. Image tile: one crop of an image that is cut into several. GEMM tile: the block of the result matrix that one compute unit works on; tile quantization is the loss when the tiles do not divide evenly across the units. SoftHier tile: one tile of a tile-based many-PE chip. | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| PE (processing element)       | One small compute unit of a many-PE chip.                                                                                                                                                                                                                                                                 | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| SRAM                          | Static random-access memory: fast memory on the chip itself.                                                                                                                                                                                                                                              | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| many-PE chip, tile-based chip | A chip built from many processing elements grouped in tiles.                                                                                                                                                                                                                                              | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| MLIR                          | A compiler framework for building toolchains that translate a model into code for a chip. Standard gloss; the project README names it.                                                                                                                                                                    | field | [SoftHier and the project](../knowledge/softhier-and-the-project.md) |
| TPU                           | Tensor processing unit: Google's accelerator chip for models; the cloud service of an early VLA ran on several of them.                                                                                                                                                                                   | field | [RT-2](../resources/models/rt-2.md)                                  |
