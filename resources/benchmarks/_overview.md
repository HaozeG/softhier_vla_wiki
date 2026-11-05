# resources/benchmarks/

Sources that define how robot policies are evaluated: simulation benchmarks, their task suites, generalization settings and metrics, and the baseline results they publish. Inference-speed profiling of models lives in `serving/`, not here.

- [VLABench](vlabench.md) — 100 MuJoCo manipulation tasks (60 primitive, 40 composite) stressing knowledge, implicit language and long horizons; Progress Score; fine-tuned OpenVLA, Octo, RDT-1B, two LLM workflows and seven VLMs all score low
