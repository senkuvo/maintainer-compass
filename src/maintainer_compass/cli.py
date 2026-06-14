from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .report import render
from .scanner import scan_repository
from .templates import write_templates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maintainer-compass",
        description="Audit an open-source repository for maintainer readiness.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan a repository")
    scan.add_argument("path", nargs="?", default=".", help="repository path to scan")
    scan.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="report format",
    )
    scan.add_argument("--output", help="write report to this file")
    scan.add_argument(
        "--only-failures",
        action="store_true",
        help="limit report findings to checks that need attention",
    )
    scan.add_argument(
        "--fail-under",
        type=int,
        metavar="SCORE",
        help="exit with status 2 when score is below SCORE",
    )

    init = subparsers.add_parser("init", help="write starter maintainer files")
    init.add_argument("path", nargs="?", default=".", help="repository path")
    init.add_argument("--overwrite", action="store_true", help="replace existing template files")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        result = scan_repository(args.path)
        output = render(result, args.format, only_failures=args.only_failures)
        if args.output:
            Path(args.output).write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        if args.fail_under is not None and result.score < args.fail_under:
            return 2
        return 0

    if args.command == "init":
        written = write_templates(args.path, overwrite=args.overwrite)
        if written:
            print("Wrote starter files:")
            for path in written:
                print(f"- {path}")
        else:
            print("No files written; templates already exist.")
        return 0

    parser.print_help(sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
