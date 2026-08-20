# The stack's eyes: a real browser behind one HTTP door (server.py). The
# Playwright base image carries Chromium and the matching driver; the
# vault's own image stays lean because this one does not.
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy
# `playwright` is pinned to the image's own version and installed
# explicitly: the base image bakes the *browsers*, but on the beta host
# the module was not importable by the python uvicorn runs under —
# `pip show playwright` answered "not found" and the container
# crash-looped from its first deploy, with every capture riding the
# honest plain-fetch fallback. The pin keeps the pip module matched to
# the baked browsers.
RUN pip install --no-cache-dir fastapi uvicorn playwright==1.47.0
WORKDIR /srv
COPY server.py .
EXPOSE 8400
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8400"]
