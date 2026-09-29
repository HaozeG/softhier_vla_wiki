---
type: paper
tags: [vla, small-model, diffusion-head, lora, pythia]
sources: [arxiv:2409.12514, https://arxiv.org/abs/2409.12514, https://tiny-vla.github.io]
---
# TinyVLA: Towards Fast, Data-Efficient Vision-Language-Action Models for Robotic Manipulation

Wen, Zhu, Li, Zhu, Tang, Wu, Xu, Liu, Cheng, Shen, Peng, Feng, Tang (ECNU, Midea, and others), arXiv 2409.12514 (v5, May 2025; IEEE RA-L 2025).

## Summary
TinyVLA is one of the first explicit efforts at a small, fast VLA. It builds sub-1.5B VLMs on Pythia backbones with a LLaVA-style recipe, fine-tunes them with LoRA, and attaches a diffusion policy head, without pretraining on large robot datasets. It reports higher success and about 20× lower latency than OpenVLA on the authors' real-robot tasks.

## Key claims
- **Design (§III):** Pythia-based VLMs of 70M–1.4B parameters trained with the LLaVA pipeline; on robot data the VLM is fine-tuned with LoRA (about 5% trainable) and LoRA is merged after training; a diffusion policy head (adaptive pooling, LayerNorm, 3-layer MLP conditioning) is trained fully; no Open X-Embodiment pretraining.
- **Sizes (Table II):** TinyVLA-S 422M total / 101M trainable; -B 740M / 138M; -H 1.3B / 143M; OpenVLA 7.2B / 195M.
- **Real-world (5 single-arm tasks, 100 demonstrations each, Table II):** TinyVLA-H 94.0% vs OpenVLA 68.3% vs Diffusion Policy 35.3%; TinyVLA-S 23.3%, -B 77.4% (scales with model size). Bimanual UR5 (Table III): OpenVLA 0% on all three tasks (fine-tuned from single-arm OXE pretraining), TinyVLA-H 30–77%.
- **Simulation (MetaWorld, 50 tasks, Table I):** 31.6% vs Diffusion Policy 10.5%.
- **Latency (Table IV, A6000, per action prediction):** OpenVLA-7B 292 ms → OpenVLA with the 1B backbone 140 ms → TinyVLA-1B 14 ms; the authors attribute the remaining 10× to replacing autoregressive action tokens with a diffusion head.
- **Ablation (Table V):** diffusion head 86–98% vs ACT head 8–23% vs MLP head 0%.
- **Limitations implied:** evaluations are task-specific fine-tunes on a handful of tasks; no cross-embodiment pretraining, which SmolVLA later cites as limiting generalization.

## Relevance to SoftHier-VLA
Historical precursor to [SmolVLA](smolvla.md) and evidence that a decode-free action head, not just a smaller LLM, dominates the latency win. See [VLA architecture overview](../knowledge/vla-architecture-overview.md).

See also: [Octo](octo.md), [OpenVLA](openvla.md), [SmolVLA](smolvla.md).
