"""LegacyMapper-owned output-artifact lifecycle: rerun/recovery safety (V4.2-R6).

Owns exactly one responsibility: preventing a stale artifact from an
earlier `full` run into the same `--output` directory from ever appearing
to belong to the *current* run (V4.2-R6 sections 4/5). This is narrowly
scoped to the one artifact pair R6's characterization found genuinely at
risk -- the AI proposal files -- not a general cleanup framework:

- `index/`, `documentation/`, `context/`, `ai_context/` are unconditionally
  overwritten in full by the deterministic stage that owns them every time
  that stage runs, so they can only go stale when their owning stage does
  not run this time (an upstream failure) -- a case `run_summary_presenter`
  already reports correctly by deriving `output_locations` from which
  stages actually succeeded *this* run, never from filesystem existence
  (see V4.2-R6 section 6). No physical cleanup is needed there.
- `proposals/` is different: it is written only when `--allow-ai-
  interpretation` is passed AND AI interpretation returns a result, so an
  earlier run's proposal files can easily survive, unchanged, into a later
  run that never touches that code path at all -- and unlike the other
  directories, a stale `AI_PROPOSALS_PENDING_REVIEW.md` invites a human to
  act on it. `output_locations`-based reporting alone (as above) already
  keeps LegacyMapper's own generated summaries from referencing it, but the
  file would still physically sit there looking untouched, so this module
  also removes it.
"""
from __future__ import annotations

from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

# The exact, fixed set of filenames `full_pipeline._write_proposal_output`
# ever writes under `proposals/` -- never anything else. Keeping this list
# next to the reset function (rather than re-deriving it from source) keeps
# both explicit about the same narrow ownership contract.
KNOWN_PROPOSAL_FILENAMES: tuple[str, ...] = ("AI_PROPOSALS.json", "AI_PROPOSALS_PENDING_REVIEW.md")


def reset_stale_proposal_artifacts(output: Path) -> None:
    """Removes only LegacyMapper's own proposal files from `output/proposals/`, if present.

    Called unconditionally at the start of every `full` run (V4.2-R6
    section 5), before any stage runs, so `proposals/` can never end a run
    containing content from a *different* run: either this run's own AI
    stage rewrites it fresh later, or it stays absent for the rest of the
    run. Never touches any file whose name is not in
    `KNOWN_PROPOSAL_FILENAMES`, and removes the directory itself only once
    it is empty -- an unrelated file a user placed under `proposals/` is
    always preserved (V4.2-R6 section 16), and nothing outside `output` is
    ever touched (source immutability is unaffected by this function).
    """
    proposals_dir = Path(output) / "proposals"
    if not proposals_dir.is_dir():
        return
    for name in KNOWN_PROPOSAL_FILENAMES:
        candidate = proposals_dir / name
        if candidate.is_file():
            candidate.unlink()
    try:
        proposals_dir.rmdir()
    except OSError:
        pass  # not empty -- an unrelated file is present; leave it and the directory alone


def sync_generated_partition_directory(directory: Path, partitions: dict[str, str]) -> None:
    """Writes this run's partitioned-documentation files into `directory`,
    removing only stale LegacyMapper-owned `.md` files a previous run left
    behind (V4.2-R8 section 11).

    `documentation/functional_flows/`, `documentation/database_access/`, and
    `documentation/unresolved_findings/` hold only generated `.md` partition
    files whose exact filename set is data-derived and can shrink or change
    between two runs into the same `--output` directory (e.g. a project is
    removed, or the number of unresolved-finding categories changes) --
    unlike the fixed top-level `documentation/*.md` filenames, a stale
    partition file is not simply overwritten by name and must be actively
    removed so it cannot survive looking like current-run evidence.

    Only files with the `.md` extension are ever considered stale and
    removed; any other file (e.g. a note a person placed in this directory)
    is preserved unconditionally, exactly as `reset_stale_proposal_artifacts`
    preserves anything outside its own known-owned filename set -- this
    function generalizes that same rule to a known-owned *extension* because
    partition filenames are themselves deterministic and data-derived rather
    than a fixed literal list. The directory itself is created only when
    there is at least one partition to write, and removed again once empty
    (never when a non-`.md` file remains).
    """
    directory = Path(directory)
    if partitions:
        directory.mkdir(parents=True, exist_ok=True)
    if directory.is_dir():
        for existing in directory.glob("*.md"):
            if existing.name not in partitions:
                existing.unlink()
    for name, content in partitions.items():
        (directory / name).write_text(content, encoding="utf-8")
    if directory.is_dir() and not partitions:
        try:
            directory.rmdir()
        except OSError:
            pass  # not empty -- an unrelated file is present; leave it and the directory alone


def sync_generated_json_partition_directory(directory: Path, partitions: dict[str, str]) -> None:
    """Same stale-file safety as `sync_generated_partition_directory`, for JSON
    partitions written atomically (V4.3-R6).

    `consumer_projection/parts/` holds only generated `.json` partition files
    whose exact filename set is data-derived (`len(flow_ids) / partition_size`
    partitions) and shrinks or grows between two runs into the same
    `--output` directory exactly like `documentation/<doc>/` already does for
    Markdown partitions -- a rerun with fewer flows must not leave a stale
    `part-000009.json` looking like current-run evidence. This sibling
    function exists, rather than generalizing `sync_generated_partition_directory`
    itself, because these partitions are LegacyMapper's own authoritative
    machine artifacts (like `RUN_SUMMARY.json`/`index/*.json`, V4.2-R6) and so
    are written with `atomic_write_text` rather than a plain `write_text` --
    changing the existing function's write primitive would also change
    behavior for its unrelated, pre-existing Markdown callers.

    Only files with the `.json` extension are ever considered stale and
    removed; any other file is preserved unconditionally. The directory
    itself is created only when there is at least one partition to write, and
    removed again once empty (never when a non-`.json` file remains).
    """
    directory = Path(directory)
    if partitions:
        directory.mkdir(parents=True, exist_ok=True)
    if directory.is_dir():
        for existing in directory.glob("*.json"):
            if existing.name not in partitions:
                existing.unlink()
    for name, content in partitions.items():
        atomic_write_text(directory / name, content)
    if directory.is_dir() and not partitions:
        try:
            directory.rmdir()
        except OSError:
            pass  # not empty -- an unrelated file is present; leave it and the directory alone
