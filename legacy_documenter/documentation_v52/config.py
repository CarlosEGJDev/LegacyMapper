"""Declarative configuration loading + validation: profiles, noise policies,
language catalogs and templates (R1 sections 6, 8, 10, 14).

Everything here is data (JSON) resolved with the precedence
`custom directory (if it provides the id) -> packaged default`.
A custom item that fails validation raises `ConfigError` with a readable
message; the caller (`engine`) decides between warning+fallback (default) and
failure (strict mode) -- errors are never swallowed here.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .categories import CATEGORIES, INTERNAL_ONLY
from .noise import VISIBILITIES, NoisePolicy, NoisePolicyError

DEFAULTS_DIR = Path(__file__).resolve().parent / "defaults"
CONTRACT_VERSION = "1"

# Fields a template may reference, per slot. Internal ids are not here on purpose:
# a template can only ever see human-facing values (INTERNAL_ONLY by construction).
SYSTEM_SLOT_FIELDS = {
    "modules_top": {"name", "solutions", "screens", "flows", "incoming_flows", "data_ops", "slug"},
    "modules_all": {"name", "solutions", "screens", "flows", "incoming_flows", "real_flows", "data_ops", "unresolved_total", "slug"},
    "solutions_top": {"name", "path", "projects"},
    "solutions_all": {"name", "path", "projects", "slug"},
    "internal_libraries": {"name", "projects_using", "class"},
    "unclassified_libraries": {"name", "projects_using", "class"},
    "platform_libraries": {"name", "projects_using", "class"},
    "data_providers": {"name", "count"},
    "data_packages": {"package", "objects"},
    "configs": {"path", "marker"},
}
MODULE_SLOT_FIELDS = {
    "entry_points": {"webform", "events", "real_flows"},
    "entry_point_events": {"webform", "event", "handler", "kind"},
    "flows": {"state", "webform", "event", "handler", "terminal"},
    "incoming_summary": {"origin", "webform", "flows"},
    "incoming_flows": {"origin", "webform", "event", "handler", "state"},
    "data_targets": {"target", "kind", "count", "confidence", "origin"},
    "indirect_targets": {"target", "kind", "flows"},
    "data_operations": {"where", "kind", "target", "confidence", "origin"},
    "unresolved": {"target", "count", "category"},
    "project_refs_out": {"name", "path"},
    "project_refs_in": {"name", "path"},
    "libraries": {"name", "path", "class"},
    "files": {"name", "path", "kind", "component_count", "slug"},
    "solution_links": {"name", "path", "slug"},
}
SOLUTION_SLOT_FIELDS = {
    "projects": {"name", "path", "slug"},
}
FILE_SLOT_FIELDS = {
    "components": {"name", "kind", "member_count", "slug"},
}
COMPONENT_SLOT_FIELDS = {
    "methods": {"name", "kind", "accessibility", "shared", "slug"},
    "ambiguous_methods": {"name", "overload_count"},
}
METHOD_SLOT_FIELDS = {
    "calls_out_resolved": {"target", "confidence", "origin"},
    "calls_out_unresolved": {"target", "confidence", "origin"},
    "calls_in": {"caller", "origin"},
    "data_access": {"kind", "target", "confidence", "origin"},
    "data_access_transactional": {"kind", "target", "confidence", "origin"},
}
_SCOPE_SLOT_FIELDS = {
    "module": MODULE_SLOT_FIELDS, "solution": SOLUTION_SLOT_FIELDS, "file": FILE_SLOT_FIELDS,
    "component": COMPONENT_SLOT_FIELDS, "method": METHOD_SLOT_FIELDS,
}
SYSTEM_VALUE_FIELDS = {
    "name", "solutions", "projects", "source_files", "screens", "flows", "real_flows", "infra_flows", "unresolved_flows",
    "percent", "objects", "sql", "edges", "solution_links", "configs", "connections", "data_ops", "unowned_flows",
}
MODULE_VALUE_FIELDS = {
    "name", "path", "slug", "solutions", "output_type", "project_type", "copy_marker", "source_files", "screens",
    "events", "flows", "real_flows", "tx_flows", "incoming_flows", "incoming_screens", "data_ops", "infra_ops",
    "indirect_targets", "unresolved_total", "unresolved_flows",
}
SOLUTION_VALUE_FIELDS = {"name", "path", "slug", "project_count"}
FILE_VALUE_FIELDS = {"name", "path", "kind", "module_name", "module_slug", "slug", "component_count", "ownership_note"}
COMPONENT_VALUE_FIELDS = {
    "name", "kind", "module_name", "module_slug", "file_name", "file_path", "file_slug", "slug", "accessibility",
    "modifiers", "namespace", "inherits", "implements", "confidence", "member_count", "codebehind", "master_page",
}
METHOD_VALUE_FIELDS = {
    "name", "kind", "accessibility", "shared", "slug", "component_name", "component_slug", "file_name", "file_slug",
    "module_name", "module_slug", "calls_out_count", "calls_in_count", "data_access_count",
}
_SCOPE_VALUE_FIELDS = {
    "module": MODULE_VALUE_FIELDS, "solution": SOLUTION_VALUE_FIELDS, "file": FILE_VALUE_FIELDS,
    "component": COMPONENT_VALUE_FIELDS, "method": METHOD_VALUE_FIELDS,
}
PROFILE_PARAMS = {"body_row_limit"}
BLOCK_TYPES = {"heading", "paragraph", "note", "table", "bullets", "link", "interpreted", "partitioned_table"}
TRANSLATE_PREFIXES = {"state", "direction", "noise", "kind", "depclass", "filekind", "compkind", "methodkind"}
LINK_TYPES = ("module", "solution", "file", "component", "method")
_PARAM_FUNCS = ("count", "total", "shown", "noise", "noise_count")
_COND_HEADS = {
    "nonempty", "empty", "nonempty_total", "empty_total", "zero", "positive", "value", "empty_value",
    "has_noise", "has_noise_text", "interpreted", "no_interpreted", "gap", "more_than_limit",
}


class ConfigError(ValueError):
    """A configuration item (profile/template/catalog/policy) is invalid."""


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"{path}: no se pudo leer como JSON válido ({exc})") from exc


@dataclass
class OutputProfile:
    id: str
    audience: str
    max_detail_level: int
    visible_categories: tuple
    detail_on_demand: str
    language: str
    noise_policy: str
    noise_visibility_overrides: dict
    unresolved_behavior: str
    body_row_limit: int
    output_dir: str
    templates: tuple
    max_items_per_part: int
    max_bytes_per_part: int
    source: str = "default"

    @staticmethod
    def from_dict(data: dict, source: str = "default") -> "OutputProfile":
        where = f"perfil {data.get('id', '?')!r}"
        for key in ("id", "audience", "max_detail_level", "visible_categories", "detail_on_demand", "language",
                    "noise_policy", "unresolved_behavior", "body_row_limit", "output_dir", "templates", "partition"):
            if key not in data:
                raise ConfigError(f"{where}: falta el campo '{key}'")
        if data.get("contract_version") != CONTRACT_VERSION:
            raise ConfigError(f"{where}: contract_version {data.get('contract_version')!r} no soportada (se espera {CONTRACT_VERSION!r})")
        categories = tuple(data["visible_categories"])
        for category in categories:
            if category not in CATEGORIES:
                raise ConfigError(f"{where}: categoría desconocida {category!r}")
        if INTERNAL_ONLY in categories and not data.get("allow_internal_only"):
            raise ConfigError(f"{where}: INTERNAL_ONLY nunca es visible salvo 'allow_internal_only': true explícito")
        if data["detail_on_demand"] not in ("none", "documents"):
            raise ConfigError(f"{where}: detail_on_demand debe ser 'none' o 'documents'")
        if data["unresolved_behavior"] not in ("summary_only", "summary_with_link", "inline"):
            raise ConfigError(f"{where}: unresolved_behavior inválido")
        if not (isinstance(data["max_detail_level"], int) and 1 <= data["max_detail_level"] <= 4):
            raise ConfigError(f"{where}: max_detail_level debe ser un entero 1-4")
        limits = data["partition"]
        items, size = limits.get("max_items_per_part"), limits.get("max_bytes_per_part")
        if not (isinstance(items, int) and items > 0 and isinstance(size, int) and size > 0):
            raise ConfigError(f"{where}: partition requiere max_items_per_part y max_bytes_per_part enteros positivos")
        overrides = dict(data.get("noise_visibility_overrides", {}))
        for category, visibility in overrides.items():
            if visibility not in VISIBILITIES:
                raise ConfigError(f"{where}: visibilidad de ruido inválida para {category!r}: {visibility!r}")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(data["output_dir"])):
            raise ConfigError(f"{where}: output_dir debe ser un nombre simple de directorio")
        return OutputProfile(
            id=data["id"], audience=data["audience"], max_detail_level=data["max_detail_level"],
            visible_categories=categories, detail_on_demand=data["detail_on_demand"], language=data["language"],
            noise_policy=data["noise_policy"], noise_visibility_overrides=overrides,
            unresolved_behavior=data["unresolved_behavior"], body_row_limit=int(data["body_row_limit"]),
            output_dir=data["output_dir"], templates=tuple(data["templates"]),
            max_items_per_part=items, max_bytes_per_part=size, source=source,
        )


class Catalog:
    """Language catalog: flat `key -> text with {params}`. Missing keys fall back to the
    default `es` catalog; a key missing everywhere yields a visible marker and is recorded."""

    def __init__(self, lang: str, texts: dict, fallback: dict) -> None:
        self.lang = lang
        self._texts = texts
        self._fallback = fallback
        self.missing: set[str] = set()

    def has(self, key: str) -> bool:
        return key in self._texts or key in self._fallback

    def raw(self, key: str) -> str:
        """Unformatted catalog string (the renderer formats and escapes parameters)."""
        template = self._texts.get(key, self._fallback.get(key))
        if template is None:
            self.missing.add(key)
            return f"[[{key}]]"
        return template

    def text(self, key: str, **params) -> str:
        template = self._texts.get(key, self._fallback.get(key))
        if template is None:
            self.missing.add(key)
            return f"[[{key}]]"
        try:
            return template.format_map(_SafeDict(params))
        except (ValueError, IndexError):
            return template


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class ConfigRegistry:
    """Resolves defaults with optional custom overlays; collects warnings."""

    def __init__(self, custom_dir: str | Path | None = None, strict: bool = False) -> None:
        self.custom_dir = Path(custom_dir) if custom_dir else None
        self.strict = strict
        self.warnings: list[str] = []

    # ---------------------------------------------------------------- helpers
    def _custom_file(self, kind: str, name: str) -> Path | None:
        if self.custom_dir is None:
            return None
        path = self.custom_dir / kind / f"{name}.json"
        return path if path.is_file() else None

    def _resolve(self, kind: str, name: str, build, validate_custom=None):
        """custom (if exists and valid) -> default. Invalid custom: warning+default, or raise if strict."""
        custom = self._custom_file(kind, name)
        if custom is not None:
            try:
                item = build(_load_json(custom), "custom")
                if validate_custom:
                    validate_custom(item)
                return item
            except (ConfigError, NoisePolicyError) as exc:
                message = f"{kind}/{name} personalizado inválido ({custom}): {exc}"
                if self.strict:
                    raise ConfigError(message) from exc
                self.warnings.append(f"{message}. Se usa el valor por defecto.")
        default = DEFAULTS_DIR / kind / f"{name}.json"
        if not default.is_file():
            raise ConfigError(f"{kind}/{name}: no existe ni personalizado ni por defecto")
        return build(_load_json(default), "default")

    # ---------------------------------------------------------------- items
    def profile(self, name: str) -> OutputProfile:
        return self._resolve("profiles", name, lambda data, src: OutputProfile.from_dict(data, src))

    def noise_policy(self, name: str) -> NoisePolicy:
        return self._resolve("noise", name, lambda data, src: _noise_from(data))

    def catalog(self, lang: str) -> Catalog:
        fallback = _load_json(DEFAULTS_DIR / "i18n" / "es.json")
        texts = self._resolve("i18n", lang, lambda data, src: _catalog_texts(data)) if (
            (DEFAULTS_DIR / "i18n" / f"{lang}.json").is_file() or self._custom_file("i18n", lang)
        ) else fallback
        if texts is fallback and lang != "es":
            self.warnings.append(f"catálogo de idioma '{lang}' no existe; se usa 'es'.")
        return Catalog(lang, texts, fallback)

    def template(self, template_id: str, profile: OutputProfile, catalog: Catalog) -> dict:
        def build(data: dict, source: str) -> dict:
            if source == "custom":
                validate_template(data, catalog, profile, expected_id=template_id)
            data["_source"] = source
            return data

        return self._resolve("templates", template_id, build)


def _catalog_texts(data: dict) -> dict:
    if not isinstance(data, dict) or not all(isinstance(v, str) for v in data.values()):
        raise ConfigError("un catálogo de idioma debe ser un objeto {clave: texto}")
    return data


def _noise_from(data: dict) -> NoisePolicy:
    return NoisePolicy.from_dict(data)


# ------------------------------------------------------------------ templates
def _slot_fields(source: str, scope: str) -> set[str]:
    parts = source.split(".")
    if scope == "system" and len(parts) == 2 and parts[0] == "slots" and parts[1] in SYSTEM_SLOT_FIELDS:
        return SYSTEM_SLOT_FIELDS[parts[1]]
    if (
        scope in _SCOPE_SLOT_FIELDS and len(parts) == 3 and parts[0] == scope and parts[1] == "slots"
        and parts[2] in _SCOPE_SLOT_FIELDS[scope]
    ):
        return _SCOPE_SLOT_FIELDS[scope][parts[2]]
    raise ConfigError(f"fuente desconocida {source!r} para el ámbito '{scope}'")


def _check_param_path(path: str, scope: str) -> None:
    if path.startswith("const:"):
        return
    head, _, rest = path.partition(":")
    if rest and head in _PARAM_FUNCS:
        _slot_fields(rest, scope)
        return
    if path.startswith("system."):
        if path[7:] not in SYSTEM_VALUE_FIELDS:
            raise ConfigError(f"parámetro desconocido {path!r}")
    elif scope in _SCOPE_VALUE_FIELDS and path.startswith(f"{scope}."):
        if path[len(scope) + 1:] not in _SCOPE_VALUE_FIELDS[scope]:
            raise ConfigError(f"parámetro desconocido {path!r}")
    elif path.startswith("profile."):
        if path[8:] not in PROFILE_PARAMS:
            raise ConfigError(f"parámetro desconocido {path!r}")
    else:
        raise ConfigError(f"parámetro desconocido {path!r}")


def _check_condition(cond: str, scope: str) -> None:
    """Clauses joined by `&&` (all must hold); each clause is `head:arg`. The `*_total`
    heads take a `|`-separated list of slot sources."""
    for clause in cond.split("&&"):
        head, _, arg = clause.partition(":")
        if head not in _COND_HEADS:
            raise ConfigError(f"condición desconocida {cond!r}")
        if head in ("nonempty_total", "empty_total"):
            for source in arg.split("|"):
                _slot_fields(source, scope)
        elif head in ("nonempty", "empty", "has_noise", "has_noise_text", "more_than_limit"):
            _slot_fields(arg, scope)
        elif head in ("zero", "positive", "value", "empty_value"):
            _check_param_path(arg, scope)


def validate_template(data: dict, catalog: Catalog, profile: OutputProfile, expected_id: str | None = None) -> None:
    """Raises `ConfigError` (readable) if `data` is not a valid template descriptor."""
    if not isinstance(data, dict):
        raise ConfigError("el template debe ser un objeto JSON")
    for key in ("id", "contract_version", "scope", "file", "blocks"):
        if key not in data:
            raise ConfigError(f"falta el campo obligatorio '{key}'")
    if data["contract_version"] != CONTRACT_VERSION:
        raise ConfigError(f"contract_version {data['contract_version']!r} no soportada")
    if expected_id and data["id"] != expected_id:
        raise ConfigError(f"el id {data['id']!r} no coincide con el nombre de archivo {expected_id!r}")
    scope = data["scope"]
    if scope not in ("system", "module", "solution", "file", "component", "method"):
        raise ConfigError("scope debe ser 'system', 'module', 'solution', 'file', 'component' o 'method'")
    if scope != "system" and "{slug}" not in data["file"]:
        raise ConfigError(f"un template de ámbito '{scope}' debe usar {{slug}} en 'file'")
    if not re.fullmatch(r"[A-Za-z0-9_./{}-]+", data["file"]) or ".." in data["file"] or data["file"].startswith("/"):
        raise ConfigError(f"ruta de salida no permitida: {data['file']!r}")
    if profile.id not in data.get("profile_compat", [profile.id]):
        raise ConfigError(f"no es compatible con el perfil {profile.id!r}")
    if "when" in data:
        _check_condition(data["when"], scope)
    if data.get("title_key") and not catalog.has(data["title_key"]):
        raise ConfigError(f"clave de idioma inexistente {data['title_key']!r}")
    if not isinstance(data["blocks"], list) or not data["blocks"]:
        raise ConfigError("'blocks' debe ser una lista no vacía")
    for index, block in enumerate(data["blocks"], start=1):
        _validate_block(block, scope, catalog, f"bloque #{index}")


def _validate_block(block: dict, scope: str, catalog: Catalog, where: str) -> None:
    if not isinstance(block, dict) or block.get("type") not in BLOCK_TYPES:
        raise ConfigError(f"{where}: tipo de bloque inválido ({block.get('type') if isinstance(block, dict) else block!r})")
    kind = block["type"]
    if "when" in block:
        _check_condition(block["when"], scope)
    if kind == "bullets":
        for item in block.get("items", []):
            _validate_block({"type": "paragraph", **item}, scope, catalog, f"{where} (viñeta)")
        return
    if kind in ("heading", "paragraph", "note", "link"):
        key = block.get("text_key")
        if key is None or not catalog.has(key):
            raise ConfigError(f"{where}: clave de idioma inexistente {key!r}")
        for path in (block.get("params") or {}).values():
            _check_param_path(path, scope)
        if kind == "link" and not str(block.get("target", "")).startswith("template:"):
            raise ConfigError(f"{where}: el destino del enlace debe ser 'template:<id>'")
    if kind in ("table", "partitioned_table"):
        fields = _slot_fields(block.get("source", ""), scope)
        if not block.get("columns"):
            raise ConfigError(f"{where}: la tabla requiere columnas")
        for column in block["columns"]:
            if column.get("field") not in fields:
                raise ConfigError(f"{where}: el campo {column.get('field')!r} no existe en {block['source']}")
            if not catalog.has(column.get("header_key", "")):
                raise ConfigError(f"{where}: clave de idioma inexistente {column.get('header_key')!r}")
            if column.get("translate") and column["translate"] not in TRANSLATE_PREFIXES:
                raise ConfigError(f"{where}: translate inválido {column['translate']!r}")
            if column.get("max_chars") is not None and not (isinstance(column["max_chars"], int) and column["max_chars"] > 8):
                raise ConfigError(f"{where}: max_chars debe ser un entero > 8")
            if column.get("link") is not None and column["link"] not in LINK_TYPES:
                raise ConfigError(f"{where}: link inválido {column['link']!r}")
        limit = block.get("limit")
        if kind == "table" and limit is not None and limit != "profile.body_row_limit" and not isinstance(limit, int):
            raise ConfigError(f"{where}: limit inválido {limit!r}")
        if kind == "partitioned_table" and (not block.get("name") or not re.fullmatch(r"[a-z0-9-]+", block["name"])):
            raise ConfigError(f"{where}: partitioned_table requiere 'name' [a-z0-9-]+")
    if kind == "interpreted" and block.get("target") not in ("system", "module"):
        raise ConfigError(f"{where}: interpreted.target debe ser 'system' o 'module'")
