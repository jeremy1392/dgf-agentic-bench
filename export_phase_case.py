#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--case',type=Path,required=True); ap.add_argument('--phase',required=True); ap.add_argument('--output',type=Path,required=True)
    ns=ap.parse_args(); vis=json.loads((ns.case/'05_phase_visibility.json').read_text()); allowed=set(vis[ns.phase])
    if ns.output.exists(): shutil.rmtree(ns.output)
    shutil.copytree(ns.case,ns.output,ignore=shutil.ignore_patterns('99_hidden_ground_truth.json','tool_trace.jsonl'))
    graph=json.loads((ns.case/'02_evidence_graph.json').read_text())
    for n in graph['nodes']:
        if n['evidence_id'] not in allowed:
            fp=ns.output/n['path']
            if fp.exists(): fp.unlink()
            if fp.suffix.lower()=='.svg' and fp.with_suffix('.png').exists(): fp.with_suffix('.png').unlink()
    (ns.output/'PHASE.txt').write_text(ns.phase,encoding='utf-8')
    print(ns.output)
if __name__=='__main__': main()
