#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from azure_architecture import architecture_signature
from facts_engine import generate_canonical_case
from generate_dgfbench_v6 import build_case


def sha256(path: Path):
    h = hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def canonical_sha(case: dict[str, Any]) -> str:
    raw = json.dumps(case, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _assert_unique(label: str, values: list[Any]) -> dict[str, Any]:
    normalized = [json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, (dict, list, tuple)) else str(v) for v in values]
    seen = {}
    duplicates = []
    for i, v in enumerate(normalized):
        if v in seen:
            duplicates.append({"value": v, "first_index": seen[v], "duplicate_index": i})
        else:
            seen[v] = i
    return {
        "field": label,
        "count": len(values),
        "unique_count": len(seen),
        "ok": len(duplicates) == 0,
        "duplicates": duplicates,
    }


def build_uniqueness_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    checks = []
    checks.append(_assert_unique("case_id", [x["case_id"] for x in cases]))
    checks.append(_assert_unique("project_id", [x["project"]["project_id"] for x in cases]))
    checks.append(_assert_unique("project_name", [x["project"]["project_name"] for x in cases]))
    checks.append(_assert_unique("project_code", [x["project"]["project_code"] for x in cases]))
    checks.append(_assert_unique("architecture_id", [x["architecture"]["architecture_id"] for x in cases]))
    checks.append(_assert_unique("architecture_signature", [x["architecture_signature"] for x in cases]))
    checks.append(_assert_unique("resource_prefix", [x["architecture"]["resource_prefix"] for x in cases]))
    checks.append(_assert_unique("canonical_truth_sha256", [x["canonical_sha256"] for x in cases]))
    checks.append(_assert_unique("contract_version", [x["legal_contract_version"] for x in cases]))
    checks.append(_assert_unique("hld_version", [x["hld_version"] for x in cases]))
    checks.append(_assert_unique("lld_version", [x["lld_version"] for x in cases]))

    all_people = []
    all_vendors = []
    all_cidrs = []
    for x in cases:
        all_people += list(x["people"])
        all_vendors += list(x["vendors"])
        all_cidrs += list(x["cidrs"])
    checks.append(_assert_unique("all_named_people_across_dataset", all_people))
    checks.append(_assert_unique("all_vendor_names_across_dataset", all_vendors))
    checks.append(_assert_unique("all_private_cidrs_across_dataset", all_cidrs))

    return {
        "schema": "DGF-Bench-Uniqueness-v1",
        "case_count": len(cases),
        "all_checks_passed": all(c["ok"] for c in checks),
        "checks": checks,
        "note": (
            "Case-specific identities/configurations are unique. Controlled benchmark categories such as route, gate type, "
            "Azure product names, dispositions, booleans and policy states intentionally remain reusable; prohibiting those "
            "repetitions would make cross-case comparison impossible."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Create a balanced DGF-Bench dataset for OpenRouter experiments")
    ap.add_argument("--cases-per-route", type=int, default=20)
    ap.add_argument("--seed", type=int, default=9000)
    ap.add_argument("--difficulty", type=int, choices=range(1, 6), default=4)
    ap.add_argument("--include-full-lifecycle", action="store_true")
    ap.add_argument("--output-dir", type=Path, default=Path("openrouter_dataset"))
    ns = ap.parse_args(); ns.output_dir.mkdir(parents=True, exist_ok=True)

    routes = ["buy", "integrate", "build"] + (["full_lifecycle"] if ns.include_full_lifecycle else [])
    rows = []
    audit_cases = []
    counter = 0
    total = len(routes) * ns.cases_per_route
    used_architecture_signatures: set[str] = set()

    print(f"[dataset] creating {total} cases in {ns.output_dir}", flush=True)
    print("[dataset] uniqueness policy: unique project identities + unique structural architecture signatures", flush=True)

    for route in routes:
        print(f"[dataset] route={route} ({ns.cases_per_route} cases)", flush=True)
        for _ in range(ns.cases_per_route):
            seed = ns.seed + counter
            counter += 1

            # Deterministic rejection sampling. Project identity stays tied to the
            # requested seed; only the architecture RNG stream is advanced until
            # the structural signature is new within this dataset.
            architecture_attempt = 0
            while True:
                preview = generate_canonical_case(seed, route, ns.difficulty, architecture_attempt=architecture_attempt)
                sig = architecture_signature(preview["architecture_profile"])
                if sig not in used_architecture_signatures:
                    break
                architecture_attempt += 1
                if architecture_attempt > 10_000:
                    raise RuntimeError("Unable to generate a unique architecture signature after 10,000 attempts")

            used_architecture_signatures.add(sig)
            print(
                f"[dataset] [{counter}/{total}] {route} seed={seed} arch_attempt={architecture_attempt} "
                f"signature={sig[:10]} ...",
                end="", flush=True,
            )
            cdir = build_case(ns.output_dir, seed, ns.difficulty, route, architecture_attempt=architecture_attempt)
            print(f" done -> {cdir.name}", flush=True)

            ctx = json.loads((cdir / "00_project_context.json").read_text(encoding="utf-8"))
            hidden = json.loads((cdir / "99_hidden_ground_truth.json").read_text(encoding="utf-8"))["canonical_truth"]
            arch = hidden["architecture_profile"]
            project = hidden["project"]
            case_id = ctx["case_id"]

            rows.append({
                "case_dir": cdir.name,
                "case_id": case_id,
                "route": route,
                "seed": seed,
                "difficulty": ns.difficulty,
                "architecture_attempt": architecture_attempt,
                "architecture_signature": sig,
                "project_id": project["project_id"],
                "project_name": project["project_name"],
                "public_context_sha256": sha256(cdir / "00_project_context.json"),
            })

            audit_cases.append({
                "case_id": case_id,
                "project": project,
                "architecture": arch,
                "architecture_signature": sig,
                "canonical_sha256": canonical_sha(hidden),
                "people": [project["sponsor"], project["project_manager"], project["business_owner"], project["service_owner"], project["risk_owner"], hidden["general"]["benefits_owner"]],
                "vendors": [o["vendor"] for o in hidden["procurement"]["offers"]],
                "cidrs": list(hidden["architecture"]["private_cidrs"]),
                "legal_contract_version": hidden["legal"]["contract_version"],
                "hld_version": hidden["architecture"]["hld_version"],
                "lld_version": hidden["architecture"]["lld_version"],
            })

    report = build_uniqueness_report(audit_cases)
    (ns.output_dir / "dataset_uniqueness_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not report["all_checks_passed"]:
        failed = [c["field"] for c in report["checks"] if not c["ok"]]
        raise RuntimeError("Dataset uniqueness validation failed: " + ", ".join(failed))

    manifest = {
        "schema": "DGF-Bench-OpenRouter-Dataset-v2",
        "uniqueness_enforced": True,
        "architecture_signature_uniqueness": True,
        "uniqueness_report": "dataset_uniqueness_report.json",
        "cases": rows,
    }
    (ns.output_dir / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "output_dir": str(ns.output_dir),
        "case_count": len(rows),
        "routes": routes,
        "unique_architecture_signatures": len(used_architecture_signatures),
        "uniqueness_checks_passed": report["all_checks_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
