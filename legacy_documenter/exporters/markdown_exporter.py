from pathlib import Path
from collections import Counter


class MarkdownExporter:
    """Provides the cohesive MarkdownExporter responsibility for this module."""
    def export(self, output_dir: str | Path, indexes: dict) -> None:
        """Performs export while preserving this module's deterministic contract."""
        doc_dir = Path(output_dir) / "documentation"
        doc_dir.mkdir(parents=True, exist_ok=True)
        self._write(doc_dir / "PROJECT_OVERVIEW.md", self.project_overview(indexes))
        self._write(doc_dir / "SOLUTION_STRUCTURE.md", self.solution_structure(indexes))
        self._write(doc_dir / "PROJECT_DEPENDENCIES.md", self.project_dependencies(indexes))
        self._write(doc_dir / "WEBFORMS_MAP.md", self.webforms_map(indexes))
        self._write(doc_dir / "CONFIGURATION_SUMMARY.md", self.configuration_summary(indexes))
        self._write(doc_dir / "ANALYSIS_WARNINGS.md", self.analysis_warnings(indexes))

    def _write(self, path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")

    def project_overview(self, indexes: dict) -> str:
        """Performs project overview while preserving this module's deterministic contract."""
        repo = indexes["repository"]
        counts = repo.get("stats", {})
        lines = ["# Project Overview", "", f"Root: `{repo.get('root')}`", "", "## File Counts"]
        lines += [f"- {key}: {value}" for key, value in counts.items()]
        return "\n".join(lines) + "\n"

    def solution_structure(self, indexes: dict) -> str:
        """Performs solution structure while preserving this module's deterministic contract."""
        lines = ["# Solution Structure", ""]
        for solution in indexes["solutions"]:
            lines.append(f"## {solution['name']}")
            for project in solution.get("projects", []):
                lines.append(f"- {project['name']}: `{project['path']}`")
        return "\n".join(lines) + "\n"

    def project_dependencies(self, indexes: dict) -> str:
        """Performs project dependencies while preserving this module's deterministic contract."""
        lines = ["# Project Dependencies", ""]
        for dep in indexes["dependencies"]:
            if dep["dependency_type"].startswith("Project"):
                lines.append(f"- `{dep['source']}` -> `{dep['target']}` ({dep['dependency_type']})")
        return "\n".join(lines) + "\n"

    def webforms_map(self, indexes: dict) -> str:
        """Performs webforms map while preserving this module's deterministic contract."""
        lines = ["# WebForms Map", ""]
        for form in indexes["webforms"]:
            lines.append(f"## {form['path']}")
            for key in ["codebehind", "codefile", "inherits", "master_page"]:
                if form.get(key):
                    lines.append(f"- {key}: `{form[key]}`")
            for reg in form.get("registers", []):
                lines.append(f"- register: `{reg}`")
        return "\n".join(lines) + "\n"

    def configuration_summary(self, indexes: dict) -> str:
        """Performs configuration summary while preserving this module's deterministic contract."""
        lines = ["# Configuration Summary", ""]
        for config in indexes["configuration"]:
            lines.append(f"## {config['path']}")
            lines.append(f"- appSettings: {len(config.get('appSettings', []))}")
            lines.append(f"- connectionStrings: {len(config.get('connectionStrings', []))}")
            lines.append(f"- assemblies: {len(config.get('assemblies', []))}")
        return "\n".join(lines) + "\n"

    def analysis_warnings(self, indexes: dict) -> str:
        """Performs analysis warnings while preserving this module's deterministic contract."""
        errors = indexes.get("errors", [])
        by_extractor = Counter(error.get("extractor", "unknown") for error in errors)
        lines = ["# Analysis Warnings", "", f"Errors captured: {len(errors)}"]
        lines += [f"- {name}: {count}" for name, count in by_extractor.items()]
        return "\n".join(lines) + "\n"
