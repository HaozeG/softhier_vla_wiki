---
type: concept
tags: [layer-pruning, layer-skipping, early-exit, width-pruning, distillation, structured-pruning]
sources: [resources/models/smolvla.md, resources/models/gr00t-n1.md, resources/compression/efficientvla.md, resources/compression/deer-vla.md, resources/compression/dysl-vla.md, resources/compression/clp-layer-pruning.md, resources/compression/pruned-vla-recovery.md, resources/surveys/survey-efficient-vla-guan.md, resources/serving/vla-xpu-characterization.md]
---
# Layer skipping and pruning

## Summary
VLA backbones are redundant in depth: several groups remove or skip a large fraction of LLM layers with little accuracy loss. **Static** removal (SmolVLA's first half of the LLM, GR00T N1's 12th-layer features, CKA-guided pruning before fine-tuning) gives a smaller fixed graph. **Dynamic** methods (DeeR-VLA, DySL-VLA, MoLe-VLA) skip layers per step but add control flow whose wall-clock gain trails the FLOP reduction. Aggressive weight (width) pruning breaks a VLA completely unless it is recovered by distillation. Removing layers is faster; narrowing them keeps accuracy better.

```text
shrink the backbone (what each branch acts on, then what is reported)
+-- remove depth (layers)
|   +-- static, before deployment: SmolVLA, GR00T N1, CLP, EfficientVLA
|   |     reported: fixed graph; CLP success flat to about half the layers
|   +-- dynamic, per input: DeeR-VLA, DySL-VLA, MoLe-VLA
|         reported: wall-clock gain below the FLOP gain (control flow)
+-- remove width (prune weights inside layers): pruned-VLA recovery
      reported: accuracy collapses at heavy pruning without distillation;
      with recovery, higher success than depth removal at equal cut,
      but a smaller speedup

in both: the action head's fixed flow steps set a latency floor
```

## Details
**Static removal**
- SmolVLA feeds the expert from LLM layers up to N = L/2 and found this beats a smaller VLM at similar cost; on LIBERO, N = 8 / 16 / 24 / 32 gave 75.0 / 78.5 / 79.5 / 80.3 ([SmolVLA](../resources/models/smolvla.md)). GR00T N1 uses the 12th LLM layer's features, reporting faster inference and higher success than the last layer ([GR00T N1](../resources/models/gr00t-n1.md)).
- CLP prunes redundant layers (by CKA) of both VLM and expert before fine-tuning: π0 −28% latency, GR00T-N1.5 −30% latency and −49% FLOPs, SmolVLA −32% latency; success within 0.4–0.9 points on LIBERO, flat to about 50% pruning; fine-tuning also 1.4–2.8× faster ([CLP](../resources/compression/clp-layer-pruning.md)).
- EfficientVLA prunes layers by input/output cosine similarity (L = 22 of 32 for a 7B CogACT) with MLP sparsity, in a training-free pipeline that reached 1.93× with all three components ([EfficientVLA](../resources/compression/efficientvla.md)).

**Dynamic skipping and early exit**
- DeeR-VLA: multi-exit LLM with action-consistency exit criteria and budgeted thresholds; LLM FLOPs 5.2–6.5× lower, memory 2–6× lower; wall-clock gain 55 → 17.5 ms (−68%) vs −81% theoretical, on a V100 with no early-exit code optimization ([DeeR-VLA](../resources/compression/deer-vla.md)).
- DySL-VLA: about 20% static layers plus skippable dynamic blocks with adapters; skipping is restricted near critical actions by trajectory continuity; OpenVLA-OFT on Jetson Orin 676 → 345 ms at 96.5 vs 97.1% ([DySL-VLA](../resources/compression/dysl-vla.md)). It also reports that per-layer controllers add serial latency that can cancel gains.
- Surveys additionally cite MoLe-VLA (layers as experts with self-distillation), FLOWER (drop upper layers) and speculative and parallel decoding ([Guan et al.](../resources/surveys/survey-efficient-vla-guan.md)). In speculative decoding a small draft model proposes tokens that the large model then accepts or rejects; the XPU benchmark reports it (1.11× on OpenVLA) and notes that quantization lowers its acceptance ([XPU](../resources/serving/vla-xpu-characterization.md)).

**Weight (width) pruning**
- Removing 63% of OpenVLA-OFT's backbone width drops LIBERO-Long from 93.2% to 0.8%. Offline hidden-state distillation (about 8 H100 GPU-hours, no RL) recovers 89.7%; supervised recovery suffices up to about 45% reduction; distillation matters beyond 63% ([pruned VLA recovery](../resources/compression/pruned-vla-recovery.md)).
- Width vs depth at matched compression: width gives 2.8–33 points higher success; depth gives lower latency (1.31–1.66× vs 1.14–1.18× on an H100). On Jetson Thor the 72%-width-pruned model ran 2.23× faster than the teacher (362 → 162 ms) and used 62% less memory ([pruned VLA recovery](../resources/compression/pruned-vla-recovery.md)).
- Other pruning-recovery work (RLRC: pruning plus supervised and RL recovery; GLUESTICK: training-free low-rank correction) is cited by the surveys and by [pruned VLA recovery](../resources/compression/pruned-vla-recovery.md) but was not read here.

**What the sources report overall**
- Redundant layers are reported in π0, GR00T-N1.5 and SmolVLA: CLP finds success flat up to about half the layers pruned before fine-tuning; for width pruning, hidden-state distillation matters beyond heavy pruning (see above).
- The action head sets a latency floor: with a fixed number of DDIM steps, latency stopped falling after 72% backbone reduction ([pruned VLA recovery](../resources/compression/pruned-vla-recovery.md)); see [flow-step reduction](flow-step-reduction.md).
- Dynamic schemes were measured only on GPUs, and their wall-clock gain trails their FLOP gain (DeeR-VLA, DySL-VLA above).
- Most experiments use LIBERO/CALVIN/SIMPLER, one seed for some, and 7B backbones; real-robot evidence is small (10–200 episodes).

## Open questions
- Combined effect of layer removal with quantization and token reduction on a small VLA on device hardware.
- Whether pruning before or after robot pretraining matters (CLP studied fine-tuning only).
