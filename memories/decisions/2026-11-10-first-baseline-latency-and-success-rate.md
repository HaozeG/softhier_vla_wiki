---
type: decision
tags: [baseline, latency, success-rate, simulator, golden-reference, libero, smolvla]
sources: [session:smolvla-e2e-baseline, resources/serving/vla-workload-characterization-kaist.md, resources/serving/vla-hwbench-edge-latency.md, resources/models/smolvla.md, knowledge/simulation-benchmarks.md, https://github.com/HaozeG/SoftHier-VLA/blob/main/docs/designs/smolvla-softhier-baseline.md, https://github.com/gvsoc/gvsoc/tree/soft_hier_release, https://github.com/runwangdl/softhier-mlir]
defines: [golden reference]
---
# First baseline: SmolVLA latency on SoftHier and success rate on GPU

## Context
The project has knowledge notes but nothing that runs a VLA model on SoftHier, checks a run for correctness, or measures whether a policy completes its task. The first experiment closes that gap for one model, SmolVLA ([SmolVLA](../../resources/models/smolvla.md)). The full plan is in the [design document](https://github.com/HaozeG/SoftHier-VLA/blob/main/docs/designs/smolvla-softhier-baseline.md); this note records the decisions the design rests on. Numbers produced by the experiment stay in the experiment's results file, not here ([wiki-design decision 0013](../../wiki-design/decisions/0013-scope-and-no-derived-content.md)).

Alternatives considered for the simulator: `pulp-platform/softhier-sdk` and the GVSoC `soft_hier_release` branch. For the success rate: a closed loop on the SoftHier simulator, a closed loop on GPU with a synchronous policy, and a closed loop that injects the simulated latency.

## Decision
**Two tracked metrics.**
- **Latency:** the time of one policy call (observation in, action chunk out) on SoftHier, in cycles at 1 GHz summed over the timed segments of the compiled programs. Excluded: data movement between programs, program load, real HBM timing (ideal HBM) and host-side preprocessing. Label: measured, simulated on GVSoC, ideal HBM. A figure composed from partial runs is labelled estimate ([wiki-design decision 0004](../../wiki-design/decisions/0004-evidence-tiers-for-fast-moving-vla-sources.md)).
- **Success rate:** the share of closed-loop benchmark episodes that complete the task. Label: measured, GPU fp32, synchronous eval.
- Why these two: a control period is a recurring deadline and an overrun leaves the robot acting on stale observations, which lowers task success (see [the KAIST characterization](../../resources/serving/vla-workload-characterization-kaist.md), §5 closed loop). Per-stage latency on edge hardware is the metric other work reports ([VLA-HWBench](../../resources/serving/vla-hwbench-edge-latency.md)). Success rate is the benchmark score of the model ([SmolVLA](../../resources/models/smolvla.md), [simulation benchmarks](../../knowledge/simulation-benchmarks.md)).

**Simulator and compiler.**
- Simulator: GVSoC, branch `soft_hier_release` (`github.com/gvsoc/gvsoc`), as a git submodule.
- Compiler and operator library: softhier-mlir (`github.com/runwangdl/softhier-mlir`), which has an end-to-end SmolVLA flow.
- `pulp-platform/softhier-sdk` is not used: it targets the newer `pulp.chips.softhier` model, which has no RedMulE matrix engine and none of the runtime headers softhier-mlir uses.

**Layout rule.** Parts that later experiments reuse (simulator, golden reference, LIBERO evaluation, environment scripts) live on `main` under `third_party/` and `infra/`. Everything specific to one experiment (its compiler checkout, arch file, configs, patches, records) lives under `experiments/<name>/` on that experiment's branch.

**Golden reference.** A small program, independent of the compiler flow, that runs the original SmolVLA implementation in fp32 on a fixed observation and writes every intermediate tensor in softhier-mlir's reference layout (its key names and shapes). The simulator's results are compared against it at each hand-over between programs.

**LIBERO configuration** (configuration facts):
- Checkpoint `lerobot/smolvla_libero`, fine-tuned from `lerobot/smolvla_base`; the architecture is the same as `smolvla_base`.
- Two cameras: the agent-view and wrist images, renamed to `camera1` and `camera2`, 256 by 256 at the policy input.
- Vision tokens: each image is resized with padding to 512 by 512, giving 1024 SigLIP patches per camera and 64 image tokens per camera after the 4 by 4 pixel shuffle.
- Language: right-padded to 48 tokens. State and action are padded to 32 dimensions.
- Prefix: 2 cameras of 64 image tokens, 48 language tokens and 1 state token, 177 in all, padded to a multiple of 128.
- Expert: chunk of 50 actions, 10 flow steps.
- The golden reference and the latency run use the first frame of `libero_spatial` task 0 after reset, seed 0; latency is measured in the same configuration as the robot evaluation.

**Success-rate method SR-A.** `lerobot/smolvla_libero` is evaluated closed loop on `libero_spatial`, 10 tasks with 10 episodes each, on GPU in fp32, with a synchronous policy: simulation time pauses during inference. The rate is reported with a 95 % binomial confidence interval. SR-A does not include SoftHier effects.

## Why
- Closed-loop episodes on the SoftHier simulator are not feasible at the simulator's speed, so latency and success rate come from separate runs on the same configuration.
- A synchronous GPU evaluation is the simplest success rate and matches how benchmark scores are usually reported, so later methods have a baseline to differ from.
- GVSoC `soft_hier_release` and softhier-mlir already contain the matrix engine, the runtime headers and the SmolVLA flow, which a new compiler would have to rebuild.
- The layout rule keeps `main` limited to what is reused and keeps each experiment's records on its own branch.
- Revisit if softhier-sdk gains a RedMulE model, or if the simulator becomes fast enough for closed-loop runs.

## Open questions
- **SR-B, latency-injected closed loop** after Jung et al. (see [the KAIST characterization](../../resources/serving/vla-workload-characterization-kaist.md), §5): simulation time keeps running during inference. Needs a timing wrapper around the LIBERO environment, an action queue, overlap and stale actions, and the SoftHier latency from this baseline.
- **SR-C, SR-B plus a numerical twin of SoftHier's fp16 arithmetic.** Needs a validated twin of that arithmetic, so that the policy sees the numerical errors the chip would produce.
- Open in the design, settled during the experiment: the LIBERO state dimension and observation keys, the control rate, and the published `libero_spatial` success rate of the checkpoint, if one exists.
