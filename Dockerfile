# QRME as one container: the studio built and served by the API.
#
# Two stages so the Node toolchain never ships in the runtime image — only
# the built studio does. The result serves the UI at /app and the API on the
# same origin, which is what lets a phone use it with nothing to configure.
#
#   docker build -t qrme .
#   docker run -p 8000:8000 -v qrme-data:/data \
#     -e QRME_PUBLIC_URL=https://qrme.example.com \
#     -e QRME_SIGNUP_KEY=... qrme
#
# See docs/hosting.md before publishing one.
#
# The suite end-to-end harness (docker/docker-compose.yml) builds this same
# image and overrides the command to run its bootstrap and e2e drivers, so
# changes here have to keep working there too.

# --- stage 1: build the studio -------------------------------------------
FROM node:20-slim AS studio
WORKDIR /src
# Copy manifests first so dependency install caches independently of source.
COPY app/package.json app/package-lock.json ./app/
RUN npm --prefix app ci
COPY app/ ./app/
RUN npm --prefix app run build

# --- stage 2: the service ------------------------------------------------
FROM python:3.12-slim AS runtime

# Predictable, unbuffered logs; no .pyc clutter in the layer.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    QRME_DB=/data/qrme.db \
    QRME_CONSOLE_DIR=/srv/app/dist

# The eyes: `briefcase._ocr_text` reads scanned pages and unmappable fonts
# by rasterising (poppler's pdftoppm) and reading (tesseract), both reached
# as subprocesses — no new Python dependencies. Feature-detected in code,
# so a checkout without them keeps the honest refusal; the image carries
# them so the beta can actually read what it is handed.
RUN apt-get update \
 && apt-get install -y --no-install-recommends tesseract-ocr poppler-utils ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY pyproject.toml README.md ./
COPY qrme/ ./qrme/
# `cloudgw` too, and not because this image serves it — it does not. The
# wheel declares both packages, and `qrme/routers/problems.py` imports
# `cloudgw.problems` at module load, so an image without it cannot import
# the app at all: uvicorn dies on ModuleNotFoundError and the proxy in
# front of it answers 502 with nothing in the body to say why.
COPY cloudgw/ ./cloudgw/
RUN pip install --no-cache-dir .

# The built studio, mounted by the API at /app. QRME_CONSOLE_DIR points at it
# explicitly: the installed package lives in site-packages, so the relative
# path the source tree uses would not find this copy.
COPY --from=studio /src/app/dist ./app/dist

# The database lives on a volume, not in the image: a container restart must
# never be a data-loss event.
RUN useradd --system --uid 10001 qrme \
 && mkdir -p /data && chown -R qrme:qrme /data /srv
USER qrme
VOLUME ["/data"]

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# PORT is honoured for platforms that assign one (Fly, Render, Railway…).
CMD ["sh", "-c", "uvicorn qrme.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
