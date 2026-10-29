---
type: concept
tags: [action-tokens, chunking, fast, flow-matching, diffusion, cvae, regression, execution-horizon, temporal-ensembling]
sources: [resources/models/rt-2.md, resources/models/openvla.md, resources/models/fast-tokenizer.md, resources/models/openvla-oft.md, resources/models/pi0.md, resources/models/smolvla.md, resources/models/octo.md, resources/surveys/survey-vla-action-tokenization.md, resources/models/act-aloha.md, resources/models/diffusion-policy.md, resources/surveys/tutorial-robot-learning-hf.md, resources/surveys/tutorial-flow-diffusion-mit.md]
---
# Action representation and chunking

## Summary
How a VLA represents actions decides both its accuracy and its serving cost. Per-dimension binning is simple but needs one decode pass per token and fails at high control rates; compression-based tokens (FAST) cut the token count but still decode autoregressively; a parallel regression head (OpenVLA-OFT) or a CVAE decoder (ACT) writes a chunk in one pass, and a small flow or diffusion expert refines a chunk from noise in a few steps. Continuous heads therefore fall into single-pass ones (regression, CVAE) and iterative ones (flow matching, diffusion). In imitation learning, ACT motivated chunking by compounding errors (it borrows the term from psychology); Diffusion Policy also predicts action sequences. **Chunking** (predicting H future actions per call) is what makes a slow model usable, and the execution horizon trades reactivity against compute.

## Diagram
```text
Sequential passes per chunk (after the VLM prefix pass; ACT and
Diffusion Policy have no VLM)

representation            tokens per action  sequential passes
binning (RT-2, OpenVLA)   7-8                one per token, per action
FAST tokens               not applicable     one per token: 30-60 per chunk
regression (OFT)          not applicable     1 per chunk (all D x K values)
CVAE decoder (ACT)        not applicable     1 per chunk (z = 0)
flow expert (pi0 ...)     not applicable     T = 4-10 per chunk
diffusion (Diff. Policy)  not applicable     10-16 DDIM steps per chunk

One chunk of H = 50 predicted actions (pi0; 1 char = 1 action)

|================---------.........................|
                ^        ^
              16       25

= executed in all pi0 setups (16 actions; 20 Hz robots), open loop
- also executed in the 50 Hz setups (25 actions in all)
. predicted, not executed
shorter execution: more reactive, more model calls; longer: fewer calls,
staler actions
```
The table is "Representations" below and the bar is "Chunk size and horizon".

## Details
**Representations**
- **Binning (RT-2, OpenVLA):** 256 bins per dimension (OpenVLA sets bin edges by 1st–99th quantile); 7–8 tokens per action, decoded one by one. OpenVLA ran at about 6 Hz on an RTX 4090; throughput was too low for 25–50 Hz bimanual control ([OpenVLA](../resources/models/openvla.md)).
- **FAST (DCT + BPE):** roughly 30 tokens per chunk per arm; token counts per 1-second chunk fall from 35 to 20 (5 Hz, 7-D) and from 700 to 53 (50 Hz, 14-D). It trains about 5× cheaper than diffusion π0 but serving is slower (about 750 ms vs about 100 ms per chunk on an RTX 4090) because 30–60 tokens are decoded through the full LLM ([FAST](../resources/models/fast-tokenizer.md)).
- **Parallel regression (OFT):** empty action queries with bidirectional attention (every token sees all tokens, unlike causal attention, where a token sees only earlier ones) produce all D × K values in one pass, D being the number of dimensions of one action with an L1 loss. On LIBERO, continuous actions improved success about 5 points over discrete, and L1 matched diffusion (95.3 vs 95.4) at 109.7 actions/s vs 4.2 actions/s for diffusion with 50 steps (1.9 s per 8-action call); "Hz" in that table is actions per second, not calls per second ([OpenVLA-OFT](../resources/models/openvla-oft.md)). The authors flag that L1 may struggle with truly multimodal demonstrations.
- **CVAE decoder (ACT):** a transformer trained as a conditional VAE outputs a whole k × 14 chunk in one pass; at test time the latent z is set to zero, so decoding is deterministic. Without the CVAE objective (plain regression), success on human demonstrations fell from 35.3% to 2% in simulation, while scripted (deterministic) data was unaffected ([ACT](../resources/models/act-aloha.md)).
- **Diffusion (Diffusion Policy):** a DDPM refines Gaussian noise into a T_p-step action sequence over a number of denoising steps (the paper writes K, not the chunk-size K used for OFT below), conditioned on the observations; DDIM cuts inference to 10–16 steps (about 0.1 s on an RTX 3080 with 10). The authors credit it with handling multimodal demonstrations and stable training ([Diffusion Policy](../resources/models/diffusion-policy.md)).
- **Flow/diffusion expert (π0, GR00T N1, SmolVLA):** a 100–300M expert iterates 4–10 steps over the whole chunk with the VLM prefix cached; SmolVLA found flow matching beat L1 regression (80.3 vs 75.3 on LIBERO, Table 10).
- **Flow matching and diffusion are siblings.** Both start from noise and follow a learned direction in steps. In the MIT notes a flow model simulates a deterministic ODE and a diffusion model an SDE that adds noise each step; a diffusion model with zero noise is a flow model, and flow-matching training is called simpler and more general than denoising diffusion ([flow and diffusion notes](../resources/surveys/tutorial-flow-diffusion-mit.md)). The Hugging Face tutorial instead calls flow matching a deterministic generalization of diffusion ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md)). The sources thus agree that the two are one family and disagree on which contains which.
- **Why generative heads:** point-estimate (regression) policies average between equally good modes of multimodal demonstrations ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md); [Diffusion Policy](../resources/models/diffusion-policy.md)), which is the reason given for CVAE, diffusion and flow heads.
- **Broader taxonomy:** the [tokenization survey](../resources/surveys/survey-vla-action-tokenization.md) lists eight action-token types; raw actions are the ones relevant to serving, with the caveats of data scarcity, latency and weak cross-embodiment transfer.

**Chunk size and horizon**
- π0 uses H = 50 and executes 16 actions on its 20 Hz robots and 25 on its 50 Hz robots, open-loop (no new observation is taken while they run), before re-inferring; temporal ensembling hurt performance ([π0](../resources/models/pi0.md)). In ACT, which queries the policy every step and averages the overlapping chunks with exponential weights, temporal ensembling helped (+3.3%) ([ACT](../resources/models/act-aloha.md)); the setups differ (π0 executes part of a chunk open loop, ACT re-queries every step). GR00T N1 uses H = 16; OFT uses K = 8 (LIBERO) and 25 (ALOHA); SmolVLA n = 50.
- SmolVLA ablation on LIBERO (from scratch, frozen VLM): chunk 1 → 50.0, 10 → 84.0, 30 → 78.5, 50 → 80.3, 100 → 74.5; executing more steps before re-observing lowers success (1 → 80.3, 10 → 82.8, 30 → 70.8, 50 → 51.8) ([SmolVLA](../resources/models/smolvla.md)). The paper does not say why n = 50 was chosen, although its ablation scores chunk 10 above chunk 50.
- ACT ablation (simulation, no ensembling): chunk 1 → 1%, chunk 100 → 44%, slightly lower at 200–400 (near open loop); chunking also helped two baseline methods. ACT motivates chunking by compounding errors: a chunk of k cuts the effective horizon k-fold ([ACT](../resources/models/act-aloha.md)).
- Diffusion Policy predicts T_p = 16 and executes T_a = 8 before replanning (receding horizon) for most tasks; 8 executed steps was best in its ablation, and it kept peak performance with up to 4 steps of simulated latency ([Diffusion Policy](../resources/models/diffusion-policy.md)).
- A chunk lets a slow model keep the robot moving: with 50 actions at 30 Hz a chunk lasts 1.67 s.

**Reported on combining representations**
- Discrete tokens help training speed and language following, and continuous heads help serving; π0.5 uses both stages ([π0.5](../resources/models/pi05.md)).

## Open questions
- Best chunk size for a given latency and reactivity requirement is task-specific and only ablated on LIBERO/SO100 here.
- Whether regression heads (single-pass, no steps) match flow experts at small model scale outside LIBERO is untested in these sources.
