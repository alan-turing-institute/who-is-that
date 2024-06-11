from flask import Flask, render_template, request
from .extract import Extractor
from PIL import Image
import io
import base64
import json
import os
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/", methods=["POST"])
def load_file():
    uploaded_file = request.files["file"]
    print(f"Loading file {uploaded_file.filename}")

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

    concatenated_text = "\n".join(text_items)  # Concatenate all text content into a single string

    cover_url = None
    if extractor.cover:
        image = Image.open(io.BytesIO(extractor.cover))
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        cover_url = f"data:image/jpeg;base64,{base64.b64encode(img_io.getvalue()).decode()}"

    # Pass concatenated text as a hidden form input
    return render_template(
        "process.html",
        text_items=[("Chapter " + str(i+1), content) for i, content in enumerate(text_items)],
        concatenated_text=concatenated_text,
        title=title,
        author=authors,
        cover_url=cover_url
    )

def get_context(selected_text,request):
    selected_text_start = int(request.form["selected_text_start"])
    print(f"Finishing at position: {selected_text_start}")
    concatenated_text = request.form["concatenated_text"]

    print(f"Summarising up to: {selected_text} starting at position: {selected_text_start}")

    # Use the start position to slice the concatenated text
    summary = concatenated_text[:selected_text_start + len(selected_text)]

    return summary, concatenated_text

@app.route("/summarise", methods=["POST"])
def summarise():
    option = request.form["option"]
    selected_text = request.form["selected_text"]
    print(f"Summarising up to: {selected_text}")

    author = request.form["author"]
    title = request.form["title"]
    summary, concatenated_text = get_context(selected_text, request)

    # Define the URL of your API endpoint
    backend_host = os.environ.get("BACKEND_HOST", "http://localhost")
    backend_port = os.environ.get("BACKEND_PORT", "3000")
    url = f"{backend_host}:{backend_port}/who_is_that"

    # Create the payload
    # Load context from file
    context = 'EXAMPLSE SOMETHING'

    # Define the character
    character = "Mr. Wickham"

    payload = {
        'character': character,
        'context': context
    }
    # Send the POST request
    try:
        app.logger.info(f"Sending request to backend at '{url}'...")
        response_who_is_that = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    except Exception as exc:
        print("Exception!!!!!!!!!!!!", flush=True)
        print(payload["character"], flush=True)
        print(url, flush=True)
        print(f"Exception of type {type(exc)}", flush=True)


    if option == "what_is_this" or option == "who_is_that":

        result = response_who_is_that.json()
        return render_template("process.html", text_items=[("What is this place?", result)], concatenated_text=concatenated_text, title=title, author=author)

    else:
        return render_template("process.html", text_items=[("Summary", summary)], concatenated_text=concatenated_text, title=title, author=author)

if __name__ == "__main__":
    app.run(debug=True)
