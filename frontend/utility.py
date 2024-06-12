from __future__ import annotations

import json
import logging
import os

import requests


def query_backend(character: str, context: str, action: str = "who_is_that") -> dict:
    logger = logging.getLogger("frontend.app")

    # Define the URL of your API endpoint
    backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
    backend_port = os.environ.get("BACKEND_PORT", "3000")
    if action == "who_is_that":
        url = f"{backend_host}:{backend_port}/who_is_that"
    elif action == "what_is_this":
        url = f"{backend_host}:{backend_port}/what_is_this"
    else:
        url = f"{backend_host}:{backend_port}/summarise"

    # Create the payload
    payload = {"character": character, "context": context}

    # Send the POST request
    try:
        logger.info("Sending '%s' request to backend at '%s'", action, url)
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
