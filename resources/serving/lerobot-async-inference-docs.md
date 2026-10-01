---
type: entity
tags: [lerobot, async-inference, smolvla, first-party, docs]
sources: [https://huggingface.co/docs/lerobot/async, https://huggingface.co/blog/smolvla, arxiv:2506.01844]
---
# LeRobot asynchronous inference stack (first-party docs)

## Summary
LeRobot's `async_inference` package is the reference implementation of the asynchronous inference design in the [SmolVLA paper](../models/smolvla.md): a `PolicyServer` runs the policy (possibly on another machine) and a `RobotClient` streams observations and consumes action chunks, so the robot never idles waiting for inference. The docs describe it as model-agnostic and usable with any LeRobot policy, from ACT to SmolVLA. This note records what the documentation states, not measurements.

## Details
- **Architecture:** the server starts empty and the client's first handshake specifies policy type, checkpoint (`pretrained_name_or_path`) and device (`policy_device`: cuda, mps, xpu or cpu). Client and server communicate over the network, so inference can run on a remote GPU.
- **Key parameters:** `actions_per_chunk` (default 50, "typical values 10–50") and `chunk_size_threshold` (the SmolVLA paper's g). Larger chunks lower the chance of an empty queue but accumulate error; thresholds near 0 collapse to synchronous behaviour and near 1 send an observation every step. The docs recommend about 0.5–0.6. The docs are internally inconsistent about the default (a table says 0.7; the examples use 0.5), so check the installed version.
- **Chunk aggregation:** `aggregate_fn_name` (for example `weighted_average`) blends overlapping portions of successive chunks. Note this differs from the inpainting approach in [real-time chunking](real-time-chunking.md).
- **Sizing guidance:** "π0 occupies 14 GB of memory at inference time, while SmolVLA requires only about 2 GB"; reduce the client `fps` if the queue empties; use the `--debug_visualize_queue_size` flag to tune the threshold.
- **Blog claims (qualitative, from the SmolVLA post):** 450M parameters with about 100M in the action expert; "small enough to run on CPU ... or even a MacBook"; async gives about 30% faster task completion (9.7 s vs 13.75 s) and 2× completions in fixed time (19 vs 9 cubes). These match the paper's Figure 5; the blog gives no latency numbers for CPU or MacBook.
- **Trust level:** first-party documentation, no independent measurements. For CPU numbers see [vla.simd](vla-simd.md) and [vla.cpp](vla-cpp.md).

See also: [RTC](real-time-chunking.md), [FlashVLA](flashvla-streaming.md), [Jetson-PI](jetson-pi.md).
