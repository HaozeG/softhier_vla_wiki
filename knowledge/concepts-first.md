---
type: concept
tags: [glossary, basics, roofline, flow-matching, quantization, notation]
sources: [resources/serving/vla-perf.md, resources/models/smolvla.md, resources/serving/lerobot-async-inference-docs.md, resources/serving/vla-simd.md, resources/hardware/edge-accelerator-datasheets.md, resources/compression/bitvla.md, resources/compression/quantvla.md, resources/compression/pruned-vla-recovery.md, resources/models/openvla-oft.md]
---
# Concepts first

## Summary
The other notes assume a handful of ideas, which are explained here in plain words: a robot policy is called in a loop and returns chunks of actions; a VLA is a vision-language model plus a part that outputs actions; a computing step can be limited by memory traffic instead of arithmetic (which is why a faster chip does not always give a faster robot); and a few names and symbols recur everywhere. Read this once, then use it as a lookup; each term is linked back from the notes that need it.

```text
+------------------------------+                        +----------------------+
| ROBOT + CAMERAS              | -- images + state -->  | VLA MODEL CALL       |
| executes one action every    |     (observation)      | takes latency l      |
| control step (30 Hz: 33 ms)  | <-- chunk of n ------  |                      |
+------------------------------+     actions (e.g. 50)  +----------------------+

A call returns a whole chunk; the robot works through it while the next
call runs.
```

## The robot side
- **Control step, control period, control rate.** The robot sends a new command every control period dt; the control rate is 1/dt, in hertz (Hz, per second). At 30 Hz, dt is 33 ms.
- **Action.** One command for one control step, for example target positions for the joints.
- **Action chunk.** Instead of one action per model call, the model returns H actions at once (H is also written n or K). A chunk lasts H × dt: 50 actions at 30 Hz last 1.67 s. A longer chunk gives the slow model more time between calls but makes the plan staler.
- **Latency l.** The time one model call takes. The question that organises the serving notes is how l compares with dt and with H × dt ([serving methods](serving-methods.md)).
- **Asynchronous (async) execution.** The robot keeps executing queued actions while the next call is still running, so inference overlaps motion.
- **Stale and late actions.** A chunk is computed from an observation taken l seconds ago, so its first l/dt actions describe moments that have already passed. Discarding them is "dropping stale actions"; executing the chunk from its start anyway is "lagged execution". **Chunk stitching** blends a late chunk with the actions already queued.
- **Dual system.** A big, slow model that plans, plus a small fast policy that runs at the control rate (GR00T N1, Helix).

## The model side
- **VLA, VLM.** A vision-language-action model takes camera images, a language instruction and usually the robot's state, and outputs actions. It is built on a vision-language model (VLM): an image encoder plus a language model that can read both.
- **Token.** A vector standing for a piece of the input: an image patch, a word piece, or the robot state. Model sizes count parameters: 0.45B means 450 million.
- **Prefix and prefill.** The prefix is all the observation tokens (images, text, state) fed to the language model. Prefill is the one pass that processes the whole prefix.
- **KV cache.** In each attention layer every token produces a key and a value. Storing them lets later work reuse the prefix without recomputing it. In SmolVLA the cached keys and values are what the action expert reads.
- **Self-attention and cross-attention.** In self-attention tokens look at each other. In cross-attention one set of tokens (the action tokens) looks at another set's keys and values (the VLM's).
- **Action head, action expert.** The part that turns the language model's features into actions. Three families: *discrete tokens* (the language model writes actions as words, one pass per token, as in RT-2 and OpenVLA), *parallel regression* (one pass writes all actions, as in OpenVLA-OFT), and *flow matching* with a small *action expert*.
- **Flow matching, in one paragraph.** Start from random noise shaped like the action chunk, then refine it in T small steps. At each step the expert looks at the current noisy chunk and the flow time and outputs a velocity, a direction to move the chunk; an Euler step moves it a little along that direction. After the last step (T = 10 in SmolVLA) the chunk is the predicted actions. Diffusion works the same way with a different step rule.

## The hardware side: memory-bound and compute-bound
A chip has two limits: how fast it does arithmetic (FLOP/s: floating-point operations per second; TFLOP/s is a trillion of them) and how fast it reads numbers from memory (bandwidth, in GB/s). Every phase of a model call needs both. Whichever takes longer sets the time of that phase. This rule applied phase by phase is called the **roofline** model ([VLA-Perf](../resources/serving/vla-perf.md): time = the larger of operations ÷ speed and bytes ÷ bandwidth).

```text
ONE STEP OF SMOLVLA'S ACTION EXPERT on a 10 TFLOP/s chip with 51.2 GB/s memory
(1 char = 0.2 ms)

arithmetic: 10 GFLOP / 10 TFLOP/s = 1.0 ms |#####
memory:     0.2 GB / 51.2 GB/s    = 3.9 ms |####################

The step takes the longer of the two: 3.9 ms. Faster arithmetic would not help
```

- **The example in numbers.** Arithmetic would take 1.0 ms per step, the weight reads 3.9 ms, so one step takes 3.9 ms and ten steps about 39 ms ([edge budget estimate](edge-budget-estimate.md)).
- **Intensity.** FLOP per byte read: how much arithmetic a phase does for each byte it fetches. SmolVLA's expert does about 10 GFLOP per step and reads about 0.2 GB of weights each step, so its intensity is 50 FLOP/byte.
- **Balance point.** The chip's FLOP/s divided by its bytes/s. The chip above is 10 TFLOP/s ÷ 51.2 GB/s, about 195 FLOP/byte.
- **Memory-bound** (intensity below the balance point, 50 against 195 here): the chip waits for memory. More arithmetic speed does not help; fewer or faster bytes do (smaller or lower-precision weights, keeping weights on chip).
- **Compute-bound** (intensity above the balance point): the chip waits for arithmetic. Fewer operations help (fewer tokens, fewer layers). In π0 the vision encoder and the language model have intensities of 321 and 543 FLOP/byte, so on an RTX 4090 (balance point 164) they are compute-bound while the expert, at 54, is memory-bound.
- **TOPS.** Trillions of operations per second, as quoted by vendors, often for sparse INT8 arithmetic. It is not comparable with dense BF16 FLOP/s, which is what a flow loop needs ([edge hardware](edge-hardware-and-the-10-tops-gap.md)). A GPU or NPU is the part of a chip that does the matrix arithmetic.
- **Named hardware.** Jetson Orin Nano, AGX Orin and Thor are NVIDIA embedded GPU modules; RK3588 is a Rockchip chip with a 6 TOPS NPU common in robot prototypes; Ascend 310B/310P and Hailo are other accelerators. Details are in [edge hardware](edge-hardware-and-the-10-tops-gap.md).

## Compression words
- **Quantization.** Storing numbers with fewer bits. INT8 and INT4 are 8- and 4-bit integers; **W4A8** means 4-bit weights with 8-bit activations (W8A8: both 8-bit). **Ternary** weights take only the values −1, 0 and +1 ([BitVLA](../resources/compression/bitvla.md)). **PTQ** quantizes a finished model; **QAT** trains with quantization in the loop. **GGUF** is the model file format of the llama.cpp runtime family.
- **Pruning, layer skipping, early exit.** Removing weights, whole layers, or running only some layers for each input.
- **Distillation.** Training a smaller or pruned model to imitate a bigger one ([pruned-VLA recovery](../resources/compression/pruned-vla-recovery.md)).
- **Token pruning and caching.** Dropping visual tokens or reusing the previous frame's work.

## Benchmarks and models
- **LIBERO and Meta-World** are simulated robot benchmarks; SO100 and SO101 are low-cost real arms. Most accuracy numbers in the wiki are LIBERO simulation results ([SmolVLA](smolvla.md)).
- **Models** are listed with one line each in the [models catalog](../resources/models/_overview.md); ACT is a small non-VLM policy used as a speed baseline.

## Symbols used across the notes
| Symbol  | Meaning                                                                                                                                                                                                   |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H, n, K | actions per chunk (K in OpenVLA-OFT, n in SmolVLA, H elsewhere)                                                                                                                                           |
| T       | number of flow steps per chunk                                                                                                                                                                            |
| l (ℓ)   | latency of one model call                                                                                                                                                                                 |
| dt (Δt) | control period                                                                                                                                                                                            |
| g       | fraction of a chunk left in the queue at which the next call is requested                                                                                                                                 |
| L, N    | in model notes, the number of language-model layers and the number used (SmolVLA: N = L/2); in the Jetson-PI part of [serving methods](serving-methods.md), L is the number of actions executed per chunk |
