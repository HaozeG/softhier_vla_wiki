---
type: entity
tags: [industry, on-device, vla, google-deepmind, first-party]
sources: [https://deepmind.google/blog/gemini-robotics-on-device-brings-ai-to-local-robotic-devices/]
---
# Gemini Robotics On-Device (Google DeepMind blog)

## Summary
Google DeepMind announced Gemini Robotics On-Device on 24 June 2025 as a VLA "optimized to run locally on robotic devices", able to operate without a data network. It targets bi-arm robots (ALOHA, Franka FR3, Apollo humanoid) and is offered through a trusted-tester program with an SDK and MuJoCo simulation. The announcement gives almost no hardware or latency numbers, so it is evidence that on-device VLAs are a commercial product direction, not evidence of any specific compute budget.

## Details
- **What is stated:** "operates independent of a data network", runs "entirely locally"; general-purpose dexterity; adapts to new tasks with "as few as 50 to 100 demonstrations"; the first VLA model DeepMind offers for fine-tuning.
- **Quantitative claims on the page (as extracted):** generalization success rates in the range 0.52–0.74 across visual, semantic and action tests and 0.68 average over seven dexterous fast-adaptation tasks. Instruction-following results are stated as outperforming earlier models without exact numbers.
- **Not stated:** parameter count, on-board processor, memory, power, latency or control rate ("specific computational requirements: not quantified").
- **Later releases:** search results list newer "On-Device 2" and "Gemini Robotics 2" pages; these were not opened and are not used here.
- **Trust level:** marketing-style first-party blog; use only for the existence and positioning of the product.

See also: [Helix](figure-helix.md), [Jetson specs](../hardware/nvidia-jetson-platform-specs.md).
