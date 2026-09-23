#!/usr/bin/env python3
"""Reproduce every synthetic number, table fragment and figure in the paper.

    python3 anc/reproduce.py

Input : anc/parameters.json (single source of all numerical assumptions)
Output: anc/results/summary.json, generated/*.tex (table rows), figures/*.pdf

Deterministic arithmetic on stated assumptions. Nothing is estimated from data.
"""
from __future__ import annotations

import json
import math
import pathlib
from decimal import Decimal, ROUND_HALF_UP

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS, GENERATED, FIGURES = HERE / "results", ROOT / "generated", ROOT / "figures"
REGIMES = ("S0", "S1", "S2", "S3")


def r2(x: float) -> str:
    """Two decimals, rounded half up (16.345 -> 16.35)."""
    return str(Decimal(str(round(x, 9))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def load_params() -> dict:
    with open(HERE / "parameters.json", encoding="utf-8") as fh:
        return json.load(fh)


def partition(q: float, kappa: float) -> dict:
    phi = q * kappa
    if not 0 < q < 1 or phi > 1 + 1e-12:
        raise ValueError("incoherent baseline partition")
    return {"phi": phi, "sigma": (1 - phi) / (1 - q)}


def rho(*, q, kappa, eta, m, r, bA, bH=0.0) -> float:
    return (q * kappa * eta + (1 - q) * m + r + bA) / (1 + bH)


def k_star(q, *, m, r, bA, bH=0.0):
    return m + (1 + bH - m - r - bA) / q


def compute(P: dict) -> dict:
    K, V, kappa = P["useful_hours_per_fte"], P["visits_per_population"], P["kappa"]
    frag = P["regimes"][P["fragility_regime"]]
    pops = []
    for p in P["populations"]:
        n0, q = p["people"], p["q"]
        h0 = K * n0 / V
        part = partition(q, kappa)
        row = {**p, "h0": h0, "kappa": kappa, **part, "w3": n0 - p["w1"] - p["w2"]}
        for s in REGIMES:
            g = P["regimes"][s]
            comp = {"exception": V * q * kappa * g["eta"] * h0 / K,
                    "review": V * (1 - q) * g["m"] * h0 / K,
                    "rework": V * g["hW"] / K, "upkeep": g["BA"] / K}
            comp["total"] = sum(comp.values())
            row[s] = comp
            row[f"mu_{s}"] = g["m"] / part["sigma"]
        row["eta_star"] = (1 - (1 - q) * frag["m"] - frag["hW"] / h0
                           - frag["BA"] / (V * h0)) / part["phi"]
        pops.append(row)
    totals = {s: {c: sum(p[s][c] for p in pops)
                  for c in ("exception", "review", "rework", "upkeep", "total")} for s in REGIMES}
    base = sum(p["people"] for p in pops)

    ce = P["cost_example"]
    p4 = next(p for p in pops if p["id"] == ce["population"])
    g = P["regimes"][ce["regime"]]
    hbar = p4["q"] * kappa * g["eta"] * p4["h0"] + (1 - p4["q"]) * g["m"] * p4["h0"] + g["hW"]
    cH = ce["wH"] * p4["h0"] + ce["aH"] + ce["FH"] / V + ce["lH"]
    cA0 = ce["wA"] * hbar + ce["aA"] + (ce["wA"] * g["BA"] + ce["FA"]) / V
    cost = {"hbar_A": hbar, "c_H": cH, "c_A": cA0 + ce["lA"], "breakeven_loss_A": cH - cA0}

    ri = P["route_illustration"]
    h0, m, r = ri["h0"], ri["m"], ri["hW"] / ri["h0"]
    upkeep = ri["shared_upkeep_hours"] + ri["local_upkeep_hours"]
    routes = []
    for rt in ri["routes"]:
        part = partition(rt["q"], rt["kappa"])
        bA = upkeep / (rt["visits"] * h0)
        ratio = rho(q=rt["q"], kappa=rt["kappa"], eta=rt["eta"], m=m, r=r, bA=bA)
        fte = rt["visits"] * h0 / K
        routes.append({**rt, **part, "k": rt["kappa"] * rt["eta"], "r": r, "bA": bA, "rho": ratio,
                       "baseline_fte": fte, "residual_fte": ratio * fte,
                       "upkeep_per_visit": upkeep / rt["visits"]})
    ma, npj = routes
    pooled_base = sum(x["baseline_fte"] for x in routes)
    pooled_res = sum(x["residual_fte"] for x in routes)
    ma_scaled = rho(q=ma["q"], kappa=ma["kappa"], eta=ma["eta"], m=m, r=r, bA=npj["bA"])
    direct = ma["q"] * ma["kappa"] * ma["eta"] * h0 + (1 - ma["q"]) * m * h0 + ri["hW"]
    provision = []
    for n in ri["customers"]:
        hours = ri["shared_upkeep_hours"] / n + ri["local_upkeep_hours"]
        per_visit = hours / ma["visits"]
        provision.append({"customers": n, "support_hours": hours, "per_visit": per_visit,
                          "total_per_visit": direct + per_visit,
                          "rho": (direct + per_visit) / h0})

    tr = P["trajectory"]
    alloc = [sum(p[k] for p in pops) for k in ("w1", "w2", "w3")]
    configs = []
    for c in tr["configurations"]:
        parts = [a * rem for a, rem in zip(alloc, c["remaining"])]
        configs.append({"name": c["name"], "routes": parts, "support": c["support"],
                        "total": sum(parts) + c["support"]})
    floors = [[base * (1 - a) + f for f in tr["floors"]] for a in tr["displaced"]]

    ms, tl = P["milestones"], P["tail"]
    length = []
    for d in ms["targets"]:
        dbl = math.log2(d / ms["anchor_hours_80"])
        length.append({"hours": d, "doublings": dbl, "months": ms["doubling_months"] * dbl,
                       "calendar_months": math.ceil(ms["doubling_months"] * dbl - 1e-9)})
    tail = []
    for e in tl["targets"]:
        z = math.log10(tl["e0"] / e)
        tail.append({"target": e, "z": z, "months": [nu * z for nu in tl["nu"]],
                     "cost": [c ** z for c in tl["c"]],
                     "trials_zero_failures": math.ceil(math.log(0.05) / math.log(1 - e)),
                     "nu_max_for_cohort": (tl["cohort_months"] - length[1]["calendar_months"]
                                           - tl["evaluation_months"] - tl["institution_months"]) / z})
    calendar = [{"nu": nu, "total": length[1]["calendar_months"] + math.ceil(nu * tail[0]["z"])
                 + tl["evaluation_months"] + tl["institution_months"]} for nu in tl["nu"]]

    rel = P["reliability_example"]
    n, pc = rel["gates"], rel["p_correct"]
    return {"populations": pops, "totals": totals, "baseline_total": base,
            "weighted_q": sum(p["people"] * p["q"] for p in pops) / base,
            "weighted_phi": sum(p["people"] * p["phi"] for p in pops) / base,
            "cost": cost, "routes": routes, "ma_at_high_volume": ma_scaled,
            "pooled": {"baseline_fte": pooled_base, "residual_fte": pooled_res,
                       "rho": pooled_res / pooled_base},
            "direct_hours_ma": direct, "provision": provision, "allocation": alloc,
            "configurations": configs, "floors": floors, "length": length, "tail": tail,
            "calendar": calendar,
            "reliability": {"independent": pc ** n, "lower": max(0.0, 1 - n * (1 - pc)), "upper": pc},
            "readiness_example": math.prod(P["readiness_example"]) ** (1 / len(P["readiness_example"]))}


def write_outputs(P: dict, R: dict) -> None:
    for d in (RESULTS, GENERATED, FIGURES):
        d.mkdir(exist_ok=True)
    pops = R["populations"]

    def dump(name, lines):
        (GENERATED / name).write_text("\n".join(lines) + "\n", encoding="utf-8")

    rows = [f"{p['id']} & {p['people']} & {p['h0']:.2f} & {p['q']:.2f} & "
            + " & ".join(f"{p[s]['total']:.2f}" for s in REGIMES) + r" \\" for p in pops]
    rows += [r"\midrule", r"\textbf{Total} & \textbf{140} & -- & -- & "
             + " & ".join(r"\textbf{%.2f}" % R["totals"][s]["total"] for s in REGIMES) + r" \\"]
    dump("table_workload_rows.tex", rows)
    dump("table_partition_rows.tex",
         [f"{p['id']} & {p['q']:.2f} & {p['kappa']:.2f} & {p['sigma']:.4f} & {p['phi']:.2f} & "
          f"{p['mu_S0']:.4f} & {p['mu_S3']:.4f} & {p['eta_star']:.2f}" + r" \\" for p in pops])
    rows = [f"{x['label'].replace('&', chr(92) + '&')} & {x['visits']} & {x['q']:.2f} & "
            f"{x['kappa']:.1f} & {x['phi']:.2f} & {x['eta']:.1f} & {x['upkeep_per_visit']:.2f} & "
            f"{x['bA']:.3f} & {x['rho']:.3f}" + r" \\" for x in R["routes"]]
    dump("table_routes_rows.tex", rows)
    dump("table_provision_rows.tex",
         [f"{x['customers']:,} & {x['support_hours']:.2f} & {x['per_visit']:.3f} & "
          f"{x['total_per_visit']:.3f} & {x['rho']:.3f}" + r" \\" for x in R["provision"]])
    rows = [f"{p['id']} & {p['name'].replace('&', chr(92) + '&')} & {p['people']} & {p['w1']:.2f} & "
            f"{p['w2']:.2f} & {p['w3']:.2f}" + r" \\" for p in pops]
    rows += [r"\midrule", r" & \textbf{Total} & \textbf{140} & "
             + " & ".join(r"\textbf{%.2f}" % a for a in R["allocation"]) + r" \\"]
    dump("table_allocation_rows.tex", rows)
    dump("table_trajectory_rows.tex",
         [f"{c['name']} & " + " & ".join(r2(v) for v in c["routes"])
          + f" & {r2(c['support'])} & \\textbf{{{r2(c['total'])}}}" + r" \\" for c in R["configurations"]])
    dump("table_floor_rows.tex",
         [f"{int(a * 100)}\\% & " + " & ".join(f"{v:.2f}" for v in row) + r" \\"
          for a, row in zip(P["trajectory"]["displaced"], R["floors"])])

    summary = {
        "totals_fte": {s: round(R["totals"][s]["total"], 2) for s in REGIMES},
        "weighted_exception_share": round(R["weighted_q"], 4),
        "weighted_baseline_labor_in_residual": round(R["weighted_phi"], 4),
        "eta_star_S2": {p["id"]: round(p["eta_star"], 4) for p in pops},
        "cost_example": {k: round(v, 3) for k, v in R["cost"].items()},
        "routes": {x["id"]: round(x["rho"], 4) for x in R["routes"]},
        "ma_at_high_volume": round(R["ma_at_high_volume"], 4),
        "pooled": {k: round(v, 4) for k, v in R["pooled"].items()},
        "provision": [{k: round(v, 4) for k, v in x.items()} for x in R["provision"]],
        "configurations": {c["name"]: round(c["total"], 2) for c in R["configurations"]},
        "length_milestones": R["length"], "tail": R["tail"], "calendar": R["calendar"],
        "reliability": {k: round(v, 4) for k, v in R["reliability"].items()},
        "readiness_example": round(R["readiness_example"], 4)}
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def figures(P: dict, R: dict) -> None:
    ri = P["route_illustration"]
    ma, npj = R["routes"]
    q = np.linspace(0.02, 0.66, 600)
    k_lo = k_star(q, m=ri["m"], r=ma["r"], bA=ma["bA"])
    k_hi = k_star(q, m=ri["m"], r=npj["r"], bA=npj["bA"])
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.fill_between(q, 0, np.clip(k_lo, 0, 5), color="#dbe9f6", lw=0)
    ax.fill_between(q, np.clip(k_lo, 0, 5), np.clip(k_hi, 0, 5), color="#fde0c5", lw=0)
    ax.fill_between(q, np.clip(k_hi, 0, 5), 5, color="#d9ead3", lw=0)
    l1, = ax.plot(q, k_lo, color="#1f77b4", lw=1.8, ls="--")
    l2, = ax.plot(q, k_hi, color="#ff7f0e", lw=1.8)
    ax.scatter([npj["q"]], [npj["k"]], s=55, color="#ff7f0e", edgecolor="k", lw=0.5, zorder=5)
    ax.scatter([ma["q"]], [ma["k"]], s=60, color="#1f77b4", marker="^", edgecolor="k", lw=0.5, zorder=5)
    ax.annotate(f"Build route: {npj['rho']:.2f} x baseline", (npj["q"], npj["k"]),
                xytext=(0.03, 2.25), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate(f"Integrate route: {ma['rho']:.2f} x baseline", (ma["q"], ma["k"]),
                xytext=(0.40, 0.45), fontsize=8.5, arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.text(0.02, 0.15, "Lower workload on both routes", fontsize=8.5)
    ax.text(0.30, 1.85, "Only the 95-visit route\nreduces workload", fontsize=8.5)
    ax.text(0.30, 4.6, "Higher workload on both routes", fontsize=8.5)
    ax.set_xlim(0, 0.65); ax.set_ylim(0, 5)
    ax.set_xlabel("Share of review visits escalated to humans")
    ax.set_ylabel("Human effort per exception after deployment\ndivided by the baseline average for all visits")
    fig.legend([l1, l2], ["Integrate route equality: 5 visits/month", "Build route equality: 95 visits/month"],
               loc="upper left", frameon=False, fontsize=8.5, bbox_to_anchor=(0.14, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(FIGURES / "fig_frontiers.pdf"); plt.close(fig)

    comps = [("exception", "Exception handling", "#1f77b4"), ("review", "Standard-path review", "#ff7f0e"),
             ("rework", "Additional rework", "#2ca02c"), ("upkeep", "Fixed human upkeep", "#d62728")]
    fig, ax = plt.subplots(figsize=(6.6, 3.6)); bottom = np.zeros(4); hs, ns = [], []
    for key, name, col in comps:
        v = np.array([R["totals"][s][key] for s in REGIMES])
        hs.append(ax.bar(REGIMES, v, bottom=bottom, color=col, width=0.8)); ns.append(name); bottom += v
    for i, s in enumerate(REGIMES):
        ax.text(i, bottom[i] + 2.5, f"{R['totals'][s]['total']:.2f}", ha="center", fontsize=9)
    b = ax.axhline(140, ls="--", lw=1.2, color="0.35")
    ax.set_ylim(0, 205); ax.set_ylabel("Workload-equivalent FTE (120 hours/month)")
    ax.set_xlabel("Fixed coverage and baseline selection; different operating burdens")
    ax.legend([b] + hs, ["Manual benchmark: 140"] + ns, ncol=2, fontsize=8, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(FIGURES / "fig_components.pdf"); plt.close(fig)

    names = [c["name"].replace(" ", "\n", 1) for c in R["configurations"]]
    cols = ["#f2c744", "#4fc3e8", "#36bfa8", "#8a8f98"]
    labels = ["Buy (W1)", "Integrate (W2)", "Build (W3)", "Human support"]
    fig, ax = plt.subplots(figsize=(6.6, 3.4)); bottom = np.zeros(len(names))
    for j in range(4):
        v = np.array([(c["routes"] + [c["support"]])[j] for c in R["configurations"]])
        ax.bar(names, v, bottom=bottom, color=cols[j], label=labels[j], width=0.7); bottom += v
    for i, c in enumerate(R["configurations"]):
        ax.text(i, c["total"] + 3, r2(c["total"]), ha="center", fontsize=9)
    ax.axhline(140, ls="--", lw=1.0, color="0.35"); ax.set_ylim(0, 170)
    ax.set_ylabel("Required human workload (FTE-equivalent)")
    ax.legend(ncol=2, fontsize=8, frameon=False, loc="upper right"); ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout(); fig.savefig(FIGURES / "fig_trajectory.pdf"); plt.close(fig)

    ms = P["milestones"]; t = np.linspace(0, 42, 200)
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    for d, ls in zip(ms["alternative_doublings"], ["-", "--", ":"]):
        ax.plot(t, ms["anchor_hours_80"] * 2 ** (t / d), ls=ls, lw=1.8, label=f"Chosen doubling interval: {d} months")
    for h in ms["targets"]:
        ax.axhline(h, color="0.6", lw=0.7); ax.text(42.5, h, f"{h} h", va="center", fontsize=8)
    ax.set_yscale("log", base=2); ax.set_yticks([3, 6, 12, 24, 48, 96, 192])
    ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlim(0, 42); ax.set_ylim(3, 192); ax.set_xticks(range(0, 43, 7))
    ax.set_xlabel("Months after 8 May 2026 (synthetic extrapolation)")
    ax.set_ylabel("Human-task hours at the\nchosen 80% criterion")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(FIGURES / "fig_doublings.pdf"); plt.close(fig)


def main() -> dict:
    P = load_params(); R = compute(P); write_outputs(P, R); figures(P, R); return R


if __name__ == "__main__":
    R = main()
    print("S0-S3:", [round(R["totals"][s]["total"], 2) for s in REGIMES])
    print("routes:", [(x["id"], round(x["rho"], 3)) for x in R["routes"]],
          "Integrate route at 95 visits:", round(R["ma_at_high_volume"], 3), "pooled:", round(R["pooled"]["rho"], 3))
    print("provision:", [round(x["rho"], 3) for x in R["provision"]])
    print("trajectory:", [round(c["total"], 2) for c in R["configurations"]])
    P = load_params()
    gates = [g for w in ("W1", "W2", "W3") for g in P["routes"][w]["sequence"]]
    alias = P["routes"].get("gate_type_of_label", {})
    types = [alias.get(g, g) for g in gates]
    print("gate occurrences:", len(gates), {g: types.count(g) for g in sorted(set(types))})
    print("length months:", [x["calendar_months"] for x in R["length"]],
          "calendar:", [x["total"] for x in R["calendar"]])
    print("nu max for a seven-year cohort:", [round(x["nu_max_for_cohort"], 1) for x in R["tail"]],
          "zero-failure trials:", [x["trials_zero_failures"] for x in R["tail"]])
