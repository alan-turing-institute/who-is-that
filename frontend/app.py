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
    # Use the start position to slice the concatenated text

    if option == "what_is_this":
        return render_template("process.html", text_items=[("What is this place?", selected_text)], concatenated_text=concatenated_text, title=title, author=author)

    elif option == "who_is_that":
        return render_template("process.html", text_items=[("Who is this?", selected_text)], concatenated_text=concatenated_text, title=title, author=author)

    else:
        return render_template("process.html", text_items=[("Summary", summary)], concatenated_text=concatenated_text, title=title, author=author)



if __name__ == "__main__":
    app.run(debug=True)