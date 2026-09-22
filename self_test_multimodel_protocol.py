#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import threading
import time
from pathlib import Path

from generate_dgfbench_v6 import build_case
from openrouter_eval.agent_runner import AgentConfig, run_occurrence
import openrouter_eval.benchmark_runner as br
from score_submission import score


class FakeClient:
    def __init__(self, mode="tool_submit"):
        self.mode = mode
        self.calls = 0

    def chat(self, body):
        self.calls += 1
        model = body["model"]
        if self.mode == "tool_submit":
            if self.calls == 1:
                return {
                    "model": model,
                    "provider": "fake",
                    "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12, "cost": 0.0},
                    "choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "content": "", "tool_calls": [{
                        "id": "c1", "type": "function", "function": {"name": "list_evidence", "arguments": json.dumps({"include_unavailable": True})}
                    }]}}],
                }
            return {
                "model": model,
                "provider": "fake",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost": 0.0},
                "choices": [{"finish_reason": "tool_calls", "message": {"role": "assistant", "content": "", "tool_calls": [{
                    "id": "c2", "type": "function", "function": {"name": "submit_gate_decision", "arguments": json.dumps({
                        "disposition": "GO", "finding_ids": [], "actions": [], "evidence_refs": [],
                        "authorization_required": False, "rationale": "No applicable findings.", "confidence": 0.8,
                    })}
                }]}}],
            }
        if "response_format" not in body:
            return {
                "model": model,
                "provider": "fake",
                "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13, "cost": 0.0},
                "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "I am still thinking."}}],
            }
        return {
            "model": model,
            "provider": "fake",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost": 0.0},
            "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps({
                "disposition": "REWORK", "finding_ids": [], "actions": [], "evidence_refs": [],
                "authorization_required": False, "rationale": "Forced structured finalization.", "confidence": 0.5,
            })}}],
        }


class FakeCatalogClient:
    def __init__(self, *args, **kwargs):
        self.api_key = "fake-key"

    def list_models(self):
        return [
            {"id": "fake/A", "supported_parameters": ["tools"], "architecture": {"input_modalities": ["text"]}},
            {"id": "fake/B", "supported_parameters": ["tools"], "architecture": {"input_modalities": ["text"]}},
            {"id": "fake/C", "supported_parameters": ["tools"], "architecture": {"input_modalities": ["text"]}},
        ]


def concurrency_test(root: Path) -> dict:
    dataset = root / "concurrency_dataset"
    dataset.mkdir(parents=True, exist_ok=True)
    # Three independent DGF cases are enough to create nine model×case jobs.
    for i in range(3):
        build_case(dataset, seed=98000 + i, difficulty=2, route_key="build")

    out = root / "concurrency_results"
    lock = threading.Lock()
    active = 0
    max_active = 0
    active_by_model: dict[str, int] = {}
    max_by_model: dict[str, int] = {}

    original_client = br.OpenRouterClient
    original_worker = br._run_case_model_job

    def fake_worker(**kwargs):
        nonlocal active, max_active
        job = kwargs["job"]
        budget = kwargs["budget"]
        with lock:
            active += 1
            max_active = max(max_active, active)
            active_by_model[job.model] = active_by_model.get(job.model, 0) + 1
            max_by_model[job.model] = max(max_by_model.get(job.model, 0), active_by_model[job.model])
        time.sleep(0.08)
        budget.charge(job.id, 0.01)
        with lock:
            active -= 1
            active_by_model[job.model] -= 1
        return {"model": job.model, "case": job.case_dir.name, "status": "OK", "cost": 0.01}

    try:
        br.OpenRouterClient = FakeCatalogClient
        br._run_case_model_job = fake_worker
        result = br.run_benchmark(
            dataset,
            ["fake/A", "fake/B", "fake/C"],
            out,
            max_cases=None,
            max_cost_usd=10.0,
            max_turns=2,
            max_tool_calls=2,
            max_tokens=256,
            temperature=0.0,
            vision="off",
            reasoning_effort=None,
            handoff_mode="agent",
            resume=False,
            schedule="round_robin",
            workers=4,
            max_workers_per_model=2,
            job_budget_reserve_usd=0.05,
        )
    finally:
        br.OpenRouterClient = original_client
        br._run_case_model_job = original_worker

    rows = [r for r in result if r.get("model")]
    assert len(rows) == 9, len(rows)
    assert max_active >= 3, max_active
    assert max_active <= 4, max_active
    assert all(v <= 2 for v in max_by_model.values()), max_by_model
    return {"jobs": len(rows), "max_parallel_jobs": max_active, "max_parallel_per_model": max_by_model}


def main():
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    case = build_case(root / "agent_case", seed=97601, difficulty=2, route_key="build")
    route = json.loads((case / "01_route_manifest.json").read_text(encoding="utf-8"))
    occ = route["occurrences"][0]
    caps = {"supported_parameters": ["tools", "tool_choice", "max_tokens", "response_format", "structured_outputs"], "input_modalities": ["text"]}

    rec = run_occurrence(FakeClient("tool_submit"), case, occ, caps, AgentConfig(model="fake/a", max_turns=5, max_tool_calls=5), [])
    assert rec["result"]["occurrence_id"] == occ["occurrence_id"]
    assert rec["finalization_mode"] == "submit_gate_decision"
    assert rec["resolved_models"] and rec["resolved_models"][-1] == "fake/a"

    rec2 = run_occurrence(FakeClient("structured"), case, occ, caps, AgentConfig(model="fake/b", max_turns=2, max_tool_calls=2), [])
    assert rec2["finalization_mode"] == "structured_output_fallback"
    assert rec2["result"]["disposition"] == "REWORK"

    schedule = br.build_job_schedule([Path("c1"), Path("c2"), Path("c3")], ["A", "B", "C"], "round_robin")
    order = [m for _, _, _, m in schedule]
    assert order == ["A", "B", "C", "B", "C", "A", "C", "A", "B"], order
    assert br.effective_per_model_limit(6, 3, 0) == 2

    # Budget reservations must be thread-safe and prevent new work from overcommitting a tight cap.
    budget = br.CostBudget(1.0, reserve_per_job=0.4)
    assert budget.reserve("a")
    assert budget.reserve("b")
    assert not budget.reserve("c")
    budget.charge("a", 0.1)
    budget.release("a")
    assert budget.reserve("c")

    # Incomplete submissions must not receive accidental authorization/evidence credit.
    sc = score(case, {"case_id": "x", "gate_results": []})
    assert sc["gate_attempt_rate"] == 0.0
    assert all(o["score"] == 0.0 and not o["attempted"] for o in sc["occurrences"])

    conc = concurrency_test(root)

    print(json.dumps({
        "status": "PASS",
        "typed_submission": rec["finalization_mode"],
        "structured_fallback": rec2["finalization_mode"],
        "round_robin_order": order,
        "budget_reservation": "PASS",
        "missing_gate_scoring": "zero_credit",
        "concurrency": conc,
    }, indent=2))


if __name__ == "__main__":
    main()
