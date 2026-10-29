---
type: concept
tags: [wam, world-model, overview, taxonomy]
sources: [resources/surveys/survey-world-action-models-nus.md, resources/surveys/survey-vla-embodied-ai-ma.md, resources/surveys/guide-embodied-ai.md]
---
# World action models (WAM)

## Summary
A world action model is a model in which a forecast of the future is available to the action: it uses a predicted future observation to produce the action, score it or train the action path, inside one model. A VLA only maps the present observation to actions; a world model only predicts the future. This note follows one survey ([World Action Models: A Survey](../resources/surveys/survey-world-action-models-nus.md)); other surveys may define WAM differently. The community [Embodied-AI-Guide](../resources/surveys/guide-embodied-ai.md), for example, describes a WAM only as a policy that first predicts what it will see and then derives actions, the predict-then-act case below.

```text
VLA          o, l ----------------------------> a
WORLD MODEL  o, a, l -------------------------> o'
WAM          predict-then-act:  o,l -> o' -> a
             act-then-score:    o,l -> a -> o'  (o' scores a)
             joint:             o,l -> (o', a) together

what must be generated before the action is decoded:
  Render-and-Decode : video all the way to pixels
  Latent-Only       : video backbone, pixel decoder skipped
  Video-Gen-Free    : prediction in tokens, JEPA features, geometry
```

## Details
- **Boundary:** a VLA with only an auxiliary future loss, a simulator used only as a reinforcement-learning environment, or a future head dropped before the action is computed are not WAMs. Video generators (Wan, CogVideoX, Cosmos, Sora) are one instance of world models; they become WAMs when coupled to actions.
- **Design tuple:** substrate (pixel, feature, geometric, affordance), coupling (rollout, joint generation, post-prediction head), backbone (diffusion, autoregressive, JEPA, hybrid, LLM/VLM) and deployment (open-loop, chunked, single-step, interactive).
- **Cost and frequency:** a chunked design is feasible when one forward pass over K actions costs less than K control periods; decoded pixels plus joint generation plus diffusion plus single-step control is the most expensive corner. Fast and slow loops (HarmoWAM, LingBot-VA, FFDC-WAM) mirror the [dual-system VLA](dual-system-vla.md) split.
- **Sizes the survey gives:** an 860M action expert under a Gemma3 VLA with a separate lightweight world model refreshing subgoal images every four seconds (π0.7), and a 300M expert under a PaliGemma-2B trunk (ALAM). The survey reports almost no other parameter or Hz figures.
- **Related:** the earlier [VLA survey of Ma et al.](../resources/surveys/survey-vla-embodied-ai-ma.md) lists dynamics learning and world models as VLA components; the [VLA architecture overview](vla-architecture-overview.md) and [one VLA call](one-vla-call.md) describe the VLA side.

## Open questions
- Whether a WAM's per-call workload differs from [one VLA call](one-vla-call.md) in a way the wiki should model: the survey gives a cost model but no measured breakdown.
- Other WAM definitions: [World-Action Models for Robot Learning and Control](https://arxiv.org/abs/2609.16074) and [World Action Models: The Next Frontier](https://arxiv.org/abs/2605.12090) are not ingested.
