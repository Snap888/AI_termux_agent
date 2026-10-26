"""
Model backends: OpenAI-compatible API, Ollama, llama.cpp
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
import httpx
from openai import OpenAI, AsyncOpenAI


class BaseModel:
    def chat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        raise NotImplementedError

    async def achat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        raise NotImplementedError


class OpenAICompatibleModel(BaseModel):
    def __init__(self, base_url: str, api_key: str, model_name: str, **kwargs):
        self.client = OpenAI(base_url=base_url, api_key=api_key or "no-key")
        self.async_client = AsyncOpenAI(base_url=base_url, api_key=api_key or "no-key")
        self.model_name = model_name
        self.extra = kwargs

    def chat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.extra.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", self.extra.get("max_tokens", 4096)),
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        return response.model_dump()

    async def achat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.extra.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", self.extra.get("max_tokens", 4096)),
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = await self.async_client.chat.completions.create(**params)
        return response.model_dump()


class OllamaModel(BaseModel):
    def __init__(self, host: str = "http://127.0.0.1:11434", model: str = "llama3.2"):
        self.host = host.rstrip("/")
        self.model = model

    def chat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        # Ollama native API (simplified, no full tool calling yet)
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
            },
        }
        with httpx.Client(timeout=120.0) as client:
            r = client.post(f"{self.host}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()

        # Convert to OpenAI-like format
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": data.get("message", {}).get("content", ""),
                },
                "finish_reason": "stop",
            }]
        }

    async def achat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        return self.chat(messages, tools, **kwargs)


class LlamaCppModel(BaseModel):
    """llama.cpp server (OpenAI compatible endpoint)"""

    def __init__(self, host: str = "http://127.0.0.1:8080", model_name: str = "local"):
        self.inner = OpenAICompatibleModel(
            base_url=f"{host.rstrip('/')}/v1",
            api_key="sk-no-key",
            model_name=model_name,
        )

    def chat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        return self.inner.chat(messages, tools, **kwargs)

    async def achat(self, messages: List[Dict], tools: Optional[List] = None, **kwargs) -> Dict:
        return await self.inner.achat(messages, tools, **kwargs)


def create_model(config: Dict) -> BaseModel:
    provider = config.get("model", {}).get("provider", "openai").lower()

    if provider == "ollama":
        local = config.get("local", {})
        return OllamaModel(
            host=local.get("ollama_host", "http://127.0.0.1:11434"),
            model=local.get("ollama_model", "llama3.2"),
        )
    elif provider == "llamacpp":
        local = config.get("local", {})
        return LlamaCppModel(host=local.get("llamacpp_host", "http://127.0.0.1:8080"))
    else:
        m = config.get("model", {})
        return OpenAICompatibleModel(
            base_url=m.get("base_url", "https://api.openai.com/v1"),
            api_key=m.get("api_key", ""),
            model_name=m.get("model_name", "gpt-4o"),
            temperature=m.get("temperature", 0.7),
            max_tokens=m.get("max_tokens", 4096),
        )
