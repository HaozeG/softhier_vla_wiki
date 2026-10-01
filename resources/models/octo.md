---
type: paper
tags: [vla, foundational, generalist-policy, diffusion-head, small-model]
sources: [arxiv:2405.12213, https://arxiv.org/abs/2405.12213, https://octo-models.github.io]
---
# Octo: An Open-Source Generalist Robot Policy

Octo Model Team (Berkeley, Stanford, CMU, DeepMind), arXiv 2405.12213 (v2, May 2024; RSS 2024). Not a VLM-based VLA, but the small-model reference point that later VLAs (OpenVLA, π0, SmolVLA) compare against.

## Summary
Octo is a transformer policy pretrained from scratch on 800k Open X-Embodiment episodes (25 datasets), with flexible task (language or goal image) and observation inputs and a small diffusion action head. Two checkpoints are released: Octo-Small (27M) and Octo-Base (93M). It is designed to be fine-tuned to new sensors and action spaces in hours on a consumer GPU.

## Key claims
- **Architecture (§III-A, App. D):** T5-base (111M) encodes language; a shallow convolution stack patches images (16×16 patches; 256 tokens for the third-person view, 64 for a wrist view); a block-wise causal transformer (Small: 12 layers, width 384; Base: 12 layers, width 768) with readout tokens that no other token attends to; a 3-layer MLP diffusion head (hidden 256) with 20 DDPM steps predicting an action chunk. The backbone runs once per prediction; denoising happens only in the small head (§III-C).
- **Training (§III-D):** 2 frames of history; Octo-Base trained 300k steps at batch 2048 on a TPU v4-128 in 14 hours. Fine-tuning with about 100 demonstrations takes about 5 hours on one 24 GB A5000.
- **Results (§IV):** zero-shot, 29% higher success than RT-1-X (35M) and similar to RT-2-X (55B) on WidowX and RT-1 robot; fine-tuned across six new domains averaging 72% vs 20% for a ResNet+transformer from scratch and 15% for VC-1 (Table I).
- **Ablations (Table II, WidowX):** Octo-Small 83%; discretized action heads 18%; MSE heads 35%; single-robot data 43%; ResNet-50 + transformer 70%. Diffusion decoding beat both alternatives.
- **Noted negatives (App. E):** proprioceptive input seemed to hurt; ResNet encoders were better than ViTs from scratch on small data but scaled worse; halving patch size to 16 improved grasping at 4× tokens.

## Relevance to SoftHier-VLA
Shows that a 27–93M policy with a cheap diffusion head is a viable lower bound on compute: the backbone cost is one pass over a few hundred tokens. It has no web-scale VLM pretraining, so its semantic generalization is weaker (see [OpenVLA](openvla.md) and [π0](pi0.md)). See [VLA architecture overview](../../knowledge/vla-architecture-overview.md).

See also: [TinyVLA](tinyvla.md), [OpenVLA](openvla.md), [π0](pi0.md), [GR00T N1](gr00t-n1.md), [SmolVLA](smolvla.md).
