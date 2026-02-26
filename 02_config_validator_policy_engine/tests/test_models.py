"""Tests for domain models."""

from config_validator.models import Issue, Severity, ValidationReport


class TestIssue:
    def test_as_dict(self):
        issue = Issue(path="service.name", message="missing", severity=Severity.ERROR, rule="required_field")
        d = issue.as_dict()
        assert d["path"] == "service.name"
        assert d["severity"] == "error"
        assert d["rule"] == "required_field"


class TestValidationReport:
    def test_passed_when_no_errors(self):
        report = ValidationReport(file="test.yaml")
        report.issues.append(Issue("x", "warn", Severity.WARNING, "r"))
        assert report.passed is True
        assert len(report.warnings) == 1

    def test_failed_when_errors(self):
        report = ValidationReport(file="test.yaml")
        report.issues.append(Issue("x", "bad", Severity.ERROR, "r"))
        assert report.passed is False
        assert len(report.errors) == 1

    def test_as_dict(self):
        report = ValidationReport(file="f.yaml", environment="prod")
        d = report.as_dict()
        assert d["file"] == "f.yaml"
        assert d["passed"] is True
        assert d["error_count"] == 0
