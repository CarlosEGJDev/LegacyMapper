import json
from pathlib import Path

from legacy_documenter.utils import sanitize_data


class JSONExporter:
    """Provides the cohesive JSONExporter responsibility for this module."""
    def export(self, output_dir: str | Path, indexes: dict) -> None:
        """Performs export while preserving this module's deterministic contract."""
        index_dir = Path(output_dir) / "index"
        index_dir.mkdir(parents=True, exist_ok=True)
        for name, data in indexes.items():
            (index_dir / f"{name}.json").write_text(
                json.dumps(sanitize_data(data), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
