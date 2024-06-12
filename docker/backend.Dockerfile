FROM python:3.12-alpine as base

WORKDIR /app

#
# Stage 1: Build virtual environment with required packages
#
FROM base as builder

# Install poetry
RUN apk add --no-cache gcc libffi-dev musl-dev
RUN pip install poetry
RUN python -m venv /app/venv

# Install dependencies into virtual environment
COPY . .
RUN poetry export -f requirements.txt | /app/venv/bin/pip install -r /dev/stdin

#
# Stage 2: Run flask from virtual environment
#
FROM base as final

RUN apk add --no-cache libffi
COPY --from=builder /app/venv /app/venv
COPY backend backend

# Which model to use
ENV OLLAMA_MODEL "llama3:8b"

EXPOSE 5000

CMD ["venv/bin/python", "-m", "flask", "--app", "backend/app", "run", "--host", "0.0.0.0", "--debug"]
