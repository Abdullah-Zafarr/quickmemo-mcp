# QuickMemo MCP Server Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv for fast, reliable package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src

# Install dependencies and package
RUN uv pip install --system --no-cache -e .

# Expose default environment
ENV PYTHONUNBUFFERED=1
ENV QUICKMEMO_STORAGE=/data/memos.json

VOLUME ["/data"]

# Run the MCP server via stdio
ENTRYPOINT ["quickmemo"]
