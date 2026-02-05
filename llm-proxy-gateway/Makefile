.PHONY: install test lint run

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

run:
	llm-proxy --config configs/config.example.yaml
