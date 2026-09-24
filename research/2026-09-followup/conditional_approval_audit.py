"""Read-only audit of conditional-approval behavior in the 899 original scored runs.

Eligibility is recomputed from the public rule definitions, public fact snapshots,
and occurrence-scoped mandates. Approval events are independently replayed with
the frozen environment policy, then checked against the archived scorer flags.
No model calls; no writes to original cases or results.
"""
from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
from pathlib import Path

from rules_baseline import ROOT, DEFAULT_SOURCE, DEFAULT_DATA, interpret


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def summarize(rows):
    cases = {r['case'] for r in rows}
    eligible_cases = {r['case'] for r in rows if r['eligible']}
    used_cases = {r['case'] for r in rows if r['approval_used']}
    requested_cases = {r['case'] for r in rows if r['request_count']}
    counts = dict(
        cases=len(cases), gates=len(rows), eligible_gates=sum(r['eligible'] for r in rows),
        eligible_cases=len(eligible_cases), requested_cases=len(requested_cases), used_cases=len(used_cases),
        request_calls=sum(r['request_count'] for r in rows),
        requested_gates=sum(bool(r['request_count']) for r in rows),
        requested_eligible_gates=sum(bool(r['request_count']) and r['eligible'] for r in rows),
        recorded_executed_calls=sum(r['recorded_executed_count'] for r in rows),
        replay_validated_executed_calls=sum(r['validated_executed_count'] for r in rows),
        final_verified_gates=sum(r['approval_verified'] for r in rows),
        used_gates=sum(r['approval_used'] for r in rows),
        used_gates_base_rework=sum(r['approval_used'] and r['base_disposition']=='REWORK' for r in rows),
        used_gates_base_already_conditional=sum(r['approval_used'] and r['base_disposition']=='GO_WITH_RESERVATIONS' for r in rows),
        used_gates_base_suspension=sum(r['approval_used'] and r['base_disposition']=='SUSPENSION' for r in rows),
        used_gates_changing_base_disposition=sum(r['approval_used'] and r['base_disposition']!=r['effective_disposition'] for r in rows),
        base_rework_eligible_gates=sum(r['eligible'] and r['base_disposition']=='REWORK' for r in rows),
        base_already_conditional_eligible_gates=sum(r['eligible'] and r['base_disposition']=='GO_WITH_RESERVATIONS' for r in rows),
        base_suspension_eligible_gates=sum(r['eligible'] and r['base_disposition']=='SUSPENSION' for r in rows),
        base_matches=sum(r['prediction']==r['base_disposition'] for r in rows),
        effective_matches=sum(r['prediction']==r['effective_disposition'] for r in rows),
        general_reference_changes=sum(r['gate']=='general' and r['base_disposition']!=r['effective_disposition'] for r in rows),
        effective_reference_changes=sum(r['base_disposition']!=r['effective_disposition'] for r in rows),
        indirect_general_reference_changes=sum(r['gate']=='general' and not r['approval_used'] and r['base_disposition']!=r['effective_disposition'] for r in rows),
        rejected_calls=sum(len(r['rejection_reasons']) for r in rows),
        requests_on_ineligible_gates=sum(r['request_count'] for r in rows if not r['eligible']),
        requested_ineligible_gates=sum(bool(r['request_count']) and not r['eligible'] for r in rows),
        request_rejections=dict(collections.Counter(reason for r in rows for reason in r['rejection_reasons'])),
    )
    counts.update(
        request_gate_rate_all=ratio(counts['requested_gates'],counts['gates']),
        request_gate_rate_eligible=ratio(counts['requested_eligible_gates'],counts['eligible_gates']),
        used_gate_rate_all=ratio(counts['used_gates'],counts['gates']),
        used_gate_rate_eligible=ratio(counts['used_gates'],counts['eligible_gates']),
        used_case_rate_all=ratio(counts['used_cases'],counts['cases']),
        used_case_rate_eligible=ratio(counts['used_cases'],counts['eligible_cases']),
        base_rework_acceptance_rate=ratio(counts['used_gates_base_rework'],counts['base_rework_eligible_gates']),
        base_already_conditional_use_rate=ratio(counts['used_gates_base_already_conditional'],counts['base_already_conditional_eligible_gates']),
    )
    return counts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE)
    parser.add_argument('--dataset',type=Path,default=DEFAULT_DATA)
    parser.add_argument('--results',type=Path,default=ROOT/'experiments/run_20260922_214402_941347/results')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    sys.path.insert(0,str(args.source))
    from benchmark_protocol import select_upstream
    from openrouter_eval.public_evidence import PublicEvidenceReader
    from synthetic_environment import SyntheticDGFEnvironment
    from approval_policy import validated_conditional_approval

    cached={}; models={}
    for model_dir in sorted(args.results.iterdir()):
        if not model_dir.is_dir(): continue
        rows=[]; model=None
        for folder in sorted(model_dir.glob('DGF-*')):
            score_path=folder/'score.json'
            if not score_path.exists(): continue
            score=read(score_path)
            if score.get('status') not in ('OK','AGENT_FAILURE') or not score.get('occurrences'): continue
            model=score['model']; case=args.dataset/folder.name
            if folder.name not in cached:
                route=read(case/'01_route_manifest.json')['occurrences']
                contracts=read(case/'04_gate_contracts.json')
                mandates=read(case/'06_authorization_registry.json')['mandates']
                snapshots={o['occurrence_id']:PublicEvidenceReader(case,o['gate'],o['phase']).read_evidence(
                    contracts[o['gate']]['decision_policy']['authoritative_snapshot'])['content'] for o in route}
                cached[folder.name]=(route,contracts,mandates,snapshots)
            route,contracts,mandates,snapshots=cached[folder.name]
            score_rows={s['occurrence_id']:s for s in score['occurrences']}
            history=[]; base_history=[]
            for occurrence in route:
                oid=occurrence['occurrence_id']; gate=occurrence['gate']; phase=occurrence['phase']
                policy=contracts[gate]['decision_policy']; snapshot=snapshots[oid]
                public_ref=interpret(policy,snapshot,gate,phase,select_upstream(history,phase))
                public_ref.update(occurrence)
                base_ref=interpret(policy,snapshot,gate,phase,select_upstream(base_history,phase))
                base_ref.update(occurrence); base_history.append(copy.deepcopy(base_ref))
                active_mandates=[m for m in mandates if m.get('occurrence_id')==oid and m.get('gate')==gate
                    and m.get('phase')==phase and m.get('active') is True]
                eligible=bool(public_ref['findings'] and all(f['risk_acceptance_allowed'] for f in public_ref['findings']) and active_mandates)
                path=next(folder.glob('*_'+oid+'.json')); record=read(path)
                request_events=[e for e in record.get('tool_trace',[]) if e.get('tool')=='approve_with_conditions']
                # Direct method calls never write state or logs. Match exactly the
                # archived action payload fields required by the frozen validator.
                env=SyntheticDGFEnvironment(case,phase,gate,oid)
                env.truth['reference_decisions']=[public_ref]
                validated_count=0
                for event in record.get('tool_trace',[]):
                    if event.get('tool') not in ('approve_with_conditions','return_to_design'): continue
                    actual=event.get('result') or {}; event_args=event.get('args')
                    if not isinstance(actual,dict) or actual.get('status')!='EXECUTED' or not isinstance(event_args,dict): continue
                    previous=copy.deepcopy(env.state)
                    try: checked=getattr(env,event['tool'])(**event_args)
                    except (TypeError,ValueError,KeyError):
                        env.state=previous; continue
                    fields=('status','action','gate','finding_ids','conditions','approval_reference') if event['tool']=='approve_with_conditions' else ('status','action','finding_ids','reason')
                    if checked.get('status')!='EXECUTED' or any(actual.get(k)!=checked.get(k) for k in fields):
                        env.state=previous; continue
                    if event['tool']=='approve_with_conditions': validated_count+=1
                final_approval=env.state['approvals'].get(oid)
                assert final_approval==validated_conditional_approval(case,public_ref,record)
                pred=record['result']['disposition']; used=bool(final_approval and pred=='GO_WITH_RESERVATIONS')
                effective=copy.deepcopy(public_ref)
                if used:
                    effective['disposition']='GO_WITH_RESERVATIONS'; effective['authorization_required']=True
                history.append(effective)
                s=score_rows[oid]
                assert base_ref['disposition']==s['base_reference_disposition'], (model,folder.name,oid,'base')
                assert effective['disposition']==s['reference_disposition'], (model,folder.name,oid,'effective')
                assert bool(final_approval)==s['conditional_approval_verified']
                assert used==s['conditional_approval_used']
                assert not used or eligible
                rows.append(dict(case=folder.name,occurrence_id=oid,gate=gate,phase=phase,
                    eligible=eligible,active_mandates=len(active_mandates),
                    finding_ids=[f['id'] for f in public_ref['findings']],
                    risk_acceptable_finding_ids=[f['id'] for f in public_ref['findings'] if f['risk_acceptance_allowed']],
                    request_count=len(request_events),
                    recorded_executed_count=sum(isinstance(e.get('result'),dict) and e['result'].get('status')=='EXECUTED' for e in request_events),
                    validated_executed_count=validated_count,
                    rejection_reasons=[e['result'].get('reason','unspecified') for e in request_events if isinstance(e.get('result'),dict) and e['result'].get('status')=='REJECTED'],
                    approval_verified=bool(final_approval),approval_used=used,
                    base_disposition=base_ref['disposition'],pre_approval_disposition=public_ref['disposition'],
                    effective_disposition=effective['disposition'],prediction=pred,
                    source_trace=path.relative_to(args.results).as_posix()))
        if rows: models[model]=rows
    matched_cases=set.intersection(*({r['case'] for r in rows} for rows in models.values()))
    summaries={}
    for model,rows in models.items():
        matched=[r for r in rows if r['case'] in matched_cases]
        summaries[model]=dict(all_scored=summarize(rows),common_cases=summarize(matched),
            common_cases_non_general=summarize([r for r in matched if r['gate']!='general']),
            by_gate={gate:summarize([r for r in rows if r['gate']==gate]) for gate in sorted({r['gate'] for r in rows})},
            common_cases_by_gate={gate:summarize([r for r in matched if r['gate']==gate]) for gate in sorted({r['gate'] for r in matched})})
    pairwise={}
    for i,model in enumerate(sorted(models)):
        for other in sorted(models)[i+1:]:
            a={(r['case'],r['occurrence_id']):r for r in models[model] if r['case'] in matched_cases}
            b={(r['case'],r['occurrence_id']):r for r in models[other] if r['case'] in matched_cases}
            assert a.keys()==b.keys()
            eligible=[k for k in a if a[k]['eligible'] and b[k]['eligible']]
            pairwise[model+' | '+other]=dict(eligible_both=len(eligible),both_used=sum(a[k]['approval_used'] and b[k]['approval_used'] for k in eligible),
                first_only=sum(a[k]['approval_used'] and not b[k]['approval_used'] for k in eligible),
                second_only=sum(b[k]['approval_used'] and not a[k]['approval_used'] for k in eligible),
                neither=sum(not a[k]['approval_used'] and not b[k]['approval_used'] for k in eligible))
    output=dict(analysis='Conditional-approval tool behavior; post-hoc descriptive analysis',
        data_scope='Final retained gate checkpoints for the original 899 scored runs; excludes error checkpoints and follow-up repetitions.',
        eligibility='Nonempty public-policy findings, every finding risk_acceptance_allowed, and an active mandate for that occurrence/gate/phase. General uses validated authorized reference history.',
        numerator_definition='Requested = any approve_with_conditions call. Used = independently revalidated final approval and final GO_WITH_RESERVATIONS prediction, matching frozen scorer.',
        limitations=['Tool use is behavior under this prompt and policy, not a causal or general personality/risk-preference estimate.',
            'Base/effective agreement differences are not approval counts: some approvals retain a base GO_WITH_RESERVATIONS decision; authorized upstream decisions can also change General.',
            'Conditions are checked as nonempty strings by the supplied policy, not independently adjudicated for business adequacy.',
            'Eligibility is computed from public supplied rules; it is not independent validation of those rules.'],
        common_case_count=len(matched_cases),models=summaries,paired_common_cases=pairwise)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'conditional_approval_summary.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    (args.output/'conditional_approval_items.json').write_text(json.dumps(models,indent=2)+'\n',encoding='utf-8')
    names={m:m.split('/')[1] for m in models}
    lines=['# Conditional approval behavior in the original benchmark','',
        'This post-hoc audit reads the final retained checkpoints for 899 scored runs. It makes no model calls and changes no original scores. The public policy permits either keeping the base decision or requesting authorized conditional approval. Thus approval use is a separate behavioral result, not an error count.','',
        '## Exact counts','',
        '| Model | Gates | Approval calls | Gates with a request | Rejected calls | Verified final approvals | Approvals used | Eligible gates | Use among eligible | Use among all gates |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for m,v in summaries.items():
        s=v['all_scored']
        lines.append(f"| {names[m]} | {s['gates']} | {s['request_calls']} | {s['requested_gates']} | {s['rejected_calls']} | {s['final_verified_gates']} | {s['used_gates']} | {s['eligible_gates']} | {100*s['used_gate_rate_eligible']:.2f}% | {100*s['used_gate_rate_all']:.2f}% |")
    lines += ['', 'Eligibility requires at least one open finding, every finding marked risk-acceptable by the public executable rules, and an active mandate for that precise occurrence, gate, and phase. The same public facts and policy interpreter used by the deterministic comparator reconstruct eligibility. Each recorded executed approval is then replayed under the frozen environment policy; the final approval state and final prediction must agree with the archived scorer flags. All assertions passed.',
        '', 'Luna has one verified approval that is not used: Procurement in `DGF-BUY-035087_buy` ends with REWORK, although its valid approval permits GO_WITH_RESERVATIONS. Gemini makes 466 rejected calls, in addition to 398 executed approvals; a rejection is not itself a false final approval. Conditions are checked as nonempty strings by this synthetic contract, not independently adjudicated for operational adequacy.',
        '', '## Matched comparison','',
        'All three models have 299 cases and 1,694 gates in common. General eligibility can differ because previously authorized decisions change the findings available for consolidation. Restricting to the 1,395 non-General gates fixes the same 391 eligible opportunities for every model.','',
        '| Model | All matched approvals / eligible | Matched non-General approvals / eligible | Cases with approval / cases with an eligible opportunity |',
        '|---|---:|---:|---:|']
    for m,v in summaries.items():
        s=v['common_cases']; n=v['common_cases_non_general']
        lines.append(f"| {names[m]} | {s['used_gates']}/{s['eligible_gates']} ({100*s['used_gate_rate_eligible']:.2f}%) | {n['used_gates']}/{n['eligible_gates']} ({100*n['used_gate_rate_eligible']:.2f}%) | {s['used_cases']}/{s['eligible_cases']} ({100*s['used_case_rate_eligible']:.2f}%) |")
    lines += ['', 'On the same 391 non-General opportunities, Gemini uses 391 approvals and DeepSeek 201: 1.95 times as many. This supports a descriptive difference in propensity to request/use conditional approvals under this particular prompt, policy, and dataset. It does not establish general permissiveness, stable risk preferences, or a causal personality trait. Some approvals do not relax the base disposition at all.',
        '', '## Why agreement differences are not approval counts','',
        '| Model | Used approval, base REWORK | Used approval, base SUSPENSION | Used approval, base already conditional | Local approvals changing base label | Indirect General changes | Effective matches minus base matches |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for m,v in summaries.items():
        s=v['all_scored']
        lines.append(f"| {names[m]} | {s['used_gates_base_rework']} | {s['used_gates_base_suspension']} | {s['used_gates_base_already_conditional']} | {s['used_gates_changing_base_disposition']} | {s['indirect_general_reference_changes']} | {s['effective_matches']-s['base_matches']} |")
    lines += ['', 'The quoted Gemini count of 139 counts only local approvals that change the base disposition (128 REWORK and 11 SUSPENSION), omitting 259 approvals whose base was already GO_WITH_RESERVATIONS. Two General labels also change from REWORK to GO following upstream authorization, giving 141 additional effective matches. DeepSeek has 67 local label-changing approvals but loses one former base match at General after upstream authorization, giving a net difference of 66. Luna has 98 local label-changing approvals plus two indirect General changes, giving 100. Subtracting agreement percentages therefore cannot recover approval counts.',
        '', '## By gate (all scored runs)','',
        '| Model | Gate | Gates | Eligible | Request calls | Requested gates | Used approvals | Use among eligible |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for m,v in summaries.items():
        for g,s in v['by_gate'].items():
            lines.append(f"| {names[m]} | {g} | {s['gates']} | {s['eligible_gates']} | {s['request_calls']} | {s['requested_gates']} | {s['used_gates']} | {100*s['used_gate_rate_eligible']:.2f}% |")
    lines += ['', '## Reproduction','', 'Run from the repository root:', '', '```powershell', '.venv/Scripts/python.exe research/2026-09-followup/conditional_approval_audit.py', '```', '',
        '`conditional_approval_summary.json` contains all, common-case, non-General, by-gate, and paired descriptive counts. `conditional_approval_items.json` provides all 5,094 gate records, eligibility, event counts, disposition decomposition, and original trace paths. CLI options can point to downloaded dataset, result, and frozen-source archives. Repeated trajectories and ERROR checkpoints are outside this audit. Public-policy agreement is not independent validation of the policy itself.']
    (args.output/'conditional_approval_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))


if __name__=='__main__': main()
