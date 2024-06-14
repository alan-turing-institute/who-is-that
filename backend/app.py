from __future__ import annotations

import json
import logging
import pathlib

from flask import Flask, Response, jsonify, request

from .helpers import summarise, what_is_this, who_is_that

app = Flask(__name__)
for handler in app.logger.handlers:
    handler.setFormatter(
        logging.Formatter(r"%(asctime)s %(message)s", r"[%d/%b/%Y %H:%M:%S]"),
    )


# Load the prompt template once at the start of the application
data_dir = pathlib.Path(__file__).parent.resolve()
with pathlib.Path.open(data_dir / "prompts" / "input_prompts.json") as prompt_file:
    prompt_templates: dict[str, str] = json.load(prompt_file)


@app.route("/")
def index() -> str:
    return "Backend is running"


@app.route("/who_is_that", methods=["POST"])
def api_who_is_that() -> Response:
    data = request.json
    character: str = data.get("character", "")
    context: str = data.get("context", "")
    check_spoilers: bool = data.get("check_spoilers")
    app.logger.info(
        "Received 'who_is_that' request for '%s' using %s tokens of context.",
        character,
        len(context.split()),
    )
    if not character or not context:
        return jsonify({"error": "Character and context are required"}), 400

    try:
        result = who_is_that(
            context,
            prompt_templates,
            character,
            check_spoilers=check_spoilers,
        )
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/what_is_this", methods=["POST"])
def api_what_is_this() -> Response:
    data = request.json
    thing: str = data.get("thing", "")
    context: str = data.get("context", "")
    check_spoilers: bool = data.get("check_spoilers")
    app.logger.info(
        "Received 'what_is_this' request for '%s' using %s tokens of context.",
        thing,
        len(context.split()),
    )

    if not context:
        return jsonify({"error": "Context is required"}), 400

    try:
        result = what_is_this(
            context,
            prompt_templates,
            thing,
            check_spoilers=check_spoilers,
        )
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summarise", methods=["POST"])
def api_summarise() -> Response:
    data = request.json
    context: str = data.get("context", "")
    check_spoilers: bool = data.get("check_spoilers")
    app.logger.info(
        "Received 'summarise' request using %s tokens of context.",
        len(context.split()),
    )

    if not context:
        return jsonify({"error": "Context is required"}), 400
    try:
        result = summarise(context, prompt_templates, check_spoilers=check_spoilers)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
