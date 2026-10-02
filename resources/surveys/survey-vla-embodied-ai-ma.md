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
- **Challenges (§VI):** real-time responsiveness: "current VLA models ... face a tradeoff between speed and capacity" and inference that cannot keep pace generates stale actions; also data scarcity, safety, multi-agent systems and applications.

## Related
See also: [Zhong et al.](survey-vla-action-tokenization.md), [Yu et al.](survey-efficient-vla-yu.md), [Guan et al.](survey-efficient-vla-guan.md).
