import os
import pathlib
import time

import yaml
from ollama import Client

ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
ollama_port = os.environ.get("OLLAMA_PORT", "11434")
client = Client(host=f"{ollama_host}:{ollama_port}")

# Load the yaml file as a global variable
data_dir = pathlib.Path(__file__).parent.resolve()
with pathlib.Path.open(data_dir / "spoilerdb" / "database.yml") as database_file:
    db = yaml.safe_load(database_file)


def character_or_place(word: str, text: str) -> str:
    """Determine whether the word in the text is about a character or a place.
    """
    model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
    query = "I have written the following story: '" + text + "'."
    query += " I have used the word '" + word + "' in the story."
    query += " Determine whether this word refers to a character or a place."
    query += " Provide a simple answer of 'character' or 'place' or 'neither'."
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    if "character" in response["message"]["content"]:
        return "character"
    if "place" in response["message"]["content"]:
        return "place"
    return "neither"


def spoiler_check(book: str, character: str, summary: str, model: str) -> bool:
    if book not in db or character not in db[book]["characters"]:
        return "No spoilers in the database for " + character + " in " + book + "."
    query = "Read the following summary of " + character
    query += " from '" + book + "' by " + db[book]["author"] + ": '" + summary
    query += "'. Check to see whether the following spoiler is present: '"
    query += db[book]["characters"][character]["spoilers"][0] + "'. "
    query += "Give me a simple true or false answer."
    response = client.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    answer = response["message"]["content"]
    if "true" in answer or "True" in answer or "TRUE" in answer:
        print("Spoiler detected! Regenerating summary...")
        return True
    if "false" in answer or "False" in answer or "FALSE" in answer:
        return False
    raise ValueError("Unexpected response from spoiler detection: " + answer)


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    try:
        print("Waiting for an Ollama response.", flush=True)
        response = client.chat(
            model="llama3:8b",
            messages=[
                {
                    "role": "user",
                    "content": concat,
                },
            ],
        )
        content = response["message"]["content"]
    except Exception as exc:
        print(f"Failed to retrieve summary from Ollama {exc!s}")
        response = {"message": {"content": "some text here"}}
        content = "Sorry, I could not answer your query."
    return content


def who_is_that_really(
    text: str, book: str, bookmark: str, word: str, clicked: str = "whoisthat",
) -> str:
    """Get a summary of the character's actions up to the bookmark in the text.
    This function uses the LLM to generate a summary from the supplied text.
    """
    word_type = character_or_place(word, text)

    def generate_summary() -> str:
        model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
        print(f"Using model {model}", flush=True)

        prepend_str = ""
        query = "I have written the following story: '" + text + "'."
        query += " Read up to the end of " + bookmark + "."
        if word_type == "character" and clicked != "summary":
            if clicked == "whatisthat":
                prepend_str += (
                    "Clicked a character, not a place. Running whoisthat instead... "
                )
            query += " Describe what " + word + " has done so far in 15 word or less."
            query += " Focus on key events and actions taken by this character."
        elif word_type == "place" and clicked != "summary":
            if clicked == "whoisthat":
                prepend_str = (
                    "Clicked a place, not a character. Running whatisthat instead... "
                )
            query += (
                " Create a description of the location '"
                + word
                + "' in 15 word or less."
            )
        else:
            query += " Describe the story so far in 15 word or less."
        query += " Do not reveal spoilers for later sections of the story."
        try:
            print("Waiting for an Ollama response.", flush=True)
            response = client.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
            )
            content = response["message"]["content"]
        except Exception as exc:
            print(f"Failed to retrieve summary from Ollama {exc!s}", flush=True)
            response = {"message": {"content": "some text here"}}
            content = "Sorry, I could not answer your query."
        return prepend_str + content

    summary = generate_summary()
    if word_type == "character":
        start_time = time.time()
        has_spoiler = spoiler_check(book, word, summary)
        while has_spoiler:
            summary = generate_summary()
            has_spoiler = spoiler_check(book, word, summary)
            # Check if the time has exceeded 10 seconds
            if time.time() - start_time >= 10:
                break
    return summary
