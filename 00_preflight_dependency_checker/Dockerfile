FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY preflight_checker/ preflight_checker/

RUN pip install --no-cache-dir .

ENTRYPOINT ["preflight"]
