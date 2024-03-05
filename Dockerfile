# Build Base python image
FROM python:3.11-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_INSTALLER_PARALLEL=1 \
    POETRY_INSTALLER_MAX_WORKER=10
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential curl libpq-dev vim

# Install poetry
# RUN curl -sSL https://install.python-poetry.org | python -
RUN pip install poetry

# Copy poetry file
COPY ./poetry.lock ./pyproject.toml /tmp

# Install python dependencies
RUN cd /tmp && poetry install --no-dev --no-root

# build app image
FROM base as final

# Create app dir
WORKDIR /project

# Copy project files
COPY . /project/
