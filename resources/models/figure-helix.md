---
type: entity
tags: [industry, dual-system, humanoid, onboard, first-party]
sources: [https://www.figure.ai/news/helix]
---
# Figure Helix (dual-system VLA, company blog)

## Summary
Helix is Figure's VLA for humanoid upper-body control, built as a slow "System 2" VLM plus a fast "System 1" visuomotor policy, running on the robot's embedded GPUs. It is the best-known industrial example of the dual-system serving pattern analysed in [VLA-Perf](../serving/vla-perf.md), but the public page gives frequencies and model sizes only.

## Details
- **Stated on the page:** S2 is a 7B-parameter open-weight VLM running at 7–9 Hz for scene understanding; S1 is an 80M-parameter cross-attention encoder-decoder transformer running a 200 Hz control loop; inference runs asynchronously with temporal-offset matching; the robots carry "dual low-power-consumption embedded GPUs"; about 500 hours of teleoperated training data.
- **Not stated on the page (checked):** GPU model, wattage, quantization, and latency in milliseconds. A web-search summary attributed "4-bit quantization", "under 60 W", "sub-100 ms" and "23× lower compute than a cloud implementation" to Helix; none of these appear on the fetched page, so they are treated as unverified and are not used elsewhere in this wiki.
- **Why it matters:** shows the split where the 7B model runs at under 10 Hz and only an 80M network runs at control rate, which is the extreme form of the async dual-system trade-off ([serving methods](../../knowledge/serving-methods.md)).
- **Trust level:** company announcement, no paper.

See also: [GR00T N1](gr00t-n1.md), [Gemini On-Device](gemini-robotics-on-device.md), [VLA-Perf](../serving/vla-perf.md).
