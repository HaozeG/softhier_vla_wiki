---
type: concept
tags: [dual-system, system-1, system-2, frequency, vla]
sources: [resources/surveys/survey-openhelix-dual-system.md, resources/surveys/survey-world-action-models-nus.md, resources/models/smolvla.md, resources/models/gr00t-n1.md, resources/models/pi0.md, resources/models/figure-helix.md]
---
# Dual-system VLA: big brain, small brain

## Summary
A dual-system VLA splits the work between two separate networks that run at different rates: System 2, a large vision-language model that reads the scene and instruction slowly, and System 1, a small policy that produces the actions quickly. The two are joined by a latent that System 2 hands to System 1. This differs from [SmolVLA](smolvla.md), where the vision-language trunk and the action expert sit in one model and run together inside every call.

```text
SmolVLA: one model, one rate        DUAL-SYSTEM: two models, two rates

 obs                                 obs                    obs (fresh)
  |                                   |                       |
  v                                   v                       v
+--------------+                    +-----------+         +-----------+
| VLM trunk    |                    | SYSTEM 2  | latent  | SYSTEM 1  |
| (16 layers)  |                    | large MLLM|-------->| small     |
+--------------+                    | slow, rare| held    | policy    |
  | KV cache                        +-----------+ between | fast      |
  v                                               S2 calls+-----------+
+--------------+                                              |
| action expert|                                              v
| x10 steps    |                                         actions at the
+--------------+                                         policy's rate
  |
  v                                  S2 refreshes the latent less often;
chunk of 50 actions                  S1 keeps running on the held latent
trunk + expert run together
in every call
```

## Details
**Names.** System 1 and System 2 come from "Thinking, Fast and Slow" ([OpenHelix](../resources/surveys/survey-openhelix-dual-system.md)). "Big brain" and "small brain" are informal names for System 2 and System 1. [WAM survey](../resources/surveys/survey-world-action-models-nus.md) calls the pattern a "dual-frequency slow-fast loop".

**System 2 (big brain).**
- A large MLLM or VLA, 2B to 7B parameters in the surveyed table (Qwen2-VL-2B, LLaVA-7B, OpenVLA-7B, InstructBLIP-7B).
- Slow, generalizes well, updates rarely, so its output arrives with delay.
- Its output is a latent, not actions: a language token, an `<ACT>` embedding, pooled or last-layer hidden states, or middle-layer states.

**System 1 (small brain).**
- A lightweight policy; the surveyed table lists 3D Diffuser Actor, a plain transformer, a DiT, ScaleDP and an RT-1-style network.
- Runs at high frequency and outputs the low-level actions.
- In the OpenHelix definition, takes its own fresh perception (RGB, proprioception, sometimes depth or tactile) in addition to the latent.

**What decides the split (as the sources state it).**
- Large VLAs are too slow for control: RT-2 is cited at 1-3 Hz (55B) and about 5 Hz (5B), against about 50 Hz for a lightweight policy ([OpenHelix](../resources/surveys/survey-openhelix-dual-system.md)).
- The cost model of the [WAM survey](../resources/surveys/survey-world-action-models-nus.md): a chunked design needs N_fwd(K)/K < 1/f_ctrl, a single-step design needs N_fwd(1) < 1/f_ctrl, so a large backbone is affordable only if it is called once per chunk, rarely or in a slow loop.
- Typical sizes in the WAM survey: an 860M action expert under a Gemma3 VLA (π0.7) and a 300M expert under a PaliGemma-2B trunk (ALAM).

**Contrast with other VLAs.**

| Design                                       | Models                                     | What the action part sees                                                                                                                       | Rate                                                                           |
| -------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| One-model VLA + expert                       | SmolVLA, π0                                | VLM keys and values from the same call (SmolVLA puts robot state in the VLM prefix; π0's expert takes robot state itself); no images of its own | One rate: trunk and expert run in every call                                   |
| VLM + DiT, called dual-system by its authors | GR00T N1                                   | Middle-layer VLM features by cross-attention, plus robot state; no images of its own                                                            | Stated as 10 Hz for System 2 and 120 Hz for System 1; scheduling not described |
| Dual-system (OpenHelix definition)           | LCB, DP-VLA, HiRT, RoboDual, DexVLA, Helix | A latent from System 2 plus its own real-time perception                                                                                        | Two rates: System 2 slow, System 1 fast                                        |

- OpenHelix's definition excludes π0 and GR00T-N1 because their action parts take no real-time camera images of their own (both do take robot state), and OpenHelix itself calls the definition ambiguous. The [GR00T N1](../resources/models/gr00t-n1.md) paper calls its own model dual-system, so check which definition a source uses.
- In SmolVLA the expert reads cached keys and values of the VLM's first 16 layers ([SmolVLA](smolvla.md)); in the dual-system models the interface is a latent whose form varies by method.
- Asynchronous execution in SmolVLA hides the latency of one whole call; in a dual-system model the two systems have different latencies by design.

**What the OpenHelix experiments found** (simulation only, one MLLM and one policy): the policy alone fails on moving objects; the MLLM mainly improved generalization to rephrased instructions; the latent mostly carried the instruction's semantics, and running System 2 once per 1 to 60 policy steps gave about the same performance; an auxiliary action-prediction loss gave the best result. See the [source note](../resources/surveys/survey-openhelix-dual-system.md) for caveats.

**A fast policy with no System 2 above it.** The [low-level policy loop](low-level-policy-loop.md) is the small, fast end on its own: one action per call at 50 Hz from joint and inertial sensors, commanded by a hand-made vector instead of a latent.

**World-model versions.** WAMs also use fast and slow parts: HarmoWAM and LingBot-VA hand frequent control to a lighter action expert while visual dynamics stay available, and FFDC-WAM uses a lightweight verifier to trigger replanning ([WAM overview](wam-overview.md)).

## Open questions
- How small System 2 can be: OpenHelix fixes the MLLM (LLaVA-7B) and the policy, and names the question open.
- Which latent form carries visual information when the scene changes within a System 2 interval.
- Real-robot rates: the surveys give almost no Hz figures for either system.
