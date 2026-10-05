"""Run-wide write policy shared by every output writer (V5.3-R2.8).

`--cache-mode off` means "the V5.2 path": every output is rewritten, nothing is compared to what is on disk. Both
write-skip implementations (`write_if_changed` and `documentation_v52.writer`) read this one switch, so neither
depends on the other. The pipeline sets it at the start of each run; the default is write-skip enabled.
"""
from __future__ import annotations


class WritePolicy:
    """Process-wide, single-run switch (the pipeline runs one job per process)."""

    skip_identical: bool = True

    def reset(self) -> None:
        """Back to the default (skip identical writes)."""
        self.skip_identical = True


POLICY = WritePolicy()
