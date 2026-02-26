# Preflight / Dependency Checker

A CLI tool that validates service dependencies (DNS, TCP, HTTP) before deployment.

## Features

- **DNS resolution check** — verify hostnames resolve
- **TCP connectivity check** — verify ports are reachable
- **HTTP health endpoint check** — verify endpoints return 2xx
- **Configurable timeout** per check
- **Retry with exponential backoff**
- **Structured JSON logging** to stderr
- **Proper exit codes** — `0` all pass, `1` any failure
- **JSON summary output** via `--json`

## Installation

```bash
pip install '.[dev]'   # includes pytest for development
```

## Usage

```bash
# DNS-only check
preflight example.com

# DNS + TCP check
preflight db.internal:5432

# Full DNS + TCP + HTTP check
preflight https://api.example.com/health

# Multiple targets
preflight redis.local:6379 https://api.example.com/health postgres.local:5432

# Custom options
preflight --timeout 10 --retries 5 --backoff 2.0 https://api.example.com/health

# JSON summary to stdout
preflight --json https://api.example.com/health
```

### Target formats

| Format | Checks run |
|---|---|
| `hostname` | DNS |
| `hostname:port` | DNS → TCP |
| `http(s)://…` | DNS → TCP → HTTP |

### CLI flags

| Flag | Default | Description |
|---|---|---|
| `--timeout` | `5.0` | Seconds per individual check |
| `--retries` | `3` | Max attempts per check |
| `--backoff` | `1.0` | Base seconds for exponential backoff |
| `--json` | off | Print JSON summary to stdout |

## Build standalone binary

Uses [PyInstaller](https://pyinstaller.org/) to produce a single self-contained executable — no Python needed on the target machine.

```bash
# Install dev dependencies (includes PyInstaller)
pip install '.[dev]'

# Build the binary
make build

# Binary is at dist/preflight
./dist/preflight --help
./dist/preflight https://example.com
```

Or run PyInstaller directly:

```bash
pyinstaller --onefile --name preflight --clean preflight_entry.py
```

## Docker

```bash
docker build -t preflight-checker .
docker run --rm preflight-checker https://example.com
```

## Tests

```bash
pytest -v
```

## CI

GitHub Actions workflow at `.github/workflows/preflight-checker.yml` runs tests on Python 3.10–3.12 and builds the Docker image on every push.

## Project structure

```
00_preflight_dependency_checker/
├── preflight_checker/
│   ├── __init__.py
│   ├── checker.py      # Core checks: DNS, TCP, HTTP + retry logic
│   ├── cli.py          # argparse CLI entry point
│   └── logger.py       # Structured JSON logging
├── tests/
│   ├── test_checker.py
│   └── test_cli.py
├── Makefile
├── Dockerfile
├── pyproject.toml
└── README.md
```
