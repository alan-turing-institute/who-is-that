from ollama import Client
client = Client(host='http://localhost:11434')
import yaml

# Load the yaml file as a global variable
with open('whoisthat/database.yml', 'r') as file:
  db = yaml.safe_load(file)

# TODO: add warnings for characters and books that are not in the database

def get_summary(book, bookmark, character):
  query = "I have up to the end of " + bookmark
  query += " in the book '" +  book + "' by " +  db[book]['author']
  query += ". Can you summarize the character of " +  character
  query += " for me? I don't want any spoilers."
  response = client.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  return response['message']['content']


def spoiler_check(book, bookmark, character, summary):
  # Load the db
  with open('whoisthat/database.yml', 'r') as file:
    db[book] = yaml.safe_load(file)[book]
  query = "Read the following summary of " + character
  query += " from '" +  book + "' by " +  db[book]['author'] + ": '" + summary
  query += "'. The reader has only read up to the end of " +  bookmark
  query += ". Considering this, check to see whether the following spoiler is present: '"
  query += db[book]['characters'][character]['spoilers'][0] + "'."
  response = client.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  return response['message']['content']