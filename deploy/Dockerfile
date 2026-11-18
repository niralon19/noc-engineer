# docker build -f deploy/Dockerfile --build-arg HERMES_IMAGE=<hermes image> -t <registry>/noc-engineer .
ARG HERMES_IMAGE
FROM ${HERMES_IMAGE}
COPY SOUL.md config.yaml distribution.yaml /opt/noc-engineer/
COPY skills /opt/noc-engineer/skills
COPY scripts /opt/noc-engineer/scripts
COPY cron /opt/noc-engineer/cron
COPY deploy/start.sh /opt/noc-engineer/start.sh
ENTRYPOINT ["/bin/sh", "/opt/noc-engineer/start.sh"]
