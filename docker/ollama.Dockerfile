FROM ollama/ollama as base

#
# Stage 1: Setup Ollama with supported models
#
FROM base as builder

# Install requested models
# Other models considered but no longer installed
# - gemma:2b
RUN /bin/ollama serve & sleep 5; \
    /bin/ollama run llama3:8b; \
    /bin/ollama run yarn-mistral:7b-128k;

#
# Stage 2: Run Ollama with one of the pre-downloaded models
#
FROM base as final

COPY --from=builder /root/.ollama /root/.ollama

ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]
