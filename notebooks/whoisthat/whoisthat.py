from ollama import Client
client = Client(host='http://localhost:11434')
import yaml

# Load the yaml file as a global variable
with open('whoisthat/database.yml', 'r') as file:
  db = yaml.safe_load(file)


def get_summary(book, bookmark, character):
  query = "I have read up to the end of " + bookmark
  query += " in the book '" +  book + "' by " +  db[book]['author']
  query += ". Can you summarize the character of " +  character
  query += " for me 20 words or less? Focus on key things they have done, not just how they are described."
  query += "Do not reveal spoilers for later sections of the book."
  response = client.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  return response['message']['content']


def spoiler_check(book, character, summary):
  if book not in db or character not in db[book]['characters']:
    return "No spoilers in the database for " + character + " in " + book + "."
  query = "Read the following summary of " + character
  query += " from '" +  book + "' by " +  db[book]['author'] + ": '" + summary
  query += "'. Check to see whether the following spoiler is present: '"
  query += db[book]['characters'][character]['spoilers'][0] + "'. "
  query += "Give me a yes or no answer and a short one-sentence explanation for that decision."
  response = client.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  return response['message']['content']

# TODO: Implement the following functions
# 1. Summary generation with a book text as an input
# 2. Spoiler check with a book text as an input
# 3. Spoiler check that doesn't use LLM
# 4. Use Lydia's story and character, bookmark and spoiler
# 5. Make sure you can check for multiple spoilers