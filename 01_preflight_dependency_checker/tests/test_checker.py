"""Unit tests for the checker module."""

from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

import pytest
import requests

from preflight_checker.checker import (
    CheckResult,
    Target,
    check_dns,
    check_http,
    check_tcp,
    retry,
    run_checks,
)


# ---------------------------------------------------------------------------
# Target.from_string
# ---------------------------------------------------------------------------
class TestTargetFromString:
    def test_host_only(self):
        t = Target.from_string("example.com")
        assert t.host == "example.com"
        assert t.port is None
        assert t.http_url is None

    def test_host_port(self):
        t = Target.from_string("db.local:5432")
        assert t.host == "db.local"
        assert t.port == 5432
        assert t.http_url is None

    def test_http_url(self):
        t = Target.from_string("http://api.local:8080/health")
        assert t.host == "api.local"
        assert t.port == 8080
        assert t.http_url == "http://api.local:8080/health"

    def test_https_default_port(self):
        t = Target.from_string("https://secure.example.com/healthz")
        assert t.host == "secure.example.com"
        assert t.port == 443
        assert t.http_url == "https://secure.example.com/healthz"

    def test_http_default_port(self):
        t = Target.from_string("http://plain.example.com/ready")
        assert t.host == "plain.example.com"
        assert t.port == 80


# ---------------------------------------------------------------------------
# check_dns
# ---------------------------------------------------------------------------
class TestCheckDNS:
    @patch("preflight_checker.checker.socket.getaddrinfo")
    def test_success(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.2.3.4", 0)),
        ]
        result = check_dns("example.com")
        assert result.success is True
        assert "1.2.3.4" in result.message

    @patch("preflight_checker.checker.socket.getaddrinfo", side_effect=socket.gaierror("not found"))
    def test_failure(self, _mock):
        result = check_dns("nonexistent.invalid")
        assert result.success is False
        assert "not found" in result.message


# ---------------------------------------------------------------------------
# check_tcp
# ---------------------------------------------------------------------------
class TestCheckTCP:
    @patch("preflight_checker.checker.socket.create_connection")
    def test_success(self, mock_conn):
        mock_conn.return_value.__enter__ = MagicMock()
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = check_tcp("localhost", 80)
        assert result.success is True
        assert result.target == "localhost:80"

    @patch("preflight_checker.checker.socket.create_connection", side_effect=OSError("refused"))
    def test_failure(self, _mock):
        result = check_tcp("localhost", 9999)
        assert result.success is False
        assert "refused" in result.message


# ---------------------------------------------------------------------------
# check_http
# ---------------------------------------------------------------------------
class TestCheckHTTP:
    @patch("preflight_checker.checker.requests.get")
    def test_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        result = check_http("http://example.com/health")
        assert result.success is True
        assert "200" in result.message

    @patch("preflight_checker.checker.requests.get")
    def test_non_2xx(self, mock_get):
        mock_get.return_value = MagicMock(status_code=503)
        result = check_http("http://example.com/health")
        assert result.success is False
        assert "503" in result.message

    @patch("preflight_checker.checker.requests.get", side_effect=requests.ConnectionError("timeout"))
    def test_connection_error(self, _mock):
        result = check_http("http://example.com/health")
        assert result.success is False


# ---------------------------------------------------------------------------
# retry
# ---------------------------------------------------------------------------
class TestRetry:
    def test_succeeds_first_try(self):
        fn = MagicMock(return_value=CheckResult("h", "dns", True, "ok"))
        result = retry(fn, retries=3, backoff_base=0)
        assert result.success is True
        assert fn.call_count == 1

    @patch("preflight_checker.checker.time.sleep")
    def test_succeeds_after_retries(self, mock_sleep):
        results = iter([
            CheckResult("h", "dns", False, "fail"),
            CheckResult("h", "dns", False, "fail"),
            CheckResult("h", "dns", True, "ok"),
        ])
        fn = MagicMock(side_effect=lambda: next(results))
        result = retry(fn, retries=3, backoff_base=0.01)
        assert result.success is True
        assert result.attempts == 3

    @patch("preflight_checker.checker.time.sleep")
    def test_all_retries_exhausted(self, mock_sleep):
        fn = MagicMock(return_value=CheckResult("h", "dns", False, "fail"))
        result = retry(fn, retries=2, backoff_base=0.01)
        assert result.success is False
        assert fn.call_count == 2


# ---------------------------------------------------------------------------
# run_checks (integration-style with mocks)
# ---------------------------------------------------------------------------
class TestRunChecks:
    @patch("preflight_checker.checker.check_http")
    @patch("preflight_checker.checker.check_tcp")
    @patch("preflight_checker.checker.check_dns")
    def test_full_http_target(self, mock_dns, mock_tcp, mock_http):
        mock_dns.return_value = CheckResult("h", "dns", True, "ok")
        mock_tcp.return_value = CheckResult("h:80", "tcp", True, "ok")
        mock_http.return_value = CheckResult("http://h/health", "http", True, "HTTP 200")

        targets = [Target.from_string("http://h/health")]
        results = run_checks(targets, retries=1, backoff=0)

        assert len(results) == 3
        assert all(r.success for r in results)

    @patch("preflight_checker.checker.check_dns")
    def test_dns_failure_skips_rest(self, mock_dns):
        mock_dns.return_value = CheckResult("h", "dns", False, "nope")

        targets = [Target.from_string("http://h/health")]
        results = run_checks(targets, retries=1, backoff=0)

        assert len(results) == 1
        assert results[0].success is False
