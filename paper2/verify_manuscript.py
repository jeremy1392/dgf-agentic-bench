"""Check manuscript provenance and headline arithmetic without model calls.

Run from any working directory. Uses only the standard library and released local
research artifacts; does not independently adjudicate enterprise governance rules.
"""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    checked = []
    for pattern in ("figures/fig_benchmark*", "generated/table_benchmark*.tex"):
        for path in sorted(HERE.glob(pattern)):
            original = ROOT / "paper" / path.relative_to(HERE)
            content, source = path.read_bytes(), original.read_bytes()
            if path.suffix == ".tex":
                content = content.replace(b"\r\n", b"\n")
                source = source.replace(b"\r\n", b"\n")
            assert content == source, str(path)
            checked.append({"path": path.relative_to(HERE).as_posix(),
                            "sha256": hashlib.sha256(content).hexdigest(),
                            "hash_scope": "LF-normalized text" if path.suffix == ".tex" else "original bytes"})
    assert len(checked) == 6, len(checked)
    research = ROOT / "research/2026-09-dgf-bench"
    with (research / "paper_overall.csv").open(encoding="utf-8", newline="") as stream:
        overall = list(csv.DictReader(stream))
    diagnostics = json.loads((research / "diagnostics.json").read_text(encoding="utf-8"))
    expected = {
        "deepseek/deepseek-v4.1-flash": (300, 1700, 1261, 74, 1619, 338, 1, 1),
        "google/gemini-3.8-flash": (299, 1694, 1609, 230, 1694, 85, 0, 0),
        "openai/gpt-5.6-luna": (300, 1700, 1416, 127, 1668, 221, 1, 3),
    }
    for row in overall:
        d = diagnostics[row["model"]]
        cases, gates, success, routes, decisions, evidence_only, false, misses = expected[row["model"]]
        assert int(row["cases"]) == cases
        assert int(row["gate_occurrences"]) == gates
        assert sum(x["gate_success"] for x in d["routes"].values()) == success
        assert sum(x["route_success"] for x in d["routes"].values()) == routes
        assert d["decision_correct"] == decisions
        assert d["evidence_only"] == evidence_only
        assert int(row["false_approvals"]) == false
        assert int(row["critical_misses"]) == misses
        assert abs(float(row["gate_csr"]) - success / gates) < 0.000001
    assert sum(int(r["cases"]) for r in overall) == 899
    assert sum(int(r["gate_occurrences"]) for r in overall) == 5094
    assert round(sum(float(r["total_cost_usd"]) for r in overall), 2) == 87.02
    followup=ROOT/'research/2026-09-followup'
    control=json.loads((followup/'baseline_summary.json').read_text(encoding='utf-8'))
    assert (control['cases'],control['gates'],control['strict_gate_success'],control['route_success'])==(300,1700,1700,300)
    audit=json.loads((followup/'gemini_evidence_audit.json').read_text(encoding='utf-8'))
    assert len(audit['gates'])==85
    assert audit['gate_counts']=={'all_failed_items_structurally_supported':69,'citation_defect':7,'includes_flattened_cross_object_excerpt':9}
    assert audit['failed_finding_item_counts']=={'structured_field_values_match':75,'flattened_cross_object_values_present':9}
    repeats=json.loads((followup/'repetition_analysis.json').read_text(encoding='utf-8'))
    assert (repeats['model_case_runs'],repeats['gates'])==(135,765)
    assert abs(repeats['known_cost_usd']-12.5598870228)<1e-10
    for model, counts in {
        'google/gemini-3.8-flash':(245,35,255,9),
        'openai/gpt-5.6-luna':(211,19,246,3),
        'deepseek/deepseek-v4.1-flash':(187,11,245,0),
    }.items():
        item=repeats['models'][model]; p=item['pooled']
        assert (p['strict_gates'],p['complete_routes'],p['correct_dispositions'],item['all_three_successful_cases'])==counts
        assert p['gates']==255 and p['cases']==45
        assert p['false_approvals']==p['critical_misses']==0
    all_models=json.loads((followup/'all_models_evidence_summary.json').read_text(encoding='utf-8'))['models']
    for model, counts in {
        'google/gemini-3.8-flash': (1678,284,85,0,96,96),
        'openai/gpt-5.6-luna': (1454,144,251,32,33,34),
        'deepseek/deepseek-v4.1-flash': (1313,85,354,81,43,43),
    }.items():
        a=all_models[model]
        assert (a['posthoc_relaxed_gates'],a['posthoc_relaxed_routes'],a['evidence_failed_gates'],a['wrong_decisions'],a['procurement']['strict'],a['procurement']['relaxed'])==counts
        assert sum(r['count'] for r in a['decision_confusion'])==a['gates']
        assert sum(r['count'] for r in a['decision_confusion'] if r['reference']!=r['prediction'])==a['wrong_decisions']
        assert sum(a['evidence_only_gate_categories'].values())==a['evidence_only_failed_gates']
        assert a['posthoc_relaxed_gates']-a['strict_gates']==a['evidence_only_gate_categories']['all_failed_items_structurally_supported']
        assert sum(r['relaxed'] for r in a['route_details'])==a['posthoc_relaxed_routes']
    preflight=json.loads((followup/'document_ablation_preflight.json').read_text(encoding='utf-8'))
    assert preflight['identical_docx_text_count']==len(preflight['document_text_sha256'])==26
    assert [v['reference_disposition'] for v in preflight['variants'].values()]==['GO','REWORK']
    assert preflight['model_calls']==0
    approvals=json.loads((followup/'conditional_approval_summary.json').read_text(encoding='utf-8'))
    repeat_audit=json.loads((followup/'repetition_evidence_summary.json').read_text(encoding='utf-8'))
    for model, expected in {
        'google/gemini-3.8-flash': (398,398,864,466,391,249,39,12),
        'openai/gpt-5.6-luna': (353,398,394,40,347,217,23,5),
        'deepseek/deepseek-v4.1-flash': (202,397,216,14,201,195,11,0),
    }.items():
        a=approvals['models'][model]['all_scored']
        matched=approvals['models'][model]['common_cases_non_general']
        rep=repeat_audit['models'][model]
        assert (a['used_gates'],a['eligible_gates'],a['request_calls'],a['rejected_calls'],
                matched['used_gates'],rep['pooled']['posthoc_relaxed_gates'],
                rep['pooled']['posthoc_relaxed_routes'],rep['all_three_posthoc_relaxed_cases'])==expected
        assert matched['eligible_gates']==391
    proc=json.loads((followup/'procurement_source_summary.json').read_text(encoding='utf-8'))['models']
    assert sum(v['counts']['submitted_support_entries'] for v in proc.values())==205
    assert sum(v['counts']['failed_findings'] for v in proc.values())==185
    assert sum(v['counts']['evidence_failed_gates'] for v in proc.values())==127
    ds=proc['deepseek/deepseek-v4.1-flash']
    assert ds['source_reference_status']['observed_cited_source_excluded_by_snapshot_only_contract']==26
    assert ds['counts']['entries_exact_in_own_observed_cited_csv_or_docx']==25
    assert ds['counts']['gates_with_exact_observed_csv_or_docx_alternative']==23
    coverage=json.loads((followup/'source_coverage_audit.json').read_text(encoding='utf-8'))
    assert (coverage['cases'],coverage['scheduled_occurrences'],coverage['unique_ast_fields'],
            coverage['gate_field_pairs'],coverage['mapped_unique_fields'])==(300,1700,76,84,72)
    assert coverage['physical_gate_field_counts']=={'MATCH_ESTABLISHED':21687,'NOT_ESTABLISHED':2840,'DECODED_VALUES_DISAGREE':673}
    assert coverage['scheduled_occurrence_field_counts']=={'PHYSICAL_MATCH_ACCESS_BLOCKED':1402,'READABLE_MATCH_ESTABLISHED':13271,'NOT_ESTABLISHED':1967,'DECODED_VALUES_DISAGREE':460}
    assert len(coverage['generator_omission_counterexamples'])==2
    extension=json.loads((followup/'source_record_extensions_report.json').read_text(encoding='utf-8'))
    assert extension['status']=='PASS' and len(extension['development_cases'])==3
    assert all(row['unchanged'] for row in extension['protected_tree_integrity'])
    assert coverage['model_calls']==extension['model_calls']==0
    result = {"status": "pass", "evaluable_runs": 899, "evaluable_gates": 5094,
              "figures_and_tables": checked,
              "checks": ["original figure bytes and LF-normalized table text", "headline and component counts",
                         "rounded total cost", "executed rules control", "85-gate structural audit", "135-run repetition results", "690-gate all-model sensitivity audit", "complete decision matrices", "26-document counterexample", "conditional approval behavior and eligible denominators", "observed Procurement CSV support", "repeated-trajectory evidence sensitivity", "300-case source inventory and development-only extension"],
              "boundary": "Internal consistency and provenance only; no new inference or independent expert validation."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
