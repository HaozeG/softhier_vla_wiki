---
type: paper
tags: [survey, wam, world-model, taxonomy]
sources: [arxiv:2606.20781, https://arxiv.org/abs/2606.20781]
---
# World Action Models: A Survey

Shen et al. (National University of Singapore), arXiv 2606.20781 (v1, June 2026); subtitle "Dream Less, Act More".

## Summary
A taxonomy survey of world action models (WAMs): embodied predictive-action models in which a forecast of the future is available to the action. It separates WAMs from VLAs and from world models, classifies works by what must be generated before the action is decoded and by a four-part design tuple, gives a cost model linking prediction to control frequency, and lists seven open challenges.

## Key claims
- **Definitions (§2):** a VLA models p(a | o, l) and acts from the present observation; a world model models p(o' | o, a, l) and predicts the future without having to choose the action; a WAM is a model whose "predicted future observation helps produce the action, score the action, or train the action path inside one model".
- **Three factorizations:** predict-then-act, p(o'|o,l)·q(a|o,o',l) (UniPi, AVDC); act-then-score, q(a|o,l)·p(o'|o,a,l) (candidate scoring and planning); joint, p(o',a|o,l) (GR-1/2, PAD, UWM, WorldVLA, DreamZero).
- **Outside the definition:** a VLA with only an auxiliary future loss, a simulator used only as an RL environment, or a future head discarded before the action is computed.
- **Video generators:** Wan, CogVideoX, Cosmos and Sora are one visible instance of world models; conditioned on actions they become video world models, and become WAMs once an action coupling and a deployment regime are added (for example CosmosPolicy, VidMan, VideoVLA around frozen backbones).
- **Taxonomy, view 1 (design philosophy):** Render-and-Decode (video to pixels), Latent-Only (video backbone, action from latents, features, flow or masks, pixel decoder skipped), Video-Generation-Free (prediction in LLM/VLM tokens, JEPA features, geometry, affordances or audio).
- **Taxonomy, view 2, tuple (Φ, F, B, D):** substrate Φ (pixel, feature, geometric, affordance); coupling F (action-conditioned rollout, joint generation, post-prediction head); backbone B (diffusion, autoregressive, JEPA, hybrid or mixture-of-transformers, LLM/VLM); deployment D (open-loop, chunked closed-loop, single-step closed-loop, interactive). Tables 1-2 place every surveyed work on the tuple.
- **Cost model (§4.5):** with N_fwd(H) the cost of one forward pass and f_ctrl the control frequency: open-loop C = N_fwd(T), paid once, cannot react to deviations; chunked C = ceil(T/K)·N_fwd(K), feasible when N_fwd(K)/K < 1/f_ctrl, "the common real-robot choice" because it amortizes a large backbone over several control ticks, at the cost of staleness within a chunk; single-step C = T·N_fwd(1) with the hard limit N_fwd(1) < 1/f_ctrl, feasible mainly with sparse substrates; interactive uses a cached state of size M(t) whose attention cost grows quadratically in t, so pressure falls on memory.
- **Most expensive corner:** decoded pixels, joint generation, diffusion and single-step control; "few methods can use that corner directly in production", and designs that appear to use it usually trade something away (simulation, offline rollout, a smaller model at inference).
- **Backbone cost (§4):** diffusion pays N_diff denoising steps; autoregressive models avoid denoising but pay serial cost depending on what the stream contains; JEPA is cheap because it never decodes to an observation but has no visual quality check; VLM-based WAMs inherit the VLM stack's cost, so many use chunking and a frozen backbone.
- **Chunk size (§4.3.4):** one action per pass gives low per-action latency but runs the full backbone at control frequency; long chunks spread the cost but cannot react mid-chunk; real hardware pushes toward smaller chunks or cheaper backbones.
- **Runtime mechanisms named:** adaptive-K chunking, event-triggered invocation and "dual-frequency slow-fast loops" (HarmoWAM splits reactive and predictive loops; LingBot-VA and HarmoWAM hand frequent control to a lighter action expert while visual dynamics stay available; FFDC-WAM uses a lightweight verifier to trigger replanning; NoiseGate and SANTS learn to cut denoising cost).
- **Sizes given:** π0.7 is a Gemma3-based VLA with an 860M flow-matching action expert, plus a separate lightweight BAGEL-initialized world model that refreshes multi-view subgoal images every four seconds; ALAM uses a PaliGemma-2B trunk with a Gemma-300M flow-matching expert; LDA-1B (Qwen3-VL backbone) and EgoExo-WM (DINOv3-L predictor) are named without further sizes.
- **Central trade-off (§7):** a richer predicted future trades against compute, memory, latency and action-label cost; the field is moving to "generate less of the future while preserving what control requires".
- **Seven challenges (§7):** dream more or act more (expose a fidelity-latency curve); which data source belongs to which training stage (no joint scaling law over source, stage, quality, model size and action grounding); memory that grows with scene complexity; generalization ("cannot be made generalizable by adding scale alone"); grounding abstract or latent actions; physical plausibility; evaluation as "accuracy-at-budget" (success, latency, horizon, peak memory, failure tags on one axis).
- **Two opposing evidence points on size:** Fast-WAM drops the video branch at inference and GigaWorld-Policy masks attention so future video can be skipped, suggesting the video training objective may matter more than a rendered forecast at test time; DreamZero keeps a large video backbone in closed loop through a custom optimization stack, and the paper states "the open problem is not simply to make every model smaller". Its proposed direction: train one backbone with video objectives, then let the action path choose how much of it to run.

## Caveats
- The survey reports almost no parameter counts or Hz figures; it is a taxonomy, not a benchmark.
- Table 1 lists π0.7 as pixel (decoded) and hybrid, while the text discusses it under the LLM/VLM family.
- This note was written from the survey's alphaXiv report and targeted full-text queries; Sections 5, 6, 7.4-7.6 and Table 2 were not read in full. Many cited works are 2026 preprints not checked here.
