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

    text_items = extractor.text_content
    return render_template("process.html", text_items=text_items)
    text_items = extractor.text_content  # This should be a list of tuples or strings

    # If text_items is a list of tuples, extract the text
    if isinstance(text_items[0], tuple):
        text_items = [content for _, content in text_items]

    concatenated_text = "\n".join(text_items)  # Concatenate all text content into a single string

    # Pass concatenated text as a hidden form input
    return render_template("process.html", text_items=[(str(i), content) for i, content in enumerate(text_items)], concatenated_text=concatenated_text)

@app.route("/summarise", methods=["POST"])
def summarise():
    selected_text = request.form["selected_text"]
    concatenated_text = request.form["concatenated_text"]
    print(f"Summarising up to: {selected_text}")

    # Find the selected text in the concatenated content
    position = concatenated_text.find(selected_text)
    if position != -1:
        summary = concatenated_text[:position + len(selected_text)]
    else:
        summary = "Selected text not found in content."

    return render_template("process.html", text_items=[("Summary", summary)], concatenated_text=concatenated_text)

if __name__ == "__main__":
    app.run(debug=True)
