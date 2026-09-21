#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--case',type=Path,required=True); ns=ap.parse_args(); c=ns.case
    errors=[]
    for req in ['00_project_context.json','01_route_manifest.json','02_evidence_graph.json','03_tool_schemas.json','04_gate_contracts.json','05_phase_visibility.json','99_hidden_ground_truth.json','agent_submission_template.json']:
        if not (c/req).exists(): errors.append(f'missing {req}')
    if not errors:
        gt=json.loads((c/'99_hidden_ground_truth.json').read_text()); route=json.loads((c/'01_route_manifest.json').read_text()); public=json.loads((c/'02_evidence_graph.json').read_text())
        if len(gt['reference_decisions'])!=len(route['occurrences']): errors.append('reference decision count mismatch')
        ids={n['evidence_id'] for n in gt['evidence_graph']['nodes']}; pids={n['evidence_id'] for n in public['nodes']}
        if ids!=pids: errors.append('public/hidden evidence IDs mismatch')
        for n in public['nodes']:
            if n['public_status']=='AVAILABLE' and not (c/n['path']).exists(): errors.append(f"available evidence missing: {n['evidence_id']} -> {n['path']}")
            if n['public_status']=='UNAVAILABLE' and (c/n['path']).exists(): errors.append(f"unavailable evidence unexpectedly present: {n['evidence_id']}")
    print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},indent=2))
    raise SystemExit(1 if errors else 0)
if __name__=='__main__': main()
