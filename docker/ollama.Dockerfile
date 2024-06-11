FROM ollama/ollama as base

#
# Stage 1: Setup Ollama with supported models
#
FROM base as builder

# Install requested models
RUN /bin/ollama serve & \
    sleep 5; \
    /bin/ollama run llama3:8b; \
    /bin/ollama run gemma:2b;

#
# Stage 2: Run Ollama with the pre-downloaded model
#
FROM base as final

COPY --from=builder /root/.ollama /root/.ollama

ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]
