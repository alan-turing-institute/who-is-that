from flask import Flask, request, jsonify
from ollama import Client
import yaml

app = Flask(__name__)
client = Client(host="http://localhost:11434")

# Load the prompt template once at the start of the application
with open("prompts/input_prompt.txt", "r") as file:
    prompt_template = file.read()

# Load the yaml file as a global variable
with open('spoilerdb/database.yml', 'r') as file:
  db = yaml.safe_load(file)

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


def who_is_that_really(text, book, bookmark, character, model):
  """
    Get a summary of the character's actions up to the bookmark in the text.
    This function uses the LLM to generate a summary from the supplied text.
  """
  def generate_summary():
    query = "I have written the following story: '" + text + "'."
    query += " Read up to the end of " + bookmark + "."
    query += " Describle what " +  character + " has done so far in 15 word or less."
    query += " Focus on key events and actions taken by this character."
    query += "Do not reveal spoilers for later sections of the story."
    response = client.chat(model=model, messages=[
      {
        'role': 'user',
        'content': query,
      },
    ])
    return response['message']['content']
  summary = generate_summary()
  has_spoiler = spoiler_check(book, character, summary, model)
  while has_spoiler:
    summary = generate_summary()
    has_spoiler = spoiler_check(book, character, summary, model)
  return summary


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

    # TODO: get the text of the book up to this point and the book name for Ed's function
    # text = data.get("text")
    # book = data.get("book")
    # bookmark = data.get("context")

    if not character or not context:
        return jsonify({"error": "Character and context are required"}), 400

    try:
        # Fede func
        result = who_is_that(context, prompt_template, character)
        # Ed func
        # result = who_is_that_really(text, book, bookmark, character, 'llama3')
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
