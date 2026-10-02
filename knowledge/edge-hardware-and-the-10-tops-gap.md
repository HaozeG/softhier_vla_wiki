---
type: concept
tags: [edge, hardware, tops, bandwidth, jetson, npu, data-gap]
sources: [resources/hardware/nvidia-jetson-platform-specs.md, resources/hardware/edge-accelerator-datasheets.md, resources/serving/vla-xpu-characterization.md, resources/serving/vla-cpp.md, resources/serving/vla-simd.md, resources/serving/jetson-pi.md, resources/compression/pruned-vla-recovery.md, resources/serving/vla-perf.md, resources/serving/litevla-edge.md]
---
# Edge hardware and the 10 TOPS gap

## Summary
Nearly all measured "edge VLA" results are on Jetson Orin or Thor (tens to hundreds of vendor TOPS, 100–273 GB/s), not on ~10 TOPS parts. Below Orin Nano the sources give CPU runs (Raspberry Pi 5, desktop CPUs), one leaderboard plot that includes an Ascend 310B (10 TFLOP/s) and one community report on the RK3588 (6 TOPS). The plot shows ACT at about 10 Hz on the 310B but no bar for SmolVLA or any flow-matching VLA on it. So **no flow-matching VLA is measured on a 10 TFLOP/s part, and the only flow-matching VLA number on a small NPU is one self-reported community README (SmolVLA about 5 s per chunk on the RK3588)** (SmolVLA on the 88 TFLOP/s Ascend 310P is about 2 Hz in a PyTorch baseline).

## Diagram
```text
Where VLAs have been measured, by device (units as the sources state
them; they differ, so the order is rough)

device          compute as stated       flow-matching VLA measured?
Thor            517 dense FP8 TFLOPS    pi0, pi0.5: yes
AGX Orin        275 sparse INT8 TOPS    pi0, pi0.5: yes
Ascend 310P     88 TFLOP/s BF16/FP16    SmolVLA ~2 Hz, pi0 ~1.2 Hz (plot)
Orin Nano       67 sparse INT8 TOPS     SmolVLA 358-457 ms per chunk
- - - - at or below about 40 vendor TOPS (mixed units) - - - - - - - - - - - -
Hailo-8L/8/10H  13/26/20 INT8 TOPS      no VLA data
Ascend 310B     10 TFLOP/s BF16/FP16    ACT only (~10 Hz); no SmolVLA bar
RK3588          6 TOPS INT8 (headline)  SmolVLA ~5 s/chunk, self-reported
CPU only        none used               SmolVLA 8.2 s (Pi 5), 2.1 s (i9)
```
The divider is drawn at about 40 vendor TOPS, the largest figure in the Hailo rows; the glossary's [~10 TOPS class](../glossary/hardware-and-performance.md) (about ten TOPS or less) holds only the Ascend 310B and RK3588 rows. Bandwidths and power are in the table below.

## Details
The RTX 4090 (a graphics card), A100 and H100 (datacenter GPUs), all from NVIDIA, appear in the sources as reference points, far above the ~10 TOPS class this project targets.

**Hardware classes (vendor figures; precision and sparsity matter)**

| Class                                     | Compute                                              | Memory bandwidth                        | Power                    | Source                                                                                                                              |
| ----------------------------------------- | ---------------------------------------------------- | --------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Ascend 310B                               | 10 TFLOP/s FP16                                      | 51.2 GB/s (12 GB)                       | not listed               | [XPU](../resources/serving/vla-xpu-characterization.md)                                                                             |
| Raspberry Pi AI HAT+ (Hailo-8L / Hailo-8) | 13 / 26 TOPS                                         | not listed                              | not listed               | [datasheets](../resources/hardware/edge-accelerator-datasheets.md)                                                                  |
| Hailo-10H                                 | 20 (INT8) / 40 (INT4) TOPS                           | LPDDR4/4X interface, no figure          | 2.5 W typical            | datasheets                                                                                                                          |
| Rockchip RK3588 (3-core NPU)              | 6 TOPS headline (INT8)                               | 21–22 GB/s measured (CPU); 64-bit LPDDR | est. 5–6 W under AI load | [RK3588 platform](../resources/rk3588/rk3588-platform-specs.md), [measurements](../resources/rk3588/rk3588-vlm-llm-measurements.md) |
| Jetson Orin Nano 8 GB                     | 67 sparse INT8 TOPS                                  | 102 GB/s                                | 7–25 W                   | [Jetson specs](../resources/hardware/nvidia-jetson-platform-specs.md)                                                               |
| Jetson AGX Orin 64 GB                     | 275 TOPS (sparse INT8)                               | 204.8 GB/s                              | 15–60 W                  | Jetson specs                                                                                                                        |
| Jetson Thor                               | 517 dense FP8 TFLOPS, 1035 sparse                    | 273 GB/s                                | 40–130 W                 | Jetson specs                                                                                                                        |
| RTX 4090 (reference)                      | about 165–330 dense BF16 TFLOPS, depending on source | about 1000 GB/s                         | high                     | [VLA-Perf](../resources/serving/vla-perf.md), XPU                                                                                   |

Dense-BF16 numbers for the same device differ by 2× or more between papers; compare devices on stated precision, and note that INT4/INT8 TOPS are unusable for a BF16 flow loop.

**Measured VLA points by device class** (per-model SmolVLA numbers are collected in [SmolVLA](smolvla.md), which lists the same devices from the model's side)
- **Thor:** π0 roofline 19 Hz (52.6 ms); measured π0.5 310–458 ms per chunk with system work; π0 246 ms baseline / 163 ms compiled. See [workload characterization](inference-workload-characterization.md).
- **AGX Orin:** π0 921 ms baseline; π0.5 1.4 s at 50 W (naive), 0.41 s after graph reuse and unrolling; OpenVLA-OFT 676 ms → 345 ms with layer skipping ([Jetson-PI](../resources/serving/jetson-pi.md), [DySL-VLA](../resources/compression/dysl-vla.md)).
- **Orin Nano 8 GB:** SmolVLA 358–457 ms per chunk; BitVLA (ternary, 1.3 GiB) fits and runs at 356 ms per executed action; GR00T-N1.6/N1.7 out of memory ([vla.cpp](../resources/serving/vla-cpp.md)).
- **RK3588 (6 TOPS NPU):** the most common robot-prototype board. Only community and first-party proxies exist: ACT about 121 ms, SmolVLA as three RKNN modules about 5 s (self-reported), SmolVLM-256M image encoder 842 ms at 512×512. Details and practices are in [RK3588 deployment](rk3588-vla-deployment.md).
- **CPU only:** SmolVLA 2.1 s (i9, 8 threads), 8.2 s per 50-action chunk on a Pi 5; a 60M ACT-style policy reaches 33.5 actions/s on the Pi 5 ([vla.simd](../resources/serving/vla-simd.md)).
- **Below Orin Nano on an accelerator:** ACT (34M-class policy, no VLM) on the Ascend 310B at about 10 Hz and on an i7 CPU at about 13 Hz, plus SmolVLA on that CPU at about 0.3 Hz, all read off a log-scale bar chart ([XPU characterization](../resources/serving/vla-xpu-characterization.md)); SmolVLA and π0 on the Ascend 310P (88 TFLOP/s) at about 2 and 1.2 Hz. No SmolVLA bar exists for the 310B. LiteVLA-Edge's 256M 4-bit policy at 150 ms is on an Orin (device ambiguous in the paper) and reports no task success ([LiteVLA-Edge](../resources/serving/litevla-edge.md)).

**What the sources show about the gap**
- Weight-bound devices benefit more from parameter reduction: width-pruned OpenVLA-OFT (72% smaller) ran 1.16× faster on an H100 but 2.23× on Thor ([pruned VLA recovery](../resources/compression/pruned-vla-recovery.md)).
- Memory capacity limited model choice in the sources: the 12 GB Ascend 310B cannot hold OpenVLA 7B and the 8 GB Orin Nano cannot hold GR00T-N1.6.
- Vendor TOPS are headline figures, often sparse INT8 or FP4; dense BF16 figures for the same device are lower (table above).

## Open questions
- Tabulated (not plotted) SmolVLA/flow-VLA results on Ascend 310B, Hailo or Rockchip-class NPUs, including operator support for cross-attention and flow loops.
- Power and thermal behaviour: only a 90 s passive-cooling soak (Pi 5) and a battery-life estimate ([Jetson-PI](../resources/serving/jetson-pi.md)) exist.

See also: [robot compute partitioning](robot-compute-partitioning.md) — controller versus AI tiers on Unitree and AgiBot robots.
