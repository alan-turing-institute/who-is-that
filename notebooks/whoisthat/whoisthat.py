from ollama import Client
client = Client(host='http://localhost:11434')
import yaml

# Load the yaml file as a global variable
with open('whoisthat/database.yml', 'r') as file:
  db = yaml.safe_load(file)


def who_is_that_really(model, text, book, bookmark, character=None, place=None):
  """
    Get a summary of the character's actions up to the bookmark in the text.
    This function uses the LLM to generate a summary from the supplied text.
  """
  def generate_summary():
    query = "I have written the following story: '" + text + "'."
    query += " Read up to the end of " + bookmark + "."
    if character:
      query += " Describe what " +  character + " has done so far in 15 word or less."
      query += " Focus on key events and actions taken by this character."
    elif place:
      query += " Create a description of the location '" +  place + "' in 15 word or less."
    else:
      query += " Describe the story so far in 15 word or less."
    query += " Do not reveal spoilers for later sections of the story."
    response = client.chat(model=model, messages=[
      {
        'role': 'user',
        'content': query,
      },
    ])
    return response['message']['content']
  summary = generate_summary()
  if character:
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
    print("Spoiler detected! Regenerating summary...")
    return True
  elif 'false' in answer or 'False' in answer or 'FALSE' in answer:
    return False
  else:
    raise Exception("Unexpected response from spoiler detection: " + answer)

# TODO: Implement the following functions
# 0. [x] Try with Gemma 2b or something smaller
# 1. [x] Summary generation with a book text as an input
# 2. [x] Summary function runs spoiler check inside and iterates until no spoilers are found
# 3. [x] Move these functions to backend.py
# 4. [ ] Spoiler check that doesn't use LLM
# 5. [ ] Use Lydia's story and character, bookmark and spoiler
# 6. [ ] Make sure you can check for multiple spoilers
# 7. [ ] Alternative spoiler check that does sentiment analysis