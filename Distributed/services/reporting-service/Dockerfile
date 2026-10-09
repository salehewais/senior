# Phase 11 image for Django reports and the reporting consumer.
# Same image, different commands. The private JWT key is not copied in.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin app

COPY pyproject.toml manage.py ./
COPY reporting ./reporting
COPY projections ./projections

RUN pip install --no-cache-dir .

USER app
EXPOSE 8001

# --noreload keeps one process, which receives SIGTERM. Port 8001 is not published on the host.
CMD ["python", "-u", "manage.py", "runserver", "0.0.0.0:8001", "--noreload"]
