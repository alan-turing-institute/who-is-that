import logging

from .ollama_query import OllamaQuery


def spoiler_check(context: str, summary: str) -> str:
    logger = logging.getLogger("backend.app")
    query = "CONTEXT: " + context + "\n" + "SUMMARY: " + summary + "\n" + (
        "INSTRUCTIONS: Check if the SUMMARY contains spoilers not containerd in CONTEXT. If so, provide a simple answer of '**TRUE**' or '**FALSE**'."
        "Respond as boolean in this JSON format: { \"answer\": [True or False]}")

    logger.info("Check for spoilers using %s tokens of context...", len(query.split()))
    response = OllamaQuery.query(context=query)
    answer = bool(response["message"]["content"]['answer'])
    logger.info("Response: %s", answer)
    if answer == True:
        logger.info("Spoiler detected! Regenerating new summary...")
    else:
        logger.info("No spoilers detected.")
    logger.info("Returning answer: %s", answer)
    return answer


def summarise(context: str, prompt_template: str) -> str:
    logger = logging.getLogger("backend.app")
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt_template}"
    logger.info(
        "Sending 'summarise' request using %s tokens of context...",
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)
    spoiler = spoiler_check(context, response["message"]["content"])

    if spoiler:
        response = OllamaQuery.query(context=concat)

    return response["message"]["content"]


def what_is_this(context: str, prompt_template: str, thing: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_template.replace(r"{thing}", thing)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'What is %s?' request using %s tokens of context...",
        thing,
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)

    spoiler = spoiler_check(context, response["message"]["content"])

    print('The spoiler response', spoiler, flush=True)
    print('The query response', response["message"]["content"], flush=True)

    if spoiler:
        response = OllamaQuery.query(context=concat)

    return response["message"]["content"]


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_template.replace(r"{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(
        "Sending 'Who is %s?' request using %s tokens of context...",
        character,
        len(concat.split()),
    )
    response = OllamaQuery.query(context=concat)

    spoiler = spoiler_check(context, response["message"]["content"])

    if spoiler:
        response = OllamaQuery.query(context=concat)

    return response["message"]["content"]
