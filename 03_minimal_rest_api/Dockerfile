FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY mini_api/ mini_api/

RUN pip install --no-cache-dir .

EXPOSE 8080

ENTRYPOINT ["mini-api"]
