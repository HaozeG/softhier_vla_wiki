---
type: concept
tags: [imitation-learning, behavioural-cloning, compounding-error, multimodality, generative-policy, rl]
sources: [resources/surveys/tutorial-robot-learning-hf.md, resources/models/act-aloha.md, resources/models/diffusion-policy.md, resources/surveys/guide-embodied-ai.md, resources/models/pi0.md]
---
# Imitation learning and behaviour cloning

## Summary
Most robot policies in this wiki, VLAs included, are trained by imitation: behaviour cloning (BC) fits a policy to recorded expert demonstrations as supervised learning, with no reward. The sources name two weaknesses of a plain regression policy trained this way: **compounding error** (small mistakes push the robot into states the demonstrations never show) and **poor fit to multimodal demonstrations** (it averages two equally good ways of doing a task). Action chunking was introduced against the first, and generative action heads (CVAE, diffusion, flow matching) against the second. Reinforcement learning (RL), which learns from reward by trial and error, is the other paradigm; on VLAs it appears mostly as a later stage ([fast policy trained by RL](fast-policy-trained-by-rl.md)). The [physical AI map](physical-ai-map.md) places both paradigms in the wider field.

```text
demonstrations (teleoperation: observation, action pairs; no reward)
        |
        v
 BEHAVIOUR CLONING = supervised learning  obs -> action
        |
        +-- weakness 1: compounding error ---> fix: action chunking
        |   (drift into unseen states)          (ACT; chunk of k cuts
        |                                        the horizon k-fold)
        |
        +-- weakness 2: multimodal demos ----> fix: generative head
            (regression averages modes)         CVAE (ACT), diffusion
                                                (Diffusion Policy),
                                                flow matching (pi0)

single-task BC policies (ACT, Diffusion Policy)
  --> generalist VLAs, still trained to reproduce demonstrations
  --> optional RL stage on top
```

## Details
**Behaviour cloning.** The Hugging Face tutorial defines BC as learning a mapping from observations (images plus proprioception, the robot's own joint readings) to actions from reward-free expert trajectories. Its listed advantages: training is offline and safe, no reward has to be designed, and success and resets are implicit in the data. Its limit: the policy can at best match the demonstrator ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md)). Demonstrations are usually collected by teleoperation, with a human driving the robot, for example through leader arms in ALOHA ([ACT](../resources/models/act-aloha.md)).

**Compounding error.** Errors from earlier steps accumulate and drive the robot off the training distribution (covariate shift). DAgger-style fixes need extra expert corrections during rollouts, which ACT's authors call unnatural with teleoperation. ACT instead predicts a chunk of k actions, cutting the effective horizon k-fold; in its simulated ablation success rose from 1% at k = 1 to 44% at k = 100 ([ACT](../resources/models/act-aloha.md)).

**Multimodal demonstrations.** Human demonstrations often contain several valid strategies. Regression averages them. The remedies are generative heads: a CVAE (ACT), diffusion (Diffusion Policy) and flow matching (π0, whose action expert is trained with a flow-matching loss); ACT's CVAE objective lifted success on human data from 2% to 35.3% in simulation, and Diffusion Policy commits to one mode where baselines are biased or cannot commit ([Diffusion Policy](../resources/models/diffusion-policy.md)). The head types are compared in [action representation and chunking](action-representation-and-chunking.md).

**From single-task to generalist.** The tutorial groups generalist VLAs (π0, SmolVLA) with BC methods because both are trained to reproduce demonstration trajectories; π0 pretrains on a large mixed corpus and is then fine-tuned on high-quality task data ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md); [π0](../resources/models/pi0.md)). The [Embodied-AI-Guide](../resources/surveys/guide-embodied-ai.md) also lists IL/BC and RL as the two learning paradigms.

**RL.** RL improves a policy from a reward signal; on real robots the tutorial lists sample inefficiency, unsafe exploration, reward design, success detection and resets as obstacles ([robot learning tutorial](../resources/surveys/tutorial-robot-learning-hf.md)).

## Open questions
- The sources read give no head-to-head comparison of ACT, Diffusion Policy and a flow head on the same tasks.
