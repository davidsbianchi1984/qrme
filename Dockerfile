# QRME backend image — used for `uvicorn qrme.api:app` and, in the suite
# end-to-end harness, to run the bootstrap and e2e driver (both need only httpx,
# which ships as a runtime dependency for suite/gateway.py).
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY qrme ./qrme
COPY suite ./suite
RUN pip install .

EXPOSE 8000
CMD ["uvicorn", "qrme.api:app", "--host", "0.0.0.0", "--port", "8000"]
