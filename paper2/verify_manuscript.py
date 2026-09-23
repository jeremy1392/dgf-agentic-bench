"""Check manuscript provenance and headline arithmetic without model calls.

Run from any working directory. Uses only the standard library and released local
research artifacts; does not independently adjudicate enterprise governance rules.
"""
import csv
import hashlib
import json
from decimal import Decimal
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
    D = Decimal
    assert D('.4')*D('.25') + D('.6')*D('.05') + D('.02') + D('.05') == D('.20')
    assert D('.4')*D('1.5') + D('.6')*D('.5') + D('.10') + D('.10') == D('1.10')
    followup=ROOT/'research/2026-09-followup'
    control=json.loads((followup/'baseline_summary.json').read_text(encoding='utf-8'))
    assert (control['cases'],control['gates'],control['strict_gate_success'],control['route_success'])==(300,1700,1700,300)
    audit=json.loads((followup/'gemini_evidence_audit.json').read_text(encoding='utf-8'))
    assert len(audit['gates'])==85
    assert audit['gate_counts']=={'all_failed_items_structurally_supported':69,'citation_defect':7,'includes_flattened_cross_object_excerpt':9}
    assert audit['failed_finding_item_counts']=={'structured_field_values_match':75,'flattened_cross_object_values_present':9}
    result = {"status": "pass", "evaluable_runs": 899, "evaluable_gates": 5094,
              "figures_and_tables": checked,
              "checks": ["original figure bytes and LF-normalized table text", "headline and component counts",
                         "rounded total cost", "explicit sensitivity arithmetic", "executed rules control", "85-gate structural audit"],
              "boundary": "Internal consistency and provenance only; no new inference or independent expert validation."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
