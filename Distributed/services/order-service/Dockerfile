# Phase 11 image for the order service, the outbox publisher, and the inventory consumer.
# Same image, different commands. No PEM and no token are copied into a layer.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin app

COPY pyproject.toml ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

RUN pip install --no-cache-dir .

USER app
EXPOSE 8000

# Exec form so uvicorn is PID 1 and receives SIGTERM.
CMD ["uvicorn", "order_service.presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
