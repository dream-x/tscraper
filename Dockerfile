FROM python:3.13-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    HEALTH_PORT=8000 \
    TZ=Europe/Moscow

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo "Europe/Moscow" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy project files
COPY pyproject.toml poetry.lock ./

# Configure poetry and install dependencies only
RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 10 \
    && poetry install --only=main --no-root

# Copy all source code including README.md
COPY . .

# Install the application with all files present
RUN poetry install --only=main

EXPOSE ${HEALTH_PORT}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${HEALTH_PORT}/health || exit 1

CMD ["python", "-m", "tscraper.tscraper"]
