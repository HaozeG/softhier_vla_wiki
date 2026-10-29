---
type: paper
tags: [guide, embodied-ai, taxonomy, glossary, community]
sources: [https://github.com/tianxingchen/Embodied-AI-Guide]
---
# Embodied-AI-Guide

Tianxing Chen and the Lumina Embodied AI Community, GitHub repository `tianxingchen/Embodied-AI-Guide` (README read; written mainly in Chinese; non-commercial licence). Tagged `community`: a curated learning guide and link collection, not a peer-reviewed source.

## Summary
A newcomer's map of embodied AI: a short glossary, a hands-on tutorial (training an ACT policy on the RoboTwin 2.0 simulator), and curated reading lists grouped into Algorithm, Infrastructure, Control and Hardware. Its value is as a map of which areas the field covers, not as evidence for any claim.

## Key claims
- **Top-level structure (README table of contents):** Start From Here (how to use, learning path, glossary, FAQ); Hands-on Learning (RoboTwin 2.0); Useful Info (surveys, community, labs, venues, paper lists); Algorithm; Infrastructure; Control; Hardware.
- **Algorithm (§4):** common tools; vision foundation models; robot learning; LLMs for robotics; VLA (references, classic works, hierarchical dual-system VLA, recent work); computer vision (2D/3D/4D, visual prompting and affordance); computer graphics; multimodal models; robot navigation; embodied AI for other domains (healthcare, drones, autonomous driving). The README describes it as a stack: tools, geometry and control at the bottom; vision and multimodal representations in the middle; learning and decision making (RL, IL, VLA, LLM plus planner, fast-slow systems) at the top.
- **Infrastructure (§5):** simulators (what worlds can be built), benchmarks (how methods are compared), datasets (what behaviours models learn), toolchain (data formats and policy deployment).
- **Control (§6):** classical, modern and optimal control; kinematics and dynamics; odometry and SLAM; whole-body control (WBC), including motion retargeting and teleoperation.
- **Hardware (§7):** embedded systems, mechanical and system design, sensors (depth, force, proprioception), tactile sensing, data-collection hardware, companies.
- **Glossary (§1.3, 20 terms):** manipulation and locomotion; policy; imitation learning and behaviour cloning (IL/BC); RL; VLA; VA (vision-action policy without language); world model; WAM, described as a policy that first predicts what the robot will see next and then derives actions from it; teleoperation; demonstration (trajectory); sim-to-real gap; real-to-sim; affordance; degrees of freedom (DoF); end-effector; forward and inverse kinematics (FK/IK); URDF; model predictive control (MPC); whole-body control (WBC); SLAM.

## Caveats
- The README was read through an automated summary of its Chinese text; the glossary items above are paraphrased translations, not quotes.
- Only the README was read; the topic pages (for example the algorithm page) were not.
- The guide's WAM entry is narrower than the definition used by the world-action-model survey ([Shen et al.](survey-world-action-models-nus.md)), which also counts act-then-score and joint models.

## Related
See also: [robot learning tutorial](tutorial-robot-learning-hf.md), [Ma et al. survey](survey-vla-embodied-ai-ma.md).
