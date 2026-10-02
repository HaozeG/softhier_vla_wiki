---
type: glossary
tags: [glossary, quantization, pruning, distillation]
sources: [resources/compression/bitvla.md, resources/compression/quantvla.md, resources/compression/pruned-vla-recovery.md, resources/compression/clp-layer-pruning.md]
---
# Compression

## Summary
The ways a VLA is made cheaper (fewer bits, layers, tokens or steps) and the names of the methods. All terms are standard (scope field).

## Terms
| Term                         | Meaning                                                                                    | Scope | Defined in                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------ | ----- | ------------------------------------------------------------------------ |
| quantization                 | Storing numbers with fewer bits; INT8 and INT4 are 8-bit and 4-bit integers.               | field | [quantization](../knowledge/quantization.md)                             |
| W4A8, W8A8                   | Weight and activation bit widths: 4-bit weights with 8-bit activations, or 8-bit for both. | field | [quantization](../knowledge/quantization.md)                             |
| ternary                      | Weights restricted to three values: minus one, zero and plus one.                          | field | [quantization](../knowledge/quantization.md)                             |
| PTQ, QAT                     | Post-training quantization of a finished model; quantization-aware training.               | field | [quantization](../knowledge/quantization.md)                             |
| GGUF                         | The model file format of the llama.cpp runtime family.                                     | field | [quantization](../knowledge/quantization.md)                             |
| dequantization               | Converting low-bit weights back to a wider format before arithmetic.                       | field | [quantization](../knowledge/quantization.md)                             |
| pruning, width pruning       | Removing weights; width pruning narrows each layer.                                        | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| layer skipping, early exit   | Running only some layers for each input, or stopping once the answer is settled.           | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| CKA                          | Centered kernel alignment: a similarity measure between layers' outputs.                   | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| distillation                 | Training a smaller or pruned model to imitate a bigger one.                                | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| token pruning, token caching | Dropping visual tokens, or reusing the previous frame's work.                              | field | [token pruning and caching](../knowledge/token-pruning-and-caching.md)   |
| speculative decoding         | A small draft proposes tokens that the large model then verifies.                          | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| flow-step reduction          | Running fewer flow steps, or caching expert features across steps.                         | field | [flow-step reduction](../knowledge/flow-step-reduction.md)               |
