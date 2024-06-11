# who-is-that

Generate spoiler-free summaries of characters up-to-a-given-point in a text

# Setup

- [Install `poetry`](https://python-poetry.org/docs/#installation)
- Install dependencies

```shell
$ poetry install
```

# Extract text

To extract text from an EPUB

```shell
$ poetry run extract --path <path to EPUB>
```

# Summarise character

To summarise a character up to a given chapter

```shell
$ poetry run summarise --chapter <chapter number> --character <name of character>
```

# Running Notebooks

```shell
$ poetry run jupyter notebook
```

If viewing notebook in VSCode, you need to update the config to show the poetry virtualenv:

```shell
$ poetry config virtualenvs.in-project true
```

# Run the analysis webapp

```shell
$ poetry run flask --app frontend/app ru
```

# Run the apps in Docker

From the main directory run the following:

```shell
$ docker compose -f docker/docker-compose.yaml up --build
```

to run:

- `backend` (exposed on `localhost:3000`)
- `frontend` (exposed on `localhost:4000`)
- `ollama` (exposed on `localhost:11434`)