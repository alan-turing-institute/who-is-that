from ollama import Client
client = Client(host='http://localhost:11434')
import yaml
import time

# Load the yaml file as a global variable
with open('whoisthat/database.yml', 'r') as file:
  db = yaml.safe_load(file)


def who_is_that_really(model, text, bookmark, word, clicked='whoisthat'):
  """
    Get a summary of the character's actions up to the bookmark in the text.
    This function uses the LLM to generate a summary from the supplied text.
  """
  word_type = character_or_place(model, word, text)
  def generate_summary():
    prepend_str = ""
    query = "I have written the following story: '" + text + "'."
    query += " Read up to the end of " + bookmark + "."
    if word_type == 'character' and (clicked == 'whoisthat' or clicked == 'whatisthat'):
      if clicked == 'whatisthat':
        prepend_str += "Clicked a character, not a place. Running whoisthat instead... "
      query += " Describe what " +  word + " has done so far in 15 word or less."
      query += " Focus on key events and actions taken by this character."
    elif word_type == 'place' and (clicked == 'whoisthat' or clicked == 'whatisthat'):
      if clicked == 'whoisthat':
        prepend_str = "Clicked a place, not a character. Running whatisthat instead... "
      query += " Create a description of the location '" +  word + "' in 15 word or less."
    else:
      query += " Describe the story so far in 15 word or less."
    query += " Do not reveal spoilers for later sections of the story."
    response = client.chat(model=model, messages=[
      {
        'role': 'user',
        'content': query,
      },
    ])
    return prepend_str + response['message']['content']
  summary = generate_summary()

  # Check for spoilers in the summary and regenerate if necessary
  start_time = time.time()
  has_spoiler = hallucinate_check(model, text, summary)
  while has_spoiler:
    summary = generate_summary()
    has_spoiler = hallucinate_check(model, text, summary)
    # Give up if the time has exceeded 10 seconds
    if time.time() - start_time >= 10:
      break
  return summary


def hallucinate_check(model, text, summary):
  """
    Check if the summary contains any information not present in the text.
  """
  query = "I have written the following story: '" + text + "'."
  query += " I have generated the following summary: '" + summary + "'."
  query += " Determine if the summary contains any information not present in the text."
  query += " Provide a simple answer of 'true' or 'false'."
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
  
def character_or_place(model, word, text):
  """
    Determine whether the word in the text is about a character or a place.
  """
  query = "I have written the following story: '" + text + "'."
  query += " I have used the word '" + word + "' in the story."
  query += " Determine whether this word refers to a character or a place."
  query += " Provide a simple answer of 'character' or 'place' or 'neither'."
  response = client.chat(model=model, messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  if 'character' in response['message']['content']:
    return 'character'
  elif 'place' in response['message']['content']:
    return 'place'
  else:
    return 'neither'


# TODO: Implement the following functions
# 0. [x] Try with Gemma 2b or something smaller
# 1. [x] Summary generation with a book text as an input
# 2. [x] Summary function runs spoiler check inside and iterates until no spoilers are found
# 3. [x] Move these functions to backend.py
# 4. [x] Implement character_or_place function
# 5. [x] Alternative spoiler check that sees if any information in the summary is not in the text
# 6. [ ] Update the app.py version of who_is_that_really to be in line with this script
# 7. [ ] Remove the spoiler db from the app.py version of who_is_that_really