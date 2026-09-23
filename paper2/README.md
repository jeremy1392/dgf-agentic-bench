# From Governance Reviews to Task Substitution

**DGF-Bench and the Role of Forward Deployed Engineers**  
Jeremy Canale · September 2026

[Read the second paper](From_Governance_Reviews_to_Task_Substitution.pdf) · [LaTeX source](main.tex) · [Response to the review](REVIEW_RESPONSE.md)

**20 pages, approximately 9,800 extracted words, including references and appendices.**

This is a separate, shorter manuscript based on the **same September 2026 experiment** as [The Last Human Gate](../paper/The_Last_Human_Gate.pdf). It is not an independent replication or a new set of model trials. The original paper remains available unchanged.

The second paper centers the 300-project benchmark, distinguishes decision quality from evidence conformity, gives FDE implementation work a concrete specification, and connects potential workforce substitution to measurable human labor. It replaces universal-law language with a conditional task-substitution hypothesis. The 80% FTE reduction by 2033 remains an explicitly testable projection.

The human baseline, independent semantic evidence adjudication, scaffold-removal tests, repeated model trajectories, and enterprise cohort are **proposed studies, not completed results**. No participants have been enrolled and no preregistration is claimed. A prospective study starting now cannot silently replace the original 2026 historical baseline.

## Sources and reproduction

All original benchmark data, including Word documents and architectures, remain in the [complete experiment release](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923). The [research directory](../research/2026-09-dgf-bench/) contains final tables and offline reproduction instructions. The earlier [15-project pilot](../research/2026-09-pilot/SOURCE_DOCUMENTS.md) is separate from the main experiment.

Build from this directory with a standard LaTeX installation:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The output is `main.pdf`; the published copy is `From_Governance_Reviews_to_Task_Substitution.pdf`. Figures and table fragments are included, so compilation does not require Python or API access. From the repository root, `python paper2/verify_manuscript.py` checks table/figure provenance, headline counts, and scenario arithmetic against the released local research artifacts. It does not independently validate the governance rules.

## Follow-up protocols

- [Human and rules-engine comparison](protocols/human_baseline.md)
- [Independent semantic evidence audit](protocols/semantic_evidence.md)
- [Historical and prospective cohort calendar](protocols/field_cohort.md)

Author: [Jeremy Canale](https://www.jeremycanale.com) · contact@jeremycanale.com · [LinkedIn](https://www.linkedin.com/in/jcanale13)
