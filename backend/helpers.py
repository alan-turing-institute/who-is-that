import logging

from .ollama_query import OllamaQuery


def spoiler_check(context: str, summary: str) -> bool:
    logger = logging.getLogger("backend.app")
    query = (
        f"CONTEXT: {context}\n"
        f"SUMMARY: {summary}\n"
        "INSTRUCTIONS: Check if the SUMMARY contains spoilers not found in the CONTEXT.\n"
        'Respond as a python boolean in this JSON format: { "answer": True/False }. No yapping!'
    )

    logger.info("Check for spoilers using %s tokens of context...", len(query.split()))
    response = OllamaQuery.query(context=query)["message"]["content"]
    logger.info("Response: %s", response)
    if '{"answer": True }' in response:
        logger.info("Spoiler detected! Regenerating new summary...")
        return True
    logger.info("No spoilers detected.")
    return False


def summarise(context: str, prompt_template: str) -> str:
    logger = logging.getLogger("backend.app")
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt_template}"
    logger.info(
        "Sending 'summarise' request using %s tokens of context...",
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)["message"]["content"]

    if spoiler_check(context, response):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response


def what_is_this(context: str, prompt_template: str, thing: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_template.replace(r"{thing}", thing)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'What is %s?' request using %s tokens of context...",
        thing,
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)["message"]["content"]

    if spoiler_check(context, response):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_template.replace(r"{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'Who is %s?' request using %s tokens of context...",
        character,
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)["message"]["content"]

    if spoiler_check(context, response):
        logger.warning("Found a spoiler, rerunning...")
        response = OllamaQuery.query(context=concat)["message"]["content"]

    return response
