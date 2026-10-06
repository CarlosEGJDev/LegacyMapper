"""R2.9 development-only, streamed SHA-256 comparison of complete product trees."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from time import perf_counter

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from legacy_documenter.utils.sanitizer import sanitize_data

EXCLUDED_FILES = frozenset({"RUN_SUMMARY.json", "RUN_SUMMARY.md", "index/repository.json"})
EXCLUDED_DIRECTORIES = frozenset({"_cache_v53"})
CHUNK_SIZE = 1024 * 1024
HASH_WORKERS = 8


def _hash_entry(item: tuple[Path, str]) -> tuple[str, dict]:
    path, relative = item
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
            size += len(chunk)
    return relative, {"size_bytes": size, "sha256": digest.hexdigest()}


def snapshot_tree(root: str | Path) -> dict:
    """Read every included byte; errors propagate, never become equivalence.

    Exclusions are exact root-relative paths from R2.6/R2.7/R2.8. Similarly
    named files elsewhere remain included. Symlinks are refused, not followed.
    """
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Comparison root must be an existing ordinary directory")
    included = []
    excluded = []
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            children = sorted(scan, key=lambda entry: entry.name)
        for entry in children:
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            # DirEntry uses directory-scan metadata, avoiding a separate stat
            # for each of the tens of thousands of IST output files.
            if relative in EXCLUDED_DIRECTORIES and entry.is_dir(follow_symlinks=False):
                excluded.append(relative + "/")
                continue
            if relative in EXCLUDED_FILES and not entry.is_dir(follow_symlinks=False):
                excluded.append(relative)
                continue
            if entry.is_symlink():
                raise ValueError("Symlink is not a reproducible product tree")
            if entry.is_dir(follow_symlinks=False):
                pending.append(path)
            elif entry.is_file(follow_symlinks=False):
                included.append((path, relative))
            else:
                raise ValueError("Non-ordinary file is not a reproducible product tree")
    with ThreadPoolExecutor(max_workers=HASH_WORKERS) as workers:
        entries = dict(workers.map(_hash_entry, included))
    return {"files": dict(sorted(entries.items())), "excluded": sorted(excluded),
            "total_bytes": sum(entry["size_bytes"] for entry in entries.values())}


def compare_snapshots(reference: dict, candidate: dict) -> dict:
    """Compare snapshots made by snapshot_tree; persist hashes, never contents."""
    left, right = reference["files"], candidate["files"]
    common = left.keys() & right.keys()
    added = sorted(right.keys() - left.keys())
    removed = sorted(left.keys() - right.keys())
    changed = sorted(path for path in common if left[path] != right[path])
    return {
        "contract": "LegacyMapperFullIncrementalComparison", "schema_version": "1",
        "files_compared": len(left.keys() | right.keys()), "matched": len(common) - len(changed),
        "equal": not (added or removed or changed), "added": added, "removed": removed, "changed": changed,
        "file_counts": {"reference": len(left), "candidate": len(right)},
        "total_bytes": {"reference": reference["total_bytes"], "candidate": candidate["total_bytes"]},
        "excluded": {"files": sorted(EXCLUDED_FILES), "directories": sorted(EXCLUDED_DIRECTORIES),
                     "reference": reference["excluded"], "candidate": candidate["excluded"]},
    }


def compare_trees(reference: str | Path, candidate: str | Path) -> dict:
    started = perf_counter()
    result = compare_snapshots(snapshot_tree(reference), snapshot_tree(candidate))
    result["duration_seconds"] = round(perf_counter() - started, 6)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference")
    parser.add_argument("candidate")
    parser.add_argument("--json", type=Path, help="Summary outside both product trees")
    args = parser.parse_args(argv)
    if args.json is not None:
        target = args.json.resolve()
        for root in (Path(args.reference).resolve(), Path(args.candidate).resolve()):
            if target == root or root in target.parents:
                parser.error("--json must be outside both product trees")
    try:
        result = compare_trees(args.reference, args.candidate)
    except (OSError, ValueError) as error:
        # No source content, exception text or absolute paths exported.
        print(json.dumps({"equal": False, "error": type(error).__name__}, sort_keys=True))
        return 2
    text = json.dumps(sanitize_data(result), ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    print(text, end="")
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
    return 0 if result["equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
