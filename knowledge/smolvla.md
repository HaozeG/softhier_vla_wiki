---
type: entity
tags: [smolvla, small-vla, flow-matching]
sources: [resources/models/smolvla.md]
---
# SmolVLA

## Summary
(Evaluation names and evidence tags: [glossary, evaluation and models](../glossary/evaluation-and-models.md).)

SmolVLA is Hugging Face's open 450M-parameter VLA: the first half of a SmolVLM-2 language model, 64 visual tokens per frame, and a 100M flow-matching action expert emitting 50-action chunks in 10 steps. It is the reference "small VLA" for this wiki. Its accuracy claims are on LIBERO, Meta-World and low-cost SO100/SO101 arms; its serving claims come from the paper's asynchronous stack.

```text
ONCE PER CALL (prefill): read the observation with the VLM
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
EACH OF 10 FLOW STEPS (x10)                          | layer (16 sets)
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
         +<-- velocity, 50 tokens, x10 -+
each step: Euler update of the noisy chunk with the velocity
after step 10 the chunk is the 50 actions
```

## Details
In the drawing the "VLM" box contains the vision encoder (SigLIP with pixel shuffle) and the first 16 LLM layers, the same two parts as stages 2 and 3 of [one VLA call](one-vla-call.md).

**Data flow per call (paper and first-party code, see [the source note](../resources/models/smolvla.md))**
- **Once per call, in the prefill (the prefix pass):** the three camera images (64 visual tokens each after pixel shuffle), the language prompt (padded to 48 tokens) and the robot state (1 token) form a prefix of 3 × 64 + 48 + 1 = 241 tokens. The first 16 LLM layers process it once and keep their keys and values (in attention, each token offers a key to be matched and a value to be read; a token looks at others by matching against their keys and mixing their values), one set per layer (16 sets); these stored keys and values are what the wiki calls the KV cache, the working memory attention reads from.
- **Each of the 10 flow steps:** the 50 noisy action tokens are embedded together with the flow time (a sinusoidal time embedding joined to the action embedding and passed through a small MLP) and run through the expert. In cross-attention layers the keys and values come from the cached VLM layer with the same index, after the expert's own key and value projections (the reference code repeats this projection in every step; only the VLM's keys and values are cached); in self-attention layers (every second layer) the action tokens are causal among themselves and, in the released code, also see the cached prefix. A linear layer turns the output into the velocity, and one Euler step updates the noisy chunk. After step 10 the chunk is the 50 actions.
- **What crosses from VLM to expert** is therefore keys and values (per layer), not a single feature vector, and not the final-layer output. The paper's wording is ambiguous ("features at the N-th layer" and "all features up to layer N"); the code settles it as per-layer keys and values for the layers used.

**Architecture (from [the paper](../resources/models/smolvla.md))**
- Vision-language trunk: SmolVLM-2 (SigLIP encoder plus SmolLM2 decoder); the action expert reads features from LLM layers up to N = L/2 (16 layers in the released model); no image tiling (a large image is not cut into several crops that are encoded separately: only the whole image is used); images resized to 512×512; 64 visual tokens per frame after pixel shuffle (which regroups neighbouring patch tokens into fewer, wider ones); sensorimotor state projected to one prefix token.
- Action expert: about 100M parameters, hidden size 0.75× the VLM's, alternating cross-attention and causal self-attention, flow matching, chunk n = 50, 10 integration steps at inference.
- Whole model 450M parameters; bf16 and `torch.compile` in training; the VLM stays frozen during pretraining; about 30k GPU-hours for the whole project.
- Sizes: the paper evaluates 0.24B, 0.45B and 2.25B variants in simulation; the released base checkpoint uses `SmolVLM2-500M-Video-Instruct` truncated to 16 of 32 LLM layers (3 cameras, language padded to 48 tokens), and real-world results are 0.45B only. Check which size any quoted number refers to.

**Accuracy** (success rate is the share of benchmark episodes in which the task is completed). Scores differ by paper, model size and training protocol, so compare them only inside one paper: the SmolVLA paper reports about 87 on LIBERO for the 0.45B model and about 89 for the 2.25B model, and papers that quote 88.8 mean the 2.25B model. The paper's ablations (layers used, chunk size, async versus sync) are in layer skipping and pruning, [action representation and chunking](action-representation-and-chunking.md) and serving methods.

## Open questions
- Cross-embodiment generalization beyond SO100 arms (the paper's own limitation).
- The SmolVLA paper does not report how compute splits between the vision path and the LLM half.
