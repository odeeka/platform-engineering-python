"""CLI entry point for the config validator."""

from __future__ import annotations

import argparse
import json
import sys

from .loader import load_config
from .logger import get_logger
from .models import ValidationReport
from .policies import evaluate_policies
from .schema import validate_schema

log = get_logger()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="config-validator",
        description="Validate service configuration files and enforce policies.",
    )
    p.add_argument(
        "files",
        nargs="+",
        help="Config files to validate (YAML or JSON)",
    )
    p.add_argument(
        "--env",
        default=None,
        choices=["dev", "stage", "prod"],
        help="Target environment for environment-specific rules",
    )
    p.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=False,
        help="Print JSON validation report to stdout",
    )
    return p


def validate_file(path: str, environment: str | None) -> ValidationReport:
    """Load and validate a single config file."""
    report = ValidationReport(file=path, environment=environment)

    try:
        data = load_config(path)
    except Exception as exc:
        from .models import Issue, Severity
        report.issues.append(Issue(
            path="(file)",
            message=f"Failed to parse config: {exc}",
            severity=Severity.ERROR,
            rule="parse_error",
        ))
        return report

    report.issues.extend(validate_schema(data, environment))
    report.issues.extend(evaluate_policies(data, environment))
    return report


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    reports: list[ValidationReport] = []
    for path in args.files:
        report = validate_file(path, args.env)
        reports.append(report)

        # Log each issue
        for issue in report.issues:
            log.log(
                40 if issue.severity.value == "error" else 30,  # ERROR=40, WARNING=30
                issue.message,
                extra={"file": path, "rule": issue.rule, "severity": issue.severity.value},
            )

    all_passed = all(r.passed for r in reports)

    if args.json_output:
        summary = {
            "passed": all_passed,
            "file_count": len(reports),
            "reports": [r.as_dict() for r in reports],
        }
        print(json.dumps(summary, indent=2))

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
