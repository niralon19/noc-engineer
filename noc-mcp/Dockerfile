# noc-mcp image. Build from the repo root:  docker build -f noc-mcp/Dockerfile -t <registry>/noc-mcp:<tag> .
# Use the org's approved Python base image / internal PyPI mirror if required.
FROM python:3.12-slim
WORKDIR /app
COPY noc-mcp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY noc-mcp/ /app/noc-mcp/
USER 1001
ENV PYTHONUNBUFFERED=1 NOC_MCP_CONFIG=/config/backends.yaml NOC_MCP_PIPELINE=/config/pipeline.yaml
EXPOSE 8765
CMD ["python", "/app/noc-mcp/server.py", "--http", "--port", "8765"]
