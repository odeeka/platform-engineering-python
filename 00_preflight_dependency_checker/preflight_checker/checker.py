"""Core dependency checks: DNS, TCP, HTTP."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass, field
from typing import Callable
from urllib.parse import urlparse

import requests

from .logger import get_logger

log = get_logger()


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------
@dataclass
class CheckResult:
    target: str
    check: str
    success: bool
    message: str
    attempts: int = 1
    elapsed_ms: float = 0.0


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------
def retry(
    fn: Callable[[], CheckResult],
    retries: int = 3,
    backoff_base: float = 1.0,
) -> CheckResult:
    """Run *fn* up to *retries* times with exponential backoff."""
    last_result: CheckResult | None = None
    for attempt in range(1, retries + 1):
        result = fn()
        result.attempts = attempt
        if result.success:
            return result
        last_result = result
        if attempt < retries:
            wait = backoff_base * (2 ** (attempt - 1))
            log.info(
                "Retrying in %.1fs …",
                wait,
                extra={"target": result.target, "check": result.check, "attempt": attempt},
            )
            time.sleep(wait)
    assert last_result is not None
    return last_result


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------
def check_dns(host: str, timeout: float = 5.0) -> CheckResult:
    """Resolve *host* via DNS."""
    start = time.monotonic()
    try:
        socket.setdefaulttimeout(timeout)
        addrs = socket.getaddrinfo(host, None)
        elapsed = (time.monotonic() - start) * 1000
        ips = sorted({a[4][0] for a in addrs})
        return CheckResult(
            target=host,
            check="dns",
            success=True,
            message=f"Resolved to {', '.join(ips)}",
            elapsed_ms=round(elapsed, 2),
        )
    except socket.gaierror as exc:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            target=host, check="dns", success=False,
            message=str(exc), elapsed_ms=round(elapsed, 2),
        )


def check_tcp(host: str, port: int, timeout: float = 5.0) -> CheckResult:
    """Open a TCP connection to *host*:*port*."""
    target = f"{host}:{port}"
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed = (time.monotonic() - start) * 1000
            return CheckResult(
                target=target, check="tcp", success=True,
                message="Connection established",
                elapsed_ms=round(elapsed, 2),
            )
    except (OSError, socket.timeout) as exc:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            target=target, check="tcp", success=False,
            message=str(exc), elapsed_ms=round(elapsed, 2),
        )


def check_http(url: str, timeout: float = 5.0) -> CheckResult:
    """GET *url* and expect a 2xx response."""
    start = time.monotonic()
    try:
        resp = requests.get(url, timeout=timeout)
        elapsed = (time.monotonic() - start) * 1000
        ok = 200 <= resp.status_code < 300
        return CheckResult(
            target=url, check="http", success=ok,
            message=f"HTTP {resp.status_code}",
            elapsed_ms=round(elapsed, 2),
        )
    except requests.RequestException as exc:
        elapsed = (time.monotonic() - start) * 1000
        return CheckResult(
            target=url, check="http", success=False,
            message=str(exc), elapsed_ms=round(elapsed, 2),
        )


# ---------------------------------------------------------------------------
# High-level runner
# ---------------------------------------------------------------------------
@dataclass
class Target:
    """A single dependency to validate."""
    host: str
    port: int | None = None
    http_url: str | None = None

    @classmethod
    def from_string(cls, value: str) -> "Target":
        """Parse a target string.

        Accepted formats:
          - ``host``              → DNS only
          - ``host:port``         → DNS + TCP
          - ``http(s)://…``       → DNS + TCP (if port detectable) + HTTP
        """
        if value.startswith("http://") or value.startswith("https://"):
            parsed = urlparse(value)
            host = parsed.hostname or value
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            return cls(host=host, port=port, http_url=value)
        if ":" in value:
            host, port_str = value.rsplit(":", 1)
            return cls(host=host, port=int(port_str))
        return cls(host=value)


def run_checks(
    targets: list[Target],
    timeout: float = 5.0,
    retries: int = 3,
    backoff: float = 1.0,
) -> list[CheckResult]:
    """Run all applicable checks for every target. Returns list of results."""

    results: list[CheckResult] = []

    for t in targets:
        # DNS
        result = retry(lambda t=t: check_dns(t.host, timeout), retries, backoff)
        log.info(
            result.message,
            extra={"target": t.host, "check": "dns",
                   "elapsed_ms": result.elapsed_ms, "status": "pass" if result.success else "fail"},
        )
        results.append(result)
        if not result.success:
            continue  # skip TCP/HTTP if DNS fails

        # TCP
        if t.port is not None:
            result = retry(lambda t=t: check_tcp(t.host, t.port, timeout), retries, backoff)
            log.info(
                result.message,
                extra={"target": f"{t.host}:{t.port}", "check": "tcp",
                       "elapsed_ms": result.elapsed_ms, "status": "pass" if result.success else "fail"},
            )
            results.append(result)

        # HTTP
        if t.http_url is not None:
            result = retry(lambda t=t: check_http(t.http_url, timeout), retries, backoff)
            log.info(
                result.message,
                extra={"target": t.http_url, "check": "http",
                       "elapsed_ms": result.elapsed_ms, "status": "pass" if result.success else "fail"},
            )
            results.append(result)

    return results
