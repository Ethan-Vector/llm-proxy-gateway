FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir ".[dev]"

COPY src /app/src
COPY configs /app/configs

ENV PYTHONPATH=/app/src
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8080
ENV CONFIG_PATH=configs/gateway.yaml

EXPOSE 8080

CMD ["python", "-m", "llm_proxy_gateway.main"]
