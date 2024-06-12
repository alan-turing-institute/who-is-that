from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any, Mapping, Self

from ollama import Client


class OllamaQuery:
    @classmethod
    def query(
        cls: type[Self],
        messages: list[dict[str, str]],
    ) -> Mapping[str, Any] | Iterator[Mapping[str, Any]]:

        model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
        print(f"Querying Ollama using model {model}", flush=True)

        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11434")
        ollama_server = f"{ollama_host}:{ollama_port}"
        client = Client(host=ollama_server)
        print(f"Using Ollama server at {ollama_server}", flush=True)
        try:
            response = client.chat(
                model=model,
                messages=messages,
            )
            print(f"Loading the model: {response['load_duration']/1e9:.2f}s", flush=True)
            print(f"Evaluating the prompt: {response['prompt_eval_duration']/1e9:.2f}s", flush=True)
            print(f"Evaluating the response: {response['eval_duration']/1e9:.2f}s", flush=True)
            print(f"Total time: {response['total_duration']/1e9:.2f}s", flush=True)
        except Exception as exc:
            print(f"Caught exception of type {type(exc)}")
            response = {"message": {"content": "No response from Ollama slower."}}
        return response
