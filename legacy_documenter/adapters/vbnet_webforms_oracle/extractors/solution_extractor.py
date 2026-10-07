import re
from pathlib import Path


PROJECT_RE = re.compile(
    r'Project\("\{(?P<type_guid>[^}]+)\}"\)\s*=\s*"(?P<name>[^"]+)",\s*"(?P<path>[^"]+)",\s*"\{(?P<guid>[^}]+)\}"',
    re.IGNORECASE,
)


class SolutionExtractor:
    """Provides the cohesive SolutionExtractor responsibility for this module."""
    def extract(self, path: str | Path, root: str | Path | None = None) -> dict:
        """Performs extract while preserving this module's deterministic contract."""
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8", errors="replace")
        projects = [match.groupdict() for match in PROJECT_RE.finditer(text)]
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        return {"name": file_path.stem, "path": rel, "projects": projects}
