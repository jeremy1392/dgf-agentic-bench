from __future__ import annotations
import json, re


def parse_json_object(text: str):
    text=(text or "").strip()
    try:
        obj=json.loads(text)
        if isinstance(obj,dict): return obj
    except Exception:
        pass
    m=re.search(r"\{.*\}",text,re.S)
    if m:
        try:
            obj=json.loads(m.group(0))
            if isinstance(obj,dict): return obj
        except Exception:
            pass
    return None


def normalize_submission(obj:dict, occurrence_id:str):
    allowed={"GO","GO_WITH_RESERVATIONS","REWORK","SUSPENSION","NO_GO"}
    out={
        "occurrence_id":occurrence_id,
        "disposition":str(obj.get("disposition") or "").upper(),
        "finding_ids":[str(x) for x in (obj.get("finding_ids") or [])],
        "actions":[str(x) for x in (obj.get("actions") or [])],
        "evidence_refs":[str(x) for x in (obj.get("evidence_refs") or [])],
        "authorization_required":bool(obj.get("authorization_required",False)),
        "rationale":str(obj.get("rationale") or "")[:4000],
        "confidence":float(obj.get("confidence") or 0.0),
    }
    if out["disposition"] not in allowed:
        raise ValueError(f"Invalid disposition: {out['disposition']!r}")
    return out
