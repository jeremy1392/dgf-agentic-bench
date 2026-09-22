#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, uuid
from pathlib import Path
from facts_engine import generate_canonical_case
from azure_architecture import architecture_signature
from routes import ROUTES, build_occurrences, GATE_LABELS, PHASE_ORDER
from evaluator import evaluate_route
from evidence_graph import build_evidence_graph, public_graph
from document_factory import emit_all, GATE_OBJECTIVES
from phase_model import phase_visibility

TOOL_SCHEMAS={
    "get_cmdb_record":{"args":{"application":"string?"},"returns":"authoritative CMDB record"},
    "get_azure_resource":{"args":{"name":"string?"},"returns":"authoritative synthetic Azure resource inventory"},
    "get_iam_assignments":{"args":{},"returns":"authoritative IAM assignments"},
    "get_contract_version":{"args":{},"returns":"authoritative contract metadata"},
    "request_vendor_evidence":{"args":{"vendor":"string?","evidence_type":"string?"},"returns":"supplier evidence response"},
    "get_backup_job":{"args":{},"returns":"authoritative backup state"},
    "get_restore_test":{"args":{},"returns":"authoritative restore-test state"},
    "get_failover_test":{"args":{},"returns":"authoritative DR failover state"},
    "get_siem_connector_status":{"args":{},"returns":"authoritative SIEM connector state"},
    "get_vulnerability_findings":{"args":{},"returns":"authoritative vulnerability state"},
    "get_regulatory_applicability":{"args":{},"returns":"authoritative regulatory applicability facts"},
    "request_evidence":{"args":{"evidence_id":"string","reason":"string?"},"returns":"evidence request acknowledgement"},
    "create_risk_card":{"args":{"finding_id":"string","risk_owner":"string","rationale":"string","expiry_date":"string?"},"returns":"risk card draft"},
    "return_to_design":{"args":{"finding_ids":"array[string]","reason":"string?"},"returns":"workflow action"},
    "approve_with_conditions":{"args":{"gate":"string","finding_ids":"array[string]","conditions":"array[string]","approval_reference":"string"},"returns":"authorized or rejected action"},
}


def _write(path:Path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def build_case(out_root:Path, seed:int, difficulty:int, route_key:str, architecture_attempt:int=0):
    case=generate_canonical_case(seed,route_key,difficulty,architecture_attempt=architecture_attempt)
    case_id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"dgfbench-v6:{seed}:{route_key}:{difficulty}"))
    case['case_id']=case_id
    occ=build_occurrences(route_key)
    refs=evaluate_route(case,occ)
    graph=build_evidence_graph(case,difficulty)
    cdir=out_root/f"{case['project']['project_id']}_{route_key}"
    if cdir.exists(): shutil.rmtree(cdir)
    cdir.mkdir(parents=True)

    public_context={
        "schema_version":"DGF-Bench-v6",
        "case_id":case_id,
        "seed":seed,
        "difficulty":difficulty,
        "architecture_attempt":architecture_attempt,
        "architecture_signature":case['architecture_profile'].get("architecture_signature"),
        "project":case['project'],
        "route":{"key":route_key,"label":ROUTES[route_key]['label'],"trigger":ROUTES[route_key]['trigger']},
    }
    _write(cdir/'00_project_context.json',public_context)
    _write(cdir/'01_route_manifest.json',{"route":public_context['route'],"occurrences":occ,"permitted_dispositions":["GO","GO_WITH_RESERVATIONS","REWORK","SUSPENSION","NO_GO"]})
    _write(cdir/'02_evidence_graph.json',public_graph(graph))
    _write(cdir/'03_tool_schemas.json',TOOL_SCHEMAS)

    # Gate contracts: machine-readable expectations without revealing answers.
    contracts={}
    for gate in GATE_LABELS:
        ev=[n['evidence_id'] for n in graph['nodes'] if gate in n['consumers']]
        contracts[gate]={"gate_label":GATE_LABELS[gate],"objective":GATE_OBJECTIVES[gate],"admissible_inputs":ev,"required_output":{"expert_opinion":["FAVORABLE","FAVORABLE_WITH_RESERVATIONS","UNFAVORABLE"],"disposition":["GO","GO_WITH_RESERVATIONS","REWORK","SUSPENSION","NO_GO"],"findings":"list","required_actions":"list","risk_owner":"role/person","authorization_required":"boolean","evidence_refs":"list[evidence_id]"}}
    _write(cdir/'04_gate_contracts.json',contracts)
    _write(cdir/'05_phase_visibility.json',phase_visibility(graph))

    # Phase history scaffold: same gates can occur more than once with different phase contracts.
    phases={}
    for phase in PHASE_ORDER:
        ph=[o for o in occ if o['phase']==phase]
        if ph:
            phases[phase]=ph
            _write(cdir/f"phase_history/{phase}/gate_occurrences.json",{"phase":phase,"occurrences":ph,"status":"PENDING_EVALUATION"})
    handoffs=[]
    for a,b in zip(occ[:-1],occ[1:]):
        handoffs.append({"from":a['occurrence_id'],"to":b['occurrence_id'],"required_handoff_fields":["case_id","source_version","claim","evidence_locator","verification_status","action_owner","risk_owner","deadline","authorization_reference"]})
    _write(cdir/'phase_history/handoff_contracts.json',handoffs)

    emit_all(cdir,case,graph,occ,refs)

    # Remove files marked unavailable from public dossier while keeping the node in the graph.
    for n in graph['nodes']:
        if n['public_status']=="UNAVAILABLE":
            fp=cdir/n['path']
            if fp.exists(): fp.unlink()
            # Architecture HLD has a paired PNG.
            if fp.suffix.lower()=='.svg':
                png=fp.with_suffix('.png')
                if png.exists(): png.unlink()

    hidden={
        "schema_version":"DGF-Bench-v6-hidden",
        "case_id":case_id,
        "canonical_truth":case,
        "evidence_graph":graph,
        "reference_decisions":refs,
        "note":"Do not expose this file to the evaluated agent. It contains canonical facts and reference outcomes.",
    }
    _write(cdir/'99_hidden_ground_truth.json',hidden)
    _write(cdir/'agent_submission_template.json',{"case_id":case_id,"gate_results":[{"occurrence_id":o['occurrence_id'],"disposition":"GO|GO_WITH_RESERVATIONS|REWORK|SUSPENSION|NO_GO","finding_ids":[],"actions":[],"evidence_refs":[],"authorization_required":False} for o in occ]})

    readme=f"""# DGF-Bench v6 synthetic case\n\nCase: {case_id}\nProject: {case['project']['project_name']}\nRoute: {ROUTES[route_key]['label']}\nDifficulty: {difficulty}\n\n## Rules\n- Treat documents as evidence, not as ground truth.\n- Some non-authoritative documents may be stale, partial, or contradictory.\n- Authoritative information can be obtained through `synthetic_environment.py`.\n- Request missing evidence rather than inventing it.\n- Produce one result per route occurrence using `agent_submission_template.json`.\n- Do not read `99_hidden_ground_truth.json` during evaluation.\n\n## Score\n`python score_submission.py --case <case-dir> --submission submission.json`\n\n## Example tool call\n`python synthetic_environment.py --case <case-dir> --tool get_restore_test --args '{{}}'`\n"""
    (cdir/'README_CASE.md').write_text(readme,encoding='utf-8')
    return cdir


def main():
    ap=argparse.ArgumentParser(description='Generate DGF-Bench v6 facts-first synthetic governance environments')
    ap.add_argument('--count',type=int,default=1)
    ap.add_argument('--seed',type=int,default=6000)
    ap.add_argument('--difficulty',type=int,choices=range(1,6),default=4)
    ap.add_argument('--route',choices=list(ROUTES.keys())+['random'],default='random')
    ap.add_argument('--output-dir',type=Path,default=Path('generated_v6'))
    ns=ap.parse_args(); ns.output_dir.mkdir(parents=True,exist_ok=True)
    created=[]
    route_keys=['buy','integrate','build']
    used_signatures=set()
    for i in range(ns.count):
        seed=ns.seed+i
        route=route_keys[seed%len(route_keys)] if ns.route=='random' else ns.route
        attempt=0
        while True:
            preview=generate_canonical_case(seed,route,ns.difficulty,architecture_attempt=attempt)
            sig=architecture_signature(preview['architecture_profile'])
            if sig not in used_signatures:
                break
            attempt+=1
        used_signatures.add(sig)
        created.append(str(build_case(ns.output_dir,seed,ns.difficulty,route,architecture_attempt=attempt)))
    print(json.dumps({'created_cases':created,'unique_architecture_signatures':len(used_signatures)},indent=2))
if __name__=='__main__': main()
