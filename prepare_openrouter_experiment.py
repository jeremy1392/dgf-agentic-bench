#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from generate_dgfbench_v6 import build_case


def sha256(path:Path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def main():
    ap=argparse.ArgumentParser(description="Create a balanced DGF-Bench dataset for OpenRouter experiments")
    ap.add_argument("--cases-per-route",type=int,default=20)
    ap.add_argument("--seed",type=int,default=9000)
    ap.add_argument("--difficulty",type=int,choices=range(1,6),default=4)
    ap.add_argument("--include-full-lifecycle",action="store_true")
    ap.add_argument("--output-dir",type=Path,default=Path("openrouter_dataset"))
    ns=ap.parse_args(); ns.output_dir.mkdir(parents=True,exist_ok=True)
    routes=["buy","integrate","build"] + (["full_lifecycle"] if ns.include_full_lifecycle else [])
    rows=[]; counter=0
    for route in routes:
        for i in range(ns.cases_per_route):
            seed=ns.seed+counter; counter+=1
            cdir=build_case(ns.output_dir,seed,ns.difficulty,route)
            ctx=json.loads((cdir/"00_project_context.json").read_text(encoding="utf-8"))
            rows.append({"case_dir":cdir.name,"case_id":ctx["case_id"],"route":route,"seed":seed,"difficulty":ns.difficulty,"public_context_sha256":sha256(cdir/"00_project_context.json")})
    manifest={"schema":"DGF-Bench-OpenRouter-Dataset-v1","cases":rows}
    (ns.output_dir/"dataset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"output_dir":str(ns.output_dir),"case_count":len(rows),"routes":routes},indent=2))
if __name__=="__main__": main()
