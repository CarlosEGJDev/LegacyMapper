"""V5.2 R2: measures candidate partition defaults over a real run's evidence.

Development-only tool (never imported by the product). Usage:

    python -m tools.v5_2_r2_partition_measurement <run output dir> <scratch dir>

Renders `documentation_v52/` for each candidate (max_items, max_bytes) into
`<scratch>/cand_<items>_<bytes>/` and prints file count, total size, largest
file, size percentiles and number of partition parts, so the shipped defaults
are chosen from data instead of guessed.
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

from legacy_documenter.documentation_v52.engine import (
    generate_documentation_v52, source_from_evidence_dir,
)
from legacy_documenter.documentation_v52.renderer import PartitionPolicy

CANDIDATES = [(100, 32_768), (200, 65_536), (300, 65_536), (300, 131_072), (500, 131_072), (500, 262_144), (1000, 524_288)]


def _percentile(sorted_values: list[int], fraction: float) -> int:
    return sorted_values[min(len(sorted_values) - 1, int(len(sorted_values) * fraction))] if sorted_values else 0


def main(run_dir: str, scratch: str) -> None:
    source = source_from_evidence_dir(Path(run_dir) / "evidence")
    print(f"{'items':>6} {'bytes':>8} {'files':>6} {'parts':>6} {'total MB':>9} {'max KB':>8} {'p50 KB':>7} {'p95 KB':>7} {'s':>5}")
    for items, size in CANDIDATES:
        target = Path(scratch) / f"cand_{items}_{size}"
        shutil.rmtree(target, ignore_errors=True)
        started = time.perf_counter()
        result = generate_documentation_v52(source, target, partition_override=PartitionPolicy(items, size))
        elapsed = time.perf_counter() - started
        sizes = sorted((result.output_dir / name).stat().st_size for name in result.files)
        parts = sum(info["parts"] for info in result.profiles.values())
        print(f"{items:>6} {size:>8} {len(sizes):>6} {parts:>6} {sum(sizes) / 1e6:>9.2f} {sizes[-1] / 1024:>8.1f} "
              f"{_percentile(sizes, .5) / 1024:>7.1f} {_percentile(sizes, .95) / 1024:>7.1f} {elapsed:>5.1f}")
        shutil.rmtree(target, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
