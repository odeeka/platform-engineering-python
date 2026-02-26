# Minimal REST API with Observability

A production-ready microservice with structured logging, request ID propagation, metrics, and graceful shutdown.

## Features

- **REST endpoints** — `/health`, `/metrics`, `/work`
- **Structured JSON logging** to stderr
- **Request ID propagation** — pass `X-Request-ID` header or auto-generate
- **Graceful shutdown** — handles SIGTERM/SIGINT cleanly
- **Per-request timeout** — `/work` duration capped by `--work-timeout`
- **Basic metrics** — request count, error count, per-path latency stats
- **Thread-safe** — concurrent request handling

## Installation

```bash
pip install '.[dev]'
```

## Usage

```bash
# Start the server
mini-api --port 8080

# Custom options
mini-api --host 127.0.0.1 --port 3000 --work-timeout 10
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe — returns `{"status": "ok"}` |
| GET | `/metrics` | Request count, error count, per-path latency |
| POST | `/work` | Simulate work — accepts `{"duration_s": 1.0}` |

### CLI flags

| Flag | Default | Description |
|---|---|---|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8080` | Listen port |
| `--work-timeout` | `5.0` | Max seconds for `/work` requests |

### Examples

```bash
# Health check
curl http://localhost:8080/health

# Simulate 1s of work with a custom request ID
curl -X POST http://localhost:8080/work \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req-42" \
  -d '{"duration_s": 1.0}'

# View metrics
curl http://localhost:8080/metrics
```

## Build standalone binary

```bash
make build
./dist/mini-api --port 8080
```

Or directly:

```bash
pyinstaller --onefile --name mini-api --clean mini_api_entry.py
```

## Docker

```bash
docker build -t mini-api .
docker run --rm -p 8080:8080 mini-api
```

## Tests

```bash
pytest -v
```

## CI

GitHub Actions workflow at `.github/workflows/mini-api.yml` runs tests on Python 3.10–3.12, builds the Docker image, and smoke-tests the running container.

## Project structure

```
03_minimal_rest_api/
├── mini_api/
│   ├── __init__.py
│   ├── app.py          # Flask app factory, routes, middleware
│   ├── cli.py          # argparse CLI entry point
│   ├── logger.py       # Structured JSON logging
│   ├── metrics.py      # Thread-safe in-memory metrics
│   └── server.py       # Werkzeug server with graceful shutdown
├── mini_api_entry.py   # PyInstaller entry point
├── tests/
│   ├── test_app.py     # Integration tests for all endpoints
│   ├── test_logger.py  # Logger formatting tests
│   └── test_metrics.py # Metrics collector tests
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```
