# Hermes image + this profile. Build from the repo root:
#   docker build -f deploy/Dockerfile --build-arg HERMES_IMAGE=<your hermes image> -t noc-engineer .
ARG HERMES_IMAGE
FROM ${HERMES_IMAGE}
COPY hermes-profile /opt/noc/hermes-profile
COPY cron /opt/noc/cron
COPY deploy/start.sh /opt/noc/start.sh
ENTRYPOINT ["/bin/sh", "/opt/noc/start.sh"]
