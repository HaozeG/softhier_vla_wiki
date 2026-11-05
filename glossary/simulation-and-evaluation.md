---
type: glossary
tags: [glossary, benchmarks, simulation, evaluation]
sources: [resources/benchmarks/vlabench.md, resources/models/smolvla.md, resources/surveys/guide-embodied-ai.md, resources/serving/vla-workload-characterization-kaist.md]
---
# Simulation and evaluation

## Summary
How policies are tested: benchmarks and the MuJoCo simulator, the success rate, and the gap between simulation and the real world. All terms are standard (scope field). Benchmarks are covered in [simulation benchmarks](../knowledge/simulation-benchmarks.md); simulators and the sim-to-real gap have no note yet ([physical AI map](../knowledge/physical-ai-map.md)).

## Terms
| Term                                    | Meaning                                                                                                                                                                    | Scope | Defined in                                                                 |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------------------------------- |
| LIBERO, Meta-World                      | Simulated robot-manipulation benchmarks.                                                                                                                                   | field | [SmolVLA](../knowledge/smolvla.md)                                         |
| success rate                            | Share of benchmark episodes in which the task is completed.                                                                                                                | field | [SmolVLA](../knowledge/smolvla.md)                                         |
| CALVIN                                  | Simulated benchmark of long-horizon, language-conditioned manipulation, scored by how many instructions in a row are completed.                                            | field | [simulation benchmarks](../knowledge/simulation-benchmarks.md)             |
| VLABench                                | Simulated manipulation benchmark whose tasks need world knowledge, implicit goals in natural language and long horizons, with unseen object categories as its test split.  | field | [VLABench](../resources/benchmarks/vlabench.md)                            |
| language-conditioned manipulation (LCM) | Manipulation where the task is given as a natural-language instruction.                                                                                                    | field | [VLABench](../resources/benchmarks/vlabench.md)                            |
| Progress Score                          | VLABench's graded score: a weighted sum of the share of target objects chosen correctly and the share of sub-steps completed, so a failed episode can earn partial credit. | field | [VLABench](../resources/benchmarks/vlabench.md)                            |
| domain randomization                    | Varying scene properties (object instances, poses, scale, textures, lighting, distractors) across episodes so a policy does not fit one fixed scene.                       | field | [VLABench](../resources/benchmarks/vlabench.md)                            |
| sim-to-real gap                         | The differences between a simulator and the real world (physics, rendering, sensor noise) that make a policy trained in simulation work worse on the real robot.           | field | [physical AI map](../knowledge/physical-ai-map.md)                         |
| real-to-sim                             | Reconstructing real scenes and objects in a simulator, to narrow the sim-to-real gap or to evaluate in simulation.                                                         | field | [physical AI map](../knowledge/physical-ai-map.md)                         |
| MuJoCo                                  | A physics simulator for robots; the LIBERO tasks run on it.                                                                                                                | field | [Jung et al.](../resources/serving/vla-workload-characterization-kaist.md) |
