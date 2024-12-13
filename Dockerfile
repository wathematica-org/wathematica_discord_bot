# use the latest python3.12-slim image with uv preinstalled
FROM ghcr.io/astral-sh/uv:python3.12-alpine

# update the certificates
RUN apk update && apk add ca-certificates && update-ca-certificates

# install packages
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync