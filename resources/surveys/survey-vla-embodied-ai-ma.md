---
type: paper
tags: [survey, vla, taxonomy, embodied-ai]
sources: [arxiv:2405.14093, https://arxiv.org/abs/2405.14093]
---
# A Survey on Vision-Language-Action Models for Embodied AI

Ma, Song, Zhuang, Hao, King (CUHK, Bristol, Huawei Noah's Ark), arXiv 2405.14093 (v8, May 2026; IEEE TNNLS 2025). The first survey with "VLA" in the title.

## Summary
A broad survey that organizes VLA research into three lines: components of VLAs (pretrained visual representations, dynamics learning, world models, reasoning, RL), low-level control policies (transformer, diffusion, 3D-vision, large VLAs) and high-level task planners (monolithic and modular). It also catalogs datasets, simulators and benchmarks, and lists open challenges.

## Key claims
- **Definition (§I):** the term VLA was coined by RT-2; the survey generalizes it to any model that takes vision and language and produces robot actions, calling the original RT-2-style models "Large VLAs (LVLAs)".
- **Hierarchy (Fig. 4):** most robotic systems combine a high-level task planner (decomposes an instruction into subtasks) with a low-level control policy, because the planner can be a large model while the policy focuses on speed and precision.
- **Component tour (§III-A):** RL, pretrained visual representations (CLIP, R3M, VIP), video representations, dynamics learning, world models, reasoning.
- **Control policies (§III-B):** from CLIPort and BC-Z through transformer policies (RT-1 lineage) to diffusion and large VLAs.
- **RL as a component (§II, §III-A1; read from the v8 text, so numbering may differ in earlier versions):** robot learning "is also usually framed as an RL problem" (an MDP or POMDP over trajectories), trained "via TD learning and policy gradients"; imitation learning is used when the reward is hard to define. RL "laid the foundation for embodied AI and continues to help advance VLAs". Named methods: DQN (policies from pixels, "underscoring the need for greater model capacity in end-to-end RL"); Decision Transformer and Trajectory Transformer (RL trajectories as sequence modelling); Gato (multimodal, multitask, multi-embodiment); π*0.6 ("employs RL for VLAs to learn from experience", the survey's only description of RL fine-tuning a large VLA); RLHF and SEED (RLHF with skill-based RL for sparse rewards and safety); Reflexion ("verbal RL" through linguistic feedback); Eureka (LLM-designed reward functions that "outperform expert human-engineered ones").
- **RL-adjacent methods elsewhere:** Q-Transformer (§III-B: RT-1 with autoregressive Q-functions and a conservative regularizer, so it can learn from failed trajectories); Dreamer (§III-A5: learning through imagination in a world model); RAP (LLM as policy and world model with tree search); UniSim and E2WM (world models generating experience); V-GPS (§III-A9: re-ranks VLA actions with a learned value function at test time) and RoboMonkey (a VLM-based verifier picks the action); SayCan (the low-level value function serves as affordance); NORA-1.5 ("reward-guided post-training"). Online-RL VLA works (π_RL, SimpleVLA-RL, GR-RL, IRL-VLA, iRe-VLA, ConRFT, VLA-RFT, WMPO) appear only as names in the appendix list and timeline.
- **Speed and capacity (§I, §III-B9, §III-B10d):** "conventional robot policies based on RL have largely focused on addressing a limited set of tasks within controlled environments, such as item grasping". The planner "can leverage models with high capacity while the low-level control policy can focus on speed and precision, similar to hierarchical RL". For GR00T N1 the survey reports the VLM System 2 at 10 Hz and the diffusion System 1 at 120 Hz.
- **Challenges (§VI):** real-time responsiveness: "current VLA models ... face a tradeoff between speed and capacity" and inference that cannot keep pace generates stale actions; also data scarcity, safety, multi-agent systems and applications.

## Related
See also: [Zhong et al.](survey-vla-action-tokenization.md).

## Caveats
- The survey makes no direct claim that RL policies are small or fast, gives no RL-specific limitations of fine-tuning VLAs by RL, and reports no benchmark numbers for RL methods; the SEED attribution (reference [20]) comes from the citation number in the text.
