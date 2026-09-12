from pathlib import Path

from legacy_documenter.config import DEFAULT_EXCLUDES, VTI_PREFIX
from legacy_documenter.models import SourceFile
from legacy_documenter.scanner.file_classifier import FileClassifier


class RepositoryScanner:
    """Provides the cohesive RepositoryScanner responsibility for this module."""
    def __init__(self, excludes: list[str] | None = None):
        self.excludes = set(DEFAULT_EXCLUDES)
        if excludes:
            self.excludes.update(excludes)
        self.classifier = FileClassifier()
        self.ignored: list[str] = []

    def scan(self, root: str | Path) -> list[SourceFile]:
        """Performs scan while preserving this module's deterministic contract."""
        root_path = Path(root).resolve()
        files: list[SourceFile] = []
        for path in root_path.rglob("*"):
            if self._is_excluded(path, root_path):
                if path.is_dir():
                    self.ignored.append(str(path.relative_to(root_path)))
                continue
            if not path.is_file():
                continue
            rel = path.relative_to(root_path)
            files.append(
                SourceFile(
                    relative_path=str(rel),
                    extension=path.suffix.lower(),
                    size=path.stat().st_size,
                    folder=str(rel.parent) if str(rel.parent) != "." else "",
                    name=path.name,
                    file_type=self.classifier.classify(path),
                )
            )
        return files

    def _is_excluded(self, path: Path, root: Path) -> bool:
        try:
            parts = path.relative_to(root).parts
        except ValueError:
            return True
        return any(part in self.excludes or part.lower().startswith(VTI_PREFIX) for part in parts)
