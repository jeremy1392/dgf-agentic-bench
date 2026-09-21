#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--case',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    ns=ap.parse_args()
    if ns.output.exists(): shutil.rmtree(ns.output)
    shutil.copytree(ns.case,ns.output,ignore=shutil.ignore_patterns('99_hidden_ground_truth.json','tool_trace.jsonl'))
    print(ns.output)
if __name__=='__main__': main()
