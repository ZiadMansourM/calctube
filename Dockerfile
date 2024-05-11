ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

USER appuser

COPY . .

EXPOSE 80

# Add tags for docker/metadata-action
LABEL org.opencontainers.image.tags="ziadmmh/calctube:v0.0.1"
LABEL org.opencontainers.image.authors="ziadmansour.4.9.2000@gmail.com"

CMD uvicorn main:app --host 0.0.0.0 --port 80
