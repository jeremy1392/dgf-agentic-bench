# Paper and benchmark

**[The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance](../paper/The_Last_Human_Gate.pdf)**, by Jeremy Canale (September 2026), and DGF-Bench address different research questions.

## The paper

The manuscript treats governance gates as information-transforming contracts. It develops a theoretical argument about their automation, a model of residual human work, route composition and handoff hypotheses, and a proposed test of the author's hypothesis that the DGF ecosystem will require 80% fewer workload-equivalent FTE by 2033 than in 2026, at comparable governed output, quality, and service. Complete automation remains a stronger, undated conjecture.

Its workforce figures are reproducible synthetic calculations. They are not measurements of deployed systems, and no completed enterprise cohort study is claimed. Sources and assumptions are in [paper/anc](../paper/anc/).

## The benchmark

DGF-Bench tests agents on synthetic dossiers, explicit rules, evidence tools, authorization boundaries, and structured downstream handoffs. Correct outcomes are derived from generated case facts.

Experiments can measure decision reliability, finding/action accuracy, evidence support, authorization correctness, route-level success, and model cost under a specified protocol. Scores concern review decisions, proposed actions and simulated governance operations. They do not establish completed remediation or human labor savings in production.

## Reporting experimental results

Declare the code and scoring versions, sampling policy, model settings, case counts by route, technical exclusions, and costs. Compare models on the same cases. Analyze uncertainty at the case level, retaining dependencies between gates.

A sample conditioned to cover decisions answers a different question from a sample following the generator's natural distribution. Neither automatically represents enterprise prevalence. A public-observation baseline that shares the reference evaluator checks internal consistency; independent expert review is needed to assess business validity.

Keep empirical benchmark tables separate from the manuscript's synthetic workforce examples. An incomplete run is a partial evaluation, even if every scheduled job has ended with a success or error status. Observational improvements across model generations do not by themselves prove universal governance automation.

## Publication scope

The manuscript now includes the September 2026 benchmark evaluation: 300 synthetic dossiers, three models, 899 evaluable model/case runs, and one excluded infrastructure failure. [Final data and reproduction](../research/2026-09-dgf-bench/) and the [complete release archives](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) support these measured results. Explicit policies and structured authoritative facts are available to the agents; this is a scaffolded policy-application test. Tests of actual workforce effects, institutional delegation, downstream operational acceptance, or complete enterprise automation require additional empirical designs and data.
