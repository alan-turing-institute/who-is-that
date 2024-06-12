from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any, Mapping, Self

from ollama import Client


class OllamaQuery:
    def __init__(self: Self) -> None:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11434")
        self.client = Client(host=f"{ollama_host}:{ollama_port}")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3:8b")

    def query(
        self: Self,
        messages: list[dict[str, str]],
    ) -> Mapping[str, Any] | Iterator[Mapping[str, Any]]:
        print(f"Querying Ollama using model {self.model}", flush=True)
        response = self.client.chat(
            model=self.model,
            messages=messages,
        )
        print(f"Loading the model: {response['load_duration']/1e9:.2f}s", flush=True)
        print(f"Evaluating the prompt: {response['prompt_eval_duration']/1e9:.2f}s", flush=True)
        print(f"Evaluating the response: {response['eval_duration']/1e9:.2f}s", flush=True)
        print(f"Total time: {response['total_duration']/1e9:.2f}s", flush=True)
        return response
