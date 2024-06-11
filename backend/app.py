from flask import Flask, request, jsonify
from ollama import Client
import os
import yaml
import pathlib
import time

app = Flask(__name__)
ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost")
ollama_port = os.environ.get("OLLAMA_PORT", "11434")
client = Client(host=f"{ollama_host}:{ollama_port}")


# Load the prompt template once at the start of the application
data_dir = pathlib.Path(__file__).parent.resolve()
with open(data_dir / "prompts" / "input_prompt.txt", "r") as prompt_file:
    prompt_template = prompt_file.read()

# Load the yaml file as a global variable
with open(data_dir / "spoilerdb" / "database.yml", "r") as database_file:
    db = yaml.safe_load(database_file)


@app.route("/")
def index():
    return "Backend is running"


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    try:
        app.logger.info(f"Waiting for an Ollama response.")
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
        print(f"Failed to retrieve summary from Ollama {str(exc)}")
        response = {"message": {"content": "some text here"}}
        content = "Sorry, I could not answer your query."
    return content


def who_is_that_really(
    text: str, book: str, bookmark: str, word: str, clicked: str = "whoisthat"
) -> str:
    """
    Get a summary of the character's actions up to the bookmark in the text.
    This function uses the LLM to generate a summary from the supplied text.
    """
    word_type = character_or_place(word, text)

    def generate_summary():
        model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
        app.logger.info(f"Using model {model}")

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
            app.logger.info(f"Waiting for an Ollama response.")
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
            print(f"Failed to retrieve summary from Ollama {str(exc)}")
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
                pass
    return summary


def spoiler_check(book, character, summary, model):
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
    elif "false" in answer or "False" in answer or "FALSE" in answer:
        return False
    else:
        raise Exception("Unexpected response from spoiler detection: " + answer)


def character_or_place(word: str, text: str) -> str:
    """
    Determine whether the word in the text is about a character or a place.
    """
    model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
    app.logger.info(f"Using model {model}")
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
    elif "place" in response["message"]["content"]:
        return "place"
    else:
        return "neither"


@app.route("/who_is_that", methods=["POST"])
def api_who_is_that():
    data = request.json
    character = data.get("character")
    context = data.get("context")

    # TODO: get the text of the book up to this point and the book name for Ed's function
    # text = data.get("text")
    # book = data.get("book")
    # bookmark = data.get("context")
    # word = data.get("word")
    # clicked = data.get("clicked")

    if not character or not context:
        return jsonify({"error": "Character and context are required"}), 400

    try:
        # Fede func
        result = who_is_that(context, prompt_template, character)
        # Ed func
        # who_is_that_really('llama3', text, book, bookmark, word, clicked=clicked)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
