from __future__ import annotations
import base64, copy, json, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .agent_tools import ALL_TOOLS, ToolExecutor
from .finding_catalog import build_catalog
from .json_utils import parse_json_object, normalize_submission
from .openrouter_client import OpenRouterClient, Usage, OpenRouterError
from .prompts import (
    SYSTEM_PROMPT,
    occurrence_prompt,
    OUTPUT_SCHEMA,
    SUBMIT_DECISION_TOOL,
    structured_response_format,
)


@dataclass
class AgentConfig:
    model: str
    temperature: float = 0.0
    max_tokens: int = 8192
    max_turns: int = 20
    max_tool_calls: int = 40
    reasoning_effort: str | None = None
    use_vision: bool = False
    require_parameters: bool = True


class AgentRunError(RuntimeError):
    """Agent failure that preserves usage and trace data for paper-grade accounting."""

    def __init__(self, message: str, *, kind: str, record: dict[str, Any]):
        super().__init__(message)
        self.kind = kind
        self.record = record


def _clean_message(m:dict[str,Any])->dict[str,Any]:
    keep={"role","content","tool_calls","name"}
    return {k:v for k,v in m.items() if k in keep and v is not None}


def _image_part(case_dir:Path):
    candidates=list(case_dir.glob("gate_evidence/architecture/*.png")) + list(case_dir.glob("**/Architecture_Diagram_Detailed.png"))
    if not candidates: return None
    p=candidates[0]
    b64=base64.b64encode(p.read_bytes()).decode("ascii")
    return {"type":"image_url","image_url":{"url":"data:image/png;base64,"+b64}}


def _decision_tool(strict: bool) -> dict[str, Any]:
    tool = copy.deepcopy(SUBMIT_DECISION_TOOL)
    if strict:
        tool["function"]["strict"] = True
    return tool


def _record(
    *,
    result: dict[str, Any] | None,
    usage: Usage,
    tools: ToolExecutor,
    raw_turns: list[dict[str, Any]],
    resolved_models: list[str],
    provider_values: list[Any],
    turns: int,
    tool_calls: int,
    finish_reasons: list[Any],
    truncated_response_count: int,
    finalization_mode: str | None = None,
    validation_errors: list[str] | None = None,
) -> dict[str, Any]:
    out = {
        "usage": usage.as_dict(),
        "tool_trace": tools.trace,
        "raw_turns": raw_turns,
        "resolved_models": resolved_models,
        "providers": provider_values,
        "turns": turns,
        "tool_call_count": tool_calls,
        "finish_reasons": finish_reasons,
        "last_finish_reason": finish_reasons[-1] if finish_reasons else None,
        "truncated_response_count": truncated_response_count,
        "finalization_mode": finalization_mode,
        "validation_errors": validation_errors or [],
    }
    if result is not None:
        out["result"] = result
    return out


def _normalize_payload(payload: dict[str, Any], oid: str) -> dict[str, Any]:
    # occurrence_id is owned by the harness, not trusted from the model.
    obj = dict(payload)
    obj["occurrence_id"] = oid
    return normalize_submission(obj, oid)


def _apply_common_params(body: dict[str, Any], config: AgentConfig, params: set[str]) -> None:
    if "temperature" in params:
        body["temperature"] = config.temperature
    if "max_tokens" in params:
        body["max_tokens"] = config.max_tokens
    elif "max_completion_tokens" in params:
        body["max_completion_tokens"] = config.max_tokens
    if config.reasoning_effort:
        if "reasoning_effort" in params:
            body["reasoning_effort"] = config.reasoning_effort
        elif "reasoning" in params:
            body["reasoning"] = {"effort": config.reasoning_effort}
    if config.require_parameters:
        # Provider fallback means another endpoint serving the SAME requested model,
        # not a silent switch to a different model ID. The resolved model is recorded.
        body["provider"] = {"require_parameters": True, "allow_fallbacks": True}


def run_occurrence(client:OpenRouterClient, case_dir:Path, occurrence:dict[str,Any], model_caps:dict[str,Any], config:AgentConfig, upstream:list[dict[str,Any]]):
    case_dir=Path(case_dir)
    project=json.loads((case_dir/"00_project_context.json").read_text(encoding="utf-8"))
    route_manifest=json.loads((case_dir/"01_route_manifest.json").read_text(encoding="utf-8"))
    contracts=json.loads((case_dir/"04_gate_contracts.json").read_text(encoding="utf-8"))
    catalog=build_catalog(case_dir.parent.parent.joinpath("evaluator.py") if case_dir.parent.parent.joinpath("evaluator.py").exists() else Path(__file__).resolve().parents[1]/"evaluator.py")
    gate=occurrence["gate"]; phase=occurrence["phase"]; oid=occurrence["occurrence_id"]
    candidates=catalog.get(gate,[])
    prompt=occurrence_prompt(project["project"],route_manifest["route"],occurrence,contracts[gate],candidates,upstream)
    content:Any=prompt
    if config.use_vision and gate in {"architecture","security","it","tech_readiness"} and "image" in set(model_caps.get("input_modalities") or []):
        img=_image_part(case_dir)
        if img:
            content=[{"type":"text","text":prompt},img]
    messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":content}]
    tools=ToolExecutor(case_dir,gate,phase)
    usage=Usage(); resolved_models=[]; provider_values=[]; tool_calls=0; raw_turns=[]; finish_reasons=[]; truncated_response_count=0
    validation_errors: list[str] = []
    session_id=f"dgfbench:{project['case_id']}:{config.model}:{oid}:{uuid.uuid4().hex[:8]}"
    params=set(model_caps.get("supported_parameters") or [])
    strict_structured = "structured_outputs" in params or "response_format" in params
    submit_tool = _decision_tool(strict_structured)

    def fail(message: str, kind: str, turns: int) -> None:
        raise AgentRunError(
            message,
            kind=kind,
            record=_record(
                result=None,
                usage=usage,
                tools=tools,
                raw_turns=raw_turns,
                resolved_models=resolved_models,
                provider_values=provider_values,
                turns=turns,
                tool_calls=tool_calls,
                finish_reasons=finish_reasons,
                truncated_response_count=truncated_response_count,
                validation_errors=validation_errors,
            ),
        )

    # Main investigation loop. The last turn is reserved for a forced typed submission.
    for turn in range(config.max_turns):
        force_finalize = turn == config.max_turns - 1 or tool_calls >= config.max_tool_calls
        offered_tools = [submit_tool] if force_finalize else (ALL_TOOLS + [submit_tool])
        body={
            "model":config.model,
            "messages":messages,
            "tools":offered_tools,
            "session_id":session_id,
            "usage":{"include":True},
        }
        if "parallel_tool_calls" in params:
            body["parallel_tool_calls"] = False
        if "tool_choice" in params:
            body["tool_choice"] = (
                {"type":"function","function":{"name":"submit_gate_decision"}}
                if force_finalize else "auto"
            )
        _apply_common_params(body, config, params)

        try:
            resp=client.chat(body)
        except OpenRouterError as e:
            fail(f"OpenRouter request failed: {e}", "infrastructure", turn)

        turn_usage=Usage.from_response(resp)
        usage.add(turn_usage)
        if resp.get("model"): resolved_models.append(str(resp["model"]))
        if resp.get("provider"): provider_values.append(resp["provider"])
        choices=resp.get("choices") or []
        if not choices:
            fail("No choices returned by OpenRouter", "infrastructure", turn+1)
        choice=choices[0]
        finish_reason=choice.get("finish_reason")
        finish_reasons.append(finish_reason)
        if finish_reason in {"length", "max_tokens"}:
            truncated_response_count += 1
        msg=_clean_message(choice.get("message") or {})
        raw_turns.append({
            "turn":turn,
            "assistant":msg,
            "finish_reason":finish_reason,
            "usage":turn_usage.as_dict(),
            "resolved_model":resp.get("model"),
            "provider":resp.get("provider"),
            "forced_finalization":force_finalize,
        })
        messages.append(msg)
        tc=msg.get("tool_calls") or []

        if tc:
            # A typed decision tool call is a final answer; do not send it to the environment.
            for call in tc:
                fn=(call.get("function") or {})
                if fn.get("name") != "submit_gate_decision":
                    continue
                argtext=fn.get("arguments") or "{}"
                try:
                    args=json.loads(argtext) if isinstance(argtext,str) else dict(argtext)
                    result=_normalize_payload(args, oid)
                    return _record(
                        result=result,
                        usage=usage,
                        tools=tools,
                        raw_turns=raw_turns,
                        resolved_models=resolved_models,
                        provider_values=provider_values,
                        turns=turn+1,
                        tool_calls=tool_calls,
                        finish_reasons=finish_reasons,
                        truncated_response_count=truncated_response_count,
                        finalization_mode="submit_gate_decision",
                        validation_errors=validation_errors,
                    )
                except Exception as e:
                    validation_errors.append(f"submit_gate_decision validation failed: {type(e).__name__}: {e}")
                    # Give a tool-error result so the conversation remains valid, then retry.
                    messages.append({
                        "role":"tool",
                        "tool_call_id":call.get("id") or "submit-invalid",
                        "name":"submit_gate_decision",
                        "content":json.dumps({"status":"INVALID_SUBMISSION","error":str(e)}, ensure_ascii=False),
                    })

            # Execute evidence/action tools. Calls beyond the budget receive an explicit result
            # rather than crashing the conversation; the next turn is forced to finalize.
            for call in tc:
                fn=(call.get("function") or {})
                name=fn.get("name")
                if name == "submit_gate_decision":
                    continue
                argtext=fn.get("arguments") or "{}"
                if tool_calls >= config.max_tool_calls:
                    messages.append({
                        "role":"tool",
                        "tool_call_id":call.get("id") or f"budget-{tool_calls}",
                        "name":name,
                        "content":json.dumps({
                            "status":"TOOL_BUDGET_EXHAUSTED",
                            "message":"No more investigation tools are available. Submit the gate decision now."
                        }),
                    })
                    continue
                tool_calls += 1
                try: args=json.loads(argtext) if isinstance(argtext,str) else dict(argtext)
                except Exception: args={"_raw_arguments":str(argtext)}
                try: result=tools.call(name,args)
                except Exception as e: result={"status":"TOOL_ERROR","error":str(e),"tool":name}
                messages.append({"role":"tool","tool_call_id":call.get("id") or f"call-{tool_calls}","name":name,"content":json.dumps(result,ensure_ascii=False)})
            continue

        # Plain JSON remains supported for models/providers that choose not to use the submission tool.
        final=parse_json_object(str(msg.get("content") or ""))
        if final is not None:
            try:
                normalized=_normalize_payload(final, oid)
                return _record(
                    result=normalized,
                    usage=usage,
                    tools=tools,
                    raw_turns=raw_turns,
                    resolved_models=resolved_models,
                    provider_values=provider_values,
                    turns=turn+1,
                    tool_calls=tool_calls,
                    finish_reasons=finish_reasons,
                    truncated_response_count=truncated_response_count,
                    finalization_mode="plain_json",
                    validation_errors=validation_errors,
                )
            except Exception as e:
                validation_errors.append(f"plain JSON validation failed: {type(e).__name__}: {e}")

        if not force_finalize:
            messages.append({
                "role":"user",
                "content":(
                    "Your last response was not a valid final gate decision. Continue only if material evidence is still missing; "
                    "otherwise call submit_gate_decision now. If you cannot call it, return ONLY valid JSON matching this schema: "
                    + json.dumps(OUTPUT_SCHEMA)
                ),
            })

    # Last-resort structured-output call. This removes incidental JSON-formatting failures from
    # the semantic benchmark while preserving the model's entire investigation history.
    final_body={
        "model":config.model,
        "messages":messages + [{
            "role":"user",
            "content":"Investigation is over. Return the final DGF gate decision now. Do not call any more tools."
        }],
        "session_id":session_id,
        "usage":{"include":True},
    }
    _apply_common_params(final_body, config, params)
    if "response_format" in params or "structured_outputs" in params:
        final_body["response_format"] = structured_response_format()
    try:
        resp=client.chat(final_body)
    except OpenRouterError as e:
        fail(f"OpenRouter finalization request failed: {e}", "infrastructure", config.max_turns)

    turn_usage=Usage.from_response(resp)
    usage.add(turn_usage)
    if resp.get("model"): resolved_models.append(str(resp["model"]))
    if resp.get("provider"): provider_values.append(resp["provider"])
    choices=resp.get("choices") or []
    if not choices:
        fail("No choices returned during structured finalization", "infrastructure", config.max_turns+1)
    choice=choices[0]
    finish_reason=choice.get("finish_reason")
    finish_reasons.append(finish_reason)
    if finish_reason in {"length", "max_tokens"}:
        truncated_response_count += 1
    msg=_clean_message(choice.get("message") or {})
    raw_turns.append({
        "turn":config.max_turns,
        "assistant":msg,
        "finish_reason":finish_reason,
        "usage":turn_usage.as_dict(),
        "resolved_model":resp.get("model"),
        "provider":resp.get("provider"),
        "structured_finalization":True,
    })
    final=parse_json_object(str(msg.get("content") or ""))
    if final is not None:
        try:
            normalized=_normalize_payload(final, oid)
            return _record(
                result=normalized,
                usage=usage,
                tools=tools,
                raw_turns=raw_turns,
                resolved_models=resolved_models,
                provider_values=provider_values,
                turns=config.max_turns+1,
                tool_calls=tool_calls,
                finish_reasons=finish_reasons,
                truncated_response_count=truncated_response_count,
                finalization_mode="structured_output_fallback",
                validation_errors=validation_errors,
            )
        except Exception as e:
            validation_errors.append(f"structured finalization validation failed: {type(e).__name__}: {e}")

    fail(
        f"Agent did not produce a valid typed gate decision after {config.max_turns} investigation turns plus structured finalization",
        "agent_protocol",
        config.max_turns+1,
    )
