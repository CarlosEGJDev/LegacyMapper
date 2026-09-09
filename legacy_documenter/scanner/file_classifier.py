from collections import Counter
from pathlib import Path


class FileClassifier:
    def classify(self, path: Path) -> str:
        name = path.name.lower()
        suffix = path.suffix.lower()
        if suffix == ".sln":
            return "solution"
        if suffix == ".vbproj":
            return "vb_project"
        if suffix == ".vb":
            return "vb_source"
        if suffix == ".aspx":
            return "aspx"
        if suffix == ".ascx":
            return "ascx"
        if suffix == ".master":
            return "master"
        if name == "web.config":
            return "web_config"
        if name == "app.config":
            return "app_config"
        if suffix == ".js":
            return "javascript"
        if suffix == ".css":
            return "css"
        if suffix in {".html", ".htm"}:
            return "html"
        if suffix == ".xml":
            return "xml"
        if suffix in {".resx", ".resources"}:
            return "resource"
        if suffix in {".dll", ".exe"}:
            return "assembly"
        return "other"

    def stats(self, files: list[dict]) -> dict:
        counts = Counter(item["file_type"] for item in files)
        result = {"total_files": len(files)}
        result.update(dict(sorted(counts.items())))
        return result
