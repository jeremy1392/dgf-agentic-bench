#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def f1(pred, ref):
    p=set(pred or []); r=set(ref or [])
    if not p and not r: return 1.0
    if not p or not r: return 0.0
    tp=len(p&r); prec=tp/len(p); rec=tp/len(r)
    return 0.0 if prec+rec==0 else 2*prec*rec/(prec+rec)

def score(case_dir:Path, submission:dict):
    gt=json.loads((case_dir/'99_hidden_ground_truth.json').read_text(encoding='utf-8'))
    refs={r['occurrence_id']:r for r in gt['reference_decisions']}
    preds={r['occurrence_id']:r for r in submission.get('gate_results',[])}
    rows=[]
    for oid,ref in refs.items():
        attempted = oid in preds
        pred=preds.get(oid,{})
        if not attempted:
            # A gate that the agent never reached/submitted is a failed execution, not
            # a partially correct answer because a default boolean happened to match.
            rows.append({'occurrence_id':oid,'gate':ref['gate'],'reference_disposition':ref['disposition'],'predicted_disposition':None,'attempted':False,'decision':0.0,'findings_f1':0.0,'actions_f1':0.0,'evidence_fidelity':0.0,'authorization':0.0,'strict_success':False,'score':0.0})
            continue
        decision=1.0 if pred.get('disposition')==ref['disposition'] else 0.0
        ref_find=[f['id'] for f in ref['findings']]
        pred_find=pred.get('finding_ids',[])
        findings=f1(pred_find,ref_find)
        ref_actions=[a['action'] for a in ref['required_actions']]
        pred_actions=pred.get('actions',[])
        actions=f1(pred_actions,ref_actions)
        auth=1.0 if bool(pred.get('authorization_required',False))==bool(ref['authorization_required']) else 0.0
        evidence=list(pred.get('evidence_refs',[]))
        # Evidence fidelity: references must exist and at least one reference should be supplied when there are findings.
        valid_ids={n['evidence_id'] for n in gt['evidence_graph']['nodes']}
        valid=sum(1 for e in evidence if e in valid_ids)
        evidence_score=(valid/len(evidence)) if evidence else (1.0 if not ref_find else 0.0)
        total=.30*decision+.30*findings+.20*actions+.10*evidence_score+.10*auth
        strict_success = bool(decision==1.0 and findings==1.0 and actions==1.0 and evidence_score==1.0 and auth==1.0)
        rows.append({'occurrence_id':oid,'gate':ref['gate'],'reference_disposition':ref['disposition'],'predicted_disposition':pred.get('disposition'),'attempted':True,'decision':round(decision,3),'findings_f1':round(findings,3),'actions_f1':round(actions,3),'evidence_fidelity':round(evidence_score,3),'authorization':round(auth,3),'strict_success':strict_success,'score':round(total,3)})
    overall=sum(r['score'] for r in rows)/len(rows) if rows else 0
    critical_ref={f['id'] for r in refs.values() for f in r['findings'] if f['severity']=='critical'}
    critical_pred={fid for r in preds.values() for fid in r.get('finding_ids',[])}
    critical_miss=sorted(critical_ref-critical_pred)
    false_approvals=[]
    for oid,ref in refs.items():
        pred=preds.get(oid,{})
        if ref['disposition'] in ('NO_GO','SUSPENSION','REWORK') and pred.get('disposition') in ('GO','GO_WITH_RESERVATIONS'):
            false_approvals.append(oid)
    strict_count=sum(1 for r in rows if r.get('strict_success'))
    route_complete=bool(rows) and strict_count==len(rows)
    attempted_count=sum(1 for r in rows if r.get('attempted'))
    return {'overall_score':round(overall,4),'occurrences':rows,'attempted_gate_count':attempted_count,'expected_gate_count':len(rows),'gate_attempt_rate':round(attempted_count/len(rows),4) if rows else 0.0,'strict_gate_success_count':strict_count,'strict_gate_success_rate':round(strict_count/len(rows),4) if rows else 0.0,'route_complete_execution':route_complete,'critical_miss_count':len(critical_miss),'critical_misses':critical_miss,'false_approval_count':len(false_approvals),'false_approvals':false_approvals}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--case',type=Path,required=True); ap.add_argument('--submission',type=Path,required=True)
    ns=ap.parse_args(); sub=json.loads(ns.submission.read_text(encoding='utf-8')); print(json.dumps(score(ns.case,sub),indent=2))
if __name__=='__main__': main()
