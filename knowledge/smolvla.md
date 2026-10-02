---
type: entity
tags: [smolvla, small-vla, edge, flow-matching, lerobot]
sources: [resources/models/smolvla.md, resources/serving/lerobot-async-inference-docs.md, resources/serving/vla-cpp.md, resources/serving/vla-simd.md, resources/serving/flashvla-streaming.md, resources/compression/clp-layer-pruning.md, resources/compression/pruned-vla-recovery.md, resources/compression/bitvla.md]
---
# SmolVLA

## Summary
(Evaluation names and evidence tags: [glossary, evaluation and models](../glossary/evaluation-and-models.md).)

SmolVLA is Hugging Face's open 450M-parameter VLA: the first half of a SmolVLM-2 language model, 64 visual tokens per frame, and a 100M flow-matching action expert emitting 50-action chunks in 10 steps. It is the reference "small VLA" for this wiki. Its accuracy claims are on LIBERO, Meta-World and low-cost SO100/SO101 arms; its serving claims come from the paper's asynchronous stack, and measured latencies on other hardware come from third-party runtimes and vary by 10× with implementation quality.

```text
ONCE PER CALL: read the observation with the VLM
+-----------------+           +----------------------------------------------+
| 3 camera images |-- 3x64 -->| VLM (SmolVLM-2)                              |
+-----------------+           |                                              |
| language prompt |--- 48 --->| images: SigLIP encoder + pixel shuffle       |
+-----------------+           |    -> 64 visual tokens per camera            |
| robot state     |---- 1 --->| state: linear projection -> 1 token          |
+-----------------+           | concat: 3x64 + 48 + 1 = 241 tokens           |
  arrow labels = tokens       |                                              |
                              | LLM layers 1..16 (of 32), run once           |
                              |                                              |
                              +----------------------------------------------+
                                                     | keys + values of the
                                                     | 241 tokens, per LLM
EACH OF 10 FLOW STEPS                                | layer (16 sets)
                                                     v
+-----------------+           +----------------------------------------------+
| noisy actions   |           | ACTION EXPERT (~100M, 0.75x width)           |
| 50 tokens       |           |                                              |
| + flow time     |           | cross-attention layers: attend to            |
|                 |--- 50 --->|   the cached keys + values of LLM            |
|                 |           |   layer i (the same i)                       |
|                 |           | self-attention layers (every 2nd):           |
|                 |           |   the 50 action tokens, causal among         |
|                 |           |   themselves, also see the cached            |
|                 |           |   prefix                                     |
+-----------------+           +----------------------------------------------+
         ^                              |
         +<--- velocity, 50 tokens -----+
each step: Euler update of the noisy chunk with the velocity
after step 10 the chunk is the 50 actions
```

## Details
**Data flow per call (paper and first-party code, see [the source note](../resources/models/smolvla.md))**
- **Once per call:** the three camera images (64 visual tokens each after pixel shuffle), the language prompt (padded to 48 tokens) and the robot state (1 token) form a prefix of 3 × 64 + 48 + 1 = 241 tokens. The first 16 LLM layers process it once and keep their keys and values, one set per layer (16 sets).
- **Each of the 10 flow steps:** the 50 noisy action tokens are embedded together with the flow time (a sinusoidal time embedding joined to the action embedding and passed through a small MLP) and run through the expert. In cross-attention layers the keys and values come from the cached VLM layer with the same index, after the expert's own key and value projections (the reference code repeats this projection in every step; only the VLM's keys and values are cached); in self-attention layers (every second layer) the action tokens are causal among themselves and, in the released code, also see the cached prefix. A linear layer turns the output into the velocity, and one Euler step updates the noisy chunk. After step 10 the chunk is the 50 actions.
- **What crosses from VLM to expert** is therefore keys and values (per layer), not a single feature vector, and not the final-layer output. The paper's wording is ambiguous ("features at the N-th layer" and "all features up to layer N"); the code settles it as per-layer keys and values for the layers used.

**Architecture (from [the paper](../resources/models/smolvla.md))**
- Vision-language trunk: SmolVLM-2 (SigLIP encoder plus SmolLM2 decoder); the action expert reads features from LLM layers up to N = L/2 (16 layers in the released model); no image tiling; images resized to 512×512; 64 visual tokens per frame after pixel shuffle; sensorimotor state projected to one prefix token.
- Action expert: about 100M parameters, hidden size 0.75× the VLM's, alternating cross-attention and causal self-attention, flow matching, chunk n = 50, 10 integration steps at inference.
- Whole model 450M parameters; bf16 and `torch.compile` in training; the VLM stays frozen during pretraining; about 30k GPU-hours for the whole project.
- Sizes: the paper evaluates 0.24B, 0.45B and 2.25B variants in simulation; the released base checkpoint uses `SmolVLM2-500M-Video-Instruct` truncated to 16 of 32 LLM layers (3 cameras, language padded to 48 tokens), and real-world results are 0.45B only. Check which size any quoted number refers to.

**Accuracy**
- Paper (LIBERO, from scratch ablations): N = 16 → 78.5, N = 32 → 80.3. Real world (SO100): pretrained multi-task 78.3%, no-pretraining 51.7%. Async vs sync: 73.3 vs 78.3 average success, 30% faster completion.
- LIBERO averages by size in the paper's Table 2: 0.24B 82.75, 0.45B 87.3, 2.25B 88.75; papers quoting 88.8 (for example [BitVLA](../resources/compression/bitvla.md), [LightVLA](../resources/compression/lightvla.md)) mean the 2.25B model. Other papers report lower numbers for the 0.45B model under their own training: 80.1 ([FlashVLA](../resources/serving/flashvla-streaming.md)) and 77.15 ([CLP](../resources/compression/clp-layer-pruning.md)). Compare only within one paper's protocol.

**Measured serving numbers from other sources**

| Source                                                                                       | Hardware                                            | Number                                                                     | Notes                                        |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------- |
| [vla.cpp](../resources/serving/vla-cpp.md)                                                   | RTX 3090                                            | 55.8 ms per chunk (server side)                                            | eager PyTorch 174.1 ms, compiled 65.9 ms     |
| vla.cpp                                                                                      | RTX 5070                                            | 74.1 ms                                                                    | eager 176.0 ms, graph-captured 76.3 ms       |
| vla.cpp                                                                                      | AGX Orin / RTX 3060                                 | 65.4 / 28.2 ms per executed action (S = 4, includes transport)             | about 262 / 113 ms per chunk                 |
| vla.cpp                                                                                      | Jetson Orin Nano 8 GB                               | median 358–457 ms per chunk                                                | 176/200 LIBERO-Object success at S = 4       |
| vla.cpp                                                                                      | Apple M4 (Metal)                                    | 374 ms                                                                     | 9/10 success                                 |
| vla.cpp                                                                                      | i9-14900HX, 8 threads CPU                           | 2141 ms                                                                    |                                              |
| [vla.simd](../resources/serving/vla-simd.md)                                                 | Apple M4 / i9 / Ryzen 5 / Raspberry Pi 5 CPU        | about 0.68 / 1.19 / 1.32 / 8.19 s per chunk (50 / f_eff)                   | fp32, engine-only latency                    |
| [XPU characterization](../resources/serving/vla-xpu-characterization.md) (plot, approximate) | i7-11700 CPU / Ascend 310P / Orin / Thor / RTX 4090 | about 0.3 / 2 / 1.2 / 4.9 / 11 Hz (PyTorch baseline; a 310B bar is absent) | read off a log-scale bar chart, roughly ±20% |
| [FlashVLA](../resources/serving/flashvla-streaming.md)                                       | RTX 4090 class                                      | 19.7 ms baseline → 10.1 ms streaming                                       | CUDA graphs, fused kernels                   |
| [CLP](../resources/compression/clp-layer-pruning.md)                                         | RTX 4070                                            | 201 ms → 137 ms after layer pruning                                        | different measurement boundary               |

The 10× spread across sources on similar GPUs (10–20 ms vs 65–200 ms) is an implementation effect (eager dispatch vs CUDA graphs and fused kernels), not a hardware effect. See [inference workload characterization](inference-workload-characterization.md).

**Compression evidence specific to SmolVLA:** CLP pruned 10 of 16 layers (VLM and expert) with a 0.4-point LIBERO drop and 1.47× speedup; FlashVLA streaming halves per-invocation latency with equal success. No source reports quantized SmolVLA task success other than a W8A8 CPU speed study.

**Device context:** hardware classes, and what is and is not measured below Orin, are in [edge hardware and the 10 TOPS gap](edge-hardware-and-the-10-tops-gap.md); this note is model-centric while that one is device-centric.

**Memory:** about 2 GB at inference per the [LeRobot docs](../resources/serving/lerobot-async-inference-docs.md), vs 14 GB for π0. Serving arithmetic for a 10-TOPS-class device is in [edge budget estimate](edge-budget-estimate.md).

## Open questions
- Cross-embodiment generalization beyond SO100 arms (the paper's own limitation).
- Whether the 64-token / 512×512 vision path or the LLM half dominates compute; the per-component split is not in the paper text read.
