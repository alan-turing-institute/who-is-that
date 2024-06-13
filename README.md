# who-is-that

Generate spoiler-free summaries of characters up-to-a-given-point in a text


# Run the apps in Docker

From the main directory run the following:

```shell
$ docker compose -f docker/docker-compose-integrated-ollama.yaml up --build
```

to run:

- `backend` (exposed on `localhost:3000`)
- `frontend` (exposed on `localhost:4000`)
- `ollama` (exposed on `localhost:11434`)

## Native Ollama

If you want to use a native Ollama installation instead of a Dockerised version, do the following:

- Install `ollama` (e.g. with `brew install ollama`), run it and install your desired models.
-

```shell
$ ollama serve &
$ ollama pull llama3:8b &
$ ollama pull yarn-mistral:7b-128k &
```

Now run the `frontend` and `backend` with `docker`:

```shell
$ docker compose -f docker/docker-compose-native-ollama.yaml up --build
```

this will deploy:

- `backend` (exposed on `localhost:3000`)
- `frontend` (exposed on `localhost:4000`)

## [Advanced] Just the backend

- Install and deploy `ollama` (as above)

Run just the backend with

```shell
$ poetry run flask --app backend/app run --debug
```

this will deploy:

- `backend` (exposed on `localhost:5000`)

# Running notebooks

- [Install `poetry`](https://python-poetry.org/docs/#installation)
- Install dependencies

```shell
$ poetry install
```

```shell
$ poetry run jupyter notebook
```

If viewing notebook in VSCode, you need to update the config to show the poetry virtualenv:

```shell
$ poetry config virtualenvs.in-project true
```
