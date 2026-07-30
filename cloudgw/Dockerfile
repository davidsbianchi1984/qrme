# The Cloud Model Gateway, on its own.
#
# Deliberately a separate image from the QRME app next door. The gateway is
# the one component several deployments share — it serves the greater model,
# takes contributions, and receives the error reports — so it has a different
# lifecycle, a different blast radius, and no reason to carry a Node
# toolchain or a studio build.
#
#   docker build -f cloudgw/Dockerfile -t cloudgw .
#   docker run -p 8300:8300 -v cloudgw-data:/data \
#     -e ANTHROPIC_API_KEY=... \
#     -e CLOUDGW_TOKENS="consoles:$(openssl rand -hex 24)" \
#     -e CLOUDGW_PROBLEM_READERS=me \
#     -e CLOUDGW_PROBLEMS_PATH=/data/problems.json \
#     cloudgw
#
# See docs/cloud-model.md for what each variable does and, more importantly,
# what happens when you leave one out — every default here fails closed.

FROM python:3.11-slim
WORKDIR /srv

# Only what the gateway imports. It does not need the product packages: it
# talks to PDI over HTTP like any other tenant, and it never imports qrme.
RUN pip install --no-cache-dir \
      "fastapi>=0.110" "uvicorn[standard]>=0.27" "anthropic>=0.40"

COPY cloudgw/ /srv/cloudgw/

# Where the error counters live by default. A named volume mounted here
# survives a redeploy; without one the counters are in-memory and go when
# the container does, which the boot banner says out loud.
ENV CLOUDGW_PROBLEMS_PATH=/data/problems.json
VOLUME /data

# Not root. The gateway writes exactly one file and reads none of yours.
RUN useradd --system --uid 10001 gateway \
 && mkdir -p /data && chown gateway:gateway /data
USER gateway

EXPOSE 8300

# /health is unauthenticated on purpose — a health check that needs a secret
# is one an orchestrator cannot run.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8300/health', timeout=2).status == 200 else 1)"

CMD ["python", "-m", "cloudgw", "--host", "0.0.0.0", "--port", "8300"]
