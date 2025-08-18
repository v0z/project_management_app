# Makefile

.PHONY: run test coverage lint format isort recreate_db

run:
	uvicorn app.main:app --reload

test:
	pytest -v --disable-warnings

coverage:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check app

format:
	ruff format app

isort:
	isort app

recreate_db:
	python -m scripts.recreate_db