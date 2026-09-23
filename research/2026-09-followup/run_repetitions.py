"""Run the fixed repetition plan using frozen sources and a shared spending envelope.

Default is preparation only. --execute explicitly enables paid inference. Requires
OPENROUTER_API_KEY in the environment (never accepted as a command-line argument).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'experiments/reproduction_check_20260923/verified_inputs/benchmark_source'
DATA=ROOT/'experiments/preflight_balanced_300_20260922/dataset'
OUT=ROOT/'experiments/followup_repetitions_20260923'


def ledger_cost(folder):
    total=0.0
    for p in folder.glob('repeat_*/*/*/usage_ledger.jsonl'):
        for line in p.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            r=json.loads(line)
            if r.get('unknown_cost_calls',0):raise RuntimeError('Unknown billed cost: stop for accounting review.')
            total+=float(r.get('cost',0))
    return total


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true')
    ap.add_argument('--cap-usd',type=float,default=20)
    args=ap.parse_args()
    if not 0 < args.cap_usd <= 20:raise ValueError('This approved plan permits at most USD 20.')
    plan=json.loads((HERE/'repetition_plan.json').read_text(encoding='utf-8'))
    sys.path.insert(0,str(SOURCE))
    from benchmark_protocol import source_fingerprint
    identity=json.loads((ROOT/'experiments/run_20260922_214402_941347/results/protocol_identity.json').read_text(encoding='utf-8'))
    assert source_fingerprint()==identity['sources'],'Frozen source mismatch'
    dataset=OUT/'dataset';dataset.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((DATA/'dataset_manifest.json').read_text(encoding='utf-8'))
    by_name={Path(x['case_dir']).name:x for x in manifest['cases']}
    for case in plan['cases']:
        target=dataset/case
        if not target.exists():shutil.copytree(DATA/case,target)
        for source in (DATA/case).rglob('*'):
            if source.is_file():
                assert source.read_bytes()==(target/source.relative_to(DATA/case)).read_bytes()
    manifest['cases']=[by_name[x] for x in plan['cases']]
    (dataset/'dataset_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Prepared 15 byte-verified dossiers; frozen benchmark source identity matched.',flush=True)
    if not args.execute:
        print('No API calls. Run with --execute only after local key configuration and budget approval.')
        return
    from openrouter_eval.env_loader import load_dotenv, require_api_key
    load_dotenv(ROOT/'.env')
    if not os.environ.get('OPENROUTER_API_KEY') and os.name=='nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment') as handle:
                os.environ['OPENROUTER_API_KEY']=winreg.QueryValueEx(handle,'OPENROUTER_API_KEY')[0]
        except OSError:pass
    os.environ['OPENROUTER_API_KEY']=require_api_key()
    # Retain headroom for response-boundary billing in the historical runner.
    # The provider charges in-flight responses after admission; this is not a
    # provider-enforced prepaid limit. An independently limited API key is preferable.
    operating_cap=max(0,args.cap_usd-2)
    for repeat in range(1,4):
        destination=OUT/f'repeat_{repeat}'
        cost_before=ledger_cost(OUT)
        own_cost=0.0
        if destination.exists():
            for p in destination.glob('*/*/usage_ledger.jsonl'):
                own_cost+=sum(float(json.loads(x).get('cost',0)) for x in p.read_text(encoding='utf-8').splitlines() if x.strip())
        cap=operating_cap-(cost_before-own_cost)
        if cap<=own_cost+0.5:
            print('Stopped before another trajectory: shared operating budget exhausted.',flush=True);break
        command=[sys.executable,'-u',str(SOURCE/'run_openrouter_benchmark.py'),
                 '--dataset',str(dataset),'--models',*plan['models'],'--output-dir',str(destination),
                 '--max-cost-usd',str(cap),'--workers','3','--max-workers-per-model','1',
                 '--max-turns','20','--max-tool-calls','40','--max-tokens','8192','--temperature','0',
                 '--vision','auto','--handoff-mode','agent','--schedule','round_robin',
                 '--http-retries','8','--job-budget-reserve-usd','0.5']
        print(f'Repetition {repeat}/3; prior total ${cost_before:.4f}; common operating cap ${operating_cap:.2f}',flush=True)
        process=subprocess.run(command,cwd=ROOT)
        if process.returncode:raise RuntimeError(f'Benchmark exited {process.returncode}; retain checkpoints before investigating.')
        spent=ledger_cost(OUT)
        print(f'Total recorded spending ${spent:.4f}',flush=True)
        if spent>=operating_cap:break
    print('Results retained in',OUT,flush=True)
    subprocess.run([sys.executable,str(HERE/'summarize_repetitions.py')],check=True,cwd=ROOT)


if __name__=='__main__':main()
