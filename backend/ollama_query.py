from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any, Mapping

from ollama import Client


class OllamaQuery:
    def __init__(self) -> None:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11434")
        self.client = Client(host=f"{ollama_host}:{ollama_port}")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3:8b")

    def query(self, messages: list[dict[str, str]]) -> Mapping[str, Any] | Iterator[Mapping[str, Any]]:
        print(f"Querying Ollama using model {self.model}")
        return self.client.chat(
            model=self.model,
            messages=messages,
        )
