#!/usr/bin/env python3
"""Checks that every number quoted in the manuscript follows from parameters.json.

    python3 anc/test_reproduce.py      (or: pytest anc/test_reproduce.py)
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reproduce as rp  # noqa: E402

P = rp.load_params()
R = rp.compute(P)
POP = {p["id"]: p for p in R["populations"]}


def close(a, b, tol=5e-3):
    return math.isclose(a, b, abs_tol=tol)


def test_regime_totals():
    for s, v in {"S0": 43.52, "S1": 85.32, "S2": 89.07, "S3": 168.92}.items():
        assert close(R["totals"][s]["total"], v), s
    assert close(R["weighted_q"], 0.2343, 5e-5) and close(R["weighted_phi"], 0.4686, 5e-5)


def test_partition_and_fragility():
    for p in R["populations"]:
        assert close(p["q"] * p["kappa"] + (1 - p["q"]) * p["sigma"], 1.0, 1e-12)
    assert close(POP["R4"]["eta_star"], 2.64) and close(POP["R2"]["eta_star"], 1.20)


def test_walkthrough_and_costs():
    r3 = POP["R3"]                       # IT / Enterprise Architecture walk-through
    assert close(r3["h0"], 36.0) and close(r3["sigma"] * r3["h0"], 28.10)
    assert close(r3["S0"]["total"], 7.86) and close(r3["S1"]["total"], 14.26)
    assert close(r3["S1"]["total"] - r3["S1"]["upkeep"], 13.26) and close(r3["S2"]["total"], 14.68)
    margins = {"R4": 2.64, "R3": 2.42, "R6": 1.81, "R1": 1.77, "R5": 1.77, "R7": 1.60, "R2": 1.20}
    for pid, v in margins.items():
        assert close(POP[pid]["eta_star"], v), pid
    assert close(R["cost"]["hbar_A"], 17.18)   # Operations / Tech Readiness cost example
    assert close(R["cost"]["c_H"], 2460.0) and close(R["cost"]["c_A"], 1978.0)
    assert close(R["cost"]["breakeven_loss_A"], 532.0)


def test_routes_and_provision():
    ma, npj = R["routes"]
    assert close(ma["rho"], 1.451, 5e-4) and close(npj["rho"], 0.360, 5e-4)
    assert close(ma["upkeep_per_visit"], 13.2) and close(npj["upkeep_per_visit"], 0.69)
    assert close(R["ma_at_high_volume"], 0.930, 5e-4)
    assert close(R["pooled"]["rho"], 0.41) and close(R["pooled"]["residual_fte"], 8.29)
    assert close(R["direct_hours_ma"], 21.62)
    assert [round(x["rho"], 3) for x in R["provision"]] == [1.451, 1.001, 0.956, 0.951]


def test_trajectory_and_floors():
    assert [round(a, 2) for a in R["allocation"]] == [51.25, 36.0, 52.75]
    totals = [c["total"] for c in R["configurations"]]
    assert close(totals[0], 140.0) and close(totals[1], 60.56) and close(totals[2], 16.345, 1e-2)
    assert close(totals[3], 5.0) and close(totals[4], 0.0)
    assert rp.r2(totals[2]) == "16.35"          # displayed rounded half up
    assert close(1 - 5 / 140, 0.9643, 5e-5)
    assert close(R["floors"][2][1], 19.0) and close(R["floors"][4][2], 15.0)


def test_milestones_and_workforce_hypothesis():
    assert [x["calendar_months"] for x in R["length"]] == [14, 21, 26]
    assert close(R["tail"][0]["z"], 2.301, 5e-4) and close(R["tail"][1]["z"], 3.602, 5e-4)
    assert [x["total"] for x in R["calendar"]] == [59, 73, 101]
    assert P["workforce_hypothesis"]["baseline_year"] == 2026
    assert P["workforce_hypothesis"]["deadline_year"] == 2033
    assert close(100 * P["workforce_hypothesis"]["remaining_fte_ratio_max"], 20)
    assert close(R["baseline_total"] * P["workforce_hypothesis"]["remaining_fte_ratio_max"], 28)
    assert P["tail"]["qualification_window_months"] == 76
    assert [x["total"] <= P["tail"]["qualification_window_months"] for x in R["calendar"]] == [True, True, False]
    assert close(R["tail"][0]["nu_max_for_qualification_window"], 13.47, 0.01)
    assert close(R["tail"][1]["nu_max_for_qualification_window"], 8.61, 0.01)
    assert [x["trials_zero_failures"] for x in R["tail"]] == [2995, 59914]


def test_route_registry():
    seq = [g for w in ("W1", "W2", "W3") for g in P["routes"][w]["sequence"]]
    assert [len(P["routes"][w]["sequence"]) for w in ("W1", "W2", "W3")] == [6, 6, 5] and len(seq) == 17
    alias = P["routes"]["gate_type_of_label"]
    assert len({alias.get(g, g) for g in seq}) == 8 and all(P["routes"][w]["sequence"][-1] == "General" for w in ("W1", "W2", "W3"))


def test_qualification_volume_and_renewal():
    assert close(1 - 0.05 ** (1 / 60), 0.0487, 5e-4)      # sixty failure-free visits bound the error rate below 4.9%
    a, b, r = 0.2, 0.01, 1.0
    for _ in range(2000):
        r = (1 - a) * r + b
    assert close(r, b / a, 1e-9)                          # R_inf = b / a: progress without closure when b > 0


def test_reliability_and_readiness():
    assert close(R["reliability"]["independent"], 0.8179, 5e-5)
    assert close(R["reliability"]["lower"], 0.80) and close(R["reliability"]["upper"], 0.99)
    assert close(R["readiness_example"], 0.398, 5e-4)


def test_strategic_model_comparative_statics():
    V, tau, xi, cu2, cg2 = 10.0, 1.0, 1.2, 2.0, 1.0

    def p1(s):
        z = math.exp(-(s - tau))
        return z / (1 + z) ** 2

    def solve(a):
        u = g = 0.3
        for _ in range(20000):
            lam = V * p1(xi + u + g)
            u, g = 0.5 * u + 0.5 * lam / cu2, 0.5 * g + 0.5 * lam / (cg2 + a)
        return u, g

    (u0, g0), (u1, g1) = solve(1.0), solve(1.5)
    assert xi + u0 + g0 > tau and g1 < g0 and u1 > u0 and (u1 + g1) < (u0 + g0)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("ok  ", t.__name__)
    print(f"{len(tests)} checks passed")
