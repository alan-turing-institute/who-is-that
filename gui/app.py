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

@app.route("/summarise", methods=["POST"])
def summarise():
    selected_text = request.form["selected_text"]
    print(f"Summarising: {selected_text}")
    # Add your summarisation logic here
    summary = f"Summary of: {selected_text}"  # Placeholder summary
    return render_template("process.html", text_items=[("Summary", summary)])

if __name__ == "__main__":
    app.run(debug=True)
