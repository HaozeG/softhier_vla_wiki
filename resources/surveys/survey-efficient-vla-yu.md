---
type: paper
tags: [survey, efficient-vla, taxonomy, compression, token-caching]
sources: [arxiv:2510.24795, https://arxiv.org/abs/2510.24795, https://evla-survey.github.io/]
---
# A Survey on Efficient Vision-Language-Action Models

Yu, Wang, Zeng, Zhang, Zhang, Wang, Gao, Song, Sebe, Shen (Tongji, SWJTU, UESTC, Trento), arXiv 2510.24795 (v2, Feb 2026). Project page: evla-survey.github.io.

## Summary
The first survey dedicated to efficient VLAs, covering the whole model-training-data pipeline. It organizes work into three pillars: efficient model design (architectures and compression), efficient training (pre- and post-training), and efficient data collection. It motivates efficiency with three foundational-VLA problems: real-time incompatibility, excessive computational cost, and inefficient data collection.

## Key claims
- **Motivation (§1):** OpenVLA used 21,500 A100-GPU hours on a 64-GPU cluster; π0 needed over 10,000 hours of robot trajectories.
- **Foundational pipeline (§2.1):** vision encoder (ViT, SigLIP, DINOv2, CLIP) → LLM backbone (Qwen, PaLI, Gemma, Llama, Mamba, Vicuna) → action decoder (MLP, autoregressive, or generative: diffusion/flow matching).
- **Efficient architectures (§3.1):** efficient attention (linear attention as in SARA-RT, masking as in Long-VLA and dVLA, KV-cache tricks as in RetoVLA and KV-Efficient VLA); Transformer alternatives (RoboMamba, FlowRAM); efficient action decoding (parallel decoding: OpenVLA-OFT, EdgeVLA, PD-VLA Jacobi decoding, CEED-VLA early exit, Spec-VLA speculative decoding; generative decoding); lightweight components; mixture-of-experts; hierarchical (dual-system) designs.
- **Model compression (§3.2):** layer pruning, quantization, and token optimization (token compression, token pruning, token caching). Caching methods named include VLA-Cache, HybridVLA, FlashVLA (token-aware action reuse), Fast ECoT, EfficientVLA, CronusVLA. The survey notes EfficientVLA argues that VLA-Cache is limited by the LLM memory bottleneck.
- **Limitations (§3.3):** aggressive structural optimization can cause semantic drift and hurt long-horizon dexterity; asynchronous and hierarchical designs struggle with spatiotemporal coherence; static importance metrics limit adaptability; hardware-algorithm co-design is called out as future work.
- **Training and data (§4–5):** LoRA, distillation, RL fine-tuning, data-efficient pretraining, latent actions, simulation and human-in-the-loop data.
- **Naming caveat:** the survey lists a "FlashVLA" that reuses actions based on token stability; a different paper with the same name ([FlashVLA, streaming decoding](../serving/flashvla-streaming.md)) exists, and [Guan et al.](survey-efficient-vla-guan.md) describe yet another SVD-based token-pruning "FlashVLA". Check the arXiv ID before citing.

## Related
See also: [Guan et al.](survey-efficient-vla-guan.md), [Ma et al.](survey-vla-embodied-ai-ma.md), [Zhong et al.](survey-vla-action-tokenization.md), [VLA-Perf](../serving/vla-perf.md).
