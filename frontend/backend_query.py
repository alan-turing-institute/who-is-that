from __future__ import annotations

import json
import logging
import os
import time
from typing import Self

import requests


class BackendQuery:
    logger = logging.getLogger("frontend.app")
    backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
    backend_port = os.environ.get("BACKEND_PORT", "3000")
    base_url = f"{backend_host}:{backend_port}"

    @classmethod
    def query(
        cls: type[Self],
        selected_text: str,
        context: str,
        action: str = "summarise",
        timeout: float | None = None,
        *,
        check_spoilers: bool = True,
    ) -> dict[str, str]:
        logger = logging.getLogger("frontend.app")
        start_time = time.monotonic()

        # Define the URL and payload for your API endpoint
        payload = {"context": context, "check_spoilers": check_spoilers}
        if action == "who_is_that":
            url = f"{cls.base_url}/who_is_that"
            payload["character"] = selected_text
        elif action == "what_is_this":
            url = f"{cls.base_url}/what_is_this"
            payload["thing"] = selected_text
        else:
            url = f"{cls.base_url}/summarise"

        # Send the POST request
        try:
            logger.info(
                "Sending '%s' request to backend using %s tokens of context...",
                action,
                len(context.split()),
            )
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=timeout,
            )
            result = response.json()["result"]
        except requests.exceptions.ReadTimeout:
            logger.warning("Reached timeout of %ss while waiting for backend.", timeout)
            result = "Unknown"
        except Exception as exc:
            logger.warning("Failed to extract output: %s (%s)", exc, type(exc))
            result = "Unknown"

        duration = time.monotonic() - start_time
        return {"duration": duration, "result": result}
