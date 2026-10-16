---
type: paper
tags: [survey, vla, dual-system, system-1-system-2]
sources: [arxiv:2505.03912, https://arxiv.org/abs/2505.03912]
---
# OpenHelix: A Short Survey, Empirical Analysis, and Open-Source Dual-System VLA Model for Robotic Manipulation

Cui, Ding et al. (Westlake University, Zhejiang University, Xi'an Jiaotong University, HKUST-GZ), arXiv 2505.03912 (v1, May 2025). The authors call it an initial, hastily organized report.

## Summary
A short survey of dual-system VLAs (a large, slow MLLM paired with a small, fast policy), a set of controlled experiments on CALVIN, and an open-source model, OpenHelix, built from a frozen LLaVA-7B and a pretrained 3D Diffuser Actor. The experiments ask how the MLLM should be trained, how the two systems should be connected and whether asynchronous running matters.

## Key claims
- **Why split (§1.2):** large VLAs are too slow for real-time control. The paper cites RT-2 running at 1-3 Hz (55B) and about 5 Hz (5B), against about 50 Hz for a lightweight BC-Transformer. Fine-tuning a large pretrained model on robot data also causes domain shift and forgetting.
- **Dual-system idea (§1.3), "Thinking, Fast and Slow":** System 2 is a large MLLM or VLA that is slow, generalizes well and updates rarely, so its output arrives with delay. System 1 is a lightweight policy that runs at high frequency and outputs low-level actions. The two run in parallel at different rates.
- **The paper's definition (§1.4):** "for synchronous inference to occur, System1 must incorporate real-time perception inputs (such as RGB images)". By this criterion π0 and GR00T-N1 "cannot be properly classified within the dual-system framework as they lack this essential characteristic"; §2.3.2 repeats that GR00T-N1 "doesn't fall within the scope of dual systems". §2.2 adds that "the definition of dual systems has always been ambiguous" and that π0 and GR00T-N1 were not tested.
- **Taxonomy (Table 1):**

| Method   | System 2        | MLLM training | Interface (latent)              | System 1                     | System 1 inputs              |
| -------- | --------------- | ------------- | ------------------------------- | ---------------------------- | ---------------------------- |
| LCB      | LLaVA-7B        | LoRA          | `<ACT>` language token          | 3D Diffuser Actor            | RGB, proprio, point cloud    |
| DP-VLA   | OpenVLA-7B      | frozen        | vision + language hidden states | Transformer                  | RGB, proprio                 |
| HiRT     | InstructBLIP-7B | LoRA          | pooled last-layer features      | RT-1-style (EfficientNet-B3) | RGB                          |
| RoboDual | OpenVLA-7B      | LoRA          | action latent + language        | DiT                          | RGB, depth, tactile, proprio |
| DexVLA   | Qwen2-VL-2B     | LoRA          | language                        | ScaleDP                      | RGB, proprio                 |
| Helix    | not disclosed   | not disclosed | not disclosed                   | Transformer                  | RGB, proprio                 |

- **Seven design axes (Fig. 1):** MLLM choice, policy choice (DiT and flow-matching heads are called the consensus), latent representation ("the most complex aspect": last-layer states, middle-layer states as in GR00T-N1, pooled features, learned `<ACT>` tokens), MLLM training, policy training, how the two are connected (projector, CLIP-alignment loss), and the asynchrony strategy (LCB trains synchronously and runs asynchronously at test time; HiRT uses a buffer during training; RoboDual lets the policy refine System 2's coarse actions). MiniVLA (Qwen 0.25B) is cited as a way to cut MLLM cost.
- **Setup of the experiments (§2):** LLaVA 1.0 (7B) plus 3D Diffuser Actor on CALVIN ABC to D, ablations on 100 of the 1,000 evaluation sequences; CALVIN-E (rephrased, enriched instructions) and CALVIN-D (moving objects) are harder variants.
- **Single systems fail on motion:** RoboFlamingo (MLLM plus LSTM over 6 frames) scores 100% on static objects and 0% on all four motion patterns; the policy alone scores 46-84%.
- **Pretrained policy beats scratch:** average length 3.53 against 2.85.
- **MLLM training:** full fine-tuning with a CLIP loss is best on standard CALVIN (3.53, 3.13 without the loss). Prompt tuning (frozen MLLM, only a new `<ACT>` token trained) ties on standard CALVIN (3.28-3.45) and generalizes better on CALVIN-E (2.09-2.13 against 1.74 fine-tuned and 1.46 frozen).
- **Projector pre-alignment is required:** without it all three MLLM variants reach 0% success with a pretrained policy.
- **Asynchrony barely matters:** sweeping 1 to 60 policy steps per MLLM call gives about the same performance, even on CALVIN-D. Probing the `<ACT>` latent shows it encodes the instruction's object, spatial and action words and does not change when the block moves, so the authors conclude "the MLLM merely transmits the semantics of the instructions".
- **Vision and auxiliary loss:** removing the image input drops the score to 1.77; an auxiliary loss predicting position, rotation and gripper from the `<ACT>` embedding raises it to 4.01 (the best ablation).
- **OpenHelix (§3):** LLaVA-7B is frozen; one learnable `<ACT>` token is appended to the instruction and its final-layer 4096-d embedding is projected linearly to 512-d and enters the pretrained 3D Diffuser Actor (65k-iteration checkpoint) by cross-attention, alongside 3D scene tokens (two RGB-D views) and a proprioception token. Loss is L_lm (auxiliary action prediction) plus L_policy (diffusion denoising). Training has two stages: 2k iterations of prompt and projector only, then to 100k iterations with the policy unfrozen; the MLLM stays frozen throughout.
- **Final numbers (Table 8, 1,000 sequences, average length):** policy only 3.27 on CALVIN and 1.42 on CALVIN-E; with the MLLM by prompt tuning 3.30 and 1.72; with auxiliary loss and the MLLM run every 10 policy steps 3.45 and 2.26; every 60 steps 3.44 and 2.20.

## Caveats
- Simulation only (CALVIN); no real-robot results, no latency or Hz measurements for OpenHelix, no policy parameter counts (Fig. 6 plots trainable parameters but the values are not readable from the extracted text).
- One MLLM and one policy were used, so MLLM size, policy type, latent choice and asynchrony strategy were not varied across the design axes.
- The authors admit some claims are "not yet fully verified"; table references are inconsistent (Table 3 against 4; Table 2 cited for the from-scratch result); ablations use 100 episodes with no variance reported.
- §3.2 says the `<ACT>` embedding is trained, §2.3.2 describes training only the lm-head.
- §2.3.2 describes GR00T-N1 as trained with "a frozen paradigm"; the GR00T N1 paper's Table 6 lists its vision encoder and DiT as unfrozen and only the text tokenizer as frozen.
- This note was written from the full text through an automated reading; the table above reproduces Table 1 rows as read.
