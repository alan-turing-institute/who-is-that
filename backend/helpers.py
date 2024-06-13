import logging

from .ollama_query import OllamaQuery


def spoiler_check(book: str, character: str, summary: str) -> str:
    logger = logging.getLogger("backend.app")
    query = "I have written the following story: '" + book + "'.\n"
    query += " I have used the word '" + character + "' in the story.\n"
    query += (
        " Determine whether the following summary contains spoilers or additional informantion about "
        + character
        + ".\n"
    )
    query += summary + "\n"
    query += " Provide a simple answer of 'true' or 'false'."
    query += " If so, please provide another summary without spoilers."

    logger.info("Check for spoilers using %s tokens of context...", len(query.split()))
    response = OllamaQuery.query(context=query)
    answer = response["message"]["content"]
    if "true" in answer or "True" in answer or "TRUE" in answer:
        logger.info("Spoiler detected! Regenerating summary...")
        return answer
    if "false" in answer or "False" in answer or "FALSE" in answer:
        logger.info("No spoilers detected.")
        return summary
    raise ValueError("Unexpected response from spoiler detection: " + answer)


def summarise(context: str, prompt_template: str) -> str:
    logger = logging.getLogger("backend.app")
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt_template}"
    logger.info(
        "Sending 'summarise' request using %s tokens of context...",
        len(concat.split()),
    )
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
    return response["message"]["content"]
