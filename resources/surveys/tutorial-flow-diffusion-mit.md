---
type: paper
tags: [tutorial, flow-matching, diffusion, generative-models, ode, sde]
sources: [arxiv:2506.02070, https://arxiv.org/abs/2506.02070, https://diffusion.csail.mit.edu/]
---
# An Introduction to Flow Matching and Diffusion Models

Holderrieth and Erives, lecture notes for a course whose site is diffusion.csail.mit.edu, arXiv 2506.02070 (v3, March 2026).

## Summary
Lecture notes that present flow models and diffusion models in one framework. Both generate a sample by starting from noise and simulating a differential equation whose direction is given by a neural network: an ordinary differential equation (ODE, deterministic) for a flow model and a stochastic differential equation (SDE, with added noise) for a diffusion model. Flow matching trains the flow's vector field by regression; score matching trains the score used by diffusion models. The notes also cover guidance, latent-space models and discrete diffusion.

## Key claims
- **Flow model (§2.1):** a neural network gives a vector field u(x, t), the velocity; a sample is drawn by taking X_0 from a simple distribution (usually a standard Gaussian) and simulating the ODE from t = 0 to 1. The network gives the vector field, not the flow itself.
- **Euler method (§2.1, Algorithm 1):** simulate with n steps of size h = 1/n, each X ← X + h·u(X, t); the notes also show Heun's method.
- **Diffusion model (§2.2, Algorithm 2):** the same vector field plus a diffusion coefficient σ_t times Brownian noise, simulated with Euler–Maruyama steps that add Gaussian noise each step. "A diffusion model with σ_t = 0 is a flow model"; every ODE is an SDE with zero diffusion coefficient.
- **Flow matching (§3, Eq. 26):** choose a probability path from noise to data; regress the network onto a tractable conditional vector field (conditional flow matching loss), which the notes prove is equivalent to regressing onto the intractable marginal one. Training needs no simulation.
- **Score matching (§4):** the score is the gradient of the log density. Any flow can be turned into an SDE with the same marginals by adding a score term (Theorem 17); for Gaussian paths the score and the vector field convert into each other, so one trained network gives both.
- **Relation to the literature (Summary 45, references):** many diffusion papers use discrete-time Markov chains, an inverted time convention, forward noising processes and time-reversal derivations; the notes call these special cases of their construction. They say flow matching and stochastic interpolants are simpler and more general than denoising diffusion, which needs Gaussian initial distributions and Gaussian paths, and that sampling a flow-matching model is deterministic apart from the initial noise.
- **Guidance and scale (§5–6):** classifier-free guidance mixes conditional and unconditional predictions; large image and video models use U-Nets or diffusion transformers (DiTs) and work in a VAE latent space.
- **Discrete data (§7):** continuous-time Markov chains replace ODEs and SDEs; discrete flow matching trains with a per-token classification loss.

## Caveats
- A teaching text about image, video and text generation; it does not discuss robot actions.

## Related
See also: [Diffusion Policy](../models/diffusion-policy.md), [π0](../models/pi0.md), [robot learning tutorial](tutorial-robot-learning-hf.md).
