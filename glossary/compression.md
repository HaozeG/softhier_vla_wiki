---
type: glossary
tags: [glossary, quantization, pruning, distillation]
sources: [resources/compression/bitvla.md, resources/compression/quantvla.md, resources/compression/pruned-vla-recovery.md, resources/compression/clp-layer-pruning.md]
---
# Compression

## Summary
The ways a VLA is made cheaper (fewer bits, layers, tokens or steps) and the names of the methods. All terms are standard (scope field).

## Terms
| Term                         | Meaning                                                                                                                                                                 | Scope | Defined in                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ------------------------------------------------------------------------ |
| quantization                 | Storing numbers with fewer bits so that the model needs less memory and fewer bytes read; INT8 and INT4 are eight-bit and four-bit integers.                            | field | [quantization](../knowledge/quantization.md)                             |
| W4A8, W8A8                   | Weight and activation bit widths: four-bit weights with eight-bit activations, or eight-bit for both.                                                                   | field | [quantization](../knowledge/quantization.md)                             |
| ternary                      | Weights restricted to three values: minus one, zero and plus one. Multiplications then reduce to additions.                                                             | field | [quantization](../knowledge/quantization.md)                             |
| PTQ, QAT                     | Post-training quantization of a finished model; quantization-aware training, where the model is trained with the lower precision in place.                              | field | [quantization](../knowledge/quantization.md)                             |
| calibration                  | Running a few sample inputs through a model to choose the scales used when its numbers are quantized. Standard gloss.                                                   | field | [quantization](../knowledge/quantization.md)                             |
| GGUF                         | The model file format of the llama.cpp runtime family.                                                                                                                  | field | [quantization](../knowledge/quantization.md)                             |
| dequantization               | Converting low-bit weights back to a wider format before arithmetic; when it is slow it cancels the benefit of quantizing.                                              | field | [quantization](../knowledge/quantization.md)                             |
| pruning, width pruning       | Removing weights from a model; width pruning narrows each layer instead of removing whole layers.                                                                       | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| layer skipping, early exit   | Running only some layers for each input, or stopping once the answer is settled.                                                                                        | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| CKA                          | Centered kernel alignment: a similarity measure between layers' outputs, used to find layers that can be removed.                                                       | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| distillation                 | Training a smaller or pruned model to imitate a bigger one.                                                                                                             | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| hidden-state distillation    | Distillation in which the smaller model is trained so that its internal activations, not only its outputs, match those of the bigger model. Standard gloss.             | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| LoRA                         | Low-rank adaptation: fine-tuning that trains small added matrices while the original weights stay fixed, so adapting a large model needs little memory. Standard gloss. | field | [TinyVLA](../resources/models/tinyvla.md)                                |
| token pruning, token caching | Dropping visual tokens, or reusing the previous frame's work.                                                                                                           | field | [token pruning and caching](../knowledge/token-pruning-and-caching.md)   |
| speculative decoding         | A small draft model proposes tokens that the large model then accepts or rejects, so that the large model does fewer sequential passes.                                 | field | [layer skipping and pruning](../knowledge/layer-skipping-and-pruning.md) |
| flow-step reduction          | Running fewer flow steps, or caching expert features across steps.                                                                                                      | field | [flow-step reduction](../knowledge/flow-step-reduction.md)               |
| SVD                          | Singular value decomposition: splits a matrix into simpler parts that show its main directions; some token-pruning methods use it to score tokens. Standard gloss.      | field | [Guan et al.](../resources/surveys/survey-efficient-vla-guan.md)         |
| Gumbel-softmax               | A way to pick among options with a step that can still be trained by gradient; LightVLA uses it to decide which visual tokens to keep. Standard gloss.                  | field | [LightVLA](../resources/compression/lightvla.md)                         |
