# Use the specified Python base image
FROM python:3.11-slim-bullseye

# Set environment variables
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y postgresql-client vim curl python3-opencv poppler-utils libreoffice build-essential

RUN apt install libpq-dev
RUN apt-get autoremove -y && apt-get clean
RUN pip install poetry
# Set the work directory in docker and copy project to work directory
WORKDIR /fastapi-app

# Copy the content of the local src directory to the working directory
COPY pyproject.toml poetry.lock* /fastapi-app/

# RUN poetry config installer.max-workers 10
# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the content of the local src directory to the working directory
COPY . /fastapi-app/
