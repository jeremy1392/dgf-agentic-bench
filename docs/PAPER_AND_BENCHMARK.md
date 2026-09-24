# Paper and benchmark

Jeremy Canale's research is now presented in the **[12-page concise article, The Last Human Gate: Forward Deployed Engineering for Governance Automation](../paper2/From_Governance_Reviews_to_Task_Substitution.pdf)** and the **[66-page extended original](../paper/The_Last_Human_Gate.pdf)**. The concise article replaces the former DGF-Bench empirical companion and is the recommended main manuscript. These are versions of a shared research contribution, not independent studies.

## The paper

The manuscript treats governance gates as information-transforming contracts. It develops a theoretical argument about their automation, a model of residual human work, route composition and handoff hypotheses, and a proposed test of the author's hypothesis that the DGF ecosystem will require 80% fewer workload-equivalent FTE by 2033 than in 2026, at comparable governed output, quality, and service. Complete automation remains a stronger, undated conjecture.

Its workforce figures are reproducible synthetic calculations. They are not measurements of deployed systems, and no enterprise cohort is enrolled. The original baseline year ended on 20 September 2026, so testing the exact 2033 hypothesis now requires auditable historical records. Sources and assumptions are in [paper/anc](../paper/anc/).

## The benchmark

DGF-Bench tests agents on synthetic dossiers, explicit rules, evidence tools, authorization boundaries, and structured downstream handoffs. Correct outcomes are derived from generated case facts.

Experiments can measure decision reliability, finding/action accuracy, evidence support, authorization correctness, route-level success, and model cost under a specified protocol. Scores concern review decisions, proposed actions and simulated governance operations. They do not establish completed remediation or human labor savings in production.

## Reporting experimental results

Declare the code and scoring versions, sampling policy, model settings, case counts by route, technical exclusions, and costs. Compare models on the same cases. Analyze uncertainty at the case level, retaining dependencies between gates.

A sample conditioned to cover decisions answers a different question from a sample following the generator's natural distribution. Neither automatically represents enterprise prevalence. A public-observation baseline that shares the reference evaluator checks internal consistency, not the business validity of the rules. Independent human evaluation is outside the current programme, which evaluates LLM execution of the specified decision tasks.

Keep empirical benchmark tables separate from the manuscript's synthetic workforce examples. An incomplete run is a partial evaluation, even if every scheduled job has ended with a success or error status. Observational improvements across model generations do not by themselves prove universal governance automation.

## Publication scope

The manuscript now includes the September 2026 benchmark evaluation: 300 synthetic dossiers, three models, 899 evaluable model/case runs, and one excluded infrastructure failure. [Final data and reproduction](../research/2026-09-dgf-bench/) and the [complete release archives](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923) support these measured results. Explicit policies and structured authoritative facts are available to the agents; this is a scaffolded policy-application test. Tests of actual workforce effects, institutional delegation, downstream operational acceptance, or complete enterprise automation require additional empirical designs and data.

Both papers also report the same completed follow-up: a deterministic control passing 1,700/1,700 gates, a structural provenance audit of all 690 evidence-failed gates, and 135 repeated model/case runs on 15 existing dossiers. Original and repeated inference cost USD 99.5757161948. Original strict scores remain unchanged; the structural criterion is a separate post-hoc sensitivity analysis. [Follow-up records](../research/2026-09-followup/).

The source inventory, three development dossiers, and citation prototype are offline diagnostics. The prepared 270-execution General-only comparison and broader scaffold ablation have not run. The concise paper retains the original 2033 hypothesis and distinguishes a separate prospective seven-year protocol; neither is an active enrolled study.
