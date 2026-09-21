#!/usr/bin/env python3
from __future__ import annotations
import collections, json, tempfile, shutil
from pathlib import Path
from facts_engine import generate_canonical_case
from routes import build_occurrences
from evaluator import evaluate_route
from evidence_graph import build_evidence_graph
from generate_dgfbench_v6 import build_case
from score_submission import score

ROUTES=['buy','integrate','build','full_lifecycle']

def main(n=320):
    disp=collections.Counter(); gates=collections.Counter(); modes=collections.Counter(); routes=collections.Counter()
    for i in range(n):
        route=ROUTES[i%len(ROUTES)]; difficulty=1+(i%5); seed=90000+i
        case=generate_canonical_case(seed,route,difficulty); occ=build_occurrences(route); r1=evaluate_route(case,occ); r2=evaluate_route(case,occ)
        assert r1==r2, 'evaluator must be deterministic'
        for r in r1: disp[r['disposition']]+=1; gates[r['gate']]+=1
        graph=build_evidence_graph(case,difficulty)
        ids=[x['evidence_id'] for x in graph['nodes']]; assert len(ids)==len(set(ids))
        for x in graph['nodes']: modes[x['_hidden_mode']]+=1
        routes[route]+=1
    assert set(['GO','GO_WITH_RESERVATIONS','REWORK','SUSPENSION','NO_GO']).issubset(disp), disp
    assert set(['general','it','architecture','security','tech_readiness','procurement','legal','compliance']).issubset(gates), gates

    with tempfile.TemporaryDirectory() as td:
        root=Path(td); cdir=build_case(root,99991,4,'build')
        gt=json.loads((cdir/'99_hidden_ground_truth.json').read_text())
        sub={'case_id':gt['case_id'],'gate_results':[]}
        valid=next(n['evidence_id'] for n in gt['evidence_graph']['nodes'])
        for r in gt['reference_decisions']:
            sub['gate_results'].append({'occurrence_id':r['occurrence_id'],'disposition':r['disposition'],'finding_ids':[f['id'] for f in r['findings']],'actions':[a['action'] for a in r['required_actions']],'evidence_refs':[] if not r['findings'] else [valid],'authorization_required':r['authorization_required']})
        s=score(cdir,sub); assert s['overall_score']==1.0, s
    report={'profiles_tested':n,'route_distribution':dict(routes),'dispositions':dict(disp),'gate_occurrences':dict(gates),'evidence_modes':dict(modes),'status':'PASS'}
    Path('self_test_v6_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
