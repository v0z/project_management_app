# Makefile

.PHONY: run test coverage lint format isort recreate_db

run:
	uvicorn app.main:app --reload

test:
	pytest -v --disable-warnings

coverage:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check --fix app

format:
	ruff format app

isort:
	isort app

typing:
	mypy app
	#pyrefly check app

recreate_db:
	python -m scripts.recreate_db

tree:
	tree --gitignore -A -I __init__.py