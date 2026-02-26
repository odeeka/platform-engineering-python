"""CLI entry point for the preflight dependency checker."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from .checker import Target, run_checks


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="preflight",
        description="Validate service dependencies before deployment.",
    )
    p.add_argument(
        "targets",
        nargs="+",
        help=(
            "Dependency targets to check. Formats: "
            "'hostname', 'hostname:port', or 'http(s)://…'"
        ),
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds for each check (default: 5)",
    )
    p.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retry attempts per check (default: 3)",
    )
    p.add_argument(
        "--backoff",
        type=float,
        default=1.0,
        help="Base backoff in seconds for exponential retry (default: 1.0)",
    )
    p.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        default=False,
        help="Print a JSON summary to stdout",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    targets = [Target.from_string(t) for t in args.targets]
    results = run_checks(
        targets,
        timeout=args.timeout,
        retries=args.retries,
        backoff=args.backoff,
    )

    all_ok = all(r.success for r in results)

    if args.json_output:
        summary = {
            "success": all_ok,
            "results": [asdict(r) for r in results],
        }
        print(json.dumps(summary, indent=2))

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
