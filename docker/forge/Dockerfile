# The stack's forge: a photograph in, a speakable 3-D head out, on this
# deployment's own hardware. The landmarker's weights are baked in at
# build time — the same rule the ears keep — so a running forge never
# reaches out for a model, and a face costs nobody a subscription.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn mediapipe pillow \
    numpy pygltflib
# The face landmarker, fetched once here on the machine running
# `docker compose build` and never at runtime.
RUN curl -fsSL -o /srv/face_landmarker.task \
    https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
    || (mkdir -p /srv && curl -fsSL -o /srv/face_landmarker.task \
        https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task)
WORKDIR /srv
COPY server.py facebuild.py ./
EXPOSE 8600
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8600"]
