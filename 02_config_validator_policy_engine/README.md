# Config Validator + Policy Engine

A CLI tool that validates service configuration files (YAML/JSON) and enforces deployment policies during CI.

## Features

- **YAML / JSON parsing** — auto-detects format
- **Required field validation** — configurable schema
- **Type validation** — ensures fields have correct types
- **Environment-specific rules** — prod/stage require more fields than dev
- **Policy enforcement** — no `latest` image tag, minimum replicas, valid port range
- **Error vs warning classification** — warnings don't fail the build
- **Structured JSON report** via `--json`
- **Proper exit codes** — `0` all pass, `1` any error

## Installation

```bash
pip install '.[dev]'   # includes pytest + pyinstaller
```

## Usage

```bash
# Validate a YAML config
config-validator examples/good_prod.yaml

# Validate with environment-specific rules
config-validator --env prod examples/good_prod.yaml

# Multiple files
config-validator --env prod config1.yaml config2.yaml

# JSON report to stdout
config-validator --json --env prod examples/good_prod.yaml

# Validate a bad config (exits 1)
config-validator --env prod examples/bad_prod.yaml
```

### CLI flags

| Flag | Default | Description |
|---|---|---|
| `--env` | none | Target environment: `dev`, `stage`, or `prod` |
| `--json` | off | Print structured JSON report to stdout |

### Schema rules

| Field | Type | Required |
|---|---|---|
| `service.name` | string | always |
| `service.image` | string | always |
| `service.replicas` | int | prod, stage |
| `service.port` | int | no |
| `service.environment` | string | no |
| `service.health_check` | string | prod |

### Policies

| Policy | Severity | Environments |
|---|---|---|
| No `latest` image tag | error | all |
| Port in valid range (1–65535) | error | all |
| Minimum replicas ≥ 2 | error | stage, prod |
| Health check recommended | warning | all |

## Build standalone binary

```bash
make build
./dist/config-validator --help
```

Or directly:

```bash
pyinstaller --onefile --name config-validator --clean config_validator_entry.py
```

## Docker

```bash
docker build -t config-validator .
docker run --rm -v $(pwd)/examples:/configs config-validator /configs/good_prod.yaml
```

## Tests

```bash
pytest -v
```

## CI

GitHub Actions workflow at `.github/workflows/config-validator.yml` runs tests on Python 3.10–3.12, smoke-tests example configs, and builds the Docker image.

## Project structure

```
02_config_validator_policy_engine/
├── config_validator/
│   ├── __init__.py
│   ├── cli.py            # argparse CLI entry point
│   ├── loader.py          # YAML/JSON file loader
│   ├── logger.py          # Structured JSON logging
│   ├── models.py          # Issue, ValidationReport domain models
│   ├── policies.py        # Policy engine (no_latest, min_replicas, etc.)
│   └── schema.py          # Schema validation (required fields, types)
├── config_validator_entry.py  # PyInstaller entry point
├── examples/
│   ├── good_prod.yaml
│   ├── bad_prod.yaml
│   ├── minimal_dev.yaml
│   └── service.json
├── tests/
│   ├── test_cli.py
│   ├── test_loader.py
│   ├── test_models.py
│   ├── test_policies.py
│   └── test_schema.py
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```
