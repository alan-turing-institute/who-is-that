from __future__ import annotations

import logging
import os
from typing import Self

from ollama import ChatResponse, Client, ResponseError


class OllamaQuery:
    logger = logging.getLogger("backend.app")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
    ollama_port = os.environ.get("OLLAMA_PORT", "11434")
    ollama_server = f"{ollama_host}:{ollama_port}"
    client = Client(host=ollama_server)

    @classmethod
    def query(cls: type[Self], context: str) -> ChatResponse:

        # Load the model
        context_length = len(context.split())
        if context_length > 8000:
            model = os.environ.get("OLLAMA_MODEL", "yarn-mistral:7b-128k")
        else:
            model = os.environ.get("OLLAMA_MODEL", "llama3:8b")

        # Ensure that this model is installed
        cls.ensure_model(model)

        # Set up connection to Ollama
        cls.logger.info("Querying Ollama using:")
        cls.logger.debug("... model: %s", model)
        cls.logger.debug("... server: %s", cls.ollama_server)
        cls.logger.debug("... tokens: %s", context_length)

        # Query Ollama
        try:
            response = cls.client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": context,
                    },
                ],
            )
            cls.logger.info(
                "Received response from Ollama server after %s",
                f"{(response['total_duration'] / 1e9):.2f}s",
            )
            cls.logger.debug(
                "... loading the model: %s",
                f"{(response['load_duration'] / 1e9):.2f}s",
            )
            cls.logger.debug(
                "... evaluating the prompt: %s",
                f"{(response['prompt_eval_duration'] / 1e9):.2f}s",
            )
            cls.logger.debug(
                "... evaluating the response: %s",
                f"{(response['eval_duration'] / 1e9):.2f}s",
            )
        except ResponseError as exc:
            msg = "No response from Ollama server."
            cls.logger.warning("%s '%s'", msg, exc)
            response: ChatResponse = {
                "message": {"content": msg},
            }
        return response

    @classmethod
    def ensure_model(cls: type[Self], model_name: str) -> None:
        available_models = [model["name"] for model in cls.client.list()["models"]]
        if model_name not in available_models:
            cls.logger.info("Available Ollama models: %s", available_models)
            cls.logger.info("Pulling Ollama model: %s", model_name)
            cls.logger.warning("This is likely to be slow (5-10 minutes)...")
            cls.client.pull(model_name)
