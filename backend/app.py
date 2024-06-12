import logging
import pathlib

from flask import Flask, Response, jsonify, request

from .helpers import generate_summary, who_is_that

app = Flask(__name__)
for handler in app.logger.handlers:
    handler.setFormatter(
        logging.Formatter(r"%(asctime)s %(message)s", r"[%d/%b/%Y %H:%M:%S]")
    )


# Load the prompt template once at the start of the application
data_dir = pathlib.Path(__file__).parent.resolve()
with pathlib.Path.open(data_dir / "prompts" / "input_prompt.txt") as prompt_file:
    prompt_template = prompt_file.read()


@app.route("/")
def index() -> str:
    return "Backend is running"


@app.route("/who_is_that", methods=["POST"])
def api_who_is_that() -> Response:
    data = request.json
    character: str = data.get("character", "")
    context: str = data.get("context", "")
    app.logger.info(
        "Received 'who_is_that' request for '%s' given %s tokens of context.",
        character,
        len(context.split()),
    )

    # TODO: get the text of the book up to this point and the book name for Ed's function
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


@app.route("/what_is_this", methods=["POST"])
def api_what_is_this() -> Response:
    data = request.json
    context = data.get("context")
    app.logger.info(
        "Received 'what_is_this' request given %s tokens of context.",
        len(context.split()),
    )

    # TODO: get the text of the book up to this point and the book name for Ed's function
    if not context:
        return jsonify({"error": "Context is required"}), 400
    try:
        # Fede func
        result = generate_summary(context)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summarise", methods=["POST"])
def api_summarise() -> Response:
    data = request.json
    context = data.get("context")
    app.logger.info(
        "Received 'summary' request given %s tokens of context.",
        len(context.split()),
    )

    # TODO: get the text of the book up to this point and the book name for Ed's function
    if not context:
        return jsonify({"error": "Context is required"}), 400
    try:
        # Fede func
        result = generate_summary(context)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
