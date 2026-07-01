from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .compiler import compile_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fanfic-bookmaker",
        description="Compile scene-based fiction projects into chapter and book exports.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root of the writing repository.",
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default="fanfic.yml",
        help="Optional top-level config file.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory for generated exports.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compile_project(
            root=args.root,
            config_filename=args.config_file,
            output_dir=args.output_dir,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"fanfic-bookmaker: {exc}", file=sys.stderr)
        return 1

    for path in result.generated_files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
