from __future__ import annotations

import json
import logging
import os

import requests


class BackendQuery:
    logger = logging.getLogger("frontend.app")

    @classmethod
    def query(selected_text: str, context: str, action: str = "summarise") -> dict:
        logger = logging.getLogger("frontend.app")

        # Define the base URL of your API endpoint
        backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
        backend_port = os.environ.get("BACKEND_PORT", "3000")
        base_url = f"{backend_host}:{backend_port}"

        # Define the URL and payload for your API endpoint
        if action == "who_is_that":
            url = f"{base_url}/who_is_that"
            payload = {"character": selected_text, "context": context}
        elif action == "what_is_this":
            url = f"{base_url}/what_is_this"
            payload = {"thing": selected_text, "context": context}
        else:
            url = f"{base_url}/summarise"
            payload = {"character": selected_text, "context": context}

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
