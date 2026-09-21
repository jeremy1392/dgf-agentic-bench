#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile
from pathlib import Path
from openrouter_eval.public_evidence import PublicEvidenceReader
from openrouter_eval.finding_catalog import build_catalog
from openrouter_eval.json_utils import parse_json_object, normalize_submission


def main():
    base=Path(__file__).resolve().parent
    cat=build_catalog(base/"evaluator.py")
    assert "security" in cat and any(x["id"]=="SEC-WAF-001" for x in cat["security"])
    assert "legal" in cat and "general" in cat
    obj=parse_json_object('prefix {"disposition":"GO","finding_ids":[],"actions":[],"evidence_refs":[],"authorization_required":false,"confidence":0.8} suffix')
    assert obj and normalize_submission(obj,"X")["disposition"]=="GO"
    print(json.dumps({"status":"PASS","finding_catalog_gates":sorted(cat),"finding_count":sum(len(v) for v in cat.values())},indent=2))
if __name__=="__main__": main()
