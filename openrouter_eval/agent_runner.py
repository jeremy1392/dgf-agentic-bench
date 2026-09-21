from __future__ import annotations
import base64, json, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .agent_tools import ALL_TOOLS, ToolExecutor
from .finding_catalog import build_catalog
from .json_utils import parse_json_object, normalize_submission
from .openrouter_client import OpenRouterClient, Usage, OpenRouterError
from .prompts import SYSTEM_PROMPT, occurrence_prompt, OUTPUT_SCHEMA


@dataclass
class AgentConfig:
    model: str
    temperature: float = 0.0
    max_tokens: int = 3000
    max_turns: int = 20
    max_tool_calls: int = 40
    reasoning_effort: str | None = None
    use_vision: bool = False
    require_parameters: bool = True


def _clean_message(m:dict[str,Any])->dict[str,Any]:
    keep={"role","content","tool_calls","name"}
    return {k:v for k,v in m.items() if k in keep and v is not None}


def _image_part(case_dir:Path):
    candidates=list(case_dir.glob("gate_evidence/architecture/*.png")) + list(case_dir.glob("**/Architecture_Diagram_Detailed.png"))
    if not candidates: return None
    p=candidates[0]
    b64=base64.b64encode(p.read_bytes()).decode("ascii")
    return {"type":"image_url","image_url":{"url":"data:image/png;base64,"+b64}}


def run_occurrence(client:OpenRouterClient, case_dir:Path, occurrence:dict[str,Any], model_caps:dict[str,Any], config:AgentConfig, upstream:list[dict[str,Any]]):
    case_dir=Path(case_dir)
    project=json.loads((case_dir/"00_project_context.json").read_text(encoding="utf-8"))
    route_manifest=json.loads((case_dir/"01_route_manifest.json").read_text(encoding="utf-8"))
    contracts=json.loads((case_dir/"04_gate_contracts.json").read_text(encoding="utf-8"))
    catalog=build_catalog(case_dir.parent.parent.joinpath("evaluator.py") if case_dir.parent.parent.joinpath("evaluator.py").exists() else Path(__file__).resolve().parents[1]/"evaluator.py")
    gate=occurrence["gate"]; phase=occurrence["phase"]; oid=occurrence["occurrence_id"]
    candidates=catalog.get(gate,[])
    prompt=occurrence_prompt(project["project"],route_manifest["route"],occurrence,contracts[gate],candidates,upstream)
    content:any=prompt
    if config.use_vision and gate in {"architecture","security","it","tech_readiness"} and "image" in set(model_caps.get("input_modalities") or []):
        img=_image_part(case_dir)
        if img:
            content=[{"type":"text","text":prompt},img]
    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":content}]
    tools=ToolExecutor(case_dir,gate,phase)
    usage=Usage(); resolved_models=[]; provider_values=[]; tool_calls=0; raw_turns=[]
    session_id=f"dgfbench:{project['case_id']}:{config.model}:{oid}:{uuid.uuid4().hex[:8]}"
    params=set(model_caps.get("supported_parameters") or [])

    for turn in range(config.max_turns):
        body={
            "model":config.model,
            "messages":messages,
            "tools":ALL_TOOLS,
            "session_id":session_id,
            "usage":{"include":True},
        }
        if "tool_choice" in params:
            body["tool_choice"]="auto"
        if "temperature" in params:
            body["temperature"]=config.temperature
        if "max_tokens" in params:
            body["max_tokens"]=config.max_tokens
        elif "max_completion_tokens" in params:
            body["max_completion_tokens"]=config.max_tokens
        if config.reasoning_effort and "reasoning" in params:
            body["reasoning"]={"effort":config.reasoning_effort}
        if config.require_parameters:
            body["provider"]={"require_parameters":True,"allow_fallbacks":True}
        resp=client.chat(body)
        usage.add(Usage.from_response(resp))
        if resp.get("model"): resolved_models.append(resp["model"])
        if resp.get("provider"): provider_values.append(resp["provider"])
        choices=resp.get("choices") or []
        if not choices:
            raise OpenRouterError("No choices returned by OpenRouter")
        msg=_clean_message(choices[0].get("message") or {})
        raw_turns.append({"turn":turn,"assistant":msg,"usage":Usage.from_response(resp).as_dict(),"resolved_model":resp.get("model"),"provider":resp.get("provider")})
        messages.append(msg)
        tc=msg.get("tool_calls") or []
        if tc:
            for call in tc:
                tool_calls += 1
                if tool_calls > config.max_tool_calls:
                    raise RuntimeError("Agent exceeded max_tool_calls")
                fn=(call.get("function") or {})
                name=fn.get("name")
                argtext=fn.get("arguments") or "{}"
                try: args=json.loads(argtext) if isinstance(argtext,str) else dict(argtext)
                except Exception: args={"_raw_arguments":str(argtext)}
                try: result=tools.call(name,args)
                except Exception as e: result={"status":"TOOL_ERROR","error":str(e),"tool":name}
                messages.append({"role":"tool","tool_call_id":call.get("id") or f"call-{tool_calls}","name":name,"content":json.dumps(result,ensure_ascii=False)})
            continue
        final=parse_json_object(str(msg.get("content") or ""))
        if final is not None:
            normalized=normalize_submission(final,oid)
            return {"result":normalized,"usage":usage.as_dict(),"tool_trace":tools.trace,"raw_turns":raw_turns,"resolved_models":resolved_models,"providers":provider_values,"turns":turn+1,"tool_call_count":tool_calls}
        # one repair instruction and continue
        messages.append({"role":"user","content":"Your last response was not valid JSON. Return ONLY a valid JSON object matching this schema: "+json.dumps(OUTPUT_SCHEMA)})
    raise RuntimeError(f"Agent did not produce valid JSON within {config.max_turns} turns")
