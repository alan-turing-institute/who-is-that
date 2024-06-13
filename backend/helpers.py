from __future__ import annotations

import json
import logging

from .ollama_query import OllamaQuery


def spoiler_check(context: str, summary: str, prompt_templates: dict[str, str]) -> bool:
    logger = logging.getLogger("backend.app")
    prompt = prompt_templates["spoilers"]
    concat = f"CONTEXT: {context} \n SUMMARY: {summary} \n INSTRUCTIONS: {prompt}"
    logger.info("Check for spoilers using %s tokens of context...", len(concat.split()))
    response = OllamaQuery.query(context=concat)["message"]["content"]
    try:
        answer = json.loads(response)
        if answer["answer"]:
            logger.info("Spoiler detected! Regenerating new summary...")
            return True
    except json.decoder.JSONDecodeError:
        logger.info("Malformed response: %s", response)
        return True
    logger.info("No spoilers detected.")
    return False


def summarise(context: str, prompt_templates: dict[str, str]) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_templates["summarise"]
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'summarise' request using %s tokens of context...",
        len(concat.split()),
    )

    response = OllamaQuery.query(context=concat)["message"]["content"]
    while spoiler_check(context, response, prompt_templates):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response


def what_is_this(context: str, prompt_templates: dict[str, str], thing: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_templates["what_is_this"].replace(r"{thing}", thing)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'What is %s?' request using %s tokens of context...",
        thing,
        len(concat.split()),
    )

    response = OllamaQuery.query(context=concat)["message"]["content"]
    while spoiler_check(context, response, prompt_templates):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response


def who_is_that(context: str, prompt_templates: dict[str, str], character: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_templates["who_is_that"].replace(r"{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'Who is %s?' request using %s tokens of context...",
        character,
        len(concat.split()),
    )

    response = OllamaQuery.query(context=concat)["message"]["content"]
    while spoiler_check(context, response, prompt_templates):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response
