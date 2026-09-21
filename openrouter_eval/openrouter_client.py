from __future__ import annotations
import json, os, time, random
from dataclasses import dataclass
from typing import Any
from urllib import request, error
from .env_loader import require_api_key, load_dotenv

BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(RuntimeError):
    pass


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    cached_tokens: int = 0
    cost: float = 0.0

    @classmethod
    def from_response(cls, payload: dict[str, Any]) -> "Usage":
        u = payload.get("usage") or {}
        ctd = u.get("completion_tokens_details") or {}
        ptd = u.get("prompt_tokens_details") or {}
        return cls(
            prompt_tokens=int(u.get("prompt_tokens") or 0),
            completion_tokens=int(u.get("completion_tokens") or 0),
            total_tokens=int(u.get("total_tokens") or 0),
            reasoning_tokens=int(ctd.get("reasoning_tokens") or 0),
            cached_tokens=int(ptd.get("cached_tokens") or 0),
            cost=float(u.get("cost") or 0.0),
        )

    def add(self, other: "Usage") -> None:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        self.reasoning_tokens += other.reasoning_tokens
        self.cached_tokens += other.cached_tokens
        self.cost += other.cost

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class OpenRouterClient:
    def __init__(self, api_key: str | None = None, timeout: int = 180, retries: int = 5):
        load_dotenv()
        self.api_key = api_key or require_api_key()
        self.timeout = timeout
        self.retries = retries
        self.http_referer = os.environ.get("OPENROUTER_HTTP_REFERER", "")
        self.x_title = os.environ.get("OPENROUTER_X_TITLE", "DGF-Bench")

    def _headers(self, auth: bool = True) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if auth:
            h["Authorization"] = f"Bearer {self.api_key}"
        if self.http_referer:
            h["HTTP-Referer"] = self.http_referer
        if self.x_title:
            h["X-Title"] = self.x_title
        return h

    def _json_request(self, method: str, path: str, body: dict | None = None, auth: bool = True) -> dict:
        url = BASE_URL + path
        data = None if body is None else json.dumps(body).encode("utf-8")
        last = None
        for attempt in range(self.retries + 1):
            req = request.Request(url, data=data, headers=self._headers(auth), method=method)
            try:
                with request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
            except error.HTTPError as e:
                raw = e.read().decode("utf-8", errors="replace")
                last = f"HTTP {e.code}: {raw[:2000]}"
                if e.code not in (408, 409, 429, 500, 502, 503, 504) or attempt >= self.retries:
                    raise OpenRouterError(last) from e
            except (error.URLError, TimeoutError) as e:
                last = str(e)
                if attempt >= self.retries:
                    raise OpenRouterError(last) from e
            delay = min(30.0, (2 ** attempt) + random.random())
            time.sleep(delay)
        raise OpenRouterError(last or "OpenRouter request failed")

    def list_models(self) -> list[dict[str, Any]]:
        payload = self._json_request("GET", "/models", None, auth=True)
        return list(payload.get("data") or [])

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(payload)
        payload.setdefault("usage", {"include": True})
        return self._json_request("POST", "/chat/completions", payload, auth=True)
