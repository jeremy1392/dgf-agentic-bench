#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path
from generate_fake_documents import build_case_pack

PROJECT_TYPES=['new_platform','ma_integration','new_project']

def main():
    ap=argparse.ArgumentParser(description='Generate a stratified random DGF-Bench synthetic dataset.')
    ap.add_argument('--count',type=int,default=30)
    ap.add_argument('--seed',type=int,default=1000)
    ap.add_argument('--output-dir',type=Path,default=Path('dgf_bench_dataset'))
    ap.add_argument('--min-difficulty',type=int,default=1)
    ap.add_argument('--max-difficulty',type=int,default=5)
    ap.add_argument('--conflict-rate-min',type=float,default=.02)
    ap.add_argument('--conflict-rate-max',type=float,default=.20)
    ap.add_argument('--architecture-inconsistency-min',type=float,default=.03)
    ap.add_argument('--architecture-inconsistency-max',type=float,default=.30)
    args=ap.parse_args()
    rng=random.Random(args.seed); args.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i in range(args.count):
        seed=args.seed+i
        ptype=PROJECT_TYPES[i%3] if i<3 else rng.choice(PROJECT_TYPES)
        diff=rng.randint(args.min_difficulty,args.max_difficulty)
        cr=round(rng.uniform(args.conflict_rate_min,args.conflict_rate_max),3)
        ar=round(rng.uniform(args.architecture_inconsistency_min,args.architecture_inconsistency_max),3)
        cdir,_=build_case_pack(seed,diff,ptype,args.output_dir,cr,ar)
        truth=json.loads((cdir/'99_hidden_ground_truth.json').read_text(encoding='utf-8'))
        p=truth['architecture_profile']
        rows.append({
            'case_dir':cdir.name,'seed':seed,'project_type':ptype,'difficulty':diff,
            'overall_decision':truth['overall_decision'],'edge_pattern':p['edge_pattern'],
            'compute_profile':p['compute_profile'],'data_profile':p['data_profile'],
            'network_profile':p['network_profile'],'resilience_profile':p['resilience_profile'],
            'primary_region':p['primary_region'],'secondary_region':p.get('secondary_region'),
            'multi_az':p['multi_az'],'multi_region':p['multi_region'],
            'defect_count':len(p['defects']),'semantic_fault_count':len(p.get('semantic_faults',[])),'inconsistency_count':len(p['inconsistencies']),
            'conflict_rate':cr,'architecture_inconsistency_rate':ar,
        })
    with (args.output_dir/'dataset_manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    (args.output_dir/'dataset_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'count':len(rows),'output_dir':str(args.output_dir),'manifest':'dataset_manifest.csv'},indent=2))
if __name__=='__main__': main()
