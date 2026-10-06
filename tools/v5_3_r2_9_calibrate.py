"""Sequential, resumable R2.9 IST calibration. Mutations only inside output/."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from time import perf_counter

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from legacy_documenter.cli.pipeline_stages import scan_repository
from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES
from legacy_documenter.utils.sanitizer import sanitize_data
from legacy_documenter.utils.stage_timings import TIMINGS
from legacy_documenter.utils.write_if_changed import LEDGER
from tools.v5_3_compare_full_incremental import compare_snapshots, compare_trees, snapshot_tree

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "output" / "v53r29"
SOURCE = Path(r"C:\Users\cgalianj\source\IST_40\operacional")
GRID = (0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1.0)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(sanitize_data(value), sort_keys=True, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def guarded(path: Path) -> Path:
    resolved = path.resolve()
    if WORK.resolve() not in resolved.parents or SOURCE.resolve() == resolved or SOURCE.resolve() in resolved.parents:
        raise ValueError("Mutation target must remain strictly inside calibration output")
    return resolved


def reset_cache(target: Path, baseline: Path) -> None:
    guarded(target)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(baseline, target)


def prepare() -> dict:
    WORK.mkdir(parents=True, exist_ok=True)
    plan = WORK / "PLAN.json"
    if plan.exists():
        return json.loads(plan.read_text(encoding="utf-8"))
    scan = scan_repository(SOURCE, None)
    project_directories = sorted({Path(f.relative_path).parent.as_posix() for f in scan.files if f.file_type == "vb_project"},
                                 key=lambda p: (-len(p), p))
    groups = defaultdict(list)
    for file in scan.files:
        relative = Path(file.relative_path).as_posix()
        owner = next((p for p in project_directories if p == "." or relative.startswith(p + "/")), Path(relative).parent.as_posix())
        priority = 0 if file.file_type == "vb_source" else 1 if file.file_type in ANALYZED_FILE_TYPES else 2
        groups[(priority, owner)].append({"path": relative, "file_type": file.file_type})
    order = []
    for priority in range(3):
        buckets = [sorted(items, key=lambda item: item["path"]) for (rank, owner), items in sorted(groups.items()) if rank == priority]
        for index in range(max(map(len, buckets), default=0)):
            order.extend(bucket[index] for bucket in buckets if index < len(bucket))
    repo = guarded(WORK / "r")
    if repo.exists():
        raise ValueError("Partial repository copy exists without PLAN; inspect before resuming")
    repo.mkdir()
    started = perf_counter()
    fingerprints = []
    for entry in order:
        source = SOURCE / entry["path"]
        target = guarded(repo / entry["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        fingerprints.append((entry["path"], hashlib.sha256(source.read_bytes()).hexdigest()))
    plan_data = {"files_total": len(order), "file_types": dict(Counter(e["file_type"] for e in order)),
                 "selection": "VB first, other analyzed second, inventory last; round-robin nearest project directories; lexical ties",
                 "order": order, "source_fingerprints": fingerprints, "copy_seconds": round(perf_counter() - started, 3)}
    write_json(plan, plan_data)
    print("PREPARED", len(order), "files", flush=True)
    return plan_data


def run(name: str, output: Path, *, mode="auto", verify="fast", cache=None, threshold=None) -> dict:
    saved = WORK / "runs" / (name + ".json")
    if saved.exists():
        return json.loads(saved.read_text(encoding="utf-8"))
    telemetry = WORK / "telemetry" / (name + ".json")
    command = [sys.executable, "-X", "utf8", "-m", "tools.v5_3_r2_9_calibrate", "measure", str(telemetry),
               "full", str(WORK / "r"), "--output", str(output),
               "--cache-mode", mode, "--verify-cache=" + verify, "--long-paths"]
    if cache is not None:
        command.extend(["--cache-dir", str(cache)])
    if threshold is not None:
        command.extend(["--incremental-max-changed-ratio", str(threshold)])
    print("START", name, flush=True)
    started = perf_counter()
    # Do not persist arbitrary process output, which may contain raw diagnostic evidence.
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    seconds = perf_counter() - started
    if completed.returncode != 0:
        write_json(saved.with_suffix(".error.json"), {"name": name, "exit_code": completed.returncode, "seconds": seconds})
        raise RuntimeError("Pipeline failed: " + name + "; inspect local summary, no raw output exported")
    cache_dir = cache if cache is not None else output / "_cache_v53"
    summary = json.loads((output / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
    if summary.get("ai_requested") or summary.get("ai_invoked"):
        raise RuntimeError("Unexpected AI activity in calibration")
    metrics_path = cache_dir / "RUN_METRICS.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if mode != "off" else None
    result = {"name": name, "cache_mode": mode, "verify": verify, "threshold": threshold,
              "wall_seconds": round(seconds, 3), "metrics": metrics, "exit_code": completed.returncode,
              "ai_requested": False, "ai_invoked": False}
    mutation_state = WORK / "MUTATION.json"
    result["controlled_source_modified_from_original"] = len(json.loads(mutation_state.read_text(encoding="utf-8"))) if mutation_state.exists() else 0
    if telemetry.exists():
        result["telemetry"] = json.loads(telemetry.read_text(encoding="utf-8"))
    if metrics is not None:
        result["cache_bytes_on_disk"] = sum(p.stat().st_size for p in cache_dir.rglob("*") if p.is_file())
        result["shard_count"] = len(list((cache_dir / "extraction").glob("ex-*.json")))
    write_json(saved, result)
    print("DONE", name, round(seconds, 3), flush=True)
    return result


def compare(name: str, left: Path, right: Path) -> dict:
    saved = WORK / "comparisons" / (name + ".json")
    if saved.exists():
        result = json.loads(saved.read_text(encoding="utf-8"))
    else:
        result = compare_trees(left, right)
        write_json(saved, result)
    print("COMPARE", name, result["equal"], "changed", len(result["changed"]), flush=True)
    if not result["equal"]:
        raise RuntimeError("Deterministic divergence: " + name)
    return result


def mutate(plan: dict, count: int, marker: str) -> None:
    # Restore bytes only where necessary. Copy/edits are outside timed runs;
    # bounded parallel I/O reduces antivirus overhead without concurrent pipelines.
    state_file = WORK / "MUTATION.json"
    previous = set(json.loads(state_file.read_text(encoding="utf-8"))) if state_file.exists() else set()
    selected = {entry["path"] for entry in plan["order"][:count]}
    affected = [entry for entry in plan["order"] if entry["path"] in previous | selected]

    def change(entry):
        target = guarded(WORK / "r" / entry["path"])
        data = (SOURCE / entry["path"]).read_bytes()
        if entry["path"] not in selected:
            target.write_bytes(data)
            return
        kind = entry["file_type"]
        if kind == "vb_source":
            # Insert a valid VB comment before the first source line, exercising
            # line-dependent IDs and their effects across projects, not only hash changes.
            if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
                codec = "utf-16-le" if data.startswith(b"\xff\xfe") else "utf-16-be"
                data = data[:2] + ("' " + marker + "\r\n").encode(codec) + data[2:]
            else:
                bom = b"\xef\xbb\xbf" if data.startswith(b"\xef\xbb\xbf") else b""
                data = bom + ("' " + marker + "\r\n").encode("ascii") + data[len(bom):]
        elif kind in {"aspx", "ascx", "master", "vb_project", "web_config"}:
            text = "\r\n<!-- " + marker + " -->\r\n"
            if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
                text_bytes = text.encode("utf-16-le" if data.startswith(b"\xff\xfe") else "utf-16-be")
            else:
                text_bytes = text.encode("ascii")
            data += text_bytes
        elif kind == "solution":
            text = "\r\n# " + marker + "\r\n"
            codec = "utf-16-le" if data.startswith(b"\xff\xfe") else "utf-16-be" if data.startswith(b"\xfe\xff") else "ascii"
            data += text.encode(codec)
        else:
            # Non-extractor inputs: metadata inventory stress only; never parsed.
            data += ("\r\n" + marker + "\r\n").encode("ascii")
        target.write_bytes(data)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(change, affected))
    write_json(state_file, sorted(selected))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("baseline", "cold-proof", "verify", "grid", "repeat-high", "threshold", "audit"))
    parser.add_argument("--ratios", help="Explicit comma-separated adaptive grid, recorded in GRID_REQUESTS.json")
    args = parser.parse_args(argv)
    plan = prepare()
    incremental, reference = WORK / "i", WORK / "f"
    baseline_cache = WORK / "baseline_cache"
    if args.phase == "baseline":
        cold_was_saved = (WORK / "runs" / "A_auto_cold.json").exists()
        run("A_auto_cold", incremental)
        cold_snapshot_path = WORK / "COLD_SNAPSHOT.json"
        if not cold_was_saved and not cold_snapshot_path.exists():
            write_json(cold_snapshot_path, snapshot_tree(incremental))
        run("B_auto_warm", incremental)
        run("C_off", reference, mode="off")
        compare("baseline_auto_off", reference, incremental)
        run("D_refresh", incremental, mode="refresh")
        compare("baseline_refresh_off", reference, incremental)
        if not baseline_cache.exists():
            shutil.copytree(incremental / "_cache_v53", baseline_cache)
        reference_snapshot = snapshot_tree(reference)
        write_json(WORK / "BASELINE_SNAPSHOT.json", reference_snapshot)
        if cold_snapshot_path.exists():
            cold_comparison = compare_snapshots(reference_snapshot, json.loads(cold_snapshot_path.read_text(encoding="utf-8")))
            write_json(WORK / "comparisons" / "baseline_cold_off.json", cold_comparison)
            if not cold_comparison["equal"]:
                raise RuntimeError("Cold product differs from off")
    elif args.phase == "cold-proof":
        # Useful when a prior baseline invocation captured timings but did not
        # preserve cold bytes before the warm rerun. Never relabel warm bytes cold.
        name = "A_cold_proof"
        if not (WORK / "runs" / (name + ".json")).exists():
            cache = guarded(incremental / "_cache_v53")
            if cache.exists():
                shutil.rmtree(cache)
        run(name, incremental)
        compare("baseline_cold_off", reference, incremental)
    elif args.phase == "verify":
        for repetition in range(1, 4):
            for level in ("fast", "hash"):
                run(f"verify_{level}_{repetition}", incremental, verify=level)
                compare(f"verify_{level}_{repetition}", reference, incremental)
        external = WORK / "external_cache"
        run("I_external_cold", incremental, cache=external)
        compare("external_cold_off", reference, incremental)
        run("I_external_warm", incremental, cache=external)
        compare("external_off", reference, incremental)
    elif args.phase == "grid":
        ratios = GRID if args.ratios is None else tuple(float(value) for value in args.ratios.split(","))
        if any(not 0 <= ratio <= 1 for ratio in ratios):
            parser.error("Ratios must be fractions in [0, 1]")
        requests_path = WORK / "GRID_REQUESTS.json"
        requests = json.loads(requests_path.read_text(encoding="utf-8")) if requests_path.exists() else []
        requests.append(list(ratios))
        write_json(requests_path, requests)
        for ratio in ratios:
            name = "ratio_" + str(ratio).replace(".", "_")
            count = round(plan["files_total"] * ratio)
            if (WORK / "comparisons" / (name + ".json")).exists():
                continue
            mutate(plan, count, name)
            reset_cache(incremental / "_cache_v53", baseline_cache)
            run(name + "_auto", incremental)
            # refresh retains write-skip and is the correct cost comparator for
            # the ratio fallback. It starts on the OTHER output tree, which has
            # the same previous-level product as incremental before this change.
            # Running refresh on the just-updated incremental output would bias
            # the benchmark by eliminating every changed output write.
            run(name + "_refresh", reference, mode="refresh")
            compare(name, reference, incremental)
    elif args.phase == "threshold":
        for name, count, threshold in (("G_below_candidate", 15, 0.005), ("H_above_candidate", 151, 0.005)):
            mutate(plan, count, name)
            reset_cache(incremental / "_cache_v53", baseline_cache)
            run(name, incremental, threshold=threshold)
            run(name + "_refresh", reference, mode="refresh")
            compare(name, reference, incremental)
    elif args.phase == "repeat-high":
        ratios = (0.25, 0.5, 1.0) if args.ratios is None else tuple(float(value) for value in args.ratios.split(","))
        if any(not 0 <= ratio <= 1 for ratio in ratios):
            parser.error("Ratios must be fractions in [0, 1]")
        for ratio in ratios:
            for repetition in (1, 2):
                name = f"repeat_{ratio}_{repetition}"
                if (WORK / "comparisons" / (name + ".json")).exists():
                    continue
                mutate(plan, round(plan["files_total"] * ratio), name)
                reset_cache(incremental / "_cache_v53", baseline_cache)
                if repetition == 1:
                    run(name + "_auto", incremental)
                    run(name + "_refresh", reference, mode="refresh")
                else:
                    run(name + "_refresh", reference, mode="refresh")
                    run(name + "_auto", incremental)
                compare(name, reference, incremental)
    elif args.phase == "audit":
        def fingerprint(entry):
            return entry["path"], hashlib.sha256((SOURCE / entry["path"]).read_bytes()).hexdigest()
        with ThreadPoolExecutor(max_workers=8) as pool:
            actual = list(pool.map(fingerprint, plan["order"]))
        expected = [tuple(entry) for entry in plan["source_fingerprints"]]
        inventory = {Path(file.relative_path).as_posix() for file in scan_repository(SOURCE, None).files}
        unchanged = actual == expected and inventory == {path for path, digest in expected}
        write_json(WORK / "SOURCE_AUDIT.json", {"official_source_unchanged": unchanged, "files_checked": len(actual),
                                               "scanned_inventory_unchanged": inventory == {path for path, digest in expected}})
        if not unchanged:
            raise RuntimeError("Official source differs from initial fingerprint")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "measure":
        from legacy_documenter.main import main as cli_main
        if "--allow-ai-interpretation" in sys.argv[3:]:
            raise SystemExit("Calibration never permits AI interpretation")
        telemetry_path = guarded(Path(sys.argv[2]))
        started = perf_counter()
        exit_code = cli_main(sys.argv[3:])
        write_json(telemetry_path, {"pipeline_seconds": round(perf_counter() - started, 3),
                                   **TIMINGS.snapshot(), "write_skip": LEDGER.snapshot()})
        raise SystemExit(exit_code)
    raise SystemExit(main())
