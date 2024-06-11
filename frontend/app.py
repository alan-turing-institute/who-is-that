from flask import Flask, render_template, request
from who_is_that import Extractor

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("./index.html")


@app.route("/", methods=["POST"])
def load_file():
    uploaded_file = request.files["file"]
    print(f"Loading file {uploaded_file.filename}")

    filestream = uploaded_file.stream
    filestream.seek(0)
    extractor = Extractor.from_bytes(filestream.read())

    return render_template("./process.html", text_items=extractor.text_content)


@app.route("/process", methods=["POST"])
def summarise():
    print("Summarising")
    return render_template("./process.html", text_items=[])

if __name__ == "__main__":
    app.run(debug=True)
