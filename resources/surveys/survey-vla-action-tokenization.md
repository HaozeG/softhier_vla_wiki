---
type: paper
tags: [survey, vla, action-tokens, taxonomy]
sources: [arxiv:2507.01925, https://arxiv.org/abs/2507.01925]
---
# A Survey on Vision-Language-Action Models: An Action Tokenization Perspective

Zhong, Bai, Cai, Huang, Chen, Zhang, Wang, Guo, Guan, Lui, Qi, Liang, Chen, Yang (Peking University, PKU-PsiBot), arXiv 2507.01925 (Jul 2025).

## Summary
The survey unifies VLAs as chains of "VLA modules" that produce "action tokens": intermediate or final outputs that progressively encode more actionable information. It classifies action tokens into eight types (language description, code, affordance, trajectory, goal state, latent representation, raw action, reasoning) and summarizes strengths, limitations and empirical highlights of each.

## Key claims
- **Unifying view (§1, §3):** VLA models differ mainly in how action tokens are formulated; that choice shapes foundation-model choice, data needs, training and inference efficiency, interpretability and scalability.
- **Raw action (Table 1, §10):** advantages: minimal annotation, VLM-like training and scaling. Limitations: data scarcity, high latency, poor cross-embodiment generalization. Sub-topics: autoregressive robot VLAs, diffusion-based action chunking, heterogeneous datasets and unified action spaces.
- **Reasoning and language plans:** improve action generation and long-horizon planning but add latency (Table 1).
- **Trends (§13):** the authors expect hierarchical architectures (language plans and code on top; affordance, trajectory and goal-state prediction in the middle; raw-action policy at the bottom), with reasoning integrated as needed; learning from imitation toward RL; and co-evolution of model, data and hardware.

## Related
See also: [Ma et al.](survey-vla-embodied-ai-ma.md), [FAST](../models/fast-tokenizer.md), [Yu et al.](survey-efficient-vla-yu.md).
