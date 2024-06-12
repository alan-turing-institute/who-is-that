from .ollama_query import OllamaQuery


def spoiler_check(book: str, character: str, summary: str) -> str:

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

    response = OllamaQuery.query(context=query)
    answer = response["message"]["content"]
    if "true" in answer or "True" in answer or "TRUE" in answer:
        print("Spoiler detected! Regenerating summary...")
        return answer
    if "false" in answer or "False" in answer or "FALSE" in answer:
        print("No spoilers detected.")
        return summary
    raise ValueError("Unexpected response from spoiler detection: " + answer)


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    try:
        response = OllamaQuery.query(context=concat)
        content = response["message"]["content"]

        # content = spoiler_check(context, character, content)

    except Exception as exc:
        print(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content


def generate_summary(context: str) -> str:
    prompt = f"CONTEXT: {context}. \n INSTRUCTIONS: Summarize the story so far in 100 words or less. Do not reveal spoilers for later sections of the story."
    try:
        print("Waiting for an Ollama response.", flush=True)
        response = OllamaQuery.query(context=prompt)
        content = response["message"]["content"]

    except Exception as exc:
        print(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content
