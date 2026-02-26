"""Domain models for validation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Issue:
    """A single validation or policy issue."""

    path: str  # e.g. "service.image"
    message: str
    severity: Severity
    rule: str  # which rule triggered this

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "message": self.message,
            "severity": self.severity.value,
            "rule": self.rule,
        }


@dataclass
class ValidationReport:
    """Aggregated validation report."""

    file: str
    environment: str | None = None
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def as_dict(self) -> dict:
        return {
            "file": self.file,
            "environment": self.environment,
            "passed": self.passed,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.as_dict() for i in self.issues],
        }
