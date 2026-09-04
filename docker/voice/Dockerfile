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
EXPOSE 8800
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8800"]
