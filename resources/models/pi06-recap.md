---
type: paper
tags: [rl, vla, offline-rl, pi0.6, advantage-conditioning]
sources: [arxiv:2511.14759, https://arxiv.org/abs/2511.14759]
---
# π*0.6: a VLA That Learns From Experience

Physical Intelligence, arXiv 2511.14759 (v2, November 2025). Method name RECAP (RL with Experience and Corrections via Advantage-conditioned Policies).

## Summary
RECAP improves a large flow-matching VLA (π0.6) from real deployment experience: rewards, autonomous rollouts and human corrections. It is iterated offline RL: collect data, train a language-conditioned value function, then train the VLA conditioned on a text "advantage" indicator, so the whole VLA is updated without policy gradients.

## Key claims
- **Problem (§I-II):** imitation-trained VLAs compound errors and cannot beat their demonstrations; PPO-style RL is hard to scale to real-world VLAs, and policy gradients are hard to apply to flow-matching models because they have no tractable log-likelihood.
- **Loop (§IV, Alg. 1):** (1) run the policy, label episodes success or failure, optionally let an expert intervene; (2) train a value function on all data so far; (3) train the policy with an advantage indicator. Per-task fine-tuning is SFT with the indicator fixed to true, then one or more rounds; every round fine-tunes from the pretrained checkpoint, not from the previous round, which the paper says avoids drift (§V-D).
- **Value function (§IV-A, §V-C):** multi-task, language-conditioned, distributional (201 bins), cross-entropy on Monte Carlo returns; reward is −1 per step, 0 on success, −C_fail on failure, so the value is the negative steps to success. Architecture matches the VLA with a 670M Gemma 3 backbone, so running it during VLA training "incurs minimal additional cost". The paper admits an on-policy Monte Carlo estimator is less optimal than an off-policy Q-function.
- **Policy extraction (§IV-B, Eq. 2-3):** the indicator is the text "Advantage: positive/negative" placed before the actions, so it only conditions action likelihoods; trained on both conditional and unconditional action distributions; human corrections are forced positive; the indicator is dropped 30% of the time, which enables classifier-free guidance at test time (App. E recommends a moderate β of 1.5-2.5).
- **Model (§V-A/B, App. C):** π0.6 descends from π0.5 and uses Knowledge Insulation: a Gemma 3 4B VLM plus an 860M flow-matching action expert with a stop-gradient, outputting subtask text, FAST-tokenized actions (training only) and continuous action chunks at 50 Hz. The whole VLA is trained end to end plus the separate value model. No inference latency is given; subtask prediction "runs at a lower frequency than action generation".
- **Setup (§VI):** a static bimanual robot with two 6-DoF arms and three cameras; tasks are laundry (three variants), double espresso and factory box assembly.
- **Results (§VI):** from offline RL plus SFT to the final model, throughput "more than doubles" on diverse laundry and espresso and the failure rate falls by "about a factor of two"; success is "90%+" on every task except diverse laundry; advantage conditioning gave "by far the highest throughput" against AWR and a PPO variant (PPO needed a trust-region parameter of 0.01 and still underperformed). Deployment claims: 13 hours of continuous espresso-making and over 2 hours of laundry folding in a new home.

## Caveats
- Stated limitations (§VII): humans still give reward labels, interventions and resets; exploration is naive and greedy; updates are batched offline, not a concurrent online loop; the value estimator is on-policy Monte Carlo.
- The text and appendix disagree on data counts for the failure-removal experiment (600 trajectories without interventions against about 1000 autonomous plus 280 and 378 correction episodes) and for box assembly (600 "trials" against 600 "demonstrations").
- No total parameter count, compute or latency figures; plotted values in Figs. 7-12 were not extractable.
