# Non-snapshot source coverage: conservative offline certification

All **300 dossiers** and **1700 scheduled gates** were inspected. The AST inventory contains **76 distinct fields**, of which **72** have explicit source decoders. All static gate/field pairs are inspected physically in every dossier, even where that gate is not scheduled.

This is a certification inventory, not a model experiment or an assertion that every uncertified case is impossible. Static fields include phase-inactive branches. Matching sources may coexist with contradictions. Direct-read scope, phase, and availability are evaluated separately from physical existence.

| Physical gate/field status | Count |
|---|---:|
| DECODED_VALUES_DISAGREE | 673 |
| MATCH_ESTABLISHED | 21687 |
| NOT_ESTABLISHED | 2840 |

| Scheduled gate/field status | Count |
|---|---:|
| DECODED_VALUES_DISAGREE | 460 |
| NOT_ESTABLISHED | 1967 |
| PHYSICAL_MATCH_ACCESS_BLOCKED | 1402 |
| READABLE_MATCH_ESTABLISHED | 13271 |

## Uncertified fields

- `compliance.audit_trail`: NOT_ESTABLISHED by the explicit decoders.
- `compliance.residency_compliant`: NOT_ESTABLISHED by the explicit decoders.
- `it.duplicate_capability`: NOT_ESTABLISHED by the explicit decoders.
- `tech_readiness.open_blockers`: NOT_ESTABLISHED by the explicit decoders.

## Proven generator omissions

- `it.duplicate_capability`: on `DGF-BLD-035200_build`, changing `False` to `True` changes the frozen gate decision from GO to REWORK. Only `gate_evidence/it/review_facts.json` changes; all 76 non-snapshot output payloads and renderer inputs remain identical.
- `compliance.audit_trail`: on `DGF-BUY-035000_buy`, changing `complete` to `missing` changes the frozen gate decision from GO to REWORK. Only `gate_evidence/compliance/review_facts.json` changes; all 77 non-snapshot output payloads and renderer inputs remain identical.

These counterexamples cover generated artifact contents and diagram inputs. They do not exclude a separate authoritative tool supplying the missing fact; such access would need to be specified explicitly in an ablation.

## Field inventory

| Gate | AST fields |
|---|---|
| general | `general.budget_approved_eur`, `general.budget_requested_eur`, `general.change_plan_status`, `general.roi`, `general.strategic_alignment`, `project.risk_owner` |
| it | `it.capacity_headroom_pct`, `it.catalog_status`, `it.change_record_status`, `it.cmdb_record_present`, `it.duplicate_capability`, `it.license_compliant`, `it.run_owner_present`, `it.technology_eol_months`, `it.waiver_present`, `project.risk_owner` |
| architecture | `architecture.api_gateway_present`, `architecture.api_gateway_required`, `architecture.data_owner_present`, `architecture.ip_overlap`, `architecture.latency_target_ms`, `architecture.measured_latency_ms`, `architecture.reversibility_status`, `architecture_profile.multi_az`, `architecture_profile.multi_region`, `project.business_criticality`, `project.risk_owner` |
| security | `project.data_classification`, `project.risk_owner`, `security.critical_vulns_open`, `security.internet_exposed`, `security.key_rotation_days`, `security.logs_to_siem`, `security.mfa`, `security.pentest_status`, `security.private_endpoints`, `security.shared_service_principal`, `security.waf_mode`, `security.waf_present` |
| tech_readiness | `project.risk_owner`, `tech_readiness.backup_enabled`, `tech_readiness.critical_static_findings`, `tech_readiness.dr_required`, `tech_readiness.dr_tested`, `tech_readiness.handover_signed`, `tech_readiness.load_test_pct_of_peak`, `tech_readiness.measured_data_loss_minutes`, `tech_readiness.measured_restore_hours`, `tech_readiness.on_call_defined`, `tech_readiness.open_blockers`, `tech_readiness.restore_tested`, `tech_readiness.rollback_tested`, `tech_readiness.runbook_status`, `tech_readiness.target_rpo_minutes`, `tech_readiness.target_rto_hours` |
| procurement | `procurement.offers.[*].vendor`, `procurement.offers.[selected_vendor].due_diligence`, `procurement.offers.[selected_vendor].mandatory_criteria_failed`, `procurement.offers.[selected_vendor].references_checked`, `procurement.offers.[selected_vendor].sanctions`, `procurement.offers.[selected_vendor].tco_3y_eur`, `procurement.purchasing_budget_eur`, `procurement.selected_vendor`, `project.risk_owner` |
| legal | `legal.audit_right`, `legal.dpa_status`, `legal.exit_assistance_days`, `legal.insurance_valid`, `legal.ip_ownership`, `legal.liability_cap_multiplier`, `legal.log_export_clause`, `legal.security_carveout`, `legal.signing_authority_valid`, `project.business_criticality`, `project.personal_data`, `project.risk_owner` |
| compliance | `compliance.accessibility_status`, `compliance.audit_trail`, `compliance.dpia_required`, `compliance.dpia_status`, `compliance.export_control`, `compliance.regulatory_mapping`, `compliance.residency_compliant`, `project.risk_owner` |

## Limits

- Static per-gate field inventory is an upper bound: it includes fields whose phase condition or short-circuited branch may not apply to a particular occurrence. Failure of all-static-fields certification does not prove that occurrence undecidable.
- A matching readable source is a coverage witness, not proof of unique inferability: conflicting or stale alternatives and authority resolution can still matter. Every alternative mismatch is retained.
- NOT_ESTABLISHED means no reliable implemented decoder or decoding failure; it is not a claim of physical absence. Exact scalar decoding intentionally does not substitute threshold predicates or undocumented semantic inference.
- Availability describes direct read_evidence at the frozen scope/phase/public_status. request_evidence, authoritative domain tools, extra prompt fields, diagram vision, and runtime UPSTREAM_DECISIONS are outside this certification and require their own controlled ablation interfaces.
- The selected-vendor offer decoder depends on SCORING_MATRIX and the source row jointly. A physically matching row is not declared readable when its selection dependency is blocked.
- DOCX conversion follows explicit frozen template labels and prose, not general document understanding. Source reader limits of 200 CSV rows/40000 DOCX characters are enforced.
- No independent human validation, model calls, original score changes, or new evidence generation in the dataset. Two counterfactual proofs capture generator payloads offline; they do not claim absence from every possible external tool.

## Reproduce

`python research/2026-09-followup/source_coverage_audit.py`

The summary JSON contains AST line references, every decoder specification, counts and counterexamples. The detailed JSON preserves every comparison, decoded value, dependency access check and SHA-256 of read non-snapshot source files. No raw hidden truth is included in either output.

## Tool-interface boundary

The direct-file certification must not be generalized to the whole tool interface. request_evidence returns the full gate factual_snapshot for an allowed evidence request, even if the requested ID is a non-snapshot document. A snapshot-removal ablation must control this return path. get_regulatory_applicability separately exposes residency_compliant. The two named getter methods do not themselves expose duplicate_capability or audit_trail in this frozen source.

The 76-field count concerns case facts and the output metadata `risk_owner`. Phase comes from the route manifest. General also consumes runtime `upstream_results[*].disposition` and `upstream_results[*].gate`; those AST dependencies are separately recorded in the JSON and are not expected in static source documents.
