---
type: paper
tags: [imitation-learning, diffusion, ddpm, ddim, receding-horizon, visuomotor-policy]
sources: [arxiv:2303.04137, https://arxiv.org/abs/2303.04137, https://diffusion-policy.cs.columbia.edu]
---
# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

Chi, Xu, Feng, Cousineau, Du, Burchfiel, Tedrake, Song; project site at Columbia University; arXiv 2303.04137 (v5, March 2024; an extended version of the authors' 2023 conference paper).

## Summary
Diffusion Policy represents a visuomotor policy as a conditional denoising diffusion process (DDPM) over a sequence of actions: starting from Gaussian noise, a noise-prediction network conditioned on the observations is applied K times to produce the action sequence. The authors report that this handles multimodal demonstrations, suits high-dimensional action sequences and trains stably, and that it beats prior imitation-learning methods on 15 tasks from 4 benchmarks by 46.9% on average. It executes part of each predicted sequence before replanning (receding horizon) and uses DDIM to cut the inference steps.

## Key claims
- **Policy kinds (Fig. 1):** explicit policies (regression, mixtures of Gaussians, categorical bins), implicit policies (an energy function minimised over actions, e.g. IBC) and diffusion policies (noise refined into actions by a learned gradient field).
- **Training (§2.2–2.3, Eq. 5):** an MSE loss between the added noise and the predicted noise, with the observations as conditioning, not as part of what is denoised; this is what makes inference faster and end-to-end vision training feasible.
- **Horizons (§2.3):** the policy takes the last T_o observations, predicts T_p actions and executes T_a of them before replanning. Table 7 (CNN variant) uses T_o = 2, T_a = 8, T_p = 16 for most tasks.
- **Denoiser networks (§3.1):** a 1D temporal CNN with FiLM conditioning (works out of the box, but over-smooths fast-changing actions such as velocity commands) and a time-series diffusion transformer with cross-attention to the observations (better on fast-changing actions, more sensitive to hyperparameters). The authors recommend starting with the CNN.
- **Vision (§3.2, §5.4):** ResNet-18 trained end to end, with spatial softmax and GroupNorm; a frozen pretrained encoder performs poorly; fine-tuning a CLIP ViT-B/16 with a 10× lower learning rate reaches 98% on Square in 50 epochs.
- **Steps and latency (§3.4):** DDIM decouples training from inference iterations; 100 training and 10 inference iterations give 0.1 s inference latency on an RTX 3080.
- **Why stable (§4.4):** the noise-prediction network approximates the score (the gradient of log p(a|o)), which does not depend on the normalisation constant that energy-based (implicit) policies must estimate with negative samples.
- **Position control (§4.2, §5.3):** position-control actions consistently beat velocity control for Diffusion Policy, while the baselines work best with velocity control.
- **Horizon and latency (§5.3, Fig. 5):** an action horizon of 8 steps is best for most tasks; performance holds with up to 4 steps of simulated latency.
- **Results (Tables 1, 2, 4, 6; §6–7):** better than LSTM-GMM, IBC and BET on all simulated tasks; real Push-T 95% success against 0% (IBC) and 20% (LSTM-GMM) for the best baseline variants (Table 6); bimanual egg beater 55%, mat unrolling 75% and shirt folding 75% over 20 trials each (§7). On the real Push-T set-up the policy predicts commands at 10 Hz, interpolated to 125 Hz for the robot (§6.1).

## Caveats
- §3.4 cites 10 inference iterations, while Appendix A.4 and Table 7 report 16 DDIM inference iterations for the real-world tasks and 100 (iDDPM, no DDIM) for simulation.
- The 46.9% figure is an average of relative improvements over the best baseline per task (Appendix B.2), not a success-rate difference.

## Related
See also: [ACT](act-aloha.md), [Octo](octo.md), [TinyVLA](tinyvla.md), [flow and diffusion notes](../surveys/tutorial-flow-diffusion-mit.md).
