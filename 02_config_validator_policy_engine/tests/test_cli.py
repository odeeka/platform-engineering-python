"""Tests for the CLI module."""

import json
from unittest.mock import patch

import pytest

from config_validator.cli import main
from config_validator.models import Issue, Severity, ValidationReport


class TestCLI:
    def test_exit_0_on_valid_config(self, tmp_path):
        f = tmp_path / "good.yaml"
        f.write_text(
            "service:\n  name: x\n  image: x:1.0\n  replicas: 3\n"
            "  port: 8080\n  health_check: /health\n"
        )
        with pytest.raises(SystemExit) as exc_info:
            main([str(f), "--env", "prod"])
        assert exc_info.value.code == 0

    def test_exit_1_on_invalid_config(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("service:\n  name: x\n")  # missing image → error
        with pytest.raises(SystemExit) as exc_info:
            main([str(f)])
        assert exc_info.value.code == 1

    def test_json_output(self, tmp_path, capsys):
        f = tmp_path / "ok.yaml"
        f.write_text("service:\n  name: svc\n  image: svc:2.0\n  health_check: /h\n")
        with pytest.raises(SystemExit):
            main(["--json", str(f)])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "passed" in data
        assert "reports" in data

    def test_multiple_files(self, tmp_path, capsys):
        f1 = tmp_path / "a.yaml"
        f1.write_text("service:\n  name: a\n  image: a:1.0\n  health_check: /h\n")
        f2 = tmp_path / "b.yaml"
        f2.write_text("service:\n  name: b\n  image: b:2.0\n  health_check: /h\n")
        with pytest.raises(SystemExit) as exc_info:
            main(["--json", str(f1), str(f2)])
        assert exc_info.value.code == 0
        data = json.loads(capsys.readouterr().out)
        assert data["file_count"] == 2

    def test_unparsable_file(self, tmp_path):
        f = tmp_path / "broken.yaml"
        f.write_text("- not\n- a\n- mapping\n")
        with pytest.raises(SystemExit) as exc_info:
            main([str(f)])
        assert exc_info.value.code == 1
