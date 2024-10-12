FROM python:3.12

# ensure that the environment has curl and certificates are up to date
RUN apt-get update && apt-get install --no-install-recommends -y curl ca-certificates

# setup uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN ["/bin/bash", "-c", "$HOME/.cargo/env"]

# install packages
WORKDIR /tmp
COPY uv.lock pyproject.toml ./
RUN uv sync
WORKDIR /