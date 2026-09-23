"""No-inference comparator using only the published agent-visible rule contract.

Generate and score in separate processes. Generation blocks hidden reference reads.
Never imports evaluator.py or score_submission.py in generate mode.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / 'experiments/reproduction_check_20260923/verified_inputs/benchmark_source'
DEFAULT_DATA = ROOT / 'experiments/preflight_balanced_300_20260922/dataset'
DEST = Path(__file__).resolve().parent


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def finding(fid, severity, message, action, owner, evidence,
            disposition='REWORK', risk_acceptance_allowed=False):
    return dict(id=fid, severity=severity, message=message, required_action=action,
                disposition=disposition, risk_acceptance_allowed=risk_acceptance_allowed)


def interpret(policy, snapshot, gate, phase, upstream):
    # Implement the public result-combination contract, not hidden per-case answers.
    def result(gate, phase, findings, risk_owner, upstream=None):
        disposition = max((f['disposition'] for f in findings),
                          key=policy['priority_low_to_high'].index, default='GO')
        return dict(disposition=disposition, findings=findings,
                    authorization_required=disposition in policy['authorization_required_for'])
    code = policy['rule_definition_python']
    tree = ast.parse(code)
    assert len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
    assert not any(isinstance(x, (ast.Import, ast.ImportFrom)) for x in ast.walk(tree))
    forbidden = {'open','exec','eval','compile','__import__','globals','locals','getattr'}
    assert not any(isinstance(x, ast.Name) and x.id in forbidden for x in ast.walk(tree))
    env = {'__builtins__': {'next':next, 'str':str, 'len':len, 'all':all, 'bool':bool},
           'finding':finding, '_result':result}
    exec(compile(tree, '<agent-visible-policy>', 'exec'), env)
    fn = env[tree.body[0].name]
    return fn(snapshot, phase, upstream) if gate=='general' else fn(snapshot, phase)


def generate(args):
    sys.path.insert(0, str(args.source))
    from openrouter_eval.public_evidence import PublicEvidenceReader
    reads = set()
    data_root = args.dataset.resolve()
    def audit(event, values):
        if event != 'open' or not isinstance(values[0], (str, bytes)): return
        p = Path(values[0]).resolve()
        if p.is_relative_to(data_root):
            if 'hidden' in p.name.lower() or p.name in {'tool_trace.jsonl','environment_state.json'}:
                raise PermissionError('Comparator cannot read evaluator-only input')
            reads.add(p.relative_to(data_root).as_posix())
    sys.addaudithook(audit)
    start=time.perf_counter(); cases=sorted(args.dataset.glob('DGF-*'))
    assert len(cases)==300
    policy_hashes=set()
    for case in cases:
        route=json.loads((case/'01_route_manifest.json').read_text(encoding='utf-8'))
        contracts=json.loads((case/'04_gate_contracts.json').read_text(encoding='utf-8'))
        predictions=[]; records={}; history=[]
        for occurrence in route['occurrences']:
            gate=occurrence['gate'];phase=occurrence['phase'];oid=occurrence['occurrence_id']
            policy=contracts[gate]['decision_policy']
            policy_hashes.add(hashlib.sha256(policy['rule_definition_python'].encode()).hexdigest())
            reader=PublicEvidenceReader(case,gate,phase)
            eid=policy['authoritative_snapshot']; observed=reader.read_evidence(eid)
            assert observed['status']=='OK'
            specialists=[x for x in history if x['gate']!='general' and x['phase']==phase]
            if not specialists:
                specialists=[]
                for x in reversed(history):
                    if x['gate']=='general':break
                    specialists.insert(0,x)
            answer=interpret(policy, observed['content'],gate,phase,specialists)
            trace=[{'tool':'read_evidence','args':{'evidence_id':eid},'result':observed}]
            refs=[eid]; support=[]
            if gate=='general':
                trace.append({'tool':'read_evidence','args':{'evidence_id':'UPSTREAM_DECISIONS'},
                              'result':{'status':'OK','evidence_id':'UPSTREAM_DECISIONS','content':specialists}})
            for f in answer['findings']:
                upstream=f['id'].startswith('GEN-UPSTREAM-')
                source='UPSTREAM_DECISIONS' if upstream else eid
                if source not in refs:refs.append(source)
                support.append({'finding_id':f['id'],'evidence_id':source,
                                'quote':json.dumps(specialists if upstream else observed['content'],ensure_ascii=False)})
            prediction=dict(occurrence_id=oid, disposition=answer['disposition'],
                            finding_ids=[f['id'] for f in answer['findings']],
                            actions=[f['required_action'] for f in answer['findings']],
                            evidence_refs=refs,evidence_support=support,
                            authorization_required=answer['authorization_required'],
                            rationale='Execute supplied rule on observed public facts; keep base disposition.',confidence=1.0)
            predictions.append(prediction);records[oid]={'result':prediction,'tool_trace':trace}
            history.append(dict(prediction,gate=gate,phase=phase))
        dump(args.output/'baseline'/case.name/'submission.json',{'gate_results':predictions})
        dump(args.output/'baseline'/case.name/'records.json',records)
    assert 'evaluator' not in sys.modules and 'score_submission' not in sys.modules
    dump(args.output/'baseline_generation.json',{
        'cases':len(cases),'seconds':time.perf_counter()-start,'paid_inference_calls':0,
        'decision_strategy':'base decision; no conditional risk acceptance requested; permitted by public policy',
        'evidence_strategy':'cite complete observed JSON snapshots; no quote-token cap in protocol',
        'public_rule_sha256':sorted(policy_hashes),'dataset_reads':sorted(reads),
        'hidden_reference_reads':0,'source':str(args.source),
        'boundary':'Rules are executable functions published to agents and derived from evaluator logic. This is a scaffold control, not independent policy validation.'})
    print('Generated',len(cases),'cases without hidden-reference reads or evaluator imports.')


def score_run(args):
    sys.path.insert(0,str(args.source))
    from score_submission import score
    scores=[]
    for folder in sorted((args.output/'baseline').glob('DGF-*')):
        prediction=json.loads((folder/'submission.json').read_text(encoding='utf-8'))
        records=json.loads((folder/'records.json').read_text(encoding='utf-8'))
        value=score(args.dataset/folder.name,prediction,tool_records=records)
        dump(folder/'score.json',value);scores.append(value)
    rows=[r for s in scores for r in s['occurrences']]
    result={'cases':len(scores),'gates':len(rows),'strict_gate_success':sum(r['strict_success'] for r in rows),
            'route_success':sum(s['route_complete_decision'] for s in scores),
            'decision_correct':sum(r['decision']==1 for r in rows),
            'evidence_only_failures':sum(r['evidence_fidelity']<1 and all(r[k]==1 for k in ['decision','findings_f1','actions_f1','authorization']) for r in rows),
            'false_approvals':sum(s['false_approval_count'] for s in scores),
            'critical_misses':sum(s['critical_miss_count'] for s in scores),'model_api_cost_usd':0,
            'note':'Generation and scoring are separate processes; hidden references read only by frozen scorer. Local compute and development are not costed.'}
    dump(args.output/'baseline_summary.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['generate','score'])
    p.add_argument('--dataset',type=Path,default=DEFAULT_DATA)
    p.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    p.add_argument('--output',type=Path,default=DEST)
    a=p.parse_args();generate(a) if a.mode=='generate' else score_run(a)
