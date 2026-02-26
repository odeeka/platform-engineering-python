"""Schema-based validation: required fields and type checking."""

from __future__ import annotations

from .models import Issue, Severity

# ---------------------------------------------------------------------------
# Schema definition — keeps things declarative and simple.
# Each field: (dotted_path, expected_type, required)
# ---------------------------------------------------------------------------
# Common fields every config must have
BASE_SCHEMA: list[tuple[str, type, bool]] = [
    ("service.name", str, True),
    ("service.image", str, True),
    ("service.replicas", int, False),
    ("service.port", int, False),
    ("service.environment", str, False),
    ("service.health_check", str, False),
]

# Extra required fields per environment
ENV_REQUIRED: dict[str, list[str]] = {
    "prod": ["service.replicas", "service.health_check"],
    "stage": ["service.replicas"],
}


def _get_nested(data: dict, dotted_path: str):
    """Traverse a nested dict by dotted key path. Returns (found, value)."""
    keys = dotted_path.split(".")
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return False, None
        current = current[key]
    return True, current


def validate_schema(
    data: dict,
    environment: str | None = None,
    schema: list[tuple[str, type, bool]] | None = None,
) -> list[Issue]:
    """Validate *data* against the schema. Returns list of issues."""

    schema = schema if schema is not None else BASE_SCHEMA
    issues: list[Issue] = []

    # ---- required + type checks from schema ----
    for path, expected_type, required in schema:
        found, value = _get_nested(data, path)
        if not found:
            if required:
                issues.append(Issue(
                    path=path,
                    message=f"Missing required field '{path}'",
                    severity=Severity.ERROR,
                    rule="required_field",
                ))
            continue
        if not isinstance(value, expected_type):
            issues.append(Issue(
                path=path,
                message=f"Expected type '{expected_type.__name__}', got '{type(value).__name__}'",
                severity=Severity.ERROR,
                rule="type_check",
            ))

    # ---- environment-specific required fields ----
    if environment and environment in ENV_REQUIRED:
        for path in ENV_REQUIRED[environment]:
            found, _ = _get_nested(data, path)
            if not found:
                issues.append(Issue(
                    path=path,
                    message=f"Field '{path}' is required for environment '{environment}'",
                    severity=Severity.ERROR,
                    rule="env_required",
                ))

    return issues
