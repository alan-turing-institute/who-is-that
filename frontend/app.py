from flask import Flask, render_template, request
from who_is_that import Extractor

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
    author = extractor.author
    title = extractor.title

    # If text_items is a list of tuples, extract the text
    if isinstance(text_items[0], tuple):
        text_items = [content for _, content in text_items]

    concatenated_text = "\n".join(text_items)  # Concatenate all text content into a single string

    # Pass concatenated text as a hidden form input
    return render_template("process.html", text_items=[("Chapter " + str(i+1), content) for i, content in enumerate(text_items)], concatenated_text=concatenated_text, title=title, author=author)

@app.route("/summarise", methods=["POST"])
def summarise():
    selected_text = request.form["selected_text"]
    selected_text_start = int(request.form["selected_text_start"])
    concatenated_text = request.form["concatenated_text"]
    author = request.form["author"]
    title = request.form["title"]

    print(f"Summarising up to: {selected_text} starting at position: {selected_text_start}")

    # Use the start position to slice the concatenated text
    summary = concatenated_text[:selected_text_start + len(selected_text)]

    return render_template("process.html", text_items=[("Summary", summary)], concatenated_text=concatenated_text, title=title, author=author)

if __name__ == "__main__":
    app.run(debug=True)
