"""CLI entry point."""

from __future__ import annotations

import argparse

from .server import run_server


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mini-api",
        description="Minimal REST API with observability.",
    )
    p.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    p.add_argument("--port", type=int, default=8080, help="Listen port (default: 8080)")
    p.add_argument(
        "--work-timeout",
        type=float,
        default=5.0,
        help="Max seconds for /work requests (default: 5.0)",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    run_server(host=args.host, port=args.port, work_timeout=args.work_timeout)


if __name__ == "__main__":
    main()
