# The stack's eyes: a real browser behind one HTTP door (server.py). The
# Playwright base image carries Chromium and the matching driver; the
# vault's own image stays lean because this one does not.
FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy
RUN pip install --no-cache-dir fastapi uvicorn
WORKDIR /srv
COPY server.py .
EXPOSE 8400
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8400"]
