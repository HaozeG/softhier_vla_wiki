---
type: comparison
tags: [benchmark, workloads, serving, roofline, batch-1, closed-loop, edge]
sources: [resources/serving/vla-workload-characterization-kaist.md, resources/models/openvla.md, resources/models/openvla-oft.md, resources/models/pi05.md, resources/models/gr00t-n1.md]
---
# Benchmark workloads: five VLAs profiled at batch size 1

What does one inference of each VLA in the [Jung et al. characterization](../resources/serving/vla-workload-characterization-kaist.md) cost, which stage dominates, and what limits that stage? The five workloads are OpenVLA (autoregressive baseline), OpenVLA-OFT, GR00T N1.6, π0.5 and Cosmos-Policy. All numbers come from that one paper, measured on the same machines. That makes them comparable with each other, unlike the mixed-source speeds in the [architecture overview](vla-architecture-overview.md).

## Summary
At batch size 1 the bottleneck follows the size of the tensors a stage processes ([source §4.2](../resources/serving/vla-workload-characterization-kaist.md)):
- **Iterative heads over a short action chunk are memory-bound.** GR00T N1.6's DiT and π0.5's 300M expert run 4 or 10 denoising steps over a few action and state tokens. Their GEMMs (matrix multiplies) reuse each weight across few tokens, so they fall below the RTX 4090 ridge point. These heads dominate latency (65% and 75% of eager E2E) and gain most from compilation.
- **Large-sequence stages are compute-bound.** OpenVLA-OFT's 7B backbone (99% of latency; the MLP head takes 0.6 ms) and Cosmos-Policy's video DiT over 7,056 latent positions sit above the ridge.
- **The autoregressive baseline** repeats the LLM-serving split: prefill is compute-bound and the 6 cached-decode passes are entirely memory-bound (67% of its 209.56 ms).

Platform balance moves the line. On Jetson Thor every stage is more bandwidth- than clock-sensitive, though the ordering by intensity mostly holds. In closed loop, raising the overlap of inference and execution speeds episodes up and costs success. How much success is lost depends on the model: π0.5 and OpenVLA-OFT lose least.

```text
One inference, batch size 1 (RTX 4090, eager; stage latency in ms)

OpenVLA      ViT 16.0 -> prefill 43.5 -> cached decode x6 = 140.9 -> 1 action
(baseline)              compute-bound    memory-bound           (7 tokens)

OpenVLA-OFT  ViT + Llama 2 7B, one pass 117 -> MLP head 0.6 -> chunk K=8
             compute-bound

GR00T N1.6   VLM 42 -> DiT head x4 steps = 78 -> chunk K=16
                       short action+state sequence, memory-bound

pi0.5        VLM 73 -> Gemma 300M expert x10 steps = 221 -> chunk K=10
                       short suffix sequence, memory-bound

Cosmos-Pol.  VAE 114 -> DiT x5 steps = 282 -> actions read from latent slots
                        9x28x28 = 7056 positions x 16 ch, compute-bound

Closed loop (one model server, one simulated robot)
 MuJoCo client --obs ~384 KB--> model server --chunk ~0.5 KB--> FIFO queue
 the queue gives 1 action every dt; next request when ceil(K*p) remain
 dt = 1.5 x RTT_max / ceil(K*p)          (p = overlap, 10/25/50 %)
```

## Comparison
Single inference. Latency is in eager mode on the RTX 4090 (Fig 3). Bound = share of GPU time (Fig 5). R = GPU/EMC sensitivity ratio on the Jetsons (§4.3.1); below 1 means more sensitive to memory bandwidth than to GPU clock. A dash means the paper gives no value.

| Model         | Paradigm             | Steps / params / chunk | E2E ms (backbone / head) | Dominant stage | GPU time        | Head GEMMs vs ridge | Compile speedup    | R Orin (head) | R Thor (head / backbone) |
| ------------- | -------------------- | ---------------------- | ------------------------ | -------------- | --------------- | ------------------- | ------------------ | ------------- | ------------------------ |
| OpenVLA       | autoregressive token | – / 7B / 1 action      | 209.56 (decode 140.90)   | cached decode  | decode 100% mem | –                   | –                  | –             | –                        |
| OpenVLA-OFT   | parallel decoding    | N/A / 7B / 8           | 117 (117 / 0.6)          | backbone 99%   | 84% compute     | backbone above      | backbone 1.42×     | –             | – / 0.27                 |
| GR00T N1.6    | iterative denoising  | 4 / 3B / 16            | 120 (42 / 78)            | head 65%       | 62% memory      | below               | head 4.42×         | 0.81          | 0.30 / 0.44              |
| π0.5          | iterative denoising  | 10 / 3B / 10           | 294 (73 / 221)           | head 75%       | 58% memory      | below               | head 7.96×         | 0.83          | 0.33 / –                 |
| Cosmos-Policy | video generation     | 5 / 2B / 16            | 396 (VAE 114 / DiT 282)  | DiT 71%        | 77% compute     | DiT above           | DiT 0.97× (slower) | –             | DiT 0.59 / VAE 0.50      |

On Orin all compute-bound stages have R between 1.03 and 1.67; the paper does not give per-stage values.

Closed loop. RTT_max is the compiled synchronous round trip including transfer (Table 7). The overlap effect compares p = 10% with p = 50% (§5.2–5.3).

| Model         | RTT_max ms: 4090 / Thor / Orin | Success drop with overlap (RTX 4090) | Episode speedup (Long) | Efficiency or SLO result           |
| ------------- | ------------------------------ | ------------------------------------ | ---------------------- | ---------------------------------- |
| GR00T N1.6    | 142.8 / 126.7 / 206.8          | 31–49 pp (with Cosmos-Policy)        | 2.8–3.0×               | about 59 actions/s at 186 J (4090) |
| π0.5          | 136.1 / 180.6 / 457.3          | 15–20 pp (with OpenVLA-OFT); least   | 3.6–3.9×               | picked under all four p25 SLOs     |
| OpenVLA-OFT   | 148.7 / 306.8 / 528.2          | 15–20 pp (with π0.5)                 | –                      | steep energy curve                 |
| Cosmos-Policy | 442.9 / 1023.0 / 2558.4        | 31–49 pp (with GR00T N1.6)           | –                      | about 17 actions/s at 2,632 J      |

## How the measurements were made
- **Inputs and checkpoints:** official LIBERO-finetuned checkpoints at native resolution and precision. Single-inference runs feed random tensors of the right shape.
- **Stage latency:** wall clock with `cuda.synchronize` at stage boundaries. Roofline uses NVIDIA NCU (FLOPs and DRAM bytes per kernel) on the RTX 4090 only.
- **DVFS:** GPU and EMC clocks swept one at a time on the Jetsons. EMC is the external memory controller, which sets DRAM bandwidth.
- **Closed loop:** the control period is not a fixed 33 ms. It is set per model, platform and overlap from the measured worst-case round trip (diagram, last line), so slower models run at slower control rates. The paper does not say whether simulated time follows the wall clock between actions, or whether a new chunk replaces the unexecuted actions of the old one (its Fig 2 and its FIFO description differ). Both choices change what the success comparison measures; see the reading notes in the [source note](../resources/serving/vla-workload-characterization-kaist.md).

## Caveats
- One paper, one software stack (PyTorch 2.10, NVIDIA only), simulation only. See its caveats in the [source note](../resources/serving/vla-workload-characterization-kaist.md).
- GR00T N1.6 is a newer model than the [GR00T N1](../resources/models/gr00t-n1.md) of the wiki's model notes. Its backbone is Cosmos-Reason, not Eagle-2, and its numbers do not carry over.
- Eager-mode splits (table 1) and compiled round trips (table 2) are different modes. Do not divide one by the other.
- Energy compares within a platform only; cross-platform energy shows trends.
- The closed-loop tables come from a simulation whose timing and queue policy are not fully specified. Under Eq 5 the overlap p also changes the control rate, so the success drop with p is not an effect of overlap alone (source note, reading notes).

## Open questions
These are things the source does not cover:
- Smaller or distilled heads: SmolVLA ([note](smolvla.md)) and 1-step distilled heads are not measured, and the paper says the latter can remove the memory-bound stage.
- Non-NVIDIA accelerators and real robots.
- The action dimension and exact token counts behind each head GEMM. The paper gives only above or below the ridge point, not per-stage intensities.

Related: [one VLA call](one-vla-call.md) (latency, async execution, stale actions), [action representation and chunking](action-representation-and-chunking.md) (the paradigms), [WAM overview](wam-overview.md) (its survey lists CosmosPolicy as a WAM example).
