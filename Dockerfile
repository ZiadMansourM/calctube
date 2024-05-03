FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi
RUN pip install --no-cache-dir uvicorn
RUN pip install --no-cache-dir pytube
RUN pip install --no-cache-dir jinja2

COPY main.py /app/
COPY templates /app/templates

EXPOSE 80

# Add tags for docker/metadata-action
LABEL org.opencontainers.image.tags="ziadmmh/calctube:v0.0.1"
LABEL org.opencontainers.image.authors="ziadmansour.4.9.2000@gmail.com"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
