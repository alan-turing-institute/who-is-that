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
        context_length = len(context.split())
        if context_length > 8000:
            model = os.environ.get("OLLAMA_MODEL", "yarn-mistral:7b-128k")
        else:
            model = os.environ.get("OLLAMA_MODEL", "llama3:8b")

        # Set up connection to Ollama
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
        ollama_port = os.environ.get("OLLAMA_PORT", "11434")
        ollama_server = f"{ollama_host}:{ollama_port}"
        client = Client(host=ollama_server)
        cls.logger.info("Preparing to query Ollama using:")
        cls.logger.info("... model: %s", model)
        cls.logger.info("... server: %s", ollama_server)

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
            cls.logger.info("Received response from Ollama server")
            load_duration = f"{(response['load_duration'] / 1e9):.2f}s"
            cls.logger.info("... Loading the model: %s", load_duration)
            prompt_eval_duration = f"{(response['prompt_eval_duration'] / 1e9):.2f}s"
            cls.logger.info("... Evaluating the prompt: %s", prompt_eval_duration)
            eval_duration = f"{(response['eval_duration'] / 1e9):.2f}s"
            cls.logger.info("... Evaluating the response: %s", eval_duration)
            total_duration = f" {(response['total_duration'] / 1e9):.2f}s"
            cls.logger.info("--> Total time: %s", total_duration)
        except ResponseError as exc:
            cls.logger.info("No response from Ollama server: '%s'", exc)
            response = {"message": {"content": "No response from Ollama server."}}
        return response
