---
type: paper
tags: [benchmark, simulation, evaluation, mujoco, language-conditioned-manipulation, generalization, long-horizon, vlm-evaluation]
sources: [https://vlabench.github.io/media/VLAbench_arxiv_v1.pdf, arxiv:2412.18194, https://arxiv.org/abs/2412.18194, https://vlabench.github.io/]
---
# VLABench: A Large-Scale Benchmark for Language-Conditioned Robotics Manipulation with Long-Horizon Reasoning Tasks

Zhang, Xu, Liu, Yu, et al. (Fudan University), arXiv 2412.18194 (v1, posted December 2024). Read from the project-site PDF; numbers checked against the arXiv HTML rendering (see Caveats for where the two differ).

## Summary
VLABench is an open-source MuJoCo benchmark of 100 language-conditioned manipulation (LCM) task categories (60 primitive, 40 composite) built for methods that rest on foundation models. Its tasks are meant to need world knowledge, implicit goals stated in natural conversation instead of templates, and multi-step reasoning over long horizons. It ships an automatic demonstration generator and evaluates three kinds of method: fine-tuned pretrained VLAs (OpenVLA, Octo, RDT-1B), training-free LLM/VLM workflows (VoxPoser, CoPA), and VLMs that plan in a skill language. All three score low; the authors conclude current VLAs do not show LLM-like generalization after fine-tuning.

## Key claims
**Benchmark design**
- **Tasks (§3.1, §6.1, Table 6):** 60 primitive tasks in five ability dimensions (mesh and texture, spatial, common sense and world knowledge, semantic instructions, physical laws) and 40 composite tasks that combine skills with long-horizon planning and logical reasoning. Ten skills: pick and place, open/close door, open/close drawer, hang, tool use, press button, insert, pour, twist, explore.
- **One task, many instances (§6.1):** a task is an asset theme plus actions; "apple on a plate" and "pear in a box" are one task, with targets, receptacles and distractors redrawn every rollout.
- **Horizon (§3.1, §6.1, Fig. 9):** composite episodes average over 500 timesteps against about 120 for primitive tasks (§3.1); Table 6 lengths are at 10 Hz control. Fig. 9 average horizon lengths: ManiSkill 52.3, LIBERO 77.3, RoboCasa Atomic 123.0, ARNOLD 125.8, VLABench Primitive 157.2, RLBench 160.2, RoboCasa Composite 371.9, VLABench Composite 502.5; the text calls these 27.0% and 35.1% above RoboCasa Atomic and Composite.
- **Comparison with other benchmarks (Table 1, authors' own):** VLABench is the only row ticked for semantically rich language, logical reasoning and knowledge; 100 tasks, 163 asset categories, 2,164 objects. LIBERO: 130 tasks, 51 categories, 75 objects; RLBench 100 tasks; CALVIN 34; RoboCasa 100 tasks, 2,509 objects; Behavior-1K 1,000 tasks.
- **Stricter generalization (§3.2):** "unseen" means unseen object *categories* (seen fruit: apple, banana, pear, orange; unseen: kiwi, mango, strawberry, lemon), not unseen instances of a seen category as in RLBench and CALVIN.
- **Metric (§3.2, Eq. 1):** Progress Score PS = α·n_correct/N + (1−α)·m_done/M, where N counts target objects and receptacles, M counts sub-steps, and α = 0.2 by default. Workflows are scored the same way: correct target identification gives 20%, success gives full marks (§9.2).
- **VLM metric (§9.3, Eqs. 2–6):** the VLM's skill sequence is turned into a dependency graph (DAG) and matched to a reference: skill recall, parameter recall, skill-and-parameter recall, and precise matching (nodes that match and satisfy their dependencies), summed with weights w1..w4 that add to 1. The weights are not given.

**Simulation and data**
- **Simulator and robot (§3.3, §7.2):** MuJoCo with dm_control. Standard evaluation uses a 7-DoF Franka Panda with a parallel gripper; end-effector position and quaternion are converted to joint angles by inverse kinematics. Other arms, dual-arm, humanoid, quadruped and mobile robots are supported.
- **Assets and scenes (§3.3, §7.1, §7.3, Table 3):** assets from RoboCasa, Objaverse, online model sites, and text/image-to-3D generation; 163 categories, 2,164 items; over 20 scene types. Grasp points were pre-annotated with GraspNet and receptacle boxes with SAM, then refined by hand.
- **Observations (§6.2):** multi-view RGB-D, segmentation, point clouds, proprioception, sparse reward; demonstrations follow an RLDS-like layout.
- **Domain randomization (§6.3):** mesh instance (for example one of 20 apples), position ±0.05 in x and y, yaw ±π/10, scale 0.95–1.05, lighting 0.8–1.2, scene textures, and optional distractor objects.
- **Automatic demonstrations (§3.4, §8):** task-specific planners call a skill library written as a domain-specific language (DSL) with skills, parameters and execution sequences; parameters come from annotations and the scene. Trajectories use RRT, SLERP for rotations and Bezier smoothing, with rejection sampling on gripper-scene point-cloud overlap and early stop on failure. GPT-4 writes ten instruction variants per data point.

**Results: fine-tuned VLAs (§4.1, §9.1, Table 2; scores are PS on a 0–100 scale)**
- **Setup:** OpenVLA (LoRA), Octo and RDT-1B (full fine-tuning) with authors' default hyperparameters, fixed epochs, trained to convergence on 4 A800 80 GB GPUs. 100 trajectories per task category, 1,600 in total, joint training on base and common-sense data. OpenVLA and Octo take one camera view, RDT-1B three.
- **Seen / unseen objects, average over eight primitive tasks (Table 2a):** base tasks Octo 1.34 / 0.77, OpenVLA 11.74 / 7.93, RDT-1B 15.37 / 9.08; common-sense tasks Octo 1.16 / 0.96, OpenVLA 8.46 / 5.11, RDT-1B 11.97 / 3.61. The best single cell is OpenVLA on Select Painting, 40.20 seen.
- **Out-of-domain language (2b), unseen similar tasks (2c), composite tasks (2d), averages:** Octo 0.00 / 0.00 / 0.00; OpenVLA 4.15 / 4.46 / 2.66; RDT-1B 4.31 / 3.85 / 3.34.
- **Authors' reading (§4.1):** RDT-1B learns skills better; OpenVLA, limited by action discretization and single-frame input, learns skills worse but keeps more on unseen-object common-sense tasks, which they credit to its Llama 2 7B base. They put current VLAs "far from" a GPT-2-level stage.

**Ablations (§10.1)**
- **From scratch vs pretrained (Table 4, seen primitive tasks, PS):** Octo 1.02 vs 1.34, OpenVLA 3.02 vs 11.74, RDT-1B 6.26 vs 15.37.
- **Open vs closed loop for RDT-1B (Table 5, PS):** open loop with 64-step chunks 15.37, 32-step chunks 15.52, closed loop 17.68. The authors read the small gain as showing the low success comes mainly from the model itself.
- **Data scaling (Fig. 12, Put Box on Painting, 100 / 500 / 1,000 / 2,000 demos):** PS rises only a few points (read off the chart: OpenVLA about 12 to 19, RDT about 15 to 21, Octo about 1 to 5); trajectories get smoother but success stays low.
- **Causes named (§10.1):** 224×224 single-image input (OpenVLA, Octo); no memory of past actions, so long tasks loop; token heads lose precision while diffusion heads lack vision-language pretraining and use large separate encoders such as T5; OpenVLA's trajectory-only pretraining may erode its VLM's knowledge, unlike RT-2's co-training.

**Results: workflows and VLMs (§4.2, §4.3, §10.2, §10.3)**
- **VoxPoser and CoPA (Fig. 4):** the text says VoxPoser reached PS 30–40 on basic tasks. Adding GPT-4V perception helped spatial tasks but lowered semantic and common-sense scores. Both did poorly on physical-law and composite tasks for lack of closed-loop feedback. Failures were traced to perception (segmentation sensitivity in CoPA), grasp planning (no rotation, centroid grasps, GraspNet finding no grasp) and errors between modules (§10.2).
- **VLMs (Fig. 5, 1-shot except GLM-4V-9B at 0-shot):** GPT-4-turbo, GPT-4o, GLM-4V-9B, MiniCPM-V2.6, Qwen2-VL-7B, InternVL2-8B, LLaVA-NeXT, scored on six dimensions. All struggle with long-horizon decomposition and logic; only GPT-4o scores on reasoning near its other dimensions, others about 20. Qwen2-VL-7B beats GPT-4-turbo on some dimensions.
- **VLM ablations (§10.3, Figs. 16–17):** chain-of-thought prompting helped InternVL2 overall and helped LLaVA-NeXT and Qwen2-VL on complex and physics tasks, but MiniCPM produced no final answer and scored 0. Few-shot examples (0 to 7) helped Qwen2-VL, with little gain past two or three shots on semantic and spatial tasks.

## Caveats
- **Simulation only;** no real-robot transfer is tested. Episodes per task for evaluation are not stated.
- **Scores are Progress Scores, not success rates.** Table 2 does not name its metric; its seen averages equal Table 4's "From Pretrained" column and Table 5's "Avg PS" row, which identifies it as PS. PS gives partial credit (20% for choosing the right objects), unlike the 0/1 task success the paper contrasts it with (§3.2).
- **Workflow numbers disagree with the figure:** the text cites PS 30–40 for VoxPoser, but Fig. 4's axis tops out near 23.
- **Horizon claim vs Fig. 9:** the text says VLABench has the longest horizon for both primitive and composite tasks, but Fig. 9 places RLBench (160.2) above VLABench Primitive (157.2); §3.1 gives about 120 timesteps for primitive tasks against 157.2 in Fig. 9.
- **Memory claim vs Octo's paper:** §10.1 says current models take only the current state; Octo's own paper uses 2 frames of history (see [Octo](../models/octo.md)). The paper also calls Octo a pretrained VLA, though Octo is not built on a VLM.
- **Version differences:** the arXiv v1 HTML cites Table 5 for the from-scratch ablation, Figure 5 for the workflow chart, Figure 17 for chain-of-thought and Figure 15 for rotation failures; the project-site PDF corrects the first, second and fourth to Table 4, Figure 4 and Figure 13. Table values are the same in both.
- **Comparison table is self-reported:** Table 1 is the authors' feature check of competing benchmarks.

## Reading notes (inference)
- The 100-demo points in Fig. 12 (about 1.3, 11.7, 15.4) look equal to the eight-task seen averages in Table 2a, not to the Select Painting scores, although the caption names a single task. Read off the chart; not stated by the paper.

## Related
See also: [OpenVLA](../models/openvla.md), [Octo](../models/octo.md), [RT-2](../models/rt-2.md).
