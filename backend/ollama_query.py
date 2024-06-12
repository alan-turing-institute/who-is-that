from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from typing import Any, Mapping, Self

from ollama import Client, ResponseError

class OllamaQuery:
    logger = logging.getLogger("backend.app")

    @classmethod
    def query(
        cls: type[Self],
        context: str,
    ) -> Mapping[str, Any] | Iterator[Mapping[str, Any]]:

        # Load the model
        model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
        cls.logger.info(f"Querying Ollama using model {model}")

        # Set up connection to Ollama
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11434")
        ollama_server = f"{ollama_host}:{ollama_port}"
        client = Client(host=ollama_server)
        cls.logger.info(f"Using Ollama server at {ollama_server}")

        # Query Ollama
        try:
            response = client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": context,
                    },
                ],
            )
            cls.logger.info(f"Loading the model: {response['load_duration']/1e9:.2f}s")
            cls.logger.info(f"Evaluating the prompt: {response['prompt_eval_duration']/1e9:.2f}s")
            cls.logger.info(f"Evaluating the response: {response['eval_duration']/1e9:.2f}s")
            cls.logger.info(f"Total time: {response['total_duration']/1e9:.2f}s")
        except ResponseError as exc:
            cls.logger.info(f"No response from Ollama server: '{exc}'")
            response = {"message": {"content": "No response from Ollama server."}}
        return response
