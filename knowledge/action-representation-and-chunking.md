---
type: concept
tags: [action-tokens, chunking, fast, flow-matching, regression, execution-horizon]
sources: [resources/rt-2.md, resources/openvla.md, resources/fast-tokenizer.md, resources/openvla-oft.md, resources/pi0.md, resources/smolvla.md, resources/octo.md, resources/real-time-chunking.md, resources/survey-vla-action-tokenization.md, resources/vla-perf.md]
---
# Action representation and chunking

## Summary
How a VLA represents actions decides both its accuracy and its serving cost. Per-dimension binning is simple but needs one decode pass per token and fails at high control rates; compression-based tokens (FAST) cut the token count but still decode autoregressively; a parallel regression head (OpenVLA-OFT) or a small flow/diffusion expert removes sequential decoding. **Chunking** (predicting H future actions per call) is what makes a slow model usable, and the execution horizon trades reactivity against compute.

## Details
**Representations**
- **Binning (RT-2, OpenVLA):** 256 bins per dimension (OpenVLA sets bin edges by 1st–99th quantile); 7–8 tokens per action, decoded one by one. OpenVLA ran at about 6 Hz on an RTX 4090; throughput was too low for 25–50 Hz bimanual control ([OpenVLA](../resources/openvla.md)).
- **FAST (DCT + BPE):** roughly 30 tokens per chunk per arm; token counts per 1-second chunk fall from 35 to 20 (5 Hz, 7-D) and from 700 to 53 (50 Hz, 14-D). It trains about 5× cheaper than diffusion π0 but serving is slower (about 750 ms vs about 100 ms per chunk on an RTX 4090) because 30–60 tokens are decoded through the full LLM ([FAST](../resources/fast-tokenizer.md)).
- **Parallel regression (OFT):** empty action queries with bidirectional attention produce all D × K values in one pass with an L1 loss. On LIBERO, continuous actions improved success about 5 points over discrete, and L1 matched diffusion (95.3 vs 95.4) at 109.7 Hz vs 4.2 Hz for diffusion with 50 steps ([OpenVLA-OFT](../resources/openvla-oft.md)). The authors flag that L1 may struggle with truly multimodal demonstrations.
- **Flow/diffusion expert (π0, GR00T N1, SmolVLA):** a 100–300M expert iterates 4–10 steps over the whole chunk with the VLM prefix cached; SmolVLA found flow matching beat L1 regression (80.3 vs 75.3 on LIBERO, Table 10). Cost model in [flow-step reduction](flow-step-reduction.md).
- **Broader taxonomy:** the [tokenization survey](../resources/survey-vla-action-tokenization.md) lists eight action-token types; raw actions are the ones relevant to serving, with the caveats of data scarcity, latency and weak cross-embodiment transfer.

**Chunk size and horizon**
- π0 uses H = 50 and executes 16–25 actions open-loop before re-inferring; temporal ensembling hurt performance ([π0](../resources/pi0.md)). GR00T N1 uses H = 16; OFT uses K = 8 (LIBERO) and 25 (ALOHA); SmolVLA n = 50.
- SmolVLA ablation on LIBERO (from scratch, frozen VLM): chunk 1 → 50.0, 10 → 84.0, 30 → 78.5, 50 → 80.3, 100 → 74.5; executing more steps before re-observing lowers success (1 → 80.3, 10 → 82.8, 30 → 70.8, 50 → 51.8) ([SmolVLA](../resources/smolvla.md)).
- In [VLA-Perf](../resources/vla-perf.md), chunk size barely changes latency (50 → 250 adds only 11% end-to-end for π0) because the expert is memory-bound, so a longer chunk is nearly free compute-wise; the cost is staleness and lower reactivity.
- A chunk lets a slow model keep the robot moving: with 50 actions at 30 Hz a chunk lasts 1.67 s. The feasibility conditions for a given latency are in [serving methods](serving-methods.md).

**Rules of thumb (supported by the sources above)**
- If the target rate exceeds what token-by-token decode can give, use chunking plus a decode-free head.
- Discrete tokens help training speed and language following; continuous heads help serving. π0.5 uses both stages ([π0.5](../resources/pi05.md)).

## Open questions
- Best chunk size for a given latency and reactivity requirement is task-specific and only ablated on LIBERO/SO100 here.
- Whether regression heads (single-pass, no steps) match flow experts at small model scale outside LIBERO is untested in these sources.
