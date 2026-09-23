"""Describe every planned fresh repetition, including missing outcomes and costs."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'experiments/followup_repetitions_20260923'


def main():
    plan=json.loads((HERE/'repetition_plan.json').read_text(encoding='utf-8'))
    records={};cost=0.0;unknown=0
    for r in range(1,4):
        for p in (OUT/f'repeat_{r}').glob('*/DGF-*/score.json'):
            s=json.loads(p.read_text(encoding='utf-8'))
            key=(r,s.get('model'),p.parent.name)
            if s.get('status') not in ['INFRA_ERROR','BUDGET_STOP'] and s.get('occurrences'):
                records[key]=s
        for p in (OUT/f'repeat_{r}').glob('*/DGF-*/usage_ledger.jsonl'):
            for line in p.read_text(encoding='utf-8').splitlines():
                if line.strip():
                    u=json.loads(line);cost+=float(u.get('cost',0));unknown+=u.get('unknown_cost_calls',0)
    models={}
    for model in plan['models']:
        repetitions=[];complete=[]
        for r in range(1,4):
            scores=[records[(r,model,c)] for c in plan['cases'] if (r,model,c) in records]
            rows=[x for s in scores for x in s['occurrences']]
            repetitions.append({'repeat':r,'evaluable_cases':len(scores),'planned_cases':15,
                                'strict_gates':sum(x['strict_success'] for x in rows),'evaluable_gates':len(rows),
                                'complete_routes':sum(s['route_complete_decision'] for s in scores),
                                'correct_dispositions':sum(x['decision']==1 for x in rows),
                                'evidence_failures':sum(x['evidence_fidelity']<1 for x in rows)})
        for case in plan['cases']:
            scores=[records.get((r,model,case)) for r in range(1,4)]
            if all(scores):
                decisions=[{x['occurrence_id']:x['predicted_disposition'] for x in s['occurrences']} for s in scores]
                complete.append({'case':case,'all_three_routes_successful':all(s['route_complete_decision'] for s in scores),
                                 'dispositions_identical_across_three':decisions[0]==decisions[1]==decisions[2]})
        models[model]={'repetitions':repetitions,'cases_with_all_three_evaluable':len(complete),
                       'cases_all_three_successful':sum(x['all_three_routes_successful'] for x in complete),
                       'case_details':complete}
    result={'generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'status':'complete' if len(records)==135 else 'not_complete','evaluable_model_case_runs':len(records),
            'planned_model_case_runs':135,'known_cost_usd':cost,'unknown_cost_calls':unknown,'models':models,
            'scope':'Three fresh trajectories on 15 fixed dossiers; original historical outcomes are not counted as another fresh repeat. Descriptive, no best-of-three selection.'}
    (HERE/'repetition_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'evaluable':len(records),'planned':135,'cost_usd':cost},indent=2))


if __name__=='__main__':main()
