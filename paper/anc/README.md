# Ancillary material

Reproduction package for *The Last Human Gate*
(Jeremy Canale, September 2026). Every number, table row and chart is deterministic arithmetic on the
assumptions in `parameters.json`. No enterprise data are used and nothing is estimated.

| File | Purpose |
|---|---|
| `parameters.json` | Single source of all synthetic assumptions: populations and route allocation, regimes S0-S3, route illustration with shared and local upkeep, trajectory configurations, length and reliability clocks, and the separate 2033 FTE hypothesis |
| `reproduce.py` | Computes all results; writes `results/summary.json`, the LaTeX table rows in `../generated/`, the four data figures in `../figures/`, and matching FTE-chart SVG/PNG exports in `../../assets/readme/` |
| `test_reproduce.py` | Ten checks tying each number quoted in the text to `parameters.json`, including the registry of the three illustrative routes (17 gate occurrences over 8 gate types) and a numerical check of the strategic-model comparative statics |
| `math_notes.pdf` / `.tex` | Derivations: workload ratio and thresholds, selection identity, strategic gate model, reliability bounds |
| `dgf_cases.json` | The three DGF cases (W1, W2, W3) and their analytical mapping, with framework page locators |
| `cohort_protocol.md` | Proposed 80% FTE-reduction study for 2033: workload-equivalent FTE, ecosystem boundary, calendar, decision rules |
| `source_map.md` | Each external reference, its use, and its verification status |

```
python3 anc/reproduce.py
python3 anc/test_reproduce.py
pdflatex main && pdflatex main && pdflatex main
```

The manuscript compiles without Python: generated rows and figures are supplied. The workflow figure is
drawn in TikZ inside the manuscript. The bibliography is a hand-written `thebibliography`; no BibTeX run
is needed.
