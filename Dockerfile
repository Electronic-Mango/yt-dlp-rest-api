FROM python:3.14-slim

COPY --from=denoland/deno:bin /deno /usr/local/bin/deno
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates

WORKDIR /app

ENV UV_NO_DEV=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY .python-version pyproject.toml uv.lock ./
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENTRYPOINT ["uv", "run", "fastapi", "run", "src/main.py"]
CMD ["--host", "0.0.0.0"]
