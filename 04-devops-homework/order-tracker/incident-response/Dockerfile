FROM node:22-bookworm-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
RUN npm install --global @github/copilot@1.0.89
RUN mkdir -p /root/.copilot
COPY incident-response/copilot-config.json /root/.copilot/config.json

WORKDIR /build
COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/opt/incident-response-venv
RUN uv sync --frozen

COPY incident-response/main.py /incident-response/main.py
COPY pyproject.toml uv.lock /workspace/
EXPOSE 8001
CMD ["uv", "run", "--project", "/build", "--no-sync", "uvicorn", "main:app", "--app-dir", "/incident-response", "--host", "0.0.0.0", "--port", "8001"]