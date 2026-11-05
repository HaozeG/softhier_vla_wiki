---
type: concept
tags: [benchmark, simulation, evaluation, generalization, libero, vlabench, task-success]
sources: [resources/benchmarks/vlabench.md, resources/models/smolvla.md, resources/models/openvla-oft.md, resources/models/tinyvla.md, resources/surveys/survey-openhelix-dual-system.md, resources/serving/vla-workload-characterization-kaist.md, resources/surveys/guide-embodied-ai.md]
---
# Simulation benchmarks for robot policies

## Summary
A simulation benchmark tests how well a policy *does tasks*. It has three parts: a task suite in a simulator, a split between seen and unseen conditions, and a score. (How fast a model *runs* is a different kind of benchmark, covered in [benchmark workloads](vla-benchmark-workloads.md).) The wiki's model sources mostly report LIBERO success rates. CALVIN and Meta-World appear once each. VLABench is the one benchmark source ingested so far. It argues that these suites use template instructions and test only unseen instances of seen object categories. It builds 100 tasks that need knowledge, implicit goals and long horizons, and there OpenVLA, Octo and RDT-1B score low after fine-tuning. The note lists the benchmarks the wiki meets, then VLABench's design, then what it reports for VLAs.

```text
 simulator (MuJoCo, ...)
 +------------------+   demos    +-----------------+  rollouts  +-------------+
 | task suite       |----------->| policy under    |----------->| score       |
 | tasks, language, |  fine-tune | test            |            | success 0/1 |
 | randomized scenes|            |                 |            | or VLABench |
 +------------------+            +-----------------+            | Progress    |
          |                                                     | Score       |
          v                                                     +-------------+
 seen vs unseen split
   LIBERO, RLBench, CALVIN: unseen instances of seen categories (VLABench's
                            description)
   VLABench: unseen categories, unseen phrasing, unseen similar tasks

 VLABench: 100 tasks, Franka Panda
   60 primitive, 5 dimensions        ~120 steps (157 in its Fig. 9)
   40 composite, skills + planning   >500 steps
   tracks: VLA (fine-tune, roll out) | workflow (zero-shot, roll out)
           | VLM (skill-language plan matched to a reference graph)
```

## Details
**Benchmarks the wiki's sources use**
| Benchmark  | Where it appears                                                                                                                                                                                        | What is reported                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| LIBERO     | [SmolVLA](../resources/models/smolvla.md), [OpenVLA-OFT](../resources/models/openvla-oft.md), [Jung et al.](../resources/serving/vla-workload-characterization-kaist.md) (MuJoCo, official checkpoints) | success rate; SmolVLA paper: OpenVLA 76.5, Octo 75.1, SmolVLA 0.45B 87.3; OpenVLA-OFT paper: OFT 97.1 |
| CALVIN     | [OpenHelix](../resources/surveys/survey-openhelix-dual-system.md)                                                                                                                                       | average completed sequence length (for example 3.27 policy only)                                      |
| Meta-World | [TinyVLA](../resources/models/tinyvla.md)                                                                                                                                                               | success rate over 50 tasks (TinyVLA 31.6%, Diffusion Policy 10.5%)                                    |
| VLABench   | [VLABench](../resources/benchmarks/vlabench.md)                                                                                                                                                         | Progress Score (partial credit) for VLAs and workflows; graph-matching score for VLM plans            |

The Embodied-AI-Guide files benchmarks under Infrastructure, next to simulators and datasets ([guide](../resources/surveys/guide-embodied-ai.md)).

**What VLABench changes ([source](../resources/benchmarks/vlabench.md))**
- **Instructions:** GPT-4 writes natural, often indirect requests ("I just worked out at the gym... grab an electrolyte drink"), in place of the templates VLABench says other suites use.
- **Generalization:** unseen means new object categories (kiwi instead of apple), out-of-domain phrasing, and unseen but similar tasks.
- **Horizon:** composite tasks average over 500 timesteps at 10 Hz control.
- **Score:** Progress Score gives 20% of the credit for picking the right objects and 80% for completed sub-steps, so a failed episode can still score.
- **Data:** demonstrations come from scripted planners over a skill library, not teleoperation.
- VLABench's comparison of itself with other suites (its Table 1) is the authors' own assessment.

**What VLABench reports for VLAs (Progress Score, 0–100)**
- Fine-tuned on 1,600 demonstrations, seen-object primitive tasks average Octo 1.34, OpenVLA 11.74, RDT-1B 15.37. On unseen object categories the averages fall to 0.77, 7.93 and 9.08 (base tasks). On out-of-domain phrasing, unseen but similar tasks and composite tasks every average is below 5, and Octo scores 0.00 on all three.
- Pretraining helps compared with training from scratch (OpenVLA 3.02 to 11.74), and going from 100 to 2,000 demonstrations raises the score by only a few points.
- Closed-loop RDT-1B scores 17.68 against 15.37 for open-loop 64-step chunks (see [action representation and chunking](action-representation-and-chunking.md)).
- The authors name single 224×224 images, no memory of past actions, the precision loss of action tokens, and OpenVLA's trajectory-only pretraining as causes. Octo's own paper reports 2 frames of history, which differs from VLABench's statement that current models see only the current state ([Octo](../resources/models/octo.md)).

**Reading the numbers together.** OpenVLA and Octo score about 75–77 on LIBERO (success rate, SmolVLA's Table 2) and 1–12 on VLABench seen primitive tasks (Progress Score). The metrics, training data and protocols differ, so the two sets are not on one scale.

## Open questions
- No benchmark source covers real-robot evaluation or real-to-sim reconstruction (SimplerEnv-style); the wiki has no such source yet.
- How newer VLAs (π0, SmolVLA, OpenVLA-OFT) score on VLABench is not in the ingested sources.
- VLABench's text and figures disagree on two points (workflow scores, primitive-task horizon); see its Caveats.
