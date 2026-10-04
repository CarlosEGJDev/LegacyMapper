"""Run-scoped, in-memory stage timings and small extras for the run metrics (V5.3-R2.7).

Observability only: nothing here is read by the pipeline to decide anything, and nothing is persisted by this
module (`cache.run_metrics` serializes a snapshot into `RUN_METRICS.json`). Like the write-skip ledger it is one
process-wide object reset at the start of each `full` run (the pipeline is single-threaded per process).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StageTimings:
    """Seconds per stage name (accumulated if a stage is timed more than once) plus free-form counters."""

    seconds: dict[str, float] = field(default_factory=dict)
    extras: dict[str, dict] = field(default_factory=dict)

    def add(self, name: str, seconds: float) -> None:
        """Adds `seconds` to the stage `name`."""
        self.seconds[name] = self.seconds.get(name, 0.0) + seconds

    def reset(self) -> None:
        """Forgets everything recorded so far."""
        self.seconds.clear()
        self.extras.clear()

    def snapshot(self) -> dict:
        """`{"stage_seconds": {...}, "extras": {...}}`, stages sorted by name, seconds rounded."""
        return {
            "stage_seconds": {name: round(self.seconds[name], 3) for name in sorted(self.seconds)},
            "extras": {name: dict(self.extras[name]) for name in sorted(self.extras)},
        }


TIMINGS = StageTimings()
