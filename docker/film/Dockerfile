# The stack's camera: one HTTP door that translates the product's
# submit-and-poll shape into whichever video house is chosen (server.py).
# No model and no weights live here — the rendering happens at the house,
# which is the whole difference between this sidecar and the ears.
FROM python:3.12-slim
RUN pip install --no-cache-dir fastapi uvicorn
WORKDIR /srv
COPY server.py .
EXPOSE 8700
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8700"]
