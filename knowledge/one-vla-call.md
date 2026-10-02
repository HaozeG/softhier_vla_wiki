---
type: concept
tags: [overview, vla, smolvla, walkthrough, start-here]
sources: [resources/models/smolvla.md, resources/serving/lerobot-async-inference-docs.md, resources/serving/vla-simd.md]
---
# One VLA call, step by step

## Summary
A robot that follows instructions needs a program that looks at its camera images and decides what its arms do next. That program is a vision-language-action ([VLA](../glossary/model-and-attention.md)) model, and each time the robot asks it, the model answers not with one command but with a short batch of commands to carry out one after another. This note follows one such call from the camera images to the batch of commands, so the later notes about speed have a picture to hang on.

The figures are approximate and illustrative: they are those of SmolVLA, a small VLA (see [SmolVLA](smolvla.md) for the sources). Other VLAs differ in details such as how they produce actions; see the [architecture overview](vla-architecture-overview.md).

## Diagram
```text
ONE CALL (repeats whenever the queue runs low)
+--------------------------+                  +----------------------------+
| ROBOT                    |                  | VISION ENCODER             |
| 3 camera images          | -- 3 images -->  | 64 tokens per image        |
| instruction, joint state |                  |                            |
+--------------------------+                  +----------------------------+
  ^           |                                             |
  |           |                                             | 3 x 64 tokens
  |           |                                             v
  |           |                               +----------------------------+
  |           +-- text 48 + state 1 tokens -->| 1. PREFIX PASS, once       |
  |                                           | 241 tokens in:             |
  | 1 action per step                         | 3x64 + 48 + 1              |
  |                                           | 16 LLM layers: keys+values |
  |                                           +----------------------------+
  |                                                         |
  |                                                         | keys + values
  |                                                         v
+--------------------------+                +-----------------------+
| 3. ACTION QUEUE          |                | 2. EXPERT STEP        |---+
| 50 actions, ~1.7 s       | 50 actions     | 50 noisy actions in,  |   | x10
| at 30 Hz                 | <-----------   | better 50 actions out |<--+
+--------------------------+                +-----------------------+

While the queue drains the robot keeps moving; the next call starts
before the queue is empty.
```

## Steps
1. **The robot observes.** It sends three camera images, its instruction text and its own joint positions (the robot state). The model's vision encoder turns each image into 64 [tokens](../glossary/model-and-attention.md) (small vectors that each stand for a piece of the input), the instruction becomes 48 tokens and the state 1 token. Together these 3 × 64 + 48 + 1 = 241 tokens are the [prefix](../glossary/model-and-attention.md): everything the model knows about the present moment.
2. **The prefix pass runs once.** The first 16 layers of the language model ([LLM](../glossary/model-and-attention.md), the part of the VLA that reads all tokens together) process the 241 tokens one time. Each layer keeps the keys and values it computed, the working memory that attention reads from (the [KV cache](../glossary/model-and-attention.md); see [keys and values](../glossary/model-and-attention.md)). This pass is not repeated: only step 3 repeats.
3. **Ten expert steps.** A smaller network, the [action expert](../glossary/action-generation.md), starts from random numbers shaped like 50 actions and improves them in 10 small steps ([flow matching](../glossary/action-generation.md); each repeat is a flow step). In every step it looks at the cached keys and values from step 2 and nudges the 50 actions toward what the model thinks the robot should do. Only this part repeats, and the prefix pass does not; the expert re-reads its own weights in every step.
4. **A chunk of 50 actions comes out.** One [action](../glossary/robot-and-control-loop.md) is one command for one control step, and the batch is an [action chunk](../glossary/robot-and-control-loop.md). At a [control rate](../glossary/robot-and-control-loop.md) of 30 [Hz](../glossary/symbols-and-conventions.md) (30 commands per second, a rate used in the SmolVLA setups: the paper's async condition uses a control period of about 33 ms at 30 fps) 50 actions last roughly 1.7 s: the [chunk duration](../glossary/robot-and-control-loop.md).
5. **The chunk goes into a queue.** The robot takes one action from the queue at each control step. When the queue falls below a set fraction of a chunk, the robot asks for the next call ([asynchronous execution](../glossary/robot-and-control-loop.md), as in the [LeRobot docs](../resources/serving/lerobot-async-inference-docs.md)).
6. **The robot keeps moving while the next call runs.** The time between asking and receiving a chunk is the call's [latency](../glossary/robot-and-control-loop.md). Following the action-supply conditions of [vla.simd](../resources/serving/vla-simd.md), the queue does not run empty while the latency stays below the chunk duration, and the margin is smaller if the late, [stale actions](../glossary/robot-and-control-loop.md) of a chunk are discarded; see [serving methods](serving-methods.md).

Where to go next: [VLA edge serving overview](vla-edge-serving-overview.md) for the findings and the reading order, [SmolVLA](smolvla.md) for the same flow with every size, and [SoftHier and the project](softhier-and-the-project.md) for what this project is about.
