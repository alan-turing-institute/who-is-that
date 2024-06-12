from __future__ import annotations

import json
import logging
import os

import requests
from flask import Request


def get_context(selected_text: str, request: Request) -> tuple[str, str]:
    logger = logging.getLogger("frontend.app")
    logger.info("Constructing context up to: '%s'", selected_text)
    selected_text_start = int(request.form["selected_text_start"])
    concatenated_text = request.form["concatenated_text"]
    # Use the start position to slice the concatenated text
    summary = concatenated_text[: selected_text_start + len(selected_text)]
    logger.info("Constructed context of %s characters.", len(summary))
    return summary, concatenated_text


def query_backend(character: str, context: str, action: str = "who_is_that") -> dict:
    logger = logging.getLogger("frontend.app")

    # Define the URL of your API endpoint
    backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
    backend_port = os.environ.get("BACKEND_PORT", "3000")
    if action == "who_is_that":
        url = f"{backend_host}:{backend_port}/who_is_that"
    else:
        url = f"{backend_host}:{backend_port}/summarise"

    # Create the payload
    payload = {"character": character, "context": context}

    # Send the POST request
    try:
        logger.info("Sending request to backend at '%s'", url)
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        result = response.json()
    except Exception as exc:
        logger.warning("Failed to extract output: %s", exc)
        result = {"result": "Unknown"}

    return result
