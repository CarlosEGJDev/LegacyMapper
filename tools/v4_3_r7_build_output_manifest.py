"""CLI wrapper over `legacy_documenter.cli.output_manifest.build_output_manifest` (V4.3-R7).

Not part of the production package; a small operator-facing tool for an
external pilot (or the Technical Lead) to run once after `python main.py
full <repository> --output <dir>` completes:

    python -m tools.v4_3_r7_build_output_manifest <dir>

Writes `<dir>/OUTPUT_MANIFEST.json` (atomically, like every other
LegacyMapper-authoritative artifact) and prints a one-line summary.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from legacy_documenter.cli.output_manifest import MANIFEST_FILENAME, build_output_manifest
from legacy_documenter.utils.atomic_write import atomic_write_text
from legacy_documenter.utils.json_rendering import render_deterministic_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", help="The --output directory of a completed LegacyMapper run")
    args = parser.parse_args(argv)

    manifest = build_output_manifest(args.output_dir)
    target = Path(args.output_dir) / MANIFEST_FILENAME
    atomic_write_text(target, render_deterministic_json(manifest))
    print(f"Wrote {target}: {manifest['file_count']} file(s), {manifest['total_bytes']} byte(s) total.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
