FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src
COPY configs /app/configs

RUN pip install --no-cache-dir -e ".[dev]" || pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["llm-proxy", "--config", "configs/config.example.yaml", "--host", "0.0.0.0", "--port", "8080"]
