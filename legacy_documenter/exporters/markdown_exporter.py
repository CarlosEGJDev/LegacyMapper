from pathlib import Path
from collections import Counter


def _repository_display_label(root: object) -> str:
    """Derives a safe, human-facing repository label from an absolute root path.

    Shows only the trailing folder name (e.g. `operacional`), never the full
    absolute path -- which on Windows also embeds the analyst's local
    username (`C:\\Users\\<username>\\...`). Used for human-facing documentation
    only; `index/repository.json`'s own `root` field keeps the full path
    unchanged as an established machine contract (V4.2-R7.1 F-04).
    """
    text = "" if root is None else str(root)
    name = Path(text).name if text else ""
    return name or "(repository root)"


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
        # V4.2-R7.1 F-04: this human-facing document shows a safe display
        # label instead of the analyst's absolute local filesystem path (which
        # also reveals the local username). `index/repository.json`'s own
        # `root` field is an established machine contract and is left
        # untouched -- this correction is scoped to human-facing output only.
        label = _repository_display_label(repo.get("root"))
        lines = ["# Project Overview", "", f"Repository: `{label}`", "", "## File Counts"]
        lines += [f"- {key}: {value}" for key, value in counts.items()]
        return "\n".join(lines) + "\n"

    def solution_structure(self, indexes: dict) -> str:
        """Performs solution structure while preserving this module's deterministic contract."""
        lines = ["# Solution Structure", ""]
        for solution in indexes["solutions"]:
            # V4.2-R7.1 F-02: always show the solution's own repository-relative
            # path alongside its name -- duplicate-named solutions (e.g. a live
            # copy and a `Backup/` copy) are then distinguishable by path even
            # though their bare names collide. Solution identity itself is
            # unchanged; this only affects the rendered header text.
            path = solution.get("path")
            header = f"{solution['name']} (`{path}`)" if path else solution["name"]
            lines.append(f"## {header}")
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
                # V4.2-R7.1 F-03: render only the register directive's own
                # source-derived attributes (e.g. TagPrefix/Namespace/Assembly),
                # sorted for determinism -- `_normalized` is WebFormsExtractor's
                # internal lowercase-keyed lookup copy of the same attributes
                # and is never a source-derived field in its own right, so it
                # is excluded here rather than rendered as raw Python dict repr.
                fields = {key: value for key, value in reg.items() if key != "_normalized"}
                if not fields:
                    continue
                lines.append("- register:")
                for key in sorted(fields):
                    lines.append(f"  - {key}: `{fields[key]}`")
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
