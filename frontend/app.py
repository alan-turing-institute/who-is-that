import base64
import io
import logging

from flask import Flask, render_template, request
from PIL import Image

from .extract import Extractor
from .utility import query_backend

app = Flask(__name__)
for handler in app.logger.handlers:
    handler.setFormatter(
        logging.Formatter(r"%(asctime)s %(message)s", r"[%d/%b/%Y %H:%M:%S]")
    )


@app.route("/")
def index() -> str:
    return render_template("load.html")


@app.route("/", methods=["POST"])
def load_file() -> str:
    uploaded_file = request.files["file"]
    app.logger.info("Loading file '%s'", uploaded_file.filename)

    filestream = uploaded_file.stream
    filestream.seek(0)
    extractor = Extractor.from_bytes(filestream.read())

    chapters = extractor.chapters
    authors_list = extractor.authors
    authors = ", ".join(authors_list)
    title = extractor.title

    # Concatenate all text content into a single string
    concatenated_html = "\n".join(chapter.html for chapter in chapters)

    cover_url = None
    if extractor.cover:
        image = Image.open(io.BytesIO(extractor.cover))
        img_io = io.BytesIO()
        image.save(img_io, "JPEG")
        img_io.seek(0)
        cover_url = (
            f"data:image/jpeg;base64,{base64.b64encode(img_io.getvalue()).decode()}"
        )

    # Finished loading file
    app.logger.info(
        "Identified '%s' as '%s' with %s chapters.",
        uploaded_file.filename,
        title,
        len(chapters),
    )

    # Dummy Ollama query for the first time to load model into memory
    _ = query_backend("", "")
    app.logger.info("Ollama model is ready")

    # Render the template with appropriate inputs
    return render_template(
        "process.html",
        html_user_content=concatenated_html,
        title=title,
        author=authors,
        cover_url=cover_url,
    )


@app.route("/summarise", methods=["POST"])
def summarise() -> str:
    author = request.form["author"]
    option = request.form["option"]
    selected_text = request.form["selected_text"]
    selected_text_context = request.form["selected_text_context"]
    title = request.form["title"]
    app.logger.info(
        "Received '%s' request for '%s' given %s tokens of context.",
        option,
        selected_text,
        len(selected_text_context.split()),
    )

    # Who is that?
    if option == "who_is_that":
        result = query_backend(
            character=selected_text,
            context=selected_text_context,
            action=option,
        )["result"]
        return render_template(
            "process.html",
            html_user_content=f"<h1>Who is {selected_text}?</h1><p>{result}</p>",
            title=title,
            author=author,
        )

    # What is this?
    if option == "what_is_this":
        result = query_backend(
            character=selected_text,
            context=selected_text_context,
            action=option,
        )["result"]
        return render_template(
            "process.html",
            html_user_content=f"<h1>What is {selected_text}?</h1><p>{result}</p>",
            title=title,
            author=author,
        )

    # Summarise
    result = query_backend(
        character=selected_text,
        context=selected_text_context,
        action="summarise",
    )["result"]

    return render_template(
        "process.html",
        html_user_content=f"<h1>Summary</h1><p>{result}</p>",
        title=title,
        author=author,
    )
