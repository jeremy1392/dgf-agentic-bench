from __future__ import annotations
import argparse, csv, json, statistics
from collections import defaultdict
from pathlib import Path


def aggregate(root:Path):
    root=Path(root); rows=[]; gate_rows=[]
    for score_path in root.glob("*/*/score.json"):
        sc=json.loads(score_path.read_text(encoding="utf-8"))
        if sc.get("status")!="OK": continue
        model=sc.get("model") or score_path.parents[1].name
        case=score_path.parent.name
        u=sc.get("openrouter_usage") or {}
        rows.append({"model":model,"case":case,"overall_score":sc.get("overall_score",0),"strict_gate_success_rate":sc.get("strict_gate_success_rate",0),"route_complete_execution":bool(sc.get("route_complete_execution",False)),"critical_miss_count":sc.get("critical_miss_count",0),"false_approval_count":sc.get("false_approval_count",0),"cost":u.get("cost",0),"tokens":u.get("total_tokens",0)})
        for o in sc.get("occurrences",[]):
            gate_rows.append({"model":model,"case":case,"gate":o.get("gate"),"score":o.get("score",0),"strict_success":bool(o.get("strict_success",False)),"decision":o.get("decision",0),"findings_f1":o.get("findings_f1",0),"actions_f1":o.get("actions_f1",0),"evidence_fidelity":o.get("evidence_fidelity",0),"authorization":o.get("authorization",0)})
    by_model=defaultdict(list)
    for r in rows: by_model[r["model"]].append(r)
    models=[]
    for m,rs in by_model.items():
        models.append({"model":m,"cases":len(rs),"mean_score":round(statistics.mean(x["overall_score"] for x in rs),4),"mean_gate_csr":round(statistics.mean(x["strict_gate_success_rate"] for x in rs),4),"route_complete_rate":round(statistics.mean(1.0 if x["route_complete_execution"] else 0.0 for x in rs),4),"critical_misses":sum(x["critical_miss_count"] for x in rs),"false_approvals":sum(x["false_approval_count"] for x in rs),"total_cost_usd":round(sum(x["cost"] for x in rs),6),"total_tokens":sum(x["tokens"] for x in rs)})
    by_gate=defaultdict(list)
    for r in gate_rows: by_gate[(r["model"],r["gate"])].append(r)
    gates=[]
    for (m,g),rs in by_gate.items():
        gates.append({"model":m,"gate":g,"n":len(rs),"csr":round(statistics.mean(1.0 if x["strict_success"] else 0.0 for x in rs),4),"mean_score":round(statistics.mean(x["score"] for x in rs),4),"decision_accuracy":round(statistics.mean(x["decision"] for x in rs),4),"findings_f1":round(statistics.mean(x["findings_f1"] for x in rs),4),"actions_f1":round(statistics.mean(x["actions_f1"] for x in rs),4),"evidence_fidelity":round(statistics.mean(x["evidence_fidelity"] for x in rs),4),"authorization_accuracy":round(statistics.mean(x["authorization"] for x in rs),4)})
    return {"models":sorted(models,key=lambda x:x["model"]),"gates":sorted(gates,key=lambda x:(x["model"],x["gate"]))}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--results",type=Path,required=True); ap.add_argument("--output",type=Path,default=None)
    ns=ap.parse_args(); out=aggregate(ns.results)
    target=ns.output or ns.results/"aggregate.json"; target.write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
