import base64
import io
import json
import os

import requests
from flask import Flask, render_template, request
from PIL import Image

from .extract import Extractor
from .summarise import get_context

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/", methods=["POST"])
def load_file() -> str:
    uploaded_file = request.files["file"]
    print(f"Loading file {uploaded_file.filename}", flush=True)

    filestream = uploaded_file.stream
    filestream.seek(0)
    extractor = Extractor.from_bytes(filestream.read())

    text_items = extractor.text_content  # This should be a list of tuples or strings
    authors_list = extractor.authors
    authors = ", ".join(authors_list)
    title = extractor.title

    # If text_items is a list of tuples, extract the text
    if isinstance(text_items[0], tuple):
        text_items = [content for _, content in text_items]

    # Concatenate all text content into a single string
    concatenated_text = "\n".join(text_items)

    cover_url = None
    if extractor.cover:
        image = Image.open(io.BytesIO(extractor.cover))
        img_io = io.BytesIO()
        image.save(img_io, "JPEG")
        img_io.seek(0)
        cover_url = (
            f"data:image/jpeg;base64,{base64.b64encode(img_io.getvalue()).decode()}"
        )

    # Pass concatenated text as a hidden form input
    return render_template(
        "process.html",
        text_items=[
            ("Chapter " + str(idx), content)
            for idx, content in enumerate(text_items, start=1)
        ],
        concatenated_text=concatenated_text,
        title=title,
        author=authors,
        cover_url=cover_url,
    )


@app.route("/summarise", methods=["POST"])
def summarise() -> str:
    option = request.form["option"]
    selected_text = request.form["selected_text"]
    print(f"Calling '{option}' on '{selected_text}'", flush=True)

    author = request.form["author"]
    title = request.form["title"]
    summary, concatenated_text = get_context(selected_text, request)

    # Define the URL of your API endpoint
    backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
    backend_port = os.environ.get("BACKEND_PORT", "3000")
    url = f"{backend_host}:{backend_port}/who_is_that"

    # Create the payload
    payload = {"character": selected_text, "context": summary}

    # Send the POST request
    try:
        print(f"Sending request to backend at '{url}'...", flush=True)
        response_who_is_that = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        result = response_who_is_that.json()
    except Exception as exc:
        print(f"Failed to extract output {exc!s}")
        result = "Unknown"

    if option == "who_is_that":
        return render_template(
            "process.html",
            text_items=[(f"Who is {selected_text}", result)],
            concatenated_text=concatenated_text,
            title=title,
            author=author,
        )

    if option == "what_is_this":
        return render_template(
            "process.html",
            text_items=[(f"What is {selected_text}?", result)],
            concatenated_text=concatenated_text,
            title=title,
            author=author,
        )

    return render_template(
        "process.html",
        text_items=[("Summary", result)],
        concatenated_text=concatenated_text,
        title=title,
        author=author,
    )


if __name__ == "__main__":
    app.run(debug=True)
