"""Audit completed repetitions and bootstrap whole cases within the three routes.

No model calls. --run-dir accepts an extracted repetition archive. The historical
300-case results are not pooled into this follow-up. All final traces and failed
attempts are retained in the release; this script reads scores and cost ledgers.
"""
import argparse
import collections
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
METRICS = ('strict_gate_rate', 'complete_route_rate', 'all_three_route_rate')


def measure(cases):
    scores = [s for c in cases for s in c['scores']]
    rows = [x for s in scores for x in s['occurrences']]
    return (sum(x['strict_success'] for x in rows)/len(rows),
            sum(s['route_complete_decision'] for s in scores)/len(scores),
            sum(all(s['route_complete_decision'] for s in c['scores']) for c in cases)/len(cases))


def percentile(values, p):
    v = sorted(values); position=(len(v)-1)*p; low=int(position)
    return v[low]+(v[min(low+1,len(v)-1)]-v[low])*(position-low)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run-dir', type=Path, default=ROOT/'experiments/followup_repetitions_20260923')
    ap.add_argument('--output-dir', type=Path, default=HERE)
    args=ap.parse_args(); run=args.run_dir; out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    plan=json.loads((HERE/'repetition_plan.json').read_text(encoding='utf-8'))
    expected={(r,m,c) for r in range(1,4) for m in plan['models'] for c in plan['cases']}
    scores={}; inputs=[]; cost=collections.defaultdict(Decimal); errors=collections.Counter()
    identities=[]
    for rep in sorted(run.glob('repeat_*')):
        r=int(rep.name.split('_')[1])
        identity=json.loads((rep/'protocol_identity.json').read_text(encoding='utf-8'))
        identities.append(identity)
        for path in sorted(rep.glob('*/DGF-*/score.json')):
            data=path.read_bytes(); s=json.loads(data); key=(r,s['model'],path.parent.name)
            assert key in expected and key not in scores
            assert s['status']=='OK', (key,s['status'])
            assert s['attempted_gate_count']==s['expected_gate_count']==len(s['occurrences'])
            assert not s['model_resolution_mismatch']
            assert s['resolved_models']==[s['model']]
            assert s['strict_gate_success_count']==sum(x['strict_success'] for x in s['occurrences'])
            assert bool(s['route_complete_decision'])==all(x['strict_success'] for x in s['occurrences'])
            scores[key]=s
            inputs.append({'path':path.relative_to(run).as_posix(),'sha256':hashlib.sha256(data).hexdigest()})
            ledger=path.parent/'usage_ledger.jsonl'
            for line in ledger.read_text(encoding='utf-8').splitlines():
                u=json.loads(line); assert not u.get('unknown_cost_calls',0)
                cost[s['model']]+=Decimal(str(u.get('cost',0)))
            for ep in path.parent.glob('*_ERROR_*.json'):
                e=json.loads(ep.read_text(encoding='utf-8'))
                message=str(e.get('error',''))
                category='key_limit' if 'Key limit exceeded' in message else ('provider_finish_error' if 'finish_reason=error' in message else 'other')
                errors[category]+=1
    assert set(scores)==expected, (len(scores),len(expected))
    assert len(identities)==3 and identities[0]==identities[1]==identities[2], 'Protocol identities differ'
    models={}; csv_rows=[]
    for model in plan['models']:
        case_records=[]; repeats=[]
        for c in plan['cases']:
            ss=[scores[(r,model,c)] for r in range(1,4)]
            maps=[{x['occurrence_id']:x for x in s['occurrences']} for s in ss]
            assert maps[0].keys()==maps[1].keys()==maps[2].keys()
            decisions=[{k:v['predicted_disposition'] for k,v in m.items()} for m in maps]
            case_records.append({'case':c,'route':c.split('-')[1],'scores':ss,
                'all_three_routes_successful':all(s['route_complete_decision'] for s in ss),
                'route_outcomes_vary':len({s['route_complete_decision'] for s in ss})>1,
                'dispositions_identical':decisions[0]==decisions[1]==decisions[2],
                'gates_with_variable_dispositions':sum(len({m[k]['predicted_disposition'] for m in maps})>1 for k in maps[0]),
                'gates_with_variable_evidence_pass':sum(len({m[k]['evidence_fidelity']==1 for m in maps})>1 for k in maps[0])})
        for r in range(1,4):
            ss=[scores[(r,model,c)] for c in plan['cases']]; rows=[x for s in ss for x in s['occurrences']]
            record={'model':model,'repeat':r,'cases':len(ss),'gates':len(rows),
                'strict_gates':sum(x['strict_success'] for x in rows),
                'complete_routes':sum(s['route_complete_decision'] for s in ss),
                'correct_dispositions':sum(x['decision']==1 for x in rows),
                'false_approvals':sum(s['false_approval_count'] for s in ss),
                'critical_misses':sum(s['critical_miss_count'] for s in ss),
                'evidence_failures':sum(x['evidence_fidelity']<1 for x in rows)}
            repeats.append(record);csv_rows.append(record)
        # Draw five entire cases per route with replacement; each draw retains all
        # three trajectories and every gate. 15 cases, not 255 independent gates.
        rng=random.Random(24092026); boot=[[] for _ in METRICS]
        strata=[[c for c in case_records if c['route']==route] for route in ('BUY','INT','BLD')]
        assert [len(s) for s in strata]==[5,5,5]
        for _ in range(10000):
            sample=[rng.choice(s) for s in strata for _ in range(5)]
            for values,v in zip(boot,measure(sample)): values.append(v)
        ss=[s for c in case_records for s in c['scores']]
        models[model]={'repetitions':repeats,
            'pooled':{k:sum(r[k] for r in repeats) for k in ['cases','gates','strict_gates','complete_routes','correct_dispositions','false_approvals','critical_misses','evidence_failures']},
            'rates':dict(zip(METRICS,measure(case_records))),
            'case_bootstrap_95':{k:[percentile(b,.025),percentile(b,.975)] for k,b in zip(METRICS,boot)},
            'all_three_successful_cases':sum(c['all_three_routes_successful'] for c in case_records),
            'cases_with_variable_route_outcome':sum(c['route_outcomes_vary'] for c in case_records),
            'cases_with_identical_dispositions':sum(c['dispositions_identical'] for c in case_records),
            'gates_with_variable_dispositions':sum(c['gates_with_variable_dispositions'] for c in case_records),
            'gates_with_variable_evidence_pass':sum(c['gates_with_variable_evidence_pass'] for c in case_records),
            'known_cost_usd':float(cost[model]),'providers':sorted({p for s in ss for p in s['providers']}),
            'resumed_cases':sum(s['resumed_gate_count']>0 for s in ss),
            'resumed_gates':sum(s['resumed_gate_count'] for s in ss),
            'truncated_response_count':sum(s['truncated_response_count'] for s in ss),
            'cases':[{k:v for k,v in c.items() if k!='scores'} for c in case_records]}
    result={'status':'complete','model_case_runs':len(scores),'gates':sum(m['pooled']['gates'] for m in models.values()),
            'known_cost_usd':float(sum(cost.values())),'unknown_cost_calls':0,
            'retained_error_checkpoints':dict(errors),'protocol_identity_equal_across_repeats':True,
            'bootstrap':{'draws':10000,'seed':24092026,'method':'95% percentile, five whole cases per route sampled with replacement; all three trajectories retained together; exploratory intervals on 15 cases. Zero observed events may give degenerate bootstrap intervals, not proof of zero population risk.'},
            'interpretation':'Within-sample repetition of existing dossiers, not an independent dataset replication. Optional authorized approvals can change dispositions without being errors. Infrastructure resumes preserve completed prefixes; failed attempts contribute cost but are not extra completed trajectories.',
            'models':models,'score_inputs':inputs}
    (out/'repetition_analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with (out/'repetition_by_run.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(csv_rows[0]));writer.writeheader();writer.writerows(csv_rows)
    print(json.dumps({k:v for k,v in result.items() if k not in ['score_inputs','models']},indent=2))
    for model,m in models.items():print(model,json.dumps({k:v for k,v in m.items() if k not in ['cases','repetitions']}))


if __name__=='__main__':main()
