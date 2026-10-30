"""Human template system (post-V5 template productization).

    LegacyMapperHumanTemplate 1.0  =  template.yaml + document.html + styles.css + pdf.css + assets/

A template owns LAYOUT and PRESENTATION only: section order/visibility, labels, typography, colours and the HTML shell. It can never
change truth: it receives the already validated `BehavioralDocument`, it contains no code (placeholders are `{{name}}` from a closed
set, no expressions/loops/includes), CSS is screened for imports/URLs/expressions, and the renderer - not the template - decides what
content exists. A template never calls a provider and never reads Evidence or the baseline.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.utils.path_contract import builtin_templates_root

CONTRACT = "LegacyMapperHumanTemplate"
CONTRACT_VERSION = "1.0"

SECTION_IDS = ("cover", "ai_notice", "toc", "solution", "project", "modules", "important_views", "view_chapters", "cross_view", "data", "usage",
               "unresolved", "appendix")
#: Gate C: `unresolved` (and the `flow`/`actions` chapter parts that carry per-action UNRESOLVED routes) can never be hidden by a template.
REQUIRED_SECTIONS = ("cover", "ai_notice", "toc", "solution", "project", "view_chapters", "unresolved", "appendix")
CHAPTER_PARTS = ("title", "one_line", "what_it_does", "usage", "ui", "flow", "actions", "data", "classes", "invocations", "messages", "knowledge", "evidence")
REQUIRED_CHAPTER_PARTS = ("title", "one_line", "what_it_does", "usage", "flow", "actions")
LAYOUT_VALUES = {"title_alignment": ("center", "left"), "view_title_alignment": ("center", "left"), "paragraph_alignment": ("justify", "left"),
                 "diagram_alignment": ("center", "left"), "ai_marker": ("chapter", "none")}
LAYOUT_DEFAULTS = {"title_alignment": "center", "view_title_alignment": "center", "paragraph_alignment": "justify", "diagram_alignment": "center",
                   "ai_marker": "chapter"}
PLACEHOLDERS = ("title", "subtitle", "lang", "style", "toc", "ai_notice", "content", "legend", "footer", "script", "template_id", "template_version")
KNOWN_FIELDS = (
    "solution.name", "solution.projects", "project.name", "project.summary", "module.classification", "module.claim", "view.name", "view.view",
    "view.title", "view.usage", "view.actions", "view.ui", "view.classes", "view.reached_by", "view.reaches", "view.messages", "view.unresolved",
    "view.what_it_does", "view.ai_narrative", "view.ai_action_notes", "document.catalog", "document.measurements", "document.usage_summary",
    "document.ai_manifest", "document.baseline",
)
PDF_CLASSES = ("doc-title", "h1", "h2", "h3", "body", "caption", "technical", "evidence", "badge")
_ID = re.compile(r"^[a-z0-9][a-z0-9_.\-/]*$")
_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_\-]+)\s*\}\}")
_UNSAFE_CSS = re.compile(r"(?is)@import|@font-face|url\s*\(|expression\s*\(|javascript:|behavior\s*:|-moz-binding|<\s*/?\s*(script|style)")
_UNSAFE_HTML = re.compile(r"(?is)<\s*script|\son[a-z]+\s*=|javascript:|<\s*iframe|<\s*object|<\s*embed|<\s*link|<\s*meta\s+http-equiv")


class TemplateError(ValueError):
    """The template violates the contract or the safety rules (it is never partially applied)."""


# ---------------------------------------------------------------- minimal YAML subset (maps, lists, scalars, comments)
def _scalar(text: str):
    t = text.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    low = t.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    return t


def parse_yaml(text: str) -> dict:
    """Subset: `key: value`, nested maps by 2-space indentation, `- item` lists of scalars, `[a, b]`, `#` comments. Anything else is an error."""
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = re.sub(r"(?<!\S)#.*$", "", raw).rstrip()
        if not line.strip():
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise TemplateError(f"template.yaml line {n}: tabs are not allowed")
        lines.append((n, len(line) - len(line.lstrip(" ")), line.strip()))

    def block(i: int, indent: int):
        if i >= len(lines):
            return None, i
        if lines[i][2].startswith("- "):
            items = []
            while i < len(lines) and lines[i][1] == indent and lines[i][2].startswith("- "):
                items.append(_scalar(lines[i][2][2:]))
                i += 1
            return items, i
        out: dict = {}
        while i < len(lines) and lines[i][1] == indent:
            n, _ind, content = lines[i]
            if content.startswith("- ") or ":" not in content:
                raise TemplateError(f"template.yaml line {n}: unsupported syntax")
            key, _, rest = content.partition(":")
            key = key.strip()
            if not re.fullmatch(r"[A-Za-z0-9_\-]+", key):
                raise TemplateError(f"template.yaml line {n}: invalid key")
            if rest.strip():
                out[key] = _scalar(rest)
                i += 1
            else:
                if i + 1 < len(lines) and lines[i + 1][1] > indent:
                    out[key], i = block(i + 1, lines[i + 1][1])
                else:
                    out[key] = None
                    i += 1
        if i < len(lines) and lines[i][1] > indent:
            raise TemplateError(f"template.yaml line {lines[i][0]}: unexpected indentation")
        return out, i

    value, end = block(0, lines[0][1] if lines else 0)
    if end != len(lines) or not isinstance(value, dict):
        raise TemplateError("template.yaml: invalid structure")
    return value


# ---------------------------------------------------------------- CSS subset for the PDF writer
_COLOR = re.compile(r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")


def _color(value: str):
    m = _COLOR.match(value.strip())
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(round(int(h[i:i + 2], 16) / 255, 3) for i in (0, 2, 4))


def _size(value: str):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(pt|px)\s*", value)
    if not m:
        return None
    n = float(m.group(1))
    return n if m.group(2) == "pt" else round(n * 0.75, 2)


def parse_pdf_css(text: str) -> dict:
    """Reads `.doc-title{font-size:26pt;color:#111}` rules for the known classes into a flat style dict. Unknown classes are ignored."""
    props: dict[str, dict[str, str]] = {}
    for sel, body in re.findall(r"\.([A-Za-z0-9_\-]+)\s*\{([^}]*)\}", text):
        if sel not in PDF_CLASSES:
            continue
        decl = {}
        for part in body.split(";"):
            if ":" in part:
                k, _, v = part.partition(":")
                decl[k.strip().lower()] = v.strip()
        props.setdefault(sel, {}).update(decl)
    style: dict = {"heading_sizes": {}, "heading_colors": {}}
    for level, cls in ((1, "h1"), (2, "h2"), (3, "h3")):
        size = _size(props.get(cls, {}).get("font-size", ""))
        if size:
            style["heading_sizes"][level] = size
        col = _color(props.get(cls, {}).get("color", ""))
        if col:
            style["heading_colors"][level] = col
    for cls, key in (("body", "body_size"), ("caption", "caption_size"), ("technical", "technical_size"), ("evidence", "evidence_size")):
        size = _size(props.get(cls, {}).get("font-size", ""))
        if size:
            style[key] = size
    title = _size(props.get("doc-title", {}).get("font-size", ""))
    if title:
        style["title_size"] = title
    tcol = _color(props.get("doc-title", {}).get("color", ""))
    if tcol:
        style["title_color"] = tcol
    if props.get("doc-title", {}).get("text-align", "").lower() == "center":
        style["title_align"] = "center"
    if props.get("body", {}).get("text-align", "").lower() == "justify":
        style["justify"] = True
    space = _size(props.get("body", {}).get("margin-bottom", ""))
    if space:
        style["paragraph_space"] = space
    style["heading_align"], style["heading_before"], style["heading_after"] = {}, {}, {}
    for level, cls in ((1, "h1"), (2, "h2"), (3, "h3")):
        decl = props.get(cls, {})
        if decl.get("text-align", "").lower() == "center":
            style["heading_align"][level] = "center"
        before, after = _size(decl.get("margin-top", "")), _size(decl.get("margin-bottom", ""))
        if before is not None:
            style["heading_before"][level] = before
        if after is not None:
            style["heading_after"][level] = after
    return style


# ---------------------------------------------------------------- the template object
@dataclass
class HumanTemplate:
    directory: Path
    manifest: dict
    document_html: str
    styles_css: str
    pdf_css: str
    pdf_style: dict
    sections: tuple
    chapter_parts: tuple
    labels: dict
    layout: dict
    required_fields: tuple
    optional_fields: tuple
    files: dict = field(default_factory=dict)

    @property
    def template_id(self) -> str:
        return self.manifest["template_id"]

    @property
    def language(self) -> str:
        return self.manifest["language"]

    def label(self, key: str, default: str = "") -> str:
        return str(self.labels.get(key, default))

    def has(self, section: str) -> bool:
        return section in self.sections

    def part(self, name: str) -> bool:
        return name in self.chapter_parts

    def fill(self, **values: str) -> str:
        """Substitutes the closed set of placeholders. Values are already-escaped HTML produced by the renderer."""
        def sub(m: re.Match) -> str:
            return str(values.get(m.group(1), ""))
        return _PLACEHOLDER.sub(sub, self.document_html)

    def manifest_record(self) -> dict:
        return {"contract": CONTRACT, "contract_version": CONTRACT_VERSION, "template_id": self.template_id,
                "template_version": self.manifest["template_version"], "audience": self.manifest["audience"], "language": self.language,
                "sections": list(self.sections), "chapter_parts": list(self.chapter_parts), "layout": dict(sorted(self.layout.items())),
                "required_fields": list(self.required_fields),
                "optional_fields": list(self.optional_fields), "files": dict(sorted(self.files.items())), "provider_calls": 0,
                "directory": self.directory.name}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TemplateError(f"cannot read {path.name}: {exc.__class__.__name__}") from None


def load_template(directory: str | Path) -> HumanTemplate:
    """Loads and validates one template directory. Raises TemplateError; nothing is partially applied."""
    root = Path(directory)
    if not root.is_dir():
        raise TemplateError(f"template directory not found: {root.name}")
    manifest = parse_yaml(_read(root / "template.yaml"))
    for key in ("contract", "contract_version", "template_id", "template_version", "audience", "language", "sections", "styles", "document",
                "required_fields", "optional_fields"):
        if key not in manifest or manifest[key] in (None, ""):
            raise TemplateError(f"template.yaml: missing '{key}'")
    if manifest["contract"] != CONTRACT or str(manifest["contract_version"]) != CONTRACT_VERSION:
        raise TemplateError(f"template.yaml: unsupported contract {manifest['contract']} {manifest['contract_version']}")
    if not _ID.match(str(manifest["template_id"])):
        raise TemplateError("template.yaml: invalid template_id")
    if str(manifest["language"]) not in ("es", "en"):
        raise TemplateError("template.yaml: unsupported language")
    sections = tuple(manifest["sections"] or ())
    unknown = [s for s in sections if s not in SECTION_IDS]
    if unknown:
        raise TemplateError(f"template.yaml: unknown sections {unknown}")
    if len(set(sections)) != len(sections):
        raise TemplateError("template.yaml: duplicate sections")
    missing = [s for s in REQUIRED_SECTIONS if s not in sections]
    if missing:
        raise TemplateError(f"template.yaml: required sections missing {missing}")
    parts = tuple(manifest.get("view_chapter") or CHAPTER_PARTS)
    bad_parts = [p for p in parts if p not in CHAPTER_PARTS]
    if bad_parts or [p for p in REQUIRED_CHAPTER_PARTS if p not in parts]:
        raise TemplateError(f"template.yaml: invalid view_chapter parts {bad_parts or 'required missing'}")
    required = tuple(manifest["required_fields"] or ())
    optional = tuple(manifest["optional_fields"] or ())
    for f in required + optional:
        if f not in KNOWN_FIELDS:
            raise TemplateError(f"template.yaml: unknown field '{f}'")
    styles = manifest["styles"] if isinstance(manifest["styles"], dict) else {}
    files: dict[str, str] = {}

    def load(rel: str, what: str) -> str:
        if not rel or rel != Path(rel).name or ".." in rel:           # files live directly in the template directory
            raise TemplateError(f"template.yaml: {what} must be a plain file name")
        text = _read(root / rel)
        files[rel] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return text

    document = load(str(manifest["document"]), "document")
    css = load(str(styles.get("html") or ""), "styles.html")
    pdf_css = load(str(styles.get("pdf") or ""), "styles.pdf")
    files["template.yaml"] = hashlib.sha256(_read(root / "template.yaml").encode("utf-8")).hexdigest()
    if _UNSAFE_HTML.search(document):
        raise TemplateError("document.html: scripts, event handlers, frames or http-equiv are not allowed")
    used = set(_PLACEHOLDER.findall(document))
    if used - set(PLACEHOLDERS):
        raise TemplateError(f"document.html: unknown placeholders {sorted(used - set(PLACEHOLDERS))}")
    for must in ("content", "style"):
        if must not in used:
            raise TemplateError(f"document.html: placeholder {{{{{must}}}}} is required")
    if re.search(r"\{\{[^}]*[^A-Za-z0-9_\-\s}][^}]*\}\}", document):
        raise TemplateError("document.html: placeholders cannot contain expressions")
    for name, text in (("styles.css", css), ("pdf.css", pdf_css)):
        if _UNSAFE_CSS.search(text):
            raise TemplateError(f"{name}: imports, url(), expressions and scripts are not allowed")
    assets = manifest.get("assets") or []
    if not isinstance(assets, list):
        raise TemplateError("template.yaml: assets must be a list")
    for a in assets:
        if not isinstance(a, str) or a != Path(a).name or ".." in a or not (root / "assets" / a).is_file():
            raise TemplateError(f"template.yaml: asset '{a}' missing or not a plain file name")
        files[f"assets/{a}"] = hashlib.sha256((root / "assets" / a).read_bytes()).hexdigest()
    labels = manifest.get("labels") if isinstance(manifest.get("labels"), dict) else {}
    layout = dict(LAYOUT_DEFAULTS)
    declared = manifest.get("layout") or {}
    if not isinstance(declared, dict):
        raise TemplateError("template.yaml: layout must be a map")
    for key, value in declared.items():
        if key not in LAYOUT_VALUES or value not in LAYOUT_VALUES[key]:
            raise TemplateError(f"template.yaml: invalid layout '{key}: {value}'")
        layout[key] = value
    return HumanTemplate(root, manifest, document, css, pdf_css, parse_pdf_css(pdf_css), sections, parts, labels, layout, required, optional, files)


def template_roots(template_dir: str | Path | None = None) -> list[Path]:
    """User override first, then the built-in templates packaged inside `legacy_documenter` (never cwd/checkout relative)."""
    roots = []
    if template_dir:
        roots.append(Path(template_dir))
    roots.append(builtin_templates_root())
    return roots


def discover(template_id: str = "human/default", template_dir: str | Path | None = None) -> HumanTemplate:
    """`human/default` resolves to <root>/human/default; a user template directory is searched before the built-in templates."""
    if not re.fullmatch(r"[a-z0-9_\-]+/[a-z0-9_\-]+", template_id):
        raise TemplateError(f"invalid template id '{template_id}' (expected <kind>/<name>)")
    kind, name = template_id.split("/")
    if kind != "human":
        raise TemplateError("only 'human' templates are implemented (the 'ai' template root is reserved)")
    for root in template_roots(template_dir):
        candidate = root / kind / name
        if (candidate / "template.yaml").is_file():
            return load_template(candidate)
        direct = root / name                      # --template-dir may point straight at a directory of templates
        if template_dir and (direct / "template.yaml").is_file():
            return load_template(direct)
    raise TemplateError(f"template '{template_id}' not found")


def validate_required_fields(template: HumanTemplate, document) -> list[str]:
    """Missing required fields of the validated behavioral model (empty list = OK). Presence only: the template cannot alter values."""
    problems: list[str] = []
    views = list(getattr(document, "views", []) or [])
    for field_name in template.required_fields:
        scope, _, attr = field_name.partition(".")
        if scope == "view":
            if not views:
                problems.append(f"{field_name}: the document has no detailed views")
                continue
            for v in views:
                if not hasattr(v, attr):
                    problems.append(f"{field_name}: missing on {getattr(v, 'name', '?')}")
        else:
            target = document if scope == "document" else getattr(document, scope, None)
            if target is None or (attr and not hasattr(target, attr) and not (isinstance(target, dict) and attr in target)):
                problems.append(f"{field_name}: missing")
    return problems
