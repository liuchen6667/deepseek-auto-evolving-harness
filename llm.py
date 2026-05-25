"""
流式 LLM 客户端
纯文本流式请求，带指数退避重试。
"""

import json
import time
import random
import requests
from dataclasses import dataclass, field
from config import BASE_URL, HEADERS, MODEL, MAX_TOKENS, TEMPERATURE


@dataclass
class ToolCall:
    """一次工具调用"""
    id: str
    name: str
    arguments: str

    @property
    def args(self) -> dict:
        return json.loads(self.arguments)


@dataclass
class LLMResponse:
    """LLM 完整响应"""
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


def stream_chat(messages: list[dict], on_delta: callable = None) -> LLMResponse:
    """
    流式调用 LLM，实时通过 on_delta 回调输出文本片段。
    内置指数退避重试（网络错误、429、5xx）。
    """
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": True,
    }

    for attempt in range(4):
        try:
            return _do_stream(payload, on_delta)
        except (requests.exceptions.RequestException, ConnectionError) as e:
            if attempt == 3:
                raise
            delay = min(2 ** attempt, 16) + random.uniform(0, 1)
            time.sleep(delay)

    raise RuntimeError("unreachable")


def _do_stream(payload: dict, on_delta: callable) -> LLMResponse:
    """执行一次流式请求"""
    response = LLMResponse()

    with requests.post(
        f"{BASE_URL}/chat/completions",
        headers=HEADERS,
        json=payload,
        stream=True,
        timeout=120,
    ) as resp:
        if resp.status_code in (429, 500, 502, 503, 529):
            raise requests.exceptions.RequestException(f"HTTP {resp.status_code}")
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            data = line[6:]
            if data == "[DONE]":
                break

            chunk = json.loads(data)
            if not chunk.get("choices"):
                continue
            delta = chunk["choices"][0].get("delta", {})

            if delta.get("content"):
                response.content += delta["content"]
                if on_delta:
                    on_delta(delta["content"])

    return response
