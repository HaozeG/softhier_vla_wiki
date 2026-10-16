---
type: paper
tags: [rl, vla, residual-policy, online-rl, pi0.6]
sources: [arxiv:2604.23073, https://arxiv.org/abs/2604.23073]
---
# RL Token: Bootstrapping Online RL with Vision-Language-Action Models

Xu, Springenberg, Equi, Amin, Esmail, Levine, Ke (Physical Intelligence), arXiv 2604.23073 (v2, April 2026). Method name RLT.

## Summary
A way to improve a pretrained VLA on the precision-critical part of a task with sample-efficient online RL. A small encoder-decoder adds an "RL token" on top of the frozen VLA's final-layer embeddings; a small actor and critic trained from scratch by RL then read that token and the robot state, and output short action chunks anchored to the VLA's own proposed chunk. VLA and RL token stay frozen during RL.

## Key claims
- **Problem (§I):** VLAs struggle with "the last millimeter" (slow motions, pauses, retries, small errors in precision-critical phases). Full-model RL on a VLA is compute- and sample-inefficient; small-model real-world RL (SERL, HIL-SERL, RL-100) learns in hours but gives up the VLA's priors.
- **Base VLA (§IV, Fig. 2):** π0.6, with a SigLIP (400M) plus Gemma (4B) backbone and an 860M action expert; up to 4 camera images, language and proprioception in; chunks of H = 50 actions (1 s) out.
- **RL token (Eq. 1-2):** a learned embedding is appended to the VLA's final-layer token embeddings; the encoder output at that position is the RL token (a 1×2048 vector). A decoder must reconstruct the stop-gradient VLA embeddings from it alone, so it is a bottleneck. Language embeddings are dropped because each task has one fixed instruction. Trained on task demonstrations (optionally with VLA SFT) for 2000-10000 gradient steps (App. B).
- **What RL trains (§IV, App. B):** an actor and a critic from scratch: 2-layer MLPs with hidden size 256 (zip tie, Ethernet, charger) or 3-layer with 512 (screw). Input is the RL token plus proprioceptive position and velocity. Critic: TD3-style twin-Q, chunk-level TD (Eq. 3), 2 critic updates per actor update, update-to-data ratio 5, asynchronous rollouts and learning.
- **Actor (Eq. 4-5):** Gaussian with small fixed standard deviation, outputs an RL chunk of C = 10 actions (C < H "for reactivity"), conditioned on the VLA's sampled reference chunk. Objective −Q + β‖a − ã‖²; the reference chunk is zeroed for 50% of training samples and always given at inference.
- **What the VLA provides:** the state representation (RL token), reference chunks (which keep mode information), an exploration prior and warmup data for the replay buffer.
- **Supervision (§V):** sparse human-labelled reward (+1 for success); human interventions replace the reference chunk in stored transitions; RL is applied only to a human-selected critical phase, and the base VLA handles the rest.
- **Rates (§III, §VI-B):** control at 50 Hz, 14-D actions (so the RL chunk is 140-D); the robot executes a prefix of the VLA chunk (for example 20 steps) before replanning. Running the VLA at 50 Hz "would be infeasible", which is why the single-step ablation replaces the RL token with a ResNet-10. No inference latency or compute figures are given.
- **Tasks (Fig. 3):** M3 screw installation, zip tie fastening, Ethernet insertion, charger insertion; full tasks 30-120 s, critical phases 5-20 s; 1-10 h of teleoperated demos per task; RL ran 400-1000 episodes (about 15 min to 5 h of robot data); 50 evaluation episodes per critical phase.
- **Results (§VI):** about 3× faster critical phase even on the easier tasks; large success gains on screw and zip tie (the introduction gives screw insertion from 20% to 65%); full-task success improves "by 40%" (screw) and "60%" (zip tie), without stating absolute or relative. On Ethernet, HIL-SERL and PLD (single-step methods) fail; DAgger and DSRL reach similar success but are much slower; median episode length 146 steps for teleoperation, 228 for the base policy, 66 for RLT.
- **Ablations (Ethernet only):** replacing the RL token with ResNet-10 cuts throughput by 50%; the single-step variant (C = 1) cannot match the base policy; β = 0 gives the largest drop; removing the reference pass-through slows learning.

## Caveats
- Stated limitations (§VII): still needs human reward labels, intervention corrections and manual switching between the RL policy and the base policy.
- Baselines and ablations cover only the Ethernet task; one base VLA and one (bimanual) embodiment; no simulation benchmark; each task has its own fine-tuned VLA and RL token.
- Bar heights in Figs. 4-6 were not extractable; only numbers in the text are recorded here.
