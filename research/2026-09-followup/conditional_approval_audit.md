# Conditional approval behavior in the original benchmark

This post-hoc audit reads the final retained checkpoints for 899 scored runs. It makes no model calls and changes no original scores. The public policy permits either keeping the base decision or requesting authorized conditional approval. Thus approval use is a separate behavioral result, not an error count.

## Exact counts

| Model | Gates | Approval calls | Gates with a request | Rejected calls | Verified final approvals | Approvals used | Eligible gates | Use among eligible | Use among all gates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| deepseek-v4.1-flash | 1700 | 216 | 209 | 14 | 202 | 202 | 397 | 50.88% | 11.88% |
| gemini-3.8-flash | 1694 | 864 | 692 | 466 | 398 | 398 | 398 | 100.00% | 23.49% |
| gpt-5.6-luna | 1700 | 394 | 390 | 40 | 354 | 353 | 398 | 88.69% | 20.76% |

Eligibility requires at least one open finding, every finding marked risk-acceptable by the public executable rules, and an active mandate for that precise occurrence, gate, and phase. The same public facts and policy interpreter used by the deterministic comparator reconstruct eligibility. Each recorded executed approval is then replayed under the frozen environment policy; the final approval state and final prediction must agree with the archived scorer flags. All assertions passed.

Luna has one verified approval that is not used: Procurement in `DGF-BUY-035087_buy` ends with REWORK, although its valid approval permits GO_WITH_RESERVATIONS. Gemini makes 466 rejected calls, in addition to 398 executed approvals; a rejection is not itself a false final approval. Conditions are checked as nonempty strings by this synthetic contract, not independently adjudicated for operational adequacy.

## Matched comparison

All three models have 299 cases and 1,694 gates in common. General eligibility can differ because previously authorized decisions change the findings available for consolidation. Restricting to the 1,395 non-General gates fixes the same 391 eligible opportunities for every model.

| Model | All matched approvals / eligible | Matched non-General approvals / eligible | Cases with approval / cases with an eligible opportunity |
|---|---:|---:|---:|
| deepseek-v4.1-flash | 202/396 (51.01%) | 201/391 (51.41%) | 131/227 (57.71%) |
| gemini-3.8-flash | 398/398 (100.00%) | 391/391 (100.00%) | 227/227 (100.00%) |
| gpt-5.6-luna | 353/397 (88.92%) | 347/391 (88.75%) | 205/227 (90.31%) |

On the same 391 non-General opportunities, Gemini uses 391 approvals and DeepSeek 201: 1.95 times as many. This supports a descriptive difference in propensity to request/use conditional approvals under this particular prompt, policy, and dataset. It does not establish general permissiveness, stable risk preferences, or a causal personality trait. Some approvals do not relax the base disposition at all.

## Why agreement differences are not approval counts

| Model | Used approval, base REWORK | Used approval, base SUSPENSION | Used approval, base already conditional | Local approvals changing base label | Indirect General changes | Effective matches minus base matches |
|---|---:|---:|---:|---:|---:|---:|
| deepseek-v4.1-flash | 65 | 2 | 135 | 67 | 1 | 66 |
| gemini-3.8-flash | 128 | 11 | 259 | 139 | 2 | 141 |
| gpt-5.6-luna | 88 | 10 | 255 | 98 | 2 | 100 |

The quoted Gemini count of 139 counts only local approvals that change the base disposition (128 REWORK and 11 SUSPENSION), omitting 259 approvals whose base was already GO_WITH_RESERVATIONS. Two General labels also change from REWORK to GO following upstream authorization, giving 141 additional effective matches. DeepSeek has 67 local label-changing approvals but loses one former base match at General after upstream authorization, giving a net difference of 66. Luna has 98 local label-changing approvals plus two indirect General changes, giving 100. Subtracting agreement percentages therefore cannot recover approval counts.

## By gate (all scored runs)

| Model | Gate | Gates | Eligible | Request calls | Requested gates | Used approvals | Use among eligible |
|---|---|---:|---:|---:|---:|---:|---:|
| deepseek-v4.1-flash | architecture | 200 | 52 | 35 | 35 | 33 | 63.46% |
| deepseek-v4.1-flash | compliance | 200 | 8 | 5 | 5 | 5 | 62.50% |
| deepseek-v4.1-flash | general | 300 | 5 | 2 | 2 | 1 | 20.00% |
| deepseek-v4.1-flash | it | 300 | 115 | 57 | 57 | 57 | 49.57% |
| deepseek-v4.1-flash | legal | 200 | 67 | 28 | 28 | 28 | 41.79% |
| deepseek-v4.1-flash | procurement | 100 | 25 | 11 | 11 | 11 | 44.00% |
| deepseek-v4.1-flash | security | 300 | 97 | 62 | 55 | 52 | 53.61% |
| deepseek-v4.1-flash | tech_readiness | 100 | 28 | 16 | 16 | 15 | 53.57% |
| gemini-3.8-flash | architecture | 199 | 52 | 152 | 108 | 52 | 100.00% |
| gemini-3.8-flash | compliance | 199 | 8 | 43 | 32 | 8 | 100.00% |
| gemini-3.8-flash | general | 299 | 7 | 82 | 61 | 7 | 100.00% |
| gemini-3.8-flash | it | 299 | 115 | 158 | 142 | 115 | 100.00% |
| gemini-3.8-flash | legal | 199 | 67 | 127 | 104 | 67 | 100.00% |
| gemini-3.8-flash | procurement | 100 | 25 | 44 | 36 | 25 | 100.00% |
| gemini-3.8-flash | security | 299 | 96 | 189 | 157 | 96 | 100.00% |
| gemini-3.8-flash | tech_readiness | 100 | 28 | 69 | 52 | 28 | 100.00% |
| gpt-5.6-luna | architecture | 200 | 52 | 65 | 64 | 51 | 98.08% |
| gpt-5.6-luna | compliance | 200 | 8 | 13 | 13 | 8 | 100.00% |
| gpt-5.6-luna | general | 300 | 6 | 7 | 7 | 6 | 100.00% |
| gpt-5.6-luna | it | 300 | 115 | 79 | 77 | 75 | 65.22% |
| gpt-5.6-luna | legal | 200 | 67 | 69 | 68 | 67 | 100.00% |
| gpt-5.6-luna | procurement | 100 | 25 | 26 | 26 | 24 | 96.00% |
| gpt-5.6-luna | security | 300 | 97 | 104 | 104 | 94 | 96.91% |
| gpt-5.6-luna | tech_readiness | 100 | 28 | 31 | 31 | 28 | 100.00% |

## Reproduction

Run from the repository root:

```powershell
.venv/Scripts/python.exe research/2026-09-followup/conditional_approval_audit.py
```

`conditional_approval_summary.json` contains all, common-case, non-General, by-gate, and paired descriptive counts. `conditional_approval_items.json` provides all 5,094 gate records, eligibility, event counts, disposition decomposition, and original trace paths. CLI options can point to downloaded dataset, result, and frozen-source archives. Repeated trajectories and ERROR checkpoints are outside this audit. Public-policy agreement is not independent validation of the policy itself.
