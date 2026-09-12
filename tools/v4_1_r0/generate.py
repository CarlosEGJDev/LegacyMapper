"""Writes the two V4.1-R0 artifacts and proves determinism.

Usage: `python -m tools.v4_1_r0.generate`

Writes:
  output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
  output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Then rebuilds both payloads a second time, independently, in the same
process, and confirms the serialized bytes are identical both times
(MAINTAINABILITY_INVENTORY_DETERMINISM / REFACTOR_PLAN_DETERMINISM).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _serialize(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate(root: Path = REPO_ROOT) -> dict[str, object]:
    from . import report

    inventory_1 = _serialize(report.build_inventory(root))
    inventory_2 = _serialize(report.build_inventory(root))
    plan_1 = _serialize(report.build_plan(root))
    plan_2 = _serialize(report.build_plan(root))

    inventory_determinism = "PASS" if inventory_1 == inventory_2 else "FAIL"
    plan_determinism = "PASS" if plan_1 == plan_2 else "FAIL"

    out_dir = root / "output" / "v4_1_r0"
    out_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = out_dir / "V4_1_MAINTAINABILITY_INVENTORY.json"
    plan_path = out_dir / "V4_1_REFACTOR_PLAN.json"
    # newline="" prevents platform newline translation (Windows would
    # otherwise rewrite "\n" to "\r\n" on disk, changing the file's bytes
    # away from what was just hashed in memory).
    inventory_path.write_text(inventory_1, encoding="utf-8", newline="")
    plan_path.write_text(plan_1, encoding="utf-8", newline="")

    return {
        "inventory_path": str(inventory_path.relative_to(root).as_posix()),
        "plan_path": str(plan_path.relative_to(root).as_posix()),
        "inventory_sha256": _sha256(inventory_1),
        "plan_sha256": _sha256(plan_1),
        "inventory_determinism": inventory_determinism,
        "plan_determinism": plan_determinism,
    }


if __name__ == "__main__":
    result = generate()
    json.dump(result, sys.stdout, indent=2)
    print()
