---
type: paper
tags: [tutorial, robot-learning, imitation-learning, behavioural-cloning, reinforcement-learning, lerobot]
sources: [arxiv:2510.12403, https://arxiv.org/abs/2510.12403, https://github.com/huggingface/lerobot]
---
# Robot Learning: A Tutorial

Capuano, Pascal, Zouitine, Wolf, Aractingi (University of Oxford, Hugging Face), arXiv 2510.12403 (v1, October 2025). Code examples use Hugging Face's `lerobot` library.

## Summary
A tutorial that walks from classical model-based robotics to learned policies: reinforcement learning (RL), then imitation learning by behavioural cloning (BC) with generative models (VAEs, diffusion, flow matching), the single-task BC policies ACT and Diffusion Policy, and finally generalist language-conditioned VLAs (π0, SmolVLA). It argues that generalist VLAs belong with BC methods because both are trained to reproduce demonstration trajectories.

## Key claims
- **Classical robotics (§2):** explicit dynamics models (kinematics, feedback control) are brittle to unmodelled effects such as contact and deformation, need expert tuning, and do not improve with more data.
- **RL (§3):** an agent improves by trial and error from a scalar reward in a Markov decision process; on real robots it suffers from sample inefficiency, unsafe exploration, reward design, success detection and resets. HIL-SERL (human interventions, prior data, learned reward classifiers) is presented as making real-world RL feasible.
- **BC (§4, Eq. 18):** learn a mapping from observations (images plus proprioception) to actions from reward-free expert trajectories, as supervised learning. Advantages: offline and safe, no reward design, success and resets implicit in the data; it can be at best as good as the demonstrator.
- **BC failure modes (§4, Fig. 20):** point-estimate policies suffer from compounding errors due to covariate shift (small errors lead to out-of-distribution states) and fit multimodal demonstrations poorly, averaging between equally good modes. Generative models are the proposed remedy.
- **Generative models (§4.1):** VAEs (latent variables, ELBO), diffusion models (iterative denoising), and flow matching (§4.1.3), which regresses a vector field onto the straight path between a noise sample and a data sample and samples by forward-Euler integration over tens of steps; straighter paths can need fewer steps than diffusion.
- **ACT and Diffusion Policy (§4.2–4.3):** ACT applies a conditional VAE to action chunks to reduce compounding errors; Diffusion Policy conditions a diffusion model on an observation history to predict action chunks.
- **Generalist policies (§5):** π0 trains its VLM backbone and action expert with a flow-matching loss, samples flow time from a Beta distribution weighted toward noisier chunks, and uses as few as 10 integration steps; its pretraining mix ("the π dataset") is 10M+ trajectories, about 9.1% openly available (Open-X, DROID), followed by fine-tuning on high-quality task data. The tutorial calls flow matching "a continuous time, deterministic generalization of diffusion processes".
- **Data and tools (§1):** `LeRobotDataset` is a format for recording and streaming robot datasets; `lerobot` also implements asynchronous inference that decouples action planning from execution.

## Caveats
- First-party for `lerobot` and SmolVLA (Hugging Face authors); the code examples are written for that library.

## Related
See also: [ACT](../models/act-aloha.md), [Diffusion Policy](../models/diffusion-policy.md), [π0](../models/pi0.md), [SmolVLA](../models/smolvla.md), [flow and diffusion notes](tutorial-flow-diffusion-mit.md), [Embodied-AI-Guide](guide-embodied-ai.md).
