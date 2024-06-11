from flask import Flask, request, jsonify
from .helpers import who_is_that
import pathlib

app = Flask(__name__)

# Load the prompt template once at the start of the application
data_dir = pathlib.Path(__file__).parent.resolve()
with open(data_dir / "prompts" / "input_prompt.txt", "r") as prompt_file:
    prompt_template = prompt_file.read()


@app.route("/")
def index():
    return "Backend is running"


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
