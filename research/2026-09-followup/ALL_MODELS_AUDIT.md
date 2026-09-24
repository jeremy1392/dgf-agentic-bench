# All-model evidence and decision audit

Post-hoc analysis of all 899 original evaluable model-case runs. **No new model calls; original scores remain unchanged.** All 690 gates with a failed evidence component are included. The 135 repetition runs are separate.

## Strict versus lexical-or-structural sensitivity

| Model | Strict gates | Relaxed gates | Strict routes | Relaxed routes |
|---|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 1261/1700 (74.18%) | 1313/1700 (77.24%) | 74/300 (24.67%) | 85/300 (28.33%) |
| google/gemini-3.8-flash | 1609/1694 (94.98%) | 1678/1694 (99.06%) | 230/299 (76.92%) | 284/299 (94.98%) |
| openai/gpt-5.6-luna | 1416/1700 (83.29%) | 1454/1700 (85.53%) | 127/300 (42.33%) | 144/300 (48.00%) |

The additional pass criterion accepts a relevant exact field/value subset within one actually observed object, ignoring object field order and equivalent numeric serialization. Duplicate keys, wrong values, booleans treated as numbers, and joins across different objects do not pass. Required citations and all other original score components remain unchanged; no quotes or tool reads are repaired. Original lexical passes are retained. This is **not semantic entailment, full premise coverage, or an independent human audit**. Nonparseable prose can still be factually correct.

## Procurement

| Model | Decisions correct / 100 | Strict / 100 | Relaxed / 100 | Evidence-only failures |
|---|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 97 | 43 | 43 | 54 |
| google/gemini-3.8-flash | 100 | 96 | 96 | 4 |
| openai/gpt-5.6-luna | 96 | 33 | 34 | 63 |

All four Gemini Procurement failures are budget-related cross-object excerpts. Relaxation recovers no additional DeepSeek Procurement gate and one Luna gate. The item-level file includes per-finding excerpts, observed contents, matching paths, and original component scores. Parser failure is not proof of a false factual claim.

## Decision errors and reference definition

| Model | Wrong decisions | More restrictive | Less restrictive | False approvals | Initial-reference matches | Effective-reference matches |
|---|---:|---:|---:|---:|---:|---:|
| deepseek/deepseek-v4.1-flash | 81 | 76 | 5 | 1 | 1553 | 1619 |
| google/gemini-3.8-flash | 0 | 0 | 0 | 0 | 1553 | 1694 |
| openai/gpt-5.6-luna | 32 | 10 | 22 | 1 | 1568 | 1668 |

Policy order: GO, GO_WITH_RESERVATIONS, REWORK, SUSPENSION, NO_GO. Less restrictive does not necessarily mean approval: REWORK and SUSPENSION both block progression. DeepSeek has 35 GO-to-REWORK and 23 GO_WITH_RESERVATIONS-to-REWORK errors; Luna has 17 SUSPENSION-to-REWORK errors.

The effective reference incorporates validated conditional approvals. Gemini's 141 initial-label differences comprise 139 local approvals and two General outcomes reflecting upstream authorized changes. Initial-reference agreement answers a different question from conformity after permitted actions. The model cannot validate its own approval merely by asserting it: the mandate and conditions are checked by the frozen evaluator.

## Document-only preflight

An executed counterexample changes only the selected vendor due-diligence value in DGF-BUY-035004_buy. All 26 generated Word documents have identical extracted paragraphs and tables; the frozen required Procurement disposition changes from GO to REWORK. The differing information is in the due-diligence CSV and snapshot. A Word-only condition therefore cannot recover that distinction. A broader document-plus-record condition requires a separate sufficiency check. The frozen citation requirement also needs a common new contract before snapshots can be hidden fairly.

## Reproduction and records

- [Audit script](audit_all_models.py): reads saved scores and traces; writes separate derived outputs.
- [All-model summary and per-case route outcomes](all_models_evidence_summary.json)
- [Complete failed-evidence item records](all_models_evidence_items.json)
- [Complete effective-reference confusion matrices](decision_confusion.csv)
- [Document counterexample script](check_document_ablation.py) and [report with text hashes](document_ablation_preflight.json)
- [Matched-information ablation protocol](../../paper2/protocols/scaffold_ablation.md)

Use the frozen source extraction described in [the reproduction instructions](README.md#offline-reproduction), then run:

```powershell
python research/2026-09-followup/audit_all_models.py
python research/2026-09-followup/check_document_ablation.py
python paper2/verify_manuscript.py
```

The scripts use the original dataset and results by default; explicit dataset/run/output arguments are available. The counterexample writes new artifacts under experiments/document_ablation_preflight_20260924. It never changes original inputs. No paid ablation, human adjudication, or new enterprise observation is claimed.

Jeremy Canale · 24 September 2026
