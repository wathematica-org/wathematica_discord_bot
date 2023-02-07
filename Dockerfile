FROM python:3.10-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /tmp
ENV POETRY_NO_INTERACTION=1
COPY poetry.lock pyproject.toml ./
RUN poetry install --only main --no-root
WORKDIR /