from flask import Flask, request, jsonify
from ollama import Client
import pathlib

app = Flask(__name__)
client = Client(host="http://localhost:11434")

# Load the prompt template once at the start of the application
with open("prompts/input_prompt.txt", "r") as file:
    prompt_template = file.read()


@app.route("/")
def index():
    return "Backend is running"

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


def spoiler_check(book, character, summary, model):
  if book not in db or character not in db[book]['characters']:
    return "No spoilers in the database for " + character + " in " + book + "."
  query = "Read the following summary of " + character
  query += " from '" +  book + "' by " +  db[book]['author'] + ": '" + summary
  query += "'. Check to see whether the following spoiler is present: '"
  query += db[book]['characters'][character]['spoilers'][0] + "'. "
  query += "Give me a simple true or false answer."
  response = client.chat(model=model, messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  answer = response['message']['content']
  if 'true' in answer or 'True' in answer or 'TRUE' in answer:
    print("Spoiler detected!")
    return True
  elif 'false' in answer or 'False' in answer or 'FALSE' in answer:
    return False
  else:
    raise Exception("Unexpected response from spoiler detection: " + answer)


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
