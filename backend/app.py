from flask import Flask, request, jsonify
from ollama import Client
import pathlib

app = Flask(__name__)
client = Client(host="http://localhost:11434")

# Load the prompt template once at the start of the application
prompts_dir = pathlib.Path(__file__).parent.resolve() / "prompts"
with open(prompts_dir / "input_prompt.txt", "r") as file:
    prompt_template = file.read()


def who_is_that(context, prompt_template, character):
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    response = client.chat(
        model="gemma",
        messages=[
            {
                "role": "user",
                "content": concat,
            },
        ],
    )
    return response["message"]["content"]


@app.route("/who_is_that", methods=["POST"])
def api_who_is_that():
    data = request.json
    character = data.get("character")
    context = data.get("context")

    if not character or not context:
        return jsonify({"error": "Character and context are required"}), 400

    try:
        result = who_is_that(context, prompt_template, character)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
