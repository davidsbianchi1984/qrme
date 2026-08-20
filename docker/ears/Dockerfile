# The stack's ears: a local speech-to-text model behind one HTTP door
# (server.py). ffmpeg turns whatever recording arrives into the one shape
# the model reads; the weights are baked in at build so a running stack
# never reaches out for them. The vault's own image stays lean because
# this one does not.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn faster-whisper
# Bake the model weights into the image: the download happens at build
# time, on the machine running `docker compose build`, never at runtime.
RUN python -c "from faster_whisper import WhisperModel; \
WhisperModel('base', device='cpu', compute_type='int8')"
WORKDIR /srv
COPY server.py .
EXPOSE 8500
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8500"]
