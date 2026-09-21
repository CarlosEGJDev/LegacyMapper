"""Builds a clean, runtime-only copy of LegacyMapper for an external pilot (V4.3-R7).

Copies only what `python main.py analyze|full ...` needs to run: `main.py`,
the `legacy_documenter/` package (excluding `__pycache__`/`*.pyc`), and
`requirements-copilot.txt` -- the optional dependency declaration for the
one lazily-imported third-party module (`copilot`, imported only inside
`CopilotProvider._generate`, i.e. only when a real Copilot provider call is
actually made -- never during deterministic analysis). Excludes everything
else in this development repository -- `docs/`, `prompts/`, `tests/`,
`codex/`, `output/`, `result_codex/`, `tools/`, `README.md`, `AGENTS.md`,
`CLAUDE.md`, `PROJECT_STATE.json`, `.git*` -- none of which
`legacy_documenter`/`main.py` import or read at runtime: an AST scan of
every `legacy_documenter/**/*.py` import (V4.3-R7 internal acceptance)
found only Python standard-library modules plus that one optional module.
`requirements-copilot.txt` itself is never imported by the runtime; it is
carried only so a pilot operator can `pip install -r requirements-copilot.txt`
from inside the distribution instead of depending on the SDK already being
present in their global Python environment (V4.3 pre-closure distribution
dependency follow-up). See `docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md`
and `docs/V4_3/V4_3_PRE_CLOSURE_DISTRIBUTION_DEPENDENCY_FOLLOWUP_RESULT.md`
for the full verification.

Usage:

    python -m tools.v4_3_r7_build_pilot_distribution <destination>

`<destination>` must not already exist (or must be empty) -- this tool never
overwrites or merges into a directory that might already hold something
else, including a *previous* pilot distribution build, since a stale file
left over from an earlier LegacyMapper version silently mixed into a newer
copy would be exactly the kind of "clean distribution" defect this tool
exists to prevent.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The exact, fixed set of repository-root entries a runtime distribution
#: needs. Never derived by "copy everything except a blocklist" -- an
#: allowlist is the only way to guarantee a *new* dev-only file added to the
#: repository root in a future round does not silently leak into a pilot
#: distribution without an explicit decision to add it here.
RUNTIME_ROOT_ENTRIES: tuple[str, ...] = ("main.py", "legacy_documenter", "requirements-copilot.txt")

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def build_distribution(destination: str | Path, repo_root: str | Path = REPO_ROOT) -> list[str]:
    """Copies `RUNTIME_ROOT_ENTRIES` from `repo_root` into `destination`.

    Raises `FileExistsError` if `destination` already exists and is not
    empty. Returns the sorted list of every file path actually copied,
    relative to `destination`.
    """
    repo_root = Path(repo_root)
    destination = Path(destination)
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)

    for name in RUNTIME_ROOT_ENTRIES:
        source = repo_root / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, ignore=_IGNORE)
        else:
            shutil.copy2(source, target)

    return sorted(p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)

    copied = build_distribution(args.destination, args.repo_root)
    print(f"Copied {len(copied)} file(s) into {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
