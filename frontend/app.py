import base64
import io
import logging

from flask import Flask, jsonify, render_template, request
from PIL import Image

from .backend_query import BackendQuery
from .extract import Extractor

app = Flask(__name__)
for handler in app.logger.handlers:
    handler.setFormatter(
        logging.Formatter(r"%(asctime)s %(message)s", r"[%d/%b/%Y %H:%M:%S]"),
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
    BackendQuery.query(selected_text="", context="no context", action="summarise")
    app.logger.info("Ollama model is ready")

    # Render the template with appropriate inputs
    return render_template(
        "process.html",
        html_user_content=concatenated_html,
        title=title,
        author=authors,
        cover_url=cover_url,
    )


@app.route("/query", methods=["POST"])
def query() -> str:
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

    # Run the query against the backend
    result = BackendQuery.query(
        selected_text=selected_text,
        context=selected_text_context,
        action=option,
    )

    # Who is that?
    if option == "who_is_that":
        # result = query_backend(
        #     character=selected_text,
        #     context=selected_text_context,
        #     action=option,
        # )["result"]
        # return render_template(
        #     "process.html",
        #     summary_modal = result,
        #     title=title,
        #     author=author,
        # )
        return jsonify({"summary": result})

    # What is this?
    if option == "what_is_this":
        html_response = f"<h1>What is {selected_text}?</h1><p>{result}</p>"

    # Summarise
    else:
        html_response = f"<h1>Summary</h1><p>{result}</p>"

    return render_template(
        "process.html",
        html_user_content=html_response,
        title=title,
        author=author,
    )
