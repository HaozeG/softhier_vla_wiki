---
type: paper
tags: [imitation-learning, action-chunking, cvae, temporal-ensembling, aloha, bimanual]
sources: [arxiv:2304.13705, https://arxiv.org/abs/2304.13705, https://tonyzhaozh.github.io/aloha]
---
# Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT, ALOHA)

Zhao, Kumar, Levine, Finn (Stanford, UC Berkeley, Meta), arXiv 2304.13705 (v1, April 2023).

## Summary
The paper presents ALOHA, a bimanual teleoperation system under $20k, and ACT (Action Chunking with Transformers), an imitation-learning algorithm. ACT predicts the next k target joint positions at once (action chunking) to cut the effective horizon k-fold and so reduce compounding errors, averages overlapping chunks at run time (temporal ensembling), and is trained as a conditional VAE (CVAE) so that it can learn from variable human demonstrations. It learns 6 real fine-manipulation tasks at 80–96% on its easier ones from about 50 demonstrations (10–20 minutes) each.

## Key claims
- **Problem (§I, §II):** behavioural cloning (BC) casts imitation as supervised learning from observations to actions; its main weakness is compounding error, where small errors drive the robot off the training distribution. DAgger-style fixes need expert corrections, which the authors call unnatural with teleoperation.
- **ALOHA (§III):** two ViperX follower arms driven by joint-space mapping from two smaller leader arms that the human backdrives; 4 cameras; open hardware and software.
- **Data (§IV, §V-B):** actions are the leader arms' joint positions, tracked by a low-level PID controller in the motors; observations are 4 RGB images (480×640) and the follower joint positions (14 DoF). Control runs at 50 Hz; episodes are 400–700 steps; 50 demonstrations per task (100 for Thread Velcro).
- **Action chunking (§IV-A):** the policy models π(a_t:t+k | s_t) instead of π(a_t | s_t), giving a k-fold shorter effective horizon; chunking also helps with pauses in demonstrations that single-step policies handle poorly.
- **Temporal ensembling (§IV-A, Algorithm 2):** the policy is queried every step and the overlapping predictions for the current step are averaged with weights w_i = exp(−m·i), where w_0 is the weight of the oldest prediction; a smaller m takes in new observations faster. It adds no training cost, only inference compute.
- **CVAE (§IV-B, Algorithm 1, Fig. 4):** a transformer encoder compresses the action sequence and joint positions into a style variable z (diagonal Gaussian); the decoder (the policy: ResNet18 image backbones, transformer encoder, transformer decoder) predicts a k×14 action tensor from images, joints and z. The encoder is discarded at test time and z is set to the prior mean (zero), so decoding is deterministic. Loss: reconstruction plus β-weighted KL to N(0, I).
- **Results (Tables I–II):** ACT beats BC-ConvMLP, BeT, RT-1 and VINN on all tasks; e.g. Slide Ziploc 88% and Slot Battery 96% where baselines make no progress past the first stage; Thread Velcro only 20%. Baselines BeT and RT-1 output discretized actions; ACT outputs continuous ones.
- **Ablations (§VI, Fig. 8):** chunk size k = 1 → 1% and k = 100 → 44% averaged over 4 simulated settings (without ensembling), dipping slightly at k = 200 and 400, close to open loop; adding chunking also improves BC-ConvMLP and VINN. Temporal ensembling: +3.3% for ACT, +4% for BC-ConvMLP, −20% for VINN. Without the CVAE objective, success on human data drops from 35.3% to 2%, while scripted data is nearly unaffected.
- **High frequency (§VI-C):** in a 6-person user study, teleoperating at 5 Hz instead of 50 Hz made tasks take 62% longer.

## Caveats
- Algorithm 1 gives an MSE reconstruction loss, while the no-CVAE ablation is described as trained with L1 loss.
- The default chunk size used for the main results is not stated in the pages read for this note.
- Real-world results use one seed and 25 trials per task.

## Related
See also: [Diffusion Policy](diffusion-policy.md), [OpenVLA-OFT](openvla-oft.md), [TinyVLA](tinyvla.md), [robot learning tutorial](../surveys/tutorial-robot-learning-hf.md).
