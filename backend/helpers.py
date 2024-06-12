from .ollama_query import OllamaQuery

""" # # Load the yaml file as a global variable
data_dir = pathlib.Path(__file__).parent.resolve()
with pathlib.Path.open(data_dir / "spoilerdb" / "database.yml") as database_file:
    db = yaml.safe_load(database_file)

def character_or_place(word: str, text: str) -> str:
   Determine whether the word in the text is about a character or a place.
    query = "I have written the following story: '" + text + "'."
    query += " I have used the word '" + word + "' in the story."
    query += " Determine whether this word refers to a character or a place."
    query += " Provide a simple answer of 'character' or 'place' or 'neither'."
    client = OllamaQuery()
    response = client.query(
        [
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    if "character" in response["message"]["content"]:
        return "character"
    if "place" in response["message"]["content"]:
        return "place"
    return "neither" """


def spoiler_check(book: str, character: str, summary: str) -> str:

    query = "I have written the following story: '" + book + "'.\n"
    query += " I have used the word '" + character + "' in the story.\n"
    query += (
        " Determine whether the following summary contains spoilers or additional informantion about "
        + character
        + ".\n"
    )
    query += summary + "\n"
    query += " Provide a simple answer of 'true' or 'false'."
    query += " If so, please provide another summary without spoilers."

    client = OllamaQuery()
    response = client.query(
        [
            {
                "role": "user",
                "content": query,
            },
        ],
    )
    answer = response["message"]["content"]
    if "true" in answer or "True" in answer or "TRUE" in answer:
        print("Spoiler detected! Regenerating summary...")
        return answer
    if "false" in answer or "False" in answer or "FALSE" in answer:
        print("No spoilers detected.")
        return summary
    raise ValueError("Unexpected response from spoiler detection: " + answer)


def who_is_that(context: str, prompt_template: str, character: str) -> str:
    prompt = prompt_template.replace("{character}", character)
    concat = f"CONTEXT: {context} \n INSTRUCTIONS: {prompt}"
    try:
        print("Waiting for an Ollama response.", flush=True)
        client = OllamaQuery()
        response = client.query(
            [
                {
                    "role": "user",
                    "content": concat,
                },
            ],
        )
        content = response["message"]["content"]

        # content = spoiler_check(context, character, content)

    except Exception as exc:
        print(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content


def generate_summary(context: str) -> str:
    prompt = f"CONTEXT: {context}. \n INSTRUCTIONS: Summarize the story so far in 100 words or less. Do not reveal spoilers for later sections of the story."
    try:
        print("Waiting for an Ollama response.", flush=True)
        client = OllamaQuery()
        response = client.query(
            [
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        content = response["message"]["content"]

    except Exception as exc:
        print(f"Failed to retrieve summary from Ollama {exc!s}")
        content = "Sorry, I could not answer your query."

    return content


# def who_is_that_really(
#     text: str,
#     word: str,
#     clicked: str = "whoisthat",
# ) -> str:
#     """Get a summary of the character's actions up to the bookmark in the text.
#     This function uses the LLM to generate a summary from the supplied text.
#     """
#     # word_type = character_or_place(word, text)

#     def generate_summary() -> str:
#         model = os.environ.get("OLLAMA_MODEL", "llama3:8b")
#         print(f"Using model {model}", flush=True)

#         prepend_str = ""
#         query = "I have written the following story: '" + text + "'."
#         if word_type == "character" and clicked != "summary":
#             if clicked == "whatisthat":
#                 prepend_str += (
#                     "Clicked a character, not a place. Running whoisthat instead... "
#                 )
#             query += " Describe what " + word + " has done so far in 15 word or less."
#             query += " Focus on key events and actions taken by this character."
#         elif word_type == "place" and clicked != "summary":
#             if clicked == "whoisthat":
#                 prepend_str = (
#                     "Clicked a place, not a character. Running whatisthat instead... "
#                 )
#             query += (
#                 " Create a description of the location '"
#                 + word
#                 + "' in 15 word or less."
#             )
#         else:
#             query += " Describe the story so far in 15 word or less."
#         query += " Do not reveal spoilers for later sections of the story."
#         try:
#             print("Waiting for an Ollama response.", flush=True)
#             client = OllamaQuery()
#             response = client.query(
#                 [
#                     {
#                         "role": "user",
#                         "content": query,
#                     },
#                 ],
#             )
#             content = response["message"]["content"]
#         except Exception as exc:
#             print(f"Failed to retrieve summary from Ollama {exc!s}", flush=True)
#             response = {"message": {"content": "some text here"}}
#             content = "Sorry, I could not answer your query."
#         return prepend_str + content

#     summary = generate_summary()
#     if word_type == "character":
#         start_time = time.time()
#         has_spoiler = spoiler_check(book, word, summary)
#         while has_spoiler:
#             summary = generate_summary()
#             has_spoiler = spoiler_check(book, word, summary)
#             # Check if the time has exceeded 10 seconds
#             if time.time() - start_time >= 10:
#                 break
#     return summary
