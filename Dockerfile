FROM python:3.12-slim

# Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Poetry environment variables
ENV POETRY_VERSION=2.1.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copy all project files BEFORE installing dependencies
COPY pyproject.toml poetry.lock pytest.ini ./
COPY ./app ./app
COPY ./tests ./tests

# Install dependencies (including dev) as CI does
RUN poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR;

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI with hot-reloading
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]