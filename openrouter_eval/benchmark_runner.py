from __future__ import annotations
import argparse, csv, json, os, re, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from evaluator import evaluate_route
from score_submission import score
from .agent_runner import AgentConfig, run_occurrence
from .model_catalog import compact, input_modalities, supports
from .openrouter_client import OpenRouterClient, Usage


def slug(s:str)->str:
    return re.sub(r"[^A-Za-z0-9._-]+","__",s)[:180]


def load_model_caps(client:OpenRouterClient)->dict[str,dict[str,Any]]:
    return {m.get("id"):compact(m) for m in client.list_models() if m.get("id")}


def iter_cases(dataset:Path):
    dataset=Path(dataset)
    if (dataset/"00_project_context.json").exists():
        return [dataset]
    return sorted([p for p in dataset.iterdir() if p.is_dir() and (p/"00_project_context.json").exists()])


def run_benchmark(dataset:Path, models:list[str], out_dir:Path, max_cases:int|None, max_cost_usd:float|None, max_turns:int, max_tool_calls:int, max_tokens:int, temperature:float, vision:str, reasoning_effort:str|None, handoff_mode:str="agent", resume:bool=True):
    client=OpenRouterClient()
    catalog=load_model_caps(client)
    cases=iter_cases(dataset)
    if max_cases: cases=cases[:max_cases]
    out_dir.mkdir(parents=True,exist_ok=True)
    selected_snapshot={m:catalog.get(m) for m in models}
    (out_dir/"model_catalog_snapshot.json").write_text(json.dumps(selected_snapshot,indent=2),encoding="utf-8")
    started=datetime.now(timezone.utc).isoformat()
    manifest={"started_at":started,"dataset":str(Path(dataset).resolve()),"models":models,"case_count":len(cases),"config":{"max_cost_usd":max_cost_usd,"max_turns":max_turns,"max_tool_calls":max_tool_calls,"max_tokens":max_tokens,"temperature":temperature,"vision":vision,"reasoning_effort":reasoning_effort,"handoff_mode":handoff_mode}}
    (out_dir/"benchmark_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    total_cost=0.0; summary=[]
    for model in models:
        caps=catalog.get(model)
        if not caps:
            summary.append({"model":model,"status":"SKIPPED_NOT_IN_CATALOG"}); continue
        if "tools" not in set(caps.get("supported_parameters") or []):
            summary.append({"model":model,"status":"SKIPPED_NO_TOOLS"}); continue
        use_vision = vision=="on" or (vision=="auto" and "image" in set(caps.get("input_modalities") or []))
        for case_dir in cases:
            case_public=json.loads((case_dir/"00_project_context.json").read_text(encoding="utf-8"))
            route=json.loads((case_dir/"01_route_manifest.json").read_text(encoding="utf-8"))
            oracle_by_oid={}
            if handoff_mode=="oracle":
                hidden=json.loads((case_dir/"99_hidden_ground_truth.json").read_text(encoding="utf-8"))
                oracle_by_oid={r["occurrence_id"]:r for r in hidden.get("reference_decisions",[])}
            model_dir=out_dir/slug(model)/case_dir.name; model_dir.mkdir(parents=True,exist_ok=True)
            score_path=model_dir/"score.json"
            if resume and score_path.exists():
                sc=json.loads(score_path.read_text(encoding="utf-8")); summary.append({"model":model,"case":case_dir.name,"route":route["route"]["key"],"status":"RESUMED","overall_score":sc.get("overall_score"),"cost":sc.get("openrouter_usage",{}).get("cost",0)}); continue
            results=[]; upstream=[]; run_usage=Usage(); occurrences=route.get("occurrences",[])
            case_error=None
            for occ in occurrences:
                if max_cost_usd is not None and total_cost >= max_cost_usd:
                    case_error=f"GLOBAL_COST_BUDGET_REACHED:{max_cost_usd}"; break
                cfg=AgentConfig(model=model,temperature=temperature,max_tokens=max_tokens,max_turns=max_turns,max_tool_calls=max_tool_calls,reasoning_effort=reasoning_effort,use_vision=use_vision)
                if handoff_mode=="none":
                    upstream_for_agent=[]
                elif handoff_mode=="oracle":
                    upstream_for_agent=upstream
                else:
                    upstream_for_agent=upstream
                try:
                    record=run_occurrence(client,case_dir,occ,caps,cfg,upstream_for_agent)
                except Exception as e:
                    case_error=f"{type(e).__name__}: {e}"; break
                result=record["result"]
                results.append(result)
                if handoff_mode=="oracle":
                    ref=oracle_by_oid.get(occ["occurrence_id"],{})
                    upstream.append({"occurrence_id":occ["occurrence_id"],"gate":occ["gate"],"phase":occ["phase"],"disposition":ref.get("disposition"),"finding_ids":[f["id"] for f in ref.get("findings",[])],"actions":[a["action"] for a in ref.get("required_actions",[])]})
                elif handoff_mode=="agent":
                    upstream.append({"occurrence_id":result["occurrence_id"],"gate":occ["gate"],"phase":occ["phase"],"disposition":result["disposition"],"finding_ids":result["finding_ids"],"actions":result["actions"]})
                u=Usage(**record["usage"]); run_usage.add(u); total_cost += u.cost
                (model_dir/f"{occ['position']:02d}_{occ['occurrence_id']}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
            submission={"case_id":case_public["case_id"],"model":model,"gate_results":results}
            (model_dir/"submission.json").write_text(json.dumps(submission,ensure_ascii=False,indent=2),encoding="utf-8")
            if case_error:
                sc={"status":"ERROR","error":case_error,"overall_score":None,"openrouter_usage":run_usage.as_dict()}
            else:
                sc=score(case_dir,submission); sc["status"]="OK"; sc["openrouter_usage"]=run_usage.as_dict(); sc["model"]=model; sc["vision_used"]=use_vision
            score_path.write_text(json.dumps(sc,ensure_ascii=False,indent=2),encoding="utf-8")
            summary.append({"model":model,"case":case_dir.name,"route":route["route"]["key"],"status":sc.get("status"),"overall_score":sc.get("overall_score"),"strict_gate_success_rate":sc.get("strict_gate_success_rate"),"route_complete_execution":sc.get("route_complete_execution"),"critical_miss_count":sc.get("critical_miss_count"),"false_approval_count":sc.get("false_approval_count"),"cost":run_usage.cost,"prompt_tokens":run_usage.prompt_tokens,"completion_tokens":run_usage.completion_tokens,"tool_calls":sum(json.loads(p.read_text()).get("tool_call_count",0) for p in model_dir.glob("[0-9][0-9]_*.json"))})
            print(json.dumps(summary[-1],ensure_ascii=False))
    (out_dir/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    fields=sorted({k for row in summary for k in row})
    with (out_dir/"summary.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(summary)
    return summary


def main():
    ap=argparse.ArgumentParser(description="Run DGF-Bench agents through OpenRouter")
    ap.add_argument("--dataset",type=Path,required=True,help="Case directory or directory containing multiple cases")
    ap.add_argument("--models",nargs="+",default=None,help="Exact OpenRouter model IDs")
    ap.add_argument("--model-file",type=Path,default=None,help="JSON file with {\"models\":[...]} ")
    ap.add_argument("--output-dir",type=Path,default=Path("openrouter_results")/datetime.now().strftime("%Y%m%d_%H%M%S"))
    ap.add_argument("--max-cases",type=int,default=None)
    ap.add_argument("--max-cost-usd",type=float,default=None)
    ap.add_argument("--max-turns",type=int,default=20)
    ap.add_argument("--max-tool-calls",type=int,default=40)
    ap.add_argument("--max-tokens",type=int,default=3000)
    ap.add_argument("--temperature",type=float,default=0.0)
    ap.add_argument("--vision",choices=["auto","on","off"],default="auto")
    ap.add_argument("--reasoning-effort",choices=["low","medium","high"],default=None)
    ap.add_argument("--handoff-mode",choices=["agent","oracle","none"],default="agent",help="agent=propagate model outputs; oracle=provide reference structured handoffs; none=no upstream handoff")
    ap.add_argument("--no-resume",action="store_true")
    ns=ap.parse_args()
    models=list(ns.models or [])
    if ns.model_file:
        payload=json.loads(ns.model_file.read_text(encoding="utf-8"))
        if isinstance(payload,list):
            models.extend([x.get("id") if isinstance(x,dict) else x for x in payload])
        else:
            models.extend(payload.get("models") or [])
    models=list(dict.fromkeys(models))
    if not models:
        ap.error("Provide --models ... or --model-file models.json")
    run_benchmark(ns.dataset,models,ns.output_dir,ns.max_cases,ns.max_cost_usd,ns.max_turns,ns.max_tool_calls,ns.max_tokens,ns.temperature,ns.vision,ns.reasoning_effort,ns.handoff_mode,resume=not ns.no_resume)

if __name__=="__main__": main()
