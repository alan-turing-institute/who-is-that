from __future__ import annotations
import logging

from flask import Request


def get_context(selected_text: str, request: Request) -> tuple[str, str]:
    logger = logging.getLogger("frontend.app")
    logger.info(f"Constructing context up to: '{selected_text}'")
    selected_text_start = int(request.form["selected_text_start"])
    concatenated_text = request.form["concatenated_text"]
    # Use the start position to slice the concatenated text
    summary = concatenated_text[: selected_text_start + len(selected_text)]
    logger.info(f"Constructed context of {len(summary)} characters.")
    return summary, concatenated_text
