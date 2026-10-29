---
type: concept
tags: [physical-ai, embodied-ai, taxonomy, map, coverage]
sources: [resources/surveys/guide-embodied-ai.md, resources/surveys/tutorial-robot-learning-hf.md, session:embodied-ai-guide-peer]
---
# Physical AI map

## Summary
A map of the areas of physical AI (also called embodied AI), used to place the wiki's notes and to see which areas have none yet. It follows the [Embodied-AI-Guide](../resources/surveys/guide-embodied-ai.md) (a community guide), whose README groups the field into Algorithm, Infrastructure, Control and Hardware. Inside "robot learning" the wiki further splits a policy into four choices that can be made independently: learning paradigm, action generation, conditioning and backbone, and execution. That four-way split is the wiki's own arrangement, proposed in a session with another agent working from the guide (`session:embodied-ai-guide-peer`), not a claim of the guide.

```text
PHYSICAL AI
|
+-- Algorithm
|   +-- robot learning: a policy = 4 independent choices
|   |   +-- learning paradigm     imitation (BC) | RL | pretrain -> fine-tune
|   |   +-- action generation     tokens | regression, CVAE | diffusion, flow
|   |   +-- conditioning/backbone vision (+state) | + language (VLM -> VLA)
|   |   +-- execution             chunking, ensembling, async, open loop
|   +-- model families            ACT, Diffusion Policy, VLAs, dual-system,
|   |                             world models, WAM
|   +-- vision, 3D, affordance;   LLMs for robots; navigation
+-- Infrastructure                simulators, benchmarks, datasets, toolchain
+-- Control                       kinematics (FK/IK), MPC, WBC, SLAM
+-- Hardware                      robots, sensors, tactile, data collection
+-- (deployment compute: chips, kernels, MFU -- outside the guide's tree)
```

## Details
**The guide's areas.** Algorithm covers robot learning, VLAs (including dual-system VLAs), vision foundation models, 2D/3D vision and affordance, LLMs for robotics, and navigation. Infrastructure covers simulators, benchmarks, datasets and the toolchain. Control covers classical and optimal control, kinematics, SLAM and whole-body control. Hardware covers robots, sensors, tactile sensing and data-collection hardware. The chips and kernels a policy runs on, this project's subject, are not a section of the guide ([Embodied-AI-Guide](../resources/surveys/guide-embodied-ai.md)).

**The four policy choices.** Learning paradigm: imitation of demonstrations (behaviour cloning), RL from reward, usually as pretraining followed by fine-tuning. Action generation: discrete tokens; single-pass regression or a CVAE; or iterative diffusion or flow matching. Conditioning and backbone: a policy may read only vision and robot state, or add language through a pretrained VLM, which makes it a VLA. Execution: chunking, temporal ensembling, asynchronous execution and open-loop stretches ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md)).

**Where the wiki's notes sit.**
| Area                      | Notes                                                                                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Learning paradigm         | [imitation learning and behaviour cloning](imitation-learning-and-behaviour-cloning.md), [fast policy trained by RL](fast-policy-trained-by-rl.md)              |
| Action generation         | [action representation and chunking](action-representation-and-chunking.md)                                                                                     |
| Conditioning and backbone | [VLA architecture overview](vla-architecture-overview.md), [one VLA call](one-vla-call.md), [SmolVLA](smolvla.md)                                               |
| Execution                 | [one VLA call](one-vla-call.md), [action representation and chunking](action-representation-and-chunking.md), [low-level policy loop](low-level-policy-loop.md) |
| Model families            | [dual-system VLA](dual-system-vla.md), [WAM overview](wam-overview.md), [VLA architecture overview](vla-architecture-overview.md)                               |
| Deployment compute        | [SoftHier and the project](softhier-and-the-project.md)                                                                                                         |

**Areas with no note yet.** These are named in the guide or the tutorial, with no source ingested on them:
- Data: teleoperation set-ups, large pretraining datasets (Open X-Embodiment, DROID), dataset formats such as `LeRobotDataset` (the tutorial names them; the guide lists datasets under Infrastructure).
- Observation and action spaces: joint versus end-effector actions, position versus velocity control (Diffusion Policy reports position control works better for it).
- Simulation and evaluation: simulators, benchmarks, the sim-to-real gap and real-to-sim reconstruction.
- Perception: 3D and point-cloud inputs, affordance.
- Control foundations: forward and inverse kinematics, MPC, whole-body control, SLAM.
- Locomotion, tactile sensing and robot hardware.

**Definitions differ.** The guide describes a WAM as a policy that first predicts what it will see and then derives actions; the [WAM overview](wam-overview.md) follows a survey whose definition also covers scoring actions by their predicted outcome and joint models.

## Open questions
- Which of the uncovered areas the project needs is a project decision, not recorded here.
