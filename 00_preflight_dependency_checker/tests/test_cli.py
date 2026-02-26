"""Unit tests for the CLI module."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from preflight_checker.checker import CheckResult
from preflight_checker.cli import main


class TestCLI:
    @patch("preflight_checker.cli.run_checks")
    def test_exit_0_on_success(self, mock_run):
        mock_run.return_value = [CheckResult("h", "dns", True, "ok")]
        with pytest.raises(SystemExit) as exc_info:
            main(["example.com"])
        assert exc_info.value.code == 0

    @patch("preflight_checker.cli.run_checks")
    def test_exit_1_on_failure(self, mock_run):
        mock_run.return_value = [CheckResult("h", "dns", False, "fail")]
        with pytest.raises(SystemExit) as exc_info:
            main(["example.com"])
        assert exc_info.value.code == 1

    @patch("preflight_checker.cli.run_checks")
    def test_json_output(self, mock_run, capsys):
        mock_run.return_value = [CheckResult("h", "dns", True, "ok")]
        with pytest.raises(SystemExit):
            main(["--json", "example.com"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["success"] is True
        assert len(data["results"]) == 1

    @patch("preflight_checker.cli.run_checks")
    def test_custom_flags(self, mock_run):
        mock_run.return_value = [CheckResult("h", "dns", True, "ok")]
        with pytest.raises(SystemExit):
            main(["--timeout", "10", "--retries", "5", "--backoff", "2.0", "host"])
        # Verify run_checks was called with custom params
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 10.0
        assert kwargs["retries"] == 5
        assert kwargs["backoff"] == 2.0
