---
type: status
tags: [status, baseline, smolvla, softhier, gvsoc, softhier-mlir, libero, latency, success-rate]
sources: [https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md, https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/infra/softhier/gvsoc-patches/README.md, memories/decisions/2026-11-10-first-baseline-latency-and-success-rate.md]
evidence: [measured, estimate]
follows: []
superseded_by: []
---
# Basic integration of components

## Summary
The first stage of the project put the parts together and ran one model end to end: SmolVLA, compiled by softhier-mlir, runs on simulated SoftHier (GVSoC, ideal HBM) and matches its golden reference in the published configuration (`lerobot/smolvla_base`), and the LIBERO fine-tuned checkpoint (`lerobot/smolvla_libero`, same architecture) was scored on LIBERO on a GPU. The work is recorded in the project's [design document](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md) (section "Outcomes and deviations from plan (G5)" and the findings table) and the [GVSoC patch series README](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/infra/softhier/gvsoc-patches/README.md), both at code-repository commit `e832bfb`; the choices behind it are in the [first baseline decision](../decisions/2026-11-10-first-baseline-latency-and-success-rate.md). Below: the parts and how they connect, the evidence table, then what is still open. The simulator fixes this stage needed are logged in the [GVSoC patch log](../patches/gvsoc-soft-hier-release.md).

```text
+----------------------------+  ref.npz: tensors and actions
| golden reference           |  (fp32)
| LeRobot SmolVLA, GPU       |-----------------------+
+----------------------------+                       |
                                                     v
+----------------------------+  V -> Pa -> Pb -> X  +--------------------+
| softhier-mlir program      |  hand-over via HBM   | compare at each    |
| on GVSoC soft_hier_release |--------------------->| hand-over; gate:   |
| + ten-patch series         |  4 programs x1 call  | latency, max-abs   |
+----------------------------+                      +--------------------+

+----------------------------+  episodes x100
| LIBERO closed-loop eval    |  (10 tasks x 10)     +--------------------+
| GPU fp32, synchronous      |--------------------->| success rate       |
+----------------------------+                      +--------------------+
```

## Integrated parts
- **Simulator:** GVSoC, branch `soft_hier_release`, a submodule pinned at upstream `d806a84`, plus ten patches in the code repository (`infra/softhier/gvsoc-patches/`), applied by `setup.sh`.
- **Compiler:** softhier-mlir (`github.com/runwangdl/softhier-mlir`), on the experiment branch, with local changes as patch files. It runs one SmolVLA inference as four simulator programs: V (vision tower and connector), Pa (prefix layers one to eight), Pb (prefix layers nine to sixteen), X (action expert, ten flow steps).
- **Golden reference:** the fp32 GPU run of LeRobot's SmolVLA; its intermediate tensors and actions are what SoftHier runs are compared against.
- **LIBERO evaluation:** a wrapper around `lerobot-eval` that runs the closed-loop success rate.

## Evidence
| Claim                                                                                                                                                                                                                          | Label                                                | Source                                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SmolVLA runs end to end on simulated SoftHier in the published configuration (`lerobot/smolvla_base`, 1 camera, 256 SigLIP tokens) and passes the validity gate                                                                | measured (simulated on GVSoC, ideal HBM)             | [design, Outcomes, "G3 gate: PASS"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                       |
| Latency, published configuration: 120.716 ms against 119.1 ms published by softhier-mlir (+1.4 %, gate window ±5 %); sum of the timed segments of the four programs at 1 GHz                                                   | measured (simulated on GVSoC, ideal HBM)             | [design, Outcomes](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                                        |
| Action max-abs error against the golden reference: 0.0068 (gate limit 0.10; softhier-mlir published 0.032)                                                                                                                     | measured (simulated on GVSoC, ideal HBM)             | [design, Outcomes](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                                        |
| The latency excludes data movement between programs, program load, real HBM timing and host-side preprocessing                                                                                                                 | measured (definition of the measured figure)         | [design, Goals, "What the latency number includes"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)       |
| LIBERO configuration (`lerobot/smolvla_libero`, 2 cameras x 1024 SigLIP patches, 64 image tokens per camera, prefix 177 tokens): 479.1 ms                                                                                      | estimate (composed from partial simulated runs, G4a) | [design, Outcomes, "G4b was not run"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                     |
| The full LIBERO run (G4b) was not made: its vision phase was projected at 13386 s (3.72 h) against the 7200 s limit; owner decision "report G4a only", so no full-chain comparison with the golden reference exists for LIBERO | estimate (wall-time projection)                      | [design, Outcomes](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                                        |
| The G4a checks are weaker than designed (the prefix run only shows completion; the expert run compares `xt[2]` only)                                                                                                           | measured                                             | [design, Outcomes, "G4a checks are weaker than designed"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md) |
| Success rate of `lerobot/smolvla_libero` on `libero_spatial`, 10 tasks x 10 episodes: 59.0 % (59 of 100); no published figure for this checkpoint                                                                              | measured (GPU fp32, synchronous eval)                | [design, Outcomes, "Unresolved"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                          |
| The GVSoC fixes ship as a ten-patch series on the upstream base; on a fresh upstream checkout the tree is identical to the one that produced every measured number                                                             | measured (checked on a fresh checkout)               | [patch series README, "Expected result"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/infra/softhier/gvsoc-patches/README.md)                     |
| Kernel tests `gemm`, `norm`, `acti`, `attn` pass by exit code, counter line and no error strings; they do not check output and ran before F5 and F16, so their timings are not comparable                                      | measured                                             | [design, Outcomes, "Kernel tests (G1.5)"](https://github.com/HaozeG/SoftHier-VLA/blob/e832bfb749c38388f9ee930e1d25c03b9917b971/docs/designs/smolvla-softhier-baseline.md)                 |

## Open questions
- F19: the iDMA two-dimensional transpose is 2.3x slower than published; not investigated ([patch log](../patches/gvsoc-soft-hier-release.md), design findings table).
- The LIBERO latency is an estimate; a full-chain run and its comparison with the golden reference do not exist.
- The 59.0 % success rate has no published figure for this checkpoint to compare with.
- Rungs 3 to 5 were last run before F16; their timings predate it (design, Outcomes).
