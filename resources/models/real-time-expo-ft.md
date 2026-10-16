---
type: paper
tags: [rl, vla, residual-policy, asynchronous, latency]
sources: [arxiv:2609.18207, https://arxiv.org/abs/2609.18207]
---
# Reinforcement Learning for Real-Time Vision-Language-Action Policies

Dong, Hung, Sadigh, Finn (Stanford), arXiv 2609.18207 (v1, September 2026). Method name Real-Time EXPO-FT.

## Summary
RL fine-tuning for a large VLA that is too slow to react. A large flow-matching VLA runs asynchronously and proposes candidate action chunks; a small "edit" policy, trained by RL, adds a bounded residual to each candidate using the latest observation; a learned critic picks the best candidate. It builds on EXPO and EXPO-FT.

## Key claims
- **Problem (§I, §IV-A):** VLA inference is slow, so the action executed at time t was computed from an older observation (state s_{t−d}), a distribution shift that also breaks the Markov assumption of RL and "can bias credit assignment". Asynchronous methods (RTC, Training-Time RTC, VLASH, πR2) are mostly imitation-based and offer no mechanism for going beyond the data; plain RL on top of RTC "leaves performance on the table" because actions still come from old observations.
- **Slow, asynchronous step (§III, Fig. 2):** VLA inference starts when d steps remain in the chunk; it samples N candidate chunks from s_t, inpaints the d in-flight actions as a prefix (Training-Time RTC style), and keeps the segment a_{t+d : t+d+C}.
- **Fast, synchronous step:** at s_{t+d} the edit policy edits each candidate (within [−β, β]) using the latest observation; the critic Q(s_{t+d}, ·) takes an argmax over the 2N base and edited chunks. The paper claims the combination "remains Markovian with delays".
- **Training (§IV-B):** the VLA is trained by masked flow-matching BC only on successful episodes (demonstrations plus successful online episodes); the edit policy by the EXPO Q-maximization objective plus entropy; the critic by chunk-level TD. An optional noise-space critic (after FASTER) scores 32 noise seeds so one VLA decode suffices per backup.
- **Sizes and trainable parts (App. E):** base π0.5 with `gemma_2b_lora` language backbone and `gemma_300m_lora` action expert, horizon H = 16, execution window C = 8, 10 Euler denoising steps, N = 32 base candidates plus 32 edited; no total parameter count given. The VLA is updated (LoRA adapters, SigLIP tower, projections) by BC, one step per 20 critic steps. Edit policy: tanh-Gaussian MLP, 3 hidden layers of 256, over 56 dimensions, reusing the critic's image embedding. Critic: REDQ ensemble of 10 MLPs (256×3) on a ResNetV2 encoder (the main text says ResNet-50; the appendix gives basic blocks with depths 3,4,6,3).
- **Latency and rate (§V-C, App. E-3):** real robot is a DROID single-arm setup at 30 Hz with two 224×224 views; VLA inference about 67 ms on the authors' server; three tasks add 100 ms, which the main text calls about 167 ms (d = 5) and the appendix describes as approximating π0.5 on a typical edge GPU; Dynamic Picking keeps 67 ms with d = 3. Delay is d = ⌊t·f⌋ + 1. No measured latency for the edit policy or critic selection is given.
- **Simulation (§V-B, Table II):** Kinetix, 10 state-based tasks, 100k environment steps, delay of 4: Real-Time EXPO-FT averages 96.2%; delayed baselines DSRL 61.7, DSRL with RTC 76.1, EXPO-FT 74.9, EXPO-FT with RTC 81.7, RTC 80.0, BC 55.2; zero-delay references RLPD 81.4 and BC 90.7.
- **Real robot (§V-C, Table I):** four tasks (Dynamic Picking, Ball Balancing, Object Passing, Soccer Kicking), at most 10 minutes of online data, no human interventions, 30 trials each: Real-Time EXPO-FT 29/30 (97%) against SFT 12.5/30, SFT with RTC 18/30, RLPD 4.5/30, DSRL 18.3/30, DSRL with RTC 20/30, EXPO-FT 18.8/30, EXPO-FT with RTC 25/30.
- **Ablations:** stable performance as delay grows (H17 Unicycle) where RTC degrades; success near 100% over object speeds 0.5× to 1.25× in Object Passing; filtering at the noise level is more compute-efficient than filtering fully denoised actions (App. A).

## Caveats
- Stated limitations (§VI): environment resets are done by a human; each task needs its own success classifier; other reward formulations not explored.
- Fairness notes (stated): RLPD and DSRL get higher update-to-data learners, which the authors say favour those baselines; two tasks give privileged state to the critic and edit policy but not the VLA.
- The claim of best results in 10 of 10 simulated environments depends on a within-0.95× bolding tolerance (Chain Lander: 92 for DSRL with RTC against 96).
- Training budgets are small (about 5k-18k environment steps per task, Table IV).
