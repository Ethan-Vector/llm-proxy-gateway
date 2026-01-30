.PHONY: dev test lint fmt docker-build docker-run

dev:
	uvicorn llm_proxy_gateway.main:app --host 0.0.0.0 --port 8080 --reload

test:
	pytest -q

lint:
	ruff check .
	mypy src

fmt:
	ruff format .

docker-build:
	docker build -t ethan-llm-proxy-gateway:latest .

docker-run:
	docker run --rm -p 8080:8080 --env-file .env ethan-llm-proxy-gateway:latest
