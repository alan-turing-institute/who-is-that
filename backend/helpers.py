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

    logger.info(f"Check for spoilers using a {len(query)} character context...")
    response = OllamaQuery.query(context=query)
    answer = response["message"]["content"]
    if "true" in answer or "True" in answer or "TRUE" in answer:
        logger.info("Spoiler detected! Regenerating summary...")
        return answer
    if "false" in answer or "False" in answer or "FALSE" in answer:
        logger.info("No spoilers detected.")
        return summary
    raise ValueError("Unexpected response from spoiler detection: " + answer)


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    logger = logging.getLogger("backend.app")
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    logger.info(f"Answer 'Who is {character}?' using a {len(concat)} character context...")
    try:
        response = OllamaQuery.query(context=concat)
        content = response["message"]["content"]

        # content = spoiler_check(context, character, content)

    except Exception as exc:
        logger.info(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content


def generate_summary(context: str) -> str:
    logger = logging.getLogger("backend.app")
    logger.info(f"Generating a summary for {len(context)} character context...")
    prompt = f"CONTEXT: {context}. \n INSTRUCTIONS: Summarize the story so far in 100 words or less. Do not reveal spoilers for later sections of the story."
    try:
        response = OllamaQuery.query(context=prompt)
        content = response["message"]["content"]

    except Exception as exc:
        logger.info(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content
