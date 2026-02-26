"""Policy engine: enforceable rules on config values."""

from __future__ import annotations

from .models import Issue, Severity
from .schema import _get_nested


# ---------------------------------------------------------------------------
# Individual policy functions
# ---------------------------------------------------------------------------
# Each returns a list of Issues (empty = pass).

def no_latest_image(data: dict) -> list[Issue]:
    """Image tag must not be 'latest'."""
    found, value = _get_nested(data, "service.image")
    if not found or not isinstance(value, str):
        return []
    if value.endswith(":latest") or ":" not in value:
        return [Issue(
            path="service.image",
            message=f"Image '{value}' uses implicit or explicit 'latest' tag",
            severity=Severity.ERROR,
            rule="no_latest_image",
        )]
    return []


def minimum_replicas(data: dict, *, minimum: int = 2) -> list[Issue]:
    """Replicas must be >= *minimum* (only enforced if field present)."""
    found, value = _get_nested(data, "service.replicas")
    if not found:
        return []
    if not isinstance(value, int):
        return []
    if value < minimum:
        return [Issue(
            path="service.replicas",
            message=f"Replicas ({value}) below minimum ({minimum})",
            severity=Severity.ERROR,
            rule="minimum_replicas",
        )]
    return []


def port_range(data: dict) -> list[Issue]:
    """Port must be between 1 and 65535."""
    found, value = _get_nested(data, "service.port")
    if not found or not isinstance(value, int):
        return []
    if not (1 <= value <= 65535):
        return [Issue(
            path="service.port",
            message=f"Port {value} outside valid range 1-65535",
            severity=Severity.ERROR,
            rule="port_range",
        )]
    return []


def health_check_warning(data: dict) -> list[Issue]:
    """Warn if no health check is defined."""
    found, _ = _get_nested(data, "service.health_check")
    if not found:
        return [Issue(
            path="service.health_check",
            message="No health check endpoint defined",
            severity=Severity.WARNING,
            rule="health_check_recommended",
        )]
    return []


# ---------------------------------------------------------------------------
# Policy sets per environment
# ---------------------------------------------------------------------------
# A policy is just a callable(data) -> list[Issue].
# We group them so prod gets stricter checks.

_COMMON_POLICIES = [no_latest_image, port_range, health_check_warning]

POLICY_SETS: dict[str, list] = {
    "dev": _COMMON_POLICIES,
    "stage": _COMMON_POLICIES + [minimum_replicas],
    "prod": _COMMON_POLICIES + [minimum_replicas],
}

DEFAULT_POLICIES = _COMMON_POLICIES


def evaluate_policies(
    data: dict,
    environment: str | None = None,
) -> list[Issue]:
    """Run all applicable policies against *data*."""
    policies = POLICY_SETS.get(environment or "", DEFAULT_POLICIES)
    issues: list[Issue] = []
    for policy_fn in policies:
        issues.extend(policy_fn(data))
    return issues
