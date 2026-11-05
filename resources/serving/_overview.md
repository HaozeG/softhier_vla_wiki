# resources/serving/

Sources that measure how VLA models run on hardware: latency, bottlenecks, energy and the closed control loop, as opposed to how the models are built (`models/`).

- [Jung et al. (KAIST)](vla-workload-characterization-kaist.md) — batch-1 characterization of GR00T N1.6, π0.5, OpenVLA-OFT, Cosmos-Policy and OpenVLA on RTX 4090, Jetson Thor and Orin; roofline, DVFS, 43,200 closed-loop episodes
- [VLA-HWBench (Xu et al., NUS)](vla-hwbench-edge-latency.md) — 18 open VLAs on Jetson AGX Thor and AMD Ryzen AI Max+ 395, seven-stage latency breakdown, staged optimizations (compile, FlashRT/TensorRT, FP8/NVFP4), roofline; latency only, no task success
