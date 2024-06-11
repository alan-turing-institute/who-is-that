FROM ollama/ollama as base

#
# Stage 1: Setup Ollama with requested model
#
FROM base as builder

ENV MODEL="llama3:8b"

RUN /bin/ollama serve & \
    sleep 5; \
    /bin/ollama run ${MODEL}

#
# Stage 2: Run Ollama with the pre-downloaded model
#
FROM base as final

COPY --from=builder /root/.ollama /root/.ollama

ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]
