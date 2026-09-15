import json
from pathlib import Path

from legacy_documenter.utils import sanitize_data
from legacy_documenter.utils.atomic_write import atomic_write_text


class JSONExporter:
    """Provides the cohesive JSONExporter responsibility for this module."""
    def export(self, output_dir: str | Path, indexes: dict) -> None:
        """Performs export while preserving this module's deterministic contract.

        Writes atomically (V4.2-R6 section 7): `index/*.json` is a core
        machine-readable artifact, so a process interrupted mid-write must
        never leave a truncated/corrupted file in its place.
        """
        index_dir = Path(output_dir) / "index"
        for name, data in indexes.items():
            atomic_write_text(
                index_dir / f"{name}.json",
                json.dumps(sanitize_data(data), indent=2, ensure_ascii=False),
            )
