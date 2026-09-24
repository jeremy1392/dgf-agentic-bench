# Procurement source audit: parse failures, observed CSVs, and contract failures

This is a post-hoc diagnostic of the original trajectories. It makes no model calls and changes no primary scores or previously reported structural sensitivity scores.

The reviewer is right that failure to parse an excerpt as one JSON object does not establish false evidence. A separate, verified issue is that the frozen scorer requires `REVIEW_FACTS_PROCUREMENT` for Procurement finding support: an exact quote from a genuinely read and cited CSV can fail that contract.

## Scope and units

All 300 original Procurement occurrences across the three models were inspected (100 per model). The deeper audit includes the 127 occurrences whose original evidence score failed. Their diagnostics contain **185 failed findings**, with **205 submitted support entries** and **2 findings missing support**. A finding may have several support alternatives; an occurrence may have several findings. These denominators must not be interchanged.

| Model | Evidence-failed occurrences | Failed findings | Submitted support entries | Missing support findings |
|---|---:|---:|---:|---:|
| DeepSeek | 56 | 82 | 102 | 2 |
| Gemini | 4 | 4 | 4 | 0 |
| GPT-5.6-Luna | 67 | 99 | 99 | 0 |
| Total | 127 | 185 | 205 | 2 |

## Trace-based results

| Model | Literal quote in an observed source | Nonliteral excerpt: every extracted complete JSON field/value occurs in its own observed source | Match only in an available but unread source | No literal / extracted JSON-pair match |
|---|---:|---:|---:|---:|
| DeepSeek | 29 | 73 | 0 | 0 |
| Gemini | 0 | 4 | 0 | 0 |
| GPT-5.6-Luna | 2 | 96 | 0 | 1 |
| Total | 31 | 173 | 0 | 1 |

The last cell is **one natural-language excerpt outside the JSON-pair parser**, not a demonstrated factual error. It says: `Selected supplier is "CedarPoint Digital 4461A-3" and its observed due_diligence value is "partial".` The observed snapshot contains that selected supplier and that supplier's `due_diligence: partial`. The detailed output records the quoted strings' source paths, without turning a string match into an entailment score.

All 205 submitted supports cite evidence IDs that were actually observed and included in the submitted `evidence_refs`. **None cites an unknown or unread source.** Of the 144 excerpts that fail the single-object JSON parser, 143 contain extracted complete scalar field/value pairs all present in the cited source; the remaining item is the prose excerpt above. This is positive provenance evidence, although it does not validate every implication or association in the excerpt.

## Observed CSV evidence rejected by the snapshot-only contract

DeepSeek supplied **26** failed support entries citing CSV sources: 21 `DUE_DILIGENCE`, 3 `VENDOR_OFFERS`, and 2 `PRICING_TCO`. Every source was read and cited.

**25 are literal rows in the observed CSV output**, covering 25 failed findings across 23 occurrences. Each row identifies the supplier selected in the observed snapshot. The remaining entry joins two genuinely observed `DUE_DILIGENCE` rows using ellipses. No equivalent CSV support alternatives were submitted in the audited Gemini or Luna items.

The original scorer rejects the 26 entries at the source-ID condition before testing their quote. This does **not** mean each finding would pass a complete semantic or alternative-source evaluation: for example, a pricing row alone does not establish the purchasing envelope needed for the budget comparison. It establishes that the label `unobserved_or_wrong_reference` conflated **observed but contract-excluded** sources with genuinely missing provenance. There are no genuinely unread cited sources in this Procurement subset.

The instructions explicitly request the authoritative snapshot and prohibit ellipses. The original strict scores remain valid as compliance with that declared protocol; they should not be interpreted as counts of false factual assertions.

## Inspectable examples

1. **Observed CSV row, contract-excluded.** DeepSeek, `DGF-BUY-035002_buy`, `PROC-DD-001`: `DUE_DILIGENCE` support includes the exact row `{"due_diligence": "partial", "mandatory_failed": "2", "references_checked": "False", "sanctions": "hit", "vendor": "HelioStack Cloud 6A670-2"}`. The tool trace confirms the read, and the snapshot confirms that this is the selected vendor. The same finding also has a literal snapshot quote containing selection/budget metadata but no due-diligence field. A first-support-only classification hides the useful CSV alternative.
2. **Nonliteral join of real fields.** DeepSeek, `DGF-BUY-035001_buy`, `PROC-BUDGET-001`: `"selected_vendor": "CedarPoint Digital 2DF08-2" ... "tco_3y_eur": 1054822 ... "purchasing_budget_eur": 250000`. The three fields occur in the observed snapshot; the TCO and envelope inhabit different objects. Ellipses fail the contract; JSON parse failure does not make these numbers false.
3. **Literal but insufficient excerpt.** Luna, `DGF-BUY-035042_buy`, `PROC-DD-001`: a literal snapshot quote gives `selected_vendor`, `competition`, `rfp_requirements`, and `purchasing_budget_eur`, omitting `due_diligence`. This is an authentic quotation that does not state the rule's decisive field. Six of the 31 literal quotes in this audit are such snapshot metadata excerpts, demonstrating why literal provenance is not sufficient evidence of a finding.
4. **Prose outside the parser.** Luna, `DGF-BUY-035098_buy`, `PROC-DD-001`: the supplier/due-diligence sentence discussed above is factual on inspection, but remains outside this mechanical JSON-pair diagnostic.

Full relative checkpoint paths, checkpoint and score SHA-256 values, source IDs, pre-submission trace indices, source paths, quotes, and field/value match paths are in `procurement_source_items.json`.

## Method and limits

`procurement_source_audit.py` reconstructs phase-appropriate public evidence with the frozen `PublicEvidenceReader`. Only successful `read_evidence` or `request_evidence` results whose content exactly matches the immutable public source qualify as observations. The frozen runner returns on a valid final submission before executing other calls in that same batch, so saved tool-trace results precede submission. Available-but-unread sources are searched separately and never promoted to observed support. Dynamic upstream decisions are excluded from this Procurement artifact audit.

CSV files are presented to the agent as JSON arrays of dictionaries, preserving their string-valued cells. Literal matching uses that actual representation, not a fabricated CSV rendering. The separate scalar-pair diagnostic retains exact field names and types; `10` does not match `100` or the CSV string `"10"`, and Boolean `true` does not match numeric `1`. Numeric `30` and `30.0` are equivalent. It deliberately allows field/value occurrence in different objects, retaining their paths for inspection.

**The scalar-pair diagnostic does not validate relationships, prove full premise coverage, or adjudicate natural-language entailment.** It does not infer that the agent actually relied on a source, only that the source was returned before submission and contains the checked content. It cannot prove that all human-facing source documents are trustworthy. No global “semantic accuracy” or recovered route score is reported.

The justified interpretation is narrower: Procurement's original evidence failures mix excerpt-format violations, source-ID contract restrictions, and incomplete relevant quotations. It is not justified to describe all parser failures as unreliable facts, nor to assume that every provenance match constitutes a correct argument.

## Reproduce

From the repository root, with the released original dataset/run and frozen source available at their documented paths:

```powershell
.venv/Scripts/python.exe research/2026-09-followup/procurement_source_audit.py
```

`--run-dir`, `--dataset`, and `--output-dir` override the default artifact paths. The script writes `procurement_source_summary.json` and `procurement_source_items.json`. Its input source module is the immutable `experiments/reproduction_check_20260923/verified_inputs/benchmark_source` imported through the existing audit helper. It includes adversarial controls for numeric prefixes, Boolean/numeric confusion, CSV string coercion, and complete scalar-pair extraction.
