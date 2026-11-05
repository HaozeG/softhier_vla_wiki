---
type: concept
tags: [dual-system, system-1, system-2, frequency, vla]
sources: [resources/surveys/survey-openhelix-dual-system.md, resources/surveys/survey-world-action-models-nus.md, resources/models/smolvla.md, resources/models/gr00t-n1.md, resources/models/pi0.md, resources/models/figure-helix.md, resources/serving/vla-workload-characterization-kaist.md, https://arxiv.org/abs/2609.09158, https://arxiv.org/abs/2610.28480, https://arxiv.org/abs/2511.07820, resources/benchmarks/vlabench.md, session:vla-hwbench-reading]
---
# Dual-system VLA: big brain, small brain

## Summary
A dual-system VLA splits the work between two separate networks that run at different rates: System 2, a large vision-language model that reads the scene and instruction slowly, and System 1, a small policy that produces the actions quickly. The two are joined by a latent that System 2 hands to System 1. Below System 1 sits a layer that turns actions into motor commands, called System 0 in some humanoid work; the last sections follow this full chain and what each interface means for latency. This differs from [SmolVLA](smolvla.md), where the vision-language trunk and the action expert sit in one model and run together inside every call.

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
trunk + expert run together                   |
in every call                                 v  actions
  |                                     +-------------+
  v  actions                            |  SYSTEM 0   |  arm: IK or OSC
+--------------+                        |  (optional  |  humanoid: learned
| SYSTEM 0     |                        |  planner    |  tracker, 50 Hz
| arm control  |                        |  above it)  |
+--------------+                        +-------------+
  |  motor commands                           |  joint targets
  v                                           v
motors                                      motors
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

## The full chain down to the motors: System 0
In the examples here, a layer below System 1 turns its actions into motor commands. TANGO calls it **System 0** in a "triple-system" design (VL backbone as system-2, action expert as system-1, whole-body tracker as system-0). On the fixed-base arms here this layer is an analytic controller (inverse kinematics in VLABench, operational-space control in LIBERO); the manipulation surveys above do not name it as a system. On a humanoid it is a learned policy that also keeps balance, so it is trained, specified and discussed as its own system. SONIC adds an optional learned **kinematic planner** between the command and the tracker.

What each layer is in the examples. TANGO and SONIC are arXiv papers checked by text search for these facts but **not ingested** as source notes.

| Example                                        | System 2 + System 1                                  | Interface (one "action")                                                                     | Planner                                                                                 | System 0                                                                                                                               |
| ---------------------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| LIBERO manipulation (arm, fixed base)          | One VLA, e.g. π0.5                                   | End-effector pose delta per 20 Hz step                                                       | none                                                                                    | Analytic `OSC_POSE` controller in robosuite ([Jung et al.](../resources/serving/vla-workload-characterization-kaist.md) reading notes) |
| VLABench (arm, fixed base)                     | The evaluated policy                                 | End-effector position and quaternion                                                         | none                                                                                    | Inverse kinematics to joint angles ([VLABench](../resources/benchmarks/vlabench.md))                                                   |
| microduck (small legged robot)                 | none: gamepad, app or program                        | Hand-made 13-float command: body velocity, head, body pose                                   | none                                                                                    | Learned policy at 50 Hz writing joint targets ([low-level policy loop](low-level-policy-loop.md))                                      |
| SONIC + GR00T N1.5, 3-point (arXiv 2511.07820) | GR00T N1.5, fine-tuned on 300 VR-teleoperation demos | Same format as the teleoperator: head and wrist SE(3) poses, base height, navigation command | Learned kinematic planner: about 2 s of full-body motion at 30 fps, replans up to 10 Hz | SONIC tracking policy at 50 Hz; commands streamed to the motors at 500 Hz                                                              |
| SONIC + GR00T N1.5, whole-body                 | GR00T N1.5                                           | 78-D: 64-D universal motion token plus 14 hand joint angles                                  | skipped                                                                                 | SONIC policy decodes the token                                                                                                         |
| TANGO (humanoid navigation, arXiv 2609.09158)  | VL backbone + action expert on a remote RTX PRO 6000 | 29-DoF joint-space chunks; inference every 0.5 s, 15 actions at 30 Hz, resampled to 50 Hz    | none                                                                                    | SONIC on a Jetson Orin NX, low-level loop at about 200 Hz                                                                              |
| SuperMimic (System 0 only, arXiv 2610.28480)   | none published                                       | K = 10 future reference frames, or a velocity command through a separate encoder             | none                                                                                    | Learned tracker, joint setpoints at 50 Hz; low PD gains make the setpoint a proxy for torque                                           |

- SONIC runs its layers as parallel loops at different rates (input 100 Hz, planner 10 Hz, policy 50 Hz, command writer 500 Hz) that share data on a "latest data wins" basis.
- SONIC compares action spaces for the VLA in the whole-body mode: predicting its FSQ tokens beats predicting SMPL whole-body poses (81-D), 68% vs 27% success on average, and the SMPL version moved jerkily.
- The interface can sit at different depths: above the planner (coarse commands), at the tracker's latent (tokens) or at the reference itself (joint trajectories).

## Why the interface matters for latency
Measured, from TANGO (§5, Table 5): removing real-time chunking lowers success from 43.75% to 10.94% and raises collisions from 9.9% to 14.6%; the authors attribute this to motion continuity across chunks. SuperMimic's listed domain randomization (Table A.3: friction, joint offsets, torso centre of mass) includes no latency or action delay.

**Inference (asked for by the user; no source measures it).** A whole-body reference stream is probably more sensitive to upper-layer latency than a velocity or waypoint command, for three reasons:
- *Stale reference.* The reference is built from an observation that is one call old. If the body has drifted or been pushed, the reference may no longer fit its state, and a tracker trained to follow references has little room to deviate. With a velocity command, the lower layer chooses foot placement from its own fresh sensing.
- *Chunk-boundary jump.* A late chunk starts from where the robot was, not where it is; the gap grows with latency and shows up as a tracking-error spike. TANGO's real-time-chunking ablation is indirect support: it tests continuity across chunks, not latency size.
- *No safe default.* When a velocity command stops, holding it or sending zero lets the lower layer stand. When a reference runs out, the last frame may be an unstable pose.

Also inference: a finer command expresses more (whole-body loco-manipulation) but couples the upper layer's latency more tightly to balance. A fixed-base arm has no balance to lose, so for LIBERO a late chunk costs time or accuracy, not a fall.

## Open questions
- How small System 2 can be: OpenHelix fixes the MLLM (LLaVA-7B) and the policy, and names the question open.
- Which latent form carries visual information when the scene changes within a System 2 interval.
- Real-robot rates: the surveys give almost no Hz figures for either system.
- Whether a whole-body reference interface is in fact more latency-sensitive than a velocity command: no source found sweeps upper-layer latency against success or falls on a legged robot or humanoid.
