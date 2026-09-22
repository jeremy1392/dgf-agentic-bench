#!/usr/bin/env python3
"""One-command DGF-Bench OpenRouter experiment runner.

Examples
--------
Pilot (safe default):
    python run_full_experiment.py \
      --api-key sk-or-v1-... \
      --models z-ai/glm-5.3 z-ai/glm-5.3-flashx

Paper run (150 cases: 50 Buy + 50 Integrate + 50 Build):
    python run_full_experiment.py \
      --api-key sk-or-v1-... \
      --models MODEL_A MODEL_B MODEL_C \
      --preset paper \
      --max-cost-usd 150

Safer key entry (not stored in shell history):
    python run_full_experiment.py --models MODEL_A MODEL_B --preset paper

The script never writes the API key to disk or result files.
"""
from __future__ import annotations

import argparse
import csv
import getpass
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

PRESETS = {
    "smoke": {"cases_per_route": 1, "difficulty": 3, "default_budget": 5.0},
    "pilot": {"cases_per_route": 5, "difficulty": 4, "default_budget": 25.0},
    "paper": {"cases_per_route": 50, "difficulty": 4, "default_budget": 150.0},
}


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], env: dict[str, str], cwd: Path = ROOT) -> str:
    """Run a child process while streaming stdout/stderr live.

    v7.2 used capture_output=True, which made long dataset/model steps look frozen
    on Windows. v7.6 forces unbuffered Python and mirrors every child line as it
    arrives while still returning the combined output for callers that need it.
    """
    cmd = list(cmd)
    if cmd and Path(cmd[0]).name.lower().startswith("python") and "-u" not in cmd[:2]:
        cmd.insert(1, "-u")
    child_env = dict(env)
    child_env["PYTHONUNBUFFERED"] = "1"
    print("\n$ " + " ".join(cmd), flush=True)
    proc = subprocess.Popen(
        cmd, cwd=cwd, env=child_env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        bufsize=1, universal_newlines=True,
    )
    lines=[]
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line)
        print(line.rstrip(), flush=True)
    rc=proc.wait()
    output="".join(lines)
    if rc != 0:
        die(f"Command failed with exit code {rc}: {' '.join(cmd)}")
    return output


def parse_models(raw: list[str]) -> list[str]:
    out: list[str] = []
    for item in raw:
        for part in item.split(","):
            part = part.strip()
            if part and part not in out:
                out.append(part)
    if not out:
        die("At least one OpenRouter model ID is required.")
    return out


def wilson(successes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def pct(x: float | None) -> str:
    if x is None:
        return "—"
    return f"{100.0 * x:.1f}%"


def validate_models(models: list[str], env: dict[str, str], out_dir: Path) -> dict[str, Any]:
    # Import only after the key is set in env / os.environ.
    sys.path.insert(0, str(ROOT))
    os.environ.update({k: v for k, v in env.items() if k.startswith("OPENROUTER_")})
    from openrouter_eval.openrouter_client import OpenRouterClient
    from openrouter_eval.model_catalog import compact

    client = OpenRouterClient()
    catalog = {m.get("id"): compact(m) for m in client.list_models() if m.get("id")}
    selected: dict[str, Any] = {}
    problems: list[str] = []
    for model in models:
        caps = catalog.get(model)
        if not caps:
            problems.append(f"{model}: not found in current OpenRouter catalog")
            continue
        params = set(caps.get("supported_parameters") or [])
        if "tools" not in params:
            problems.append(f"{model}: catalog does not advertise tool calling")
            continue
        selected[model] = caps
    (out_dir / "model_catalog_selected.json").write_text(
        json.dumps(selected, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if problems:
        die("Model validation failed:\n  - " + "\n  - ".join(problems))
    print("\nValidated OpenRouter models:")
    for model, caps in selected.items():
        modalities = ",".join(caps.get("input_modalities") or [])
        print(f"  OK  {model}  context={caps.get('context_length')}  input={modalities or 'text'}")
    return selected


def collect_paper_metrics(results_dir: Path, aggregate_payload: dict[str, Any]) -> tuple[list[dict], list[dict]]:
    model_acc: dict[str, dict[str, Any]] = {}
    gate_acc: dict[tuple[str, str], dict[str, Any]] = {}
    scoreable = {"OK", "AGENT_FAILURE"}

    for score_path in results_dir.glob("*/*/score.json"):
        sc = json.loads(score_path.read_text(encoding="utf-8"))
        status = sc.get("status")
        if status not in scoreable:
            continue
        model = sc.get("model") or sc.get("requested_model") or score_path.parents[1].name
        ma = model_acc.setdefault(model, {
            "model": model, "cases": 0, "completed_cases": 0, "agent_failures": 0, "route_successes": 0,
            "gate_total": 0, "gate_attempted": 0, "gate_strict_successes": 0,
            "critical_misses": 0, "false_approvals": 0, "total_cost_usd": 0.0,
            "total_tokens": 0, "truncated_responses": 0, "model_resolution_mismatches": 0,
        })
        ma["cases"] += 1
        ma["completed_cases"] += int(status == "OK")
        ma["agent_failures"] += int(status == "AGENT_FAILURE")
        ma["route_successes"] += int(bool(sc.get("route_complete_execution", False)))
        ma["critical_misses"] += int(sc.get("critical_miss_count", 0) or 0)
        ma["false_approvals"] += int(sc.get("false_approval_count", 0) or 0)
        ma["model_resolution_mismatches"] += int(bool(sc.get("model_resolution_mismatch", False)))
        usage = sc.get("openrouter_usage") or {}
        ma["total_cost_usd"] += float(usage.get("cost", 0) or 0)
        ma["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
        ma["truncated_responses"] += int(sc.get("truncated_response_count", 0) or 0)

        for occ in sc.get("occurrences", []):
            gate = str(occ.get("gate"))
            attempted = bool(occ.get("attempted", True))
            strict = int(bool(occ.get("strict_success", False)))
            ma["gate_total"] += 1
            ma["gate_attempted"] += int(attempted)
            ma["gate_strict_successes"] += strict
            ga = gate_acc.setdefault((model, gate), {
                "model": model, "gate": gate, "n": 0, "attempted": 0, "strict_successes": 0,
                "decision_sum": 0.0, "findings_sum": 0.0, "actions_sum": 0.0,
                "evidence_sum": 0.0, "authorization_sum": 0.0,
            })
            ga["n"] += 1
            ga["attempted"] += int(attempted)
            ga["strict_successes"] += strict
            if attempted:
                ga["decision_sum"] += float(occ.get("decision", 0) or 0)
                ga["findings_sum"] += float(occ.get("findings_f1", 0) or 0)
                ga["actions_sum"] += float(occ.get("actions_f1", 0) or 0)
                ga["evidence_sum"] += float(occ.get("evidence_fidelity", 0) or 0)
                ga["authorization_sum"] += float(occ.get("authorization", 0) or 0)

    agg_models = {r["model"]: r for r in aggregate_payload.get("models", [])}
    overall_rows: list[dict] = []
    for model in sorted(model_acc):
        a = model_acc[model]
        route_rate = a["route_successes"] / a["cases"] if a["cases"] else 0.0
        gate_csr = a["gate_strict_successes"] / a["gate_total"] if a["gate_total"] else 0.0
        attempt_rate = a["gate_attempted"] / a["gate_total"] if a["gate_total"] else 0.0
        rlo, rhi = wilson(a["route_successes"], a["cases"])
        glo, ghi = wilson(a["gate_strict_successes"], a["gate_total"])
        overall_rows.append({
            "model": model, "cases": a["cases"], "completed_cases": a["completed_cases"],
            "agent_failures": a["agent_failures"], "gate_occurrences": a["gate_total"],
            "gate_attempt_rate": round(attempt_rate, 6), "mean_score": agg_models.get(model, {}).get("mean_score"),
            "gate_csr": round(gate_csr, 6), "gate_csr_ci95_low": round(glo, 6), "gate_csr_ci95_high": round(ghi, 6),
            "route_complete_rate": round(route_rate, 6), "route_complete_ci95_low": round(rlo, 6),
            "route_complete_ci95_high": round(rhi, 6), "critical_misses": a["critical_misses"],
            "false_approvals": a["false_approvals"], "total_cost_usd": round(a["total_cost_usd"], 6),
            "total_tokens": a["total_tokens"], "cost_per_case_usd": round(a["total_cost_usd"] / a["cases"], 6) if a["cases"] else None,
            "truncated_responses": a["truncated_responses"], "model_resolution_mismatches": a["model_resolution_mismatches"],
        })

    gate_rows: list[dict] = []
    for key in sorted(gate_acc):
        a = gate_acc[key]; n=a["n"]; attempted=a["attempted"]
        lo, hi = wilson(a["strict_successes"], n)
        gate_rows.append({
            "model": a["model"], "gate": a["gate"], "n": n, "attempted": attempted,
            "attempt_rate": round(attempted/n, 6) if n else 0.0,
            "csr": round(a["strict_successes"] / n, 6) if n else 0.0,
            "csr_ci95_low": round(lo, 6), "csr_ci95_high": round(hi, 6),
            "decision_accuracy": round(a["decision_sum"] / attempted, 6) if attempted else 0.0,
            "findings_f1": round(a["findings_sum"] / attempted, 6) if attempted else 0.0,
            "actions_f1": round(a["actions_sum"] / attempted, 6) if attempted else 0.0,
            "evidence_fidelity": round(a["evidence_sum"] / attempted, 6) if attempted else 0.0,
            "authorization_accuracy": round(a["authorization_sum"] / attempted, 6) if attempted else 0.0,
        })
    return overall_rows, gate_rows

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def tex_escape(s: str) -> str:
    repl = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
    return "".join(repl.get(ch, ch) for ch in s)


def write_paper_outputs(report_dir: Path, overall: list[dict], gates: list[dict], config: dict[str, Any]) -> None:
    write_csv(report_dir / "paper_overall.csv", overall)
    write_csv(report_dir / "paper_by_gate.csv", gates)
    (report_dir / "paper_results.json").write_text(
        json.dumps({"config": config, "overall": overall, "gates": gates}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    md = [
        "# DGF-Bench experiment results\n",
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n",
        "## Overall results\n",
        "| Model | Cases | Agent failures | Gate attempt | Gate CSR (95% CI) | Route complete (95% CI) | Critical misses | False approvals | Truncated | Model mismatch | Cost (USD) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in overall:
        md.append(
            f"| `{r['model']}` | {r['cases']} | {r['agent_failures']} | {pct(r['gate_attempt_rate'])} | {pct(r['gate_csr'])} "
            f"[{pct(r['gate_csr_ci95_low'])}, {pct(r['gate_csr_ci95_high'])}] | "
            f"{pct(r['route_complete_rate'])} [{pct(r['route_complete_ci95_low'])}, {pct(r['route_complete_ci95_high'])}] | "
            f"{r['critical_misses']} | {r['false_approvals']} | {r['truncated_responses']} | {r['model_resolution_mismatches']} | {r['total_cost_usd']:.4f} |"
        )
    md += ["\n## Per-gate CSR\n", "| Model | Gate | Expected | Attempted | Attempt rate | CSR (95% CI) | Decision* | Findings F1* | Actions F1* | Evidence* | Auth* |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in gates:
        md.append(
            f"| `{r['model']}` | {r['gate']} | {r['n']} | {r['attempted']} | {pct(r['attempt_rate'])} | {pct(r['csr'])} "
            f"[{pct(r['csr_ci95_low'])}, {pct(r['csr_ci95_high'])}] | {pct(r['decision_accuracy'])} | "
            f"{r['findings_f1']:.3f} | {r['actions_f1']:.3f} | {r['evidence_fidelity']:.3f} | {pct(r['authorization_accuracy'])} |"
        )
    md += [
        "\n## Interpretation note\n",
        "These results measure performance on the declared synthetic DGF-Bench population. Agent-protocol failures are retained as failed execution rather than dropped; infrastructure/budget failures are excluded and reported separately. Per-gate component metrics marked * are conditional on the gate having been attempted. These results do not by themselves demonstrate autonomous real-world enterprise governance or prove the paper's universal long-horizon claim.\n",
    ]
    (report_dir / "PAPER_RESULTS.md").write_text("\n".join(md), encoding="utf-8")

    tex = [
        r"\begin{table}[t]",
        r"\centering",
        r"\caption{DGF-Bench main experimental results. Gate CSR is the strict complete-success rate across gate occurrences; Route Complete is the fraction of routes for which every required gate occurrence is a strict success. Wilson 95\% confidence intervals are shown.}",
        r"\label{tab:dgfbench-main-results}",
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Model & Cases & Gate CSR & Route Complete & Crit. Misses & False Approvals & Cost (USD) \\",
        r"\midrule",
    ]
    for r in overall:
        tex.append(
            f"{tex_escape(r['model'])} & {r['cases']} & "
            f"{100*r['gate_csr']:.1f}\\% & {100*r['route_complete_rate']:.1f}\\% & "
            f"{r['critical_misses']} & {r['false_approvals']} & {r['total_cost_usd']:.2f} \\\\" 
        )
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (report_dir / "paper_table_overall.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")


def git_commit() -> str | None:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="One-command DGF-Bench OpenRouter experiment")
    ap.add_argument("--api-key", default=None, help="OpenRouter key. If omitted, a hidden prompt is used. Passing on CLI may leave it in shell history.")
    ap.add_argument("--models", nargs="+", required=True, help="Exact OpenRouter model IDs; space- or comma-separated")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="pilot", help="smoke=3 cases, pilot=15 cases, paper=150 cases")
    ap.add_argument("--cases-per-route", type=int, default=None, help="Override preset case count per Buy/Integrate/Build route")
    ap.add_argument("--difficulty", type=int, choices=range(1, 6), default=None)
    ap.add_argument("--seed", type=int, default=12000)
    ap.add_argument("--max-cost-usd", type=float, default=None, help="Global budget cap. Defaults depend on preset.")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--vision", choices=["auto", "on", "off"], default="auto")
    ap.add_argument("--reasoning-effort", choices=["low", "medium", "high"], default=None)
    ap.add_argument("--handoff-mode", choices=["agent", "oracle", "none"], default="agent")
    ap.add_argument("--schedule", choices=["round_robin", "model_major"], default="round_robin", help="Queue ordering. round_robin remains the paper-safe default.")
    ap.add_argument("--workers", type=int, default=6, help="Concurrent model×DGF jobs. Gates inside one route remain sequential. Default: 6")
    ap.add_argument("--max-workers-per-model", type=int, default=0, help="Per-model concurrency. 0=auto ceil(workers/models). Default: 0")
    ap.add_argument("--job-budget-reserve-usd", type=float, default=0.50, help="Concurrent budget reservation per in-flight model×DGF job. Default: 0.50")
    ap.add_argument("--max-turns", type=int, default=20)
    ap.add_argument("--max-tool-calls", type=int, default=40)
    ap.add_argument("--max-output-tokens", "--max-tokens", dest="max_tokens", type=int, default=8192, help="Maximum output/reasoning tokens per model turn. Default: 8192. --max-tokens remains an alias.")
    ap.add_argument("--include-full-lifecycle", action="store_true")
    ap.add_argument("--output-dir", type=Path, default=None)
    ap.add_argument("--dataset", type=Path, default=None, help="Use an existing dataset instead of generating one")
    ap.add_argument("--no-resume", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Prepare/validate local configuration without making model calls")
    ap.add_argument("--regenerate-smoke", action="store_true", help="Regenerate the 3-case smoke dataset instead of using the bundled one")
    ns = ap.parse_args()
    if ns.workers < 1:
        die("--workers must be >= 1")
    if ns.max_workers_per_model < 0:
        die("--max-workers-per-model must be >= 0")
    if ns.job_budget_reserve_usd < 0:
        die("--job-budget-reserve-usd must be >= 0")

    models = parse_models(ns.models)
    preset = PRESETS[ns.preset]
    cases_per_route = ns.cases_per_route if ns.cases_per_route is not None else preset["cases_per_route"]
    difficulty = ns.difficulty if ns.difficulty is not None else preset["difficulty"]
    budget = ns.max_cost_usd if ns.max_cost_usd is not None else preset["default_budget"]

    key = ns.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key and not ns.dry_run:
        key = getpass.getpass("OpenRouter API key (hidden): ").strip()
    if not key and not ns.dry_run:
        die("No OpenRouter API key provided.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_root = ns.output_dir or (ROOT / "experiments" / f"run_{stamp}")
    exp_root = exp_root.resolve()
    bundled_smoke = ROOT / "openrouter_smoke_dataset"
    if ns.dataset:
        dataset_dir = ns.dataset.resolve()
    elif ns.preset == "smoke" and bundled_smoke.exists() and not ns.regenerate_smoke:
        dataset_dir = bundled_smoke.resolve()
    else:
        dataset_dir = exp_root / "dataset"
    results_dir = exp_root / "results"
    report_dir = exp_root / "paper_outputs"
    exp_root.mkdir(parents=True, exist_ok=True); report_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if key:
        env["OPENROUTER_API_KEY"] = key
        os.environ["OPENROUTER_API_KEY"] = key
    env.setdefault("OPENROUTER_X_TITLE", "DGF-Bench")

    config: dict[str, Any] = {
        "schema": "DGF-Bench-OneClick-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "preset": ns.preset,
        "models": models,
        "cases_per_route": cases_per_route,
        "difficulty": difficulty,
        "seed": ns.seed,
        "max_cost_usd": budget,
        "temperature": ns.temperature,
        "vision": ns.vision,
        "reasoning_effort": ns.reasoning_effort,
        "handoff_mode": ns.handoff_mode,
        "schedule": ns.schedule,
        "workers": ns.workers,
        "max_workers_per_model": ns.max_workers_per_model,
        "job_budget_reserve_usd": ns.job_budget_reserve_usd,
        "max_turns": ns.max_turns,
        "max_tool_calls": ns.max_tool_calls,
        "max_output_tokens": ns.max_tokens,
        "include_full_lifecycle": ns.include_full_lifecycle,
        "git_commit": git_commit(),
        "python": sys.version,
        "api_key_stored": False,
    }
    (exp_root / "experiment_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print("=" * 78)
    print("DGF-BENCH ONE-COMMAND EXPERIMENT")
    print("=" * 78)
    print(f"Models: {', '.join(models)}")
    print(f"Preset: {ns.preset} | cases/route={cases_per_route} | difficulty={difficulty}")
    print(f"Handoff: {ns.handoff_mode} | vision={ns.vision} | temperature={ns.temperature}")
    auto_per_model = ns.max_workers_per_model if ns.max_workers_per_model > 0 else max(1, math.ceil(ns.workers / max(1, len(models))))
    print(f"Model schedule: {ns.schedule}")
    print(f"Concurrency: workers={ns.workers} | per-model={auto_per_model} | gates within each DGF remain sequential")
    print(f"Concurrent budget reserve/job: ${ns.job_budget_reserve_usd:.2f}")
    print(f"Max output tokens/turn: {ns.max_tokens}")
    print(f"Global cost cap: ${budget:.2f}")
    print(f"Experiment directory: {exp_root}")
    print("API key will NOT be written to disk.")

    if ns.dry_run:
        print("DRY RUN: no OpenRouter calls made.")
        return

    # Validate models before generating / spending on benchmark calls.
    print("\n[1/5] Validating OpenRouter models...", flush=True)
    validate_models(models, env, exp_root)

    if ns.preset == "smoke" and ns.dataset is None and dataset_dir == bundled_smoke.resolve() and not ns.regenerate_smoke:
        print(f"\n[2/5] Using bundled smoke dataset: {dataset_dir}", flush=True)
    elif ns.dataset is None:
        print(f"\n[2/5] Generating balanced dataset in: {dataset_dir}", flush=True)
        cmd = [sys.executable, "prepare_openrouter_experiment.py",
               "--cases-per-route", str(cases_per_route),
               "--seed", str(ns.seed), "--difficulty", str(difficulty),
               "--output-dir", str(dataset_dir)]
        if ns.include_full_lifecycle:
            cmd.append("--include-full-lifecycle")
        run(cmd, env)
    elif not dataset_dir.exists():
        die(f"Dataset does not exist: {dataset_dir}")

    manifest = dataset_dir / "dataset_manifest.json"
    if manifest.exists():
        config["dataset_manifest_sha256"] = sha256_file(manifest)
        config["dataset_path"] = str(dataset_dir)
        (exp_root / "experiment_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print("\n[3/5] Running agent benchmark through OpenRouter...", flush=True)
    print("      This is the paid stage. Progress will be shown per model/case/gate.", flush=True)
    cmd = [sys.executable, "run_openrouter_benchmark.py",
           "--dataset", str(dataset_dir), "--models", *models,
           "--output-dir", str(results_dir),
           "--max-cost-usd", str(budget),
           "--max-turns", str(ns.max_turns),
           "--max-tool-calls", str(ns.max_tool_calls),
           "--max-tokens", str(ns.max_tokens),
           "--temperature", str(ns.temperature),
           "--vision", ns.vision,
           "--handoff-mode", ns.handoff_mode,
           "--schedule", ns.schedule,
           "--workers", str(ns.workers),
           "--max-workers-per-model", str(ns.max_workers_per_model),
           "--job-budget-reserve-usd", str(ns.job_budget_reserve_usd)]
    if ns.reasoning_effort:
        cmd += ["--reasoning-effort", ns.reasoning_effort]
    if ns.no_resume:
        cmd.append("--no-resume")
    run(cmd, env)

    print("\n[4/5] Aggregating benchmark results...", flush=True)
    aggregate_path = report_dir / "aggregate.json"
    run([sys.executable, "aggregate_openrouter_results.py", "--results", str(results_dir), "--output", str(aggregate_path)], env)
    aggregate_payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
    print("\n[5/5] Creating paper-ready CSV / JSON / Markdown / LaTeX outputs...", flush=True)
    overall, gates = collect_paper_metrics(results_dir, aggregate_payload)
    write_paper_outputs(report_dir, overall, gates, config)

    print("\n" + "=" * 78)
    print("FINAL RESULTS")
    print("=" * 78)
    if not overall:
        print("No successful model/case results were produced. Check result score.json files.")
    else:
        for r in overall:
            print(
                f"{r['model']}: Gate CSR={pct(r['gate_csr'])} "
                f"Attempted={pct(r['gate_attempt_rate'])} "
                f"Route Complete={pct(r['route_complete_rate'])} "
                f"Agent Failures={r['agent_failures']} "
                f"Critical Misses={r['critical_misses']} "
                f"False Approvals={r['false_approvals']} "
                f"Truncated={r['truncated_responses']} "
                f"ModelMismatch={r['model_resolution_mismatches']} "
                f"Cost=${r['total_cost_usd']:.4f}"
            )
    print("\nPaper-ready outputs:")
    for name in ["PAPER_RESULTS.md", "paper_overall.csv", "paper_by_gate.csv", "paper_results.json", "paper_table_overall.tex", "aggregate.json"]:
        print(f"  {report_dir / name}")
    print(f"\nRaw model traces and scores: {results_dir}")
    print(f"Experiment config: {exp_root / 'experiment_config.json'}")


if __name__ == "__main__":
    main()
