"""V5.2 orchestration: Evidence -> Audience Transformation -> Profile -> Template -> Markdown.

Writes only under `<output>/documentation_v52/`. The legacy `documentation/`
tree is never read or written here (D-52-05).
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.utils.atomic_write import _replace_with_retry

from .categories import InterpretedSection
from .config import ConfigError, ConfigRegistry
from .renderer import MarkdownRenderer, PartitionPolicy
from .structure import Bullets, Heading, Link, Note, Paragraph, StructuredDocument, Text
from .template import TemplateEngine
from .transform import AudienceTransformer

OUTPUT_DIRNAME = "documentation_v52"
MANIFEST_FILENAME = "MANIFEST.json"
DEFAULT_PROFILES = ("general_overview", "developer_technical")
EVIDENCE_PARTITIONS = (
    "repository", "solutions", "projects", "entry_points", "functional_flows", "flow_unresolved", "data_access",
    "stored_procedures", "sql_operations", "dependencies", "configuration", "flow_summary", "webforms", "symbols",
    # V5.2 R3.4: raw per-file call records (`{file, calls:[...]}`), the same
    # shape `evidence.builder._build_call_identities` reads -- needed for
    # Method -> call traceability (section 3/4 relation A).
    "calls",
)
# Class-like Symbol kinds vs. WebForm/UserControl/MasterPage kinds, mirroring
# `legacy_documenter.evidence.builder._build_components`'s own fusion (V5.2 R3.3:
# `symbols`/`webform_components` feed Project -> Component/Archivo navigation).
_SYMBOL_KINDS = {"class", "interface", "module", "structure", "enum"}
_WEBFORM_KINDS = {"aspx", "ascx", "master"}


@dataclass
class DocumentationV52Result:
    output_dir: Path
    files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    profiles: dict = field(default_factory=dict)  # profile id -> {"files": n, "parts": n, "bytes": n, "max_file_bytes": n}


def source_from_indexes(indexes: dict, external_dependencies: list | None = None) -> dict:
    """Evidence source from the run's own in-memory `indexes` (same content
    `evidence/` persists as passthrough partitions) plus Evidence Core
    `external_dependencies` when available."""
    source = {name: indexes.get(name, [] if name not in ("repository", "flow_summary") else {}) for name in EVIDENCE_PARTITIONS}
    source["external_dependencies"] = external_dependencies or []
    # V5.2 R3.3: real WebForm/UserControl/MasterPage records (path, kind,
    # codebehind...) for Project -> Component/Archivo navigation; distinct from
    # `webforms` above, which only ever fed a count.
    source["webform_components"] = indexes.get("webforms", [])
    return source


def _unwrap(records: list) -> list:
    """Evidence entities keep the adapter's original record under `extensions[<adapter id>]`."""
    out = []
    for record in records:
        adapter = (record.get("adapter") or {}).get("id")
        extension = (record.get("extensions") or {}).get(adapter)
        out.append(extension if isinstance(extension, dict) and extension else record)
    return out


def source_from_evidence_dir(evidence_dir: str | Path) -> dict:
    """Evidence source read back from a persisted `<output>/evidence/` directory."""
    base = Path(evidence_dir)

    def load(name: str, default: object) -> object:
        file = base / f"{name}.json"
        return json.loads(file.read_text(encoding="utf-8")) if file.is_file() else default

    passthrough = ("entry_points", "functional_flows", "flow_unresolved", "data_access", "dependencies",
                   "configuration", "flow_summary", "calls")
    source: dict = {name: load(name, {} if name == "flow_summary" else []) for name in passthrough}
    source["solutions"] = _unwrap(load("solutions", []))
    source["projects"] = _unwrap(load("projects", []))
    objects = load("data_objects", [])
    source["stored_procedures"] = _unwrap([o for o in objects if o.get("object_kind") == "stored_procedure"])
    source["sql_operations"] = _unwrap([o for o in objects if o.get("object_kind") == "sql"])
    source["webforms"] = [c for c in load("components", []) if c.get("component_kind") in ("aspx", "ascx", "master")]
    scan = load("scan_summary", {})
    source["repository"] = {"root": scan.get("root", ""), "stats": scan.get("by_type", {})}
    source["external_dependencies"] = load("external_dependencies", [])
    # V5.2 R3.3: unwrap `evidence/components.json` back to the adapter's own
    # Symbol/WebForm shape (real `file`/`path`, `members`, `codebehind`...),
    # split the same way `_build_components` fused them.
    components_raw = _unwrap(load("components", []))
    source["symbols"] = [c for c in components_raw if c.get("kind") in _SYMBOL_KINDS]
    source["webform_components"] = [c for c in components_raw if c.get("kind") in _WEBFORM_KINDS]
    return source


def load_interpreted_sections(path: str | Path) -> dict[str, InterpretedSection]:
    """Optional INTERPRETED extension point (D-52-02): a JSON list of
    `{target, content, origin, created_at[, language]}`. Never required."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_interpreted_sections(data)


def parse_interpreted_sections(items: list[dict]) -> dict[str, InterpretedSection]:
    sections: dict[str, InterpretedSection] = {}
    for index, item in enumerate(items or []):
        for key in ("target", "content", "origin", "created_at"):
            if not str(item.get(key, "")).strip():
                raise ConfigError(f"interpretación #{index + 1}: falta el campo '{key}' (el origen es obligatorio)")
        sections[item["target"]] = InterpretedSection(
            target=item["target"], content=item["content"], origin=item["origin"],
            created_at=item["created_at"], language=item.get("language"),
        )
    return sections


def generate_documentation_v52(
    source: dict,
    output_dir: str | Path,
    *,
    profiles: tuple[str, ...] = DEFAULT_PROFILES,
    custom_dir: str | Path | None = None,
    strict_templates: bool = False,
    interpreted: dict[str, InterpretedSection] | None = None,
    partition_override: PartitionPolicy | None = None,
) -> DocumentationV52Result:
    """Generates `<output_dir>/documentation_v52/`.

    Custom templates/profiles/noise/catalogs come from `custom_dir` (layout:
    `templates/`, `profiles/`, `noise/`, `i18n/`, one JSON per id). An invalid
    custom item yields a visible warning and falls back to the default; with
    `strict_templates=True` it raises `ConfigError` instead.
    """
    registry = ConfigRegistry(custom_dir, strict=strict_templates)
    root = Path(output_dir) / OUTPUT_DIRNAME
    result = DocumentationV52Result(output_dir=root)
    all_files: dict[str, str] = {}
    models_cache: dict = {}
    first_catalog = None

    for profile_id in profiles:
        profile = registry.profile(profile_id)
        catalog = registry.catalog(profile.language)
        first_catalog = first_catalog or catalog
        policy = registry.noise_policy(profile.noise_policy)
        cache_key = (policy.id, catalog.text("unassigned_module"), catalog.text("origin_unknown"), catalog.text("file_ownership_shared"))
        model = models_cache.get(cache_key)
        if model is None:
            model = AudienceTransformer(
                policy, catalog.text("unassigned_module"), catalog.text("origin_unknown"), catalog.text("file_ownership_shared"),
            ).transform(source)
            models_cache[cache_key] = model
        model.interpreted = dict(interpreted or {})
        templates = {tid: registry.template(tid, profile, catalog) for tid in profile.templates}
        documents = TemplateEngine(model, profile, policy, catalog, templates).build()
        labels = {key: catalog.raw(key) for key in (
            "nav.index", "nav.previous", "nav.next", "nav.part", "nav.rows", "nav.parts_list", "nav.oversize_warning")}
        renderer = MarkdownRenderer(
            partition_override or PartitionPolicy(profile.max_items_per_part, profile.max_bytes_per_part), labels)
        rendered = renderer.render(documents)
        sizes = []
        for path, content in rendered.files.items():
            all_files[f"{profile.output_dir}/{path}"] = content
            sizes.append(len(content.encode("utf-8")))
        result.warnings.extend(f"[{profile.id}] {w}" for w in rendered.warnings)
        result.profiles[profile.id] = {
            "files": len(rendered.files), "parts": rendered.parts, "bytes": sum(sizes), "max_file_bytes": max(sizes, default=0),
            "output_dir": profile.output_dir, "language": profile.language, "source": profile.source,
            "max_items_per_part": profile.max_items_per_part, "max_bytes_per_part": profile.max_bytes_per_part,
        }
        for code in model.gaps:
            text = catalog.text(code)
            if text not in result.gaps:
                result.gaps.append(text)
        result.warnings.extend(f"[{profile.id}] clave de idioma sin traducción: {key}" for key in sorted(catalog.missing))

    result.warnings = registry.warnings + result.warnings
    readme = _root_readme(first_catalog, profiles, registry, result)
    all_files["README.md"] = readme
    _write_tree(root, all_files, result)
    return result


def _root_readme(catalog, profiles, registry, result: DocumentationV52Result) -> str:
    from .renderer import MarkdownRenderer, PartitionPolicy  # local: keep module import graph flat

    doc = StructuredDocument("README.md", Text.of(catalog.raw("readme.title")))
    doc.blocks.append(Paragraph(Text.of(catalog.raw("readme.intro"))))
    for profile_id in profiles:
        info = result.profiles[profile_id]
        key = "readme.general" if profile_id == "general_overview" else "readme.developer"
        label = catalog.raw(key) if catalog.has(key) else profile_id
        doc.blocks.append(Link(Text.of(label), f"{info['output_dir']}/README.md"))
    if result.warnings:
        doc.blocks.append(Heading(2, Text.of(catalog.raw("readme.warnings"))))
        doc.blocks.append(Bullets([Text.of("{w}", {"w": w}) for w in result.warnings[:50]]))
    if result.gaps:
        doc.blocks.append(Heading(2, Text.of(catalog.raw("readme.gaps"))))
        doc.blocks.append(Bullets([Text.of("{g}", {"g": g}) for g in result.gaps]))
    renderer = MarkdownRenderer(PartitionPolicy(10**9, 10**9), {})
    return renderer.render([doc]).files["README.md"]


def _atomic_write(path: Path, text: str) -> None:
    """Crash-safe write of exact UTF-8 bytes with LF newlines on every platform
    (the manifest hashes these bytes; `atomic_write_text` would translate `\n` on Windows)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _write_tree(root: Path, files: dict[str, str], result: DocumentationV52Result) -> None:
    """Writes files deterministically and removes stale LegacyMapper-owned `.md`
    files (and the manifest) a previous run left under this tree."""
    lowered: dict[str, str] = {}
    for relative in files:
        clash = lowered.setdefault(relative.lower(), relative)
        if clash != relative:
            raise ValueError(f"nombres de archivo que solo difieren en mayúsculas/minúsculas: {clash!r} y {relative!r}")
    root.mkdir(parents=True, exist_ok=True)
    wanted = set(files)
    for existing in sorted(root.rglob("*.md")):
        if existing.relative_to(root).as_posix() not in wanted:
            existing.unlink()
    manifest_files = []
    for relative in sorted(files):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = files[relative]
        _atomic_write(target, data)
        raw = data.encode("utf-8")
        manifest_files.append({"path": relative, "size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    result.files = [entry["path"] for entry in manifest_files]
    manifest = {
        "schema_version": "1.0",
        "contract": "LegacyMapperDocumentationV52",
        "profiles": result.profiles,
        "file_count": len(manifest_files),
        "total_bytes": sum(e["size_bytes"] for e in manifest_files),
        "warnings": result.warnings,
        "gaps": result.gaps,
        "files": manifest_files,
    }
    _atomic_write(root / MANIFEST_FILENAME, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    for directory in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
