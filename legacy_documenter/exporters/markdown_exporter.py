from pathlib import Path
from collections import Counter

from legacy_documenter.cli.artifact_lifecycle import sync_generated_partition_directory
from legacy_documenter.exporters._documentation_partitioning import build_partition_filenames


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


def _group_dependencies_by_source(deps: list[dict]) -> dict[str, list[dict]]:
    """Groups `Project*`-typed dependency edges by `source` (the natural,
    already-present grouping key for PROJECT_DEPENDENCIES.md -- no new field
    is invented). Each group's edges are sorted deterministically
    (`target`, `dependency_type`) so the partitioned output never depends on
    `indexes["dependencies"]`'s own input order.
    """
    grouped: dict[str, list[dict]] = {}
    for dep in deps:
        grouped.setdefault(dep.get("source") or "unassigned", []).append(dep)
    for key, group_deps in grouped.items():
        grouped[key] = sorted(group_deps, key=lambda d: (d.get("target") or "", d.get("dependency_type") or ""))
    return grouped


class MarkdownExporter:
    """Provides the cohesive MarkdownExporter responsibility for this module."""
    def export(self, output_dir: str | Path, indexes: dict) -> None:
        """Performs export while preserving this module's deterministic contract."""
        doc_dir = Path(output_dir) / "documentation"
        doc_dir.mkdir(parents=True, exist_ok=True)
        self._write(doc_dir / "PROJECT_OVERVIEW.md", self.project_overview(indexes))
        self._write(doc_dir / "SOLUTION_STRUCTURE.md", self.solution_structure(indexes))
        # V4.3-R4 correction (see docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md
        # section 12): PROJECT_DEPENDENCIES.md becomes a navigation/index
        # document over partitioned detail, the same treatment V4.2-R8 gave
        # FUNCTIONAL_FLOWS.md/DATABASE_ACCESS.md/UNRESOLVED_FINDINGS.md and
        # V4.3-R4 gave WEB_ENTRY_POINTS.md -- `project_dependencies()` itself
        # (the flat renderer) is unchanged and still available.
        self._write(doc_dir / "PROJECT_DEPENDENCIES.md", self.project_dependencies_navigation(indexes))
        sync_generated_partition_directory(
            doc_dir / "project_dependencies", self.project_dependencies_partitions(indexes)
        )
        self._write(doc_dir / "WEBFORMS_MAP.md", self.webforms_map(indexes))
        self._write(doc_dir / "CONFIGURATION_SUMMARY.md", self.configuration_summary(indexes))
        self._write(doc_dir / "ANALYSIS_WARNINGS.md", self.analysis_warnings(indexes))

    def _write(self, path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")

    def project_overview(self, indexes: dict) -> str:
        """Renders PROJECT_OVERVIEW.md in Spanish (V4.3-R7 BLOQUEO 2: human-readable/
        product-facing documentation is Spanish by default). File-count keys come
        straight from `repository.stats` (a machine-derived dict) and are preserved
        verbatim, never translated.
        """
        repo = indexes["repository"]
        counts = repo.get("stats", {})
        # V4.2-R7.1 F-04: this human-facing document shows a safe display
        # label instead of the analyst's absolute local filesystem path (which
        # also reveals the local username). `index/repository.json`'s own
        # `root` field is an established machine contract and is left
        # untouched -- this correction is scoped to human-facing output only.
        label = _repository_display_label(repo.get("root"))
        lines = ["# Resumen del proyecto", "", f"Repositorio: `{label}`", "", "## Conteo de archivos"]
        lines += [f"- {key}: {value}" for key, value in counts.items()]
        return "\n".join(lines) + "\n"

    def solution_structure(self, indexes: dict) -> str:
        """Renders SOLUTION_STRUCTURE.md in Spanish (V4.3-R7 BLOQUEO 2). Solution/
        project names and paths are preserved verbatim.
        """
        lines = ["# Estructura de soluciones", ""]
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

    def project_dependencies_navigation(self, indexes: dict) -> str:
        """Renders the PROJECT_DEPENDENCIES.md navigation/summary document (V4.3-R4
        correction): the same edge count `project_dependencies()` implies, plus a
        link per source-project group into `project_dependencies/<safe-name>.md`
        instead of the full `source -> target` listing. Reopened for partitioning
        by the same empirical scale evidence already cited for the other
        partitioned documents (V4.2-R7: ~9,424 lines / 978KB at real-repository
        scale).

        V4.3-R4 correction (human-documentation-in-Spanish-by-default gate):
        rendered in Spanish, like every other R4-authored human-facing document.
        This does not extend to `project_dependencies()` (the pre-existing flat
        renderer, unchanged, still English). Project names, `ProjectReference`/
        other `dependency_type` values and paths are never translated -- only
        the surrounding prose/headers are.
        """
        deps = [d for d in indexes["dependencies"] if d["dependency_type"].startswith("Project")]
        lines = ["# Dependencias de proyectos", ""]
        if not deps:
            lines.append("No se descubrieron dependencias de proyectos.")
            lines.append("")
            return "\n".join(lines) + "\n"

        groups = _group_dependencies_by_source(deps)
        filenames = build_partition_filenames(sorted(groups))
        lines.append(f"{len(deps)} arista(s) de dependencia de proyecto en {len(groups)} proyecto(s) origen.")
        lines.append("")
        lines.append(
            "El detalle completo (cada arista de dependencia `origen -> destino`) está particionado "
            "por proyecto origen abajo, nunca repetido aquí."
        )
        lines.append("")
        lines.append("| Proyecto origen | Dependencias | Detalle |")
        lines.append("|---|---|---|")
        for key in sorted(groups):
            filename = filenames[key]
            link = f"project_dependencies/{filename}"
            lines.append(f"| `{key}` | {len(groups[key])} | [{filename}]({link}) |")
        lines.append("")
        return "\n".join(lines) + "\n"

    def project_dependencies_partitions(self, indexes: dict) -> dict[str, str]:
        """Renders one `project_dependencies/<safe-name>.md` document per source
        project. Every `Project*`-typed dependency edge `project_dependencies()`
        would render appears in exactly one partition -- never duplicated or
        dropped -- ordered deterministically regardless of input order.

        V4.3-R4 correction: rendered in Spanish (see `project_dependencies_navigation`
        docstring). Project names/`dependency_type` values are preserved verbatim.
        """
        deps = [d for d in indexes["dependencies"] if d["dependency_type"].startswith("Project")]
        if not deps:
            return {}
        groups = _group_dependencies_by_source(deps)
        filenames = build_partition_filenames(sorted(groups))

        result: dict[str, str] = {}
        for key, group_deps in groups.items():
            lines = [f"# Dependencias de proyectos — {key}", ""]
            for dep in group_deps:
                lines.append(f"- `{dep['source']}` -> `{dep['target']}` ({dep['dependency_type']})")
            lines.append("")
            result[filenames[key]] = "\n".join(lines) + "\n"
        return result

    def webforms_map(self, indexes: dict) -> str:
        """Renders WEBFORMS_MAP.md in Spanish (V4.3-R7 BLOQUEO 2). Field names
        (`codebehind`/`codefile`/`inherits`/`master_page`/`register`) and every
        attribute value are JSON/source-derived identifiers and are preserved
        verbatim -- only the document title is translated. Evaluated for
        partitioning at V4.3-R4 and deliberately left flat (small at real-repository
        scale; see docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md section 12).
        """
        lines = ["# Mapa de WebForms", ""]
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
        """Renders CONFIGURATION_SUMMARY.md in Spanish (V4.3-R7 BLOQUEO 2). Field
        names (`appSettings`/`connectionStrings`/`assemblies`) are JSON contract
        keys and are preserved verbatim -- never secret values, counts only.
        """
        lines = ["# Resumen de configuración", ""]
        for config in indexes["configuration"]:
            lines.append(f"## {config['path']}")
            lines.append(f"- appSettings: {len(config.get('appSettings', []))}")
            lines.append(f"- connectionStrings: {len(config.get('connectionStrings', []))}")
            lines.append(f"- assemblies: {len(config.get('assemblies', []))}")
        return "\n".join(lines) + "\n"

    def analysis_warnings(self, indexes: dict) -> str:
        """Renders ANALYSIS_WARNINGS.md in Spanish (V4.3-R7 BLOQUEO 2). Extractor
        names come straight from `errors[].extractor` and are preserved verbatim.
        """
        errors = indexes.get("errors", [])
        by_extractor = Counter(error.get("extractor", "unknown") for error in errors)
        lines = ["# Advertencias de análisis", "", f"Errores capturados: {len(errors)}"]
        lines += [f"- {name}: {count}" for name, count in by_extractor.items()]
        return "\n".join(lines) + "\n"
