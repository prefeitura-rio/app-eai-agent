FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

RUN uv sync

CMD ["sh", "-c", "uv run alembic upgrade head && uv run gunicorn -c gunicorn_config.py src.main:app"]
