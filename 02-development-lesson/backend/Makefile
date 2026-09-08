.PHONY: install dev test lint format help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Start the dev server with hot-reload (http://localhost:8000)
	uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run all tests
	uv run pytest -v

test-q: ## Run tests (quiet)
	uv run pytest -q

lint: ## Check code with ruff
	uv run ruff check src/ tests/

format: ## Auto-format with ruff
	uv run ruff format src/ tests/
