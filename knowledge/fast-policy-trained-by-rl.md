---
type: concept
tags: [rl, fast-policy, residual-policy, vla, frequency]
sources: [resources/models/rl-token.md, resources/models/real-time-expo-ft.md, resources/models/pi06-recap.md, resources/surveys/survey-vla-embodied-ai-ma.md]
---
# Fast policy trained by RL

## Summary
Reinforcement learning (RL) enters a VLA in two ways in the sources read so far: it fine-tunes the whole large VLA offline, or it trains a small, fast network that sits next to a frozen or slow VLA and refines its actions. The second way is the "fast policy trained by RL". It is a small actor and critic trained from reward, usually with a few hours or less of real-robot data, while the large VLA supplies a reference action chunk and, in one design, the state representation.

```text
A. RL TOKEN: VLA frozen, small head trained by RL
   obs --> [VLA pi0.6] --reference chunk (H=50)------------+
              | RL token (1 x 2048)                        v
              +--> [actor MLP + critic MLP] --> RL chunk, C=10 actions
                   inputs: RL token + proprio   (control at 50 Hz)
                   loss: -Q + beta*|a - reference|^2

B. REAL-TIME EXPO-FT: VLA slow and asynchronous, edit policy fast
   obs(t) --> [VLA] --N candidate chunks--+   (starts d steps early)
                                          v
   obs(t+d), latest --> [edit policy] --> 2N chunks (N base + N edited)
                                          |
                        [critic Q] --argmax--> chunk executed

C. pi*0.6 (RECAP): no small policy; RL updates the whole VLA
   data --> [value function, 670M] --advantage--> text indicator
   [VLA: 4B VLM + 860M expert] trained conditioned on the indicator
```

## Details
**Design A: RL Token ([source](../resources/models/rl-token.md)).**
- The VLA and an encoder-decoder "RL token" are frozen. A 2- or 3-layer MLP actor and a twin-Q critic are trained from scratch by RL.
- The actor outputs shorter chunks (10 actions) than the VLA (50), "for reactivity", and is pulled toward the VLA's reference chunk by a penalty term.
- Its inputs are the RL token and proprioception; it takes no camera images of its own, so by the OpenHelix definition in [dual-system VLA](dual-system-vla.md) it is not a System 1.
- RL is applied to a human-selected critical phase of the task; the base VLA does the rest.

**Design B: Real-Time EXPO-FT ([source](../resources/models/real-time-expo-ft.md)).**
- The VLA proposes candidate chunks asynchronously, starting when d steps remain in the current chunk. A small edit policy adds a bounded residual using the latest observation, and a critic chooses among base and edited candidates.
- Two timescales: slow (VLA, observation s_t, in flight for d steps) and fast (edit policy and critic at s_{t+d}). The edit policy reuses the critic's image embedding, so it does see the latest images.
- The VLA is also updated, by behaviour cloning on successful episodes, not by Q-gradients.
- It targets the delay problem directly: an action computed d steps ago acts on a stale observation, which also violates the Markov assumption of RL.

**Design C: π*0.6 ([source](../resources/models/pi06-recap.md)).** No small policy. The value function (670M) is separate and small relative to the VLA; the VLA is trained end to end conditioned on an advantage indicator. It is the contrast case: RL changes the large model rather than adding a fast one.

**Comparison**

| Design            | What RL trains                     | What stays frozen         | Policy rate and chunk                 | Evidence                              |
| ----------------- | ---------------------------------- | ------------------------- | ------------------------------------- | ------------------------------------- |
| RL Token          | Actor and critic MLPs              | VLA, RL-token encoder     | 50 Hz control, C = 10 of H = 50       | Four bimanual tasks, 1 base VLA       |
| Real-Time EXPO-FT | Edit policy and critic (VLA by BC) | Non-LoRA language weights | 30 Hz control, VLA about 67 ms, C = 8 | Simulation plus four single-arm tasks |
| π*0.6 (RECAP)     | Whole VLA and a value model        | Nothing frozen            | 50 Hz action chunks                   | Laundry, espresso, box assembly       |

**Relation to the older picture.** The [Ma et al. survey](../resources/surveys/survey-vla-embodied-ai-ma.md) describes RL policies as the earlier approach, limited to a few tasks in controlled settings, and frames the planner and low-level policy split as "similar to hierarchical RL", where the policy "can focus on speed and precision". It describes RL as a component of VLAs through reward design (Eureka), value-based re-ranking of VLA actions (V-GPS) and Q-learning on top of RT-1 (Q-Transformer). The three papers above are the post-training counterpart: RL on top of a pretrained VLA.

**Shared supervision.** All three use sparse success rewards labelled by humans or a classifier, and rely on human interventions or resets; the sources list this as a limitation.

## Open questions
- Whether the RL-trained fast network could run on a different, smaller backbone: the sources always pair it with a VLA of several billion parameters.
- Latency of the small network: neither RL Token nor Real-Time EXPO-FT reports a measured latency for the actor, edit policy or critic selection.
- Comparison on a shared benchmark: the three papers use different tasks, robots and baselines.
