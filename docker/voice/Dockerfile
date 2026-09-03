# The stack's phone line: one HTTP door that places JIM's calls to a
# person's emergency contacts through whichever phone house is chosen,
# and turns the house's webhooks into JIM's own call-id doors (server.py,
# one row per house under houses/). The credential lives here and never
# in the product's image.
#
# No python-multipart on purpose: every vendor body is read from the raw
# request, because the raw bytes are what the house's signature covers.
# cryptography is for the two houses that sign with keys rather than an
# HMAC (Telnyx Ed25519, Vonage RS256).
FROM python:3.12-slim
RUN pip install --no-cache-dir fastapi uvicorn cryptography
WORKDIR /srv
COPY server.py .
COPY houses/ houses/
# The process that holds the house's credential does not run as root, the
# same as every other container in the stack; and the access log is off,
# because every vendor webhook URL carries the per-call signature and a log
# line is not where a capability belongs.
RUN useradd --system --no-create-home --uid 10001 voice
USER voice
EXPOSE 8800
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8800/health', timeout=4).status == 200 else 1)"]
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8800", "--no-access-log"]
