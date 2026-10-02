---
type: glossary
tags: [glossary, action-head, flow-matching, diffusion]
sources: [resources/models/smolvla.md, resources/models/openvla-oft.md, resources/models/fast-tokenizer.md]
---
# Action generation

## Summary
The ways a VLA turns its features into actions (discrete tokens, parallel regression, flow matching) and the vocabulary of the flow loop. All terms are standard (scope field).

## Terms
| Term                             | Meaning                                                                                                          | Scope | Defined in                                                                               |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ----- | ---------------------------------------------------------------------------------------- |
| discrete action tokens (binning) | Each action dimension is cut into bins and written as tokens by the language model, one pass per token.          | field | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| FAST                             | Compresses an action chunk into fewer tokens; still decoded one token at a time.                                 | field | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| parallel regression              | One pass writes all actions of a chunk through a regression head.                                                | field | [action representation and chunking](../knowledge/action-representation-and-chunking.md) |
| flow matching                    | Start from random noise shaped like the action chunk and refine it in small steps; see below.                    | field | [SmolVLA](../knowledge/smolvla.md)                                                       |
| diffusion                        | The same refine-from-noise idea with a different step rule; a sampler such as DDIM lets it use fewer steps.      | field | [flow-step reduction](../knowledge/flow-step-reduction.md)                               |
| action expert                    | The small network that runs the flow steps.                                                                      | field | [SmolVLA](../knowledge/smolvla.md)                                                       |
| DiT                              | Diffusion transformer.                                                                                           | field | [VLA architecture overview](../knowledge/vla-architecture-overview.md)                   |
| noisy chunk, flow time           | The current guess for the chunk, and how far along the refinement it is.                                         | field | [SmolVLA](../knowledge/smolvla.md)                                                       |
| velocity, Euler step             | The expert outputs a velocity, a direction to move the noisy chunk; an Euler step moves it a small way along it. | field | [SmolVLA](../knowledge/smolvla.md)                                                       |
| flow steps (T)                   | The number of refinement steps one call runs.                                                                    | field | [flow-step reduction](../knowledge/flow-step-reduction.md)                               |

## Flow matching
**Flow matching in one paragraph.** The expert is trained so that, given a noisy chunk and a flow time, it predicts the velocity that points toward the true action chunk. At run time the model starts from pure noise and applies T Euler steps; each step calls the expert once. After the last step the chunk is the predicted actions.
