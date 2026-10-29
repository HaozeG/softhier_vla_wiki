---
type: glossary
tags: [glossary, benchmarks, simulation, evaluation]
sources: [resources/models/smolvla.md, resources/surveys/guide-embodied-ai.md]
---
# Simulation and evaluation

## Summary
How policies are tested: benchmarks, the success rate, and the gap between simulation and the real world. All terms are standard (scope field). The [physical AI map](../knowledge/physical-ai-map.md) lists this area as one with no note yet.

## Terms
| Term               | Meaning                                                                                                                                                          | Scope | Defined in                                         |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | -------------------------------------------------- |
| LIBERO, Meta-World | Simulated robot-manipulation benchmarks.                                                                                                                         | field | [SmolVLA](../knowledge/smolvla.md)                 |
| success rate       | Share of benchmark episodes in which the task is completed.                                                                                                      | field | [SmolVLA](../knowledge/smolvla.md)                 |
| sim-to-real gap    | The differences between a simulator and the real world (physics, rendering, sensor noise) that make a policy trained in simulation work worse on the real robot. | field | [physical AI map](../knowledge/physical-ai-map.md) |
| real-to-sim        | Reconstructing real scenes and objects in a simulator, to narrow the sim-to-real gap or to evaluate in simulation.                                               | field | [physical AI map](../knowledge/physical-ai-map.md) |
