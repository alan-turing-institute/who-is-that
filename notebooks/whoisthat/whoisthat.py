from ollama import Client
client = Client(host='http://localhost:11434')
import yaml


def get_summary(book, bookmark, character):
  # Load the db
  with open('whoisthat/database.yml', 'r') as file:
    book_info = yaml.safe_load(file)[book]
  query = "I have up to the end of " + bookmark
  query += " in the book '" +  book + "' by " +  book_info['author']
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
    book_info = yaml.safe_load(file)[book]
  query = "Read the following summary of " + character
  query += " from '" +  book + "' by " +  book_info['author'] + ": '" + summary
  query += "'. The reader has only read up to the end of " +  bookmark
  query += ". Considering this, check to see whether the following spoiler is present: '"
  query += book_info['character']['spoiler'] + "'."
  response = client.chat(model='llama3', messages=[
    {
      'role': 'user',
      'content': query,
    },
  ])
  return response['message']['content']