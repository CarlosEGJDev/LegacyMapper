"""Style evidence for the documentary UI reconstruction (post-V5 template productization; Gate B: persisted Evidence only).

Only what the legacy sources actually declared is used -- and it is read from persisted UI Evidence (`ui_style_references`,
`ui_assets`), never from the source repository: the stylesheet(s) linked by the shell page, CssClass / class / inline style /
Width attributes of each control, and icon files that existed in the repository at analysis time. Nothing is invented and nothing is
executed (no JavaScript, no running application). `Tipo="X"` of the compiled SondaNet controls is mapped to the CSS class `X` as an
INFERENCE (the control library is a DLL and not available), so fidelity is never reported as high on that basis alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from legacy_documenter.evidence.ui_css import _color, _px, parse_css, parse_declarations  # noqa: F401  (stable import surface)

STRUCTURE_ONLY, STYLE_PARTIAL, STYLE_HIGH = "STRUCTURE_ONLY", "STYLE_PARTIAL", "STYLE_HIGH_CONFIDENCE"


@dataclass
class StyleCatalog:
    css_files: list[str] = field(default_factory=list)
    shell: str = ""
    rules: dict = field(default_factory=dict)
    icon_resolver: object | None = None       # callable(view_file, image_url) -> (data URI | None, reason); injected by behavior.ui_evidence

    @classmethod
    def from_evidence(cls, ui, shell_candidates: tuple[str, ...] = ("default.aspx",)) -> "StyleCatalog":
        """Catalog of the shell page's stylesheets from persisted `ui_style_references` (same selection rule as the original discovery)."""
        cat = cls()
        for name in shell_candidates:
            doc = ui.document(name)
            if doc is None:
                continue
            links = sorted(ui.stylesheet_links.get(doc["id"], []), key=lambda r: r["properties"]["order"])
            if not links:
                continue
            cat.shell = name
            for link in links:
                target = ui.stylesheet_files.get(link["relationships"].get("stylesheet_file") or "")
                if target is not None:
                    cat.css_files.append(link["properties"]["resolved_logical_path"])
                    cat.rules.update(target["properties"]["rules"])
            break
        return cat

    # ---- per-control resolution
    def resolve(self, attrs: dict) -> tuple[dict, list[str], list[str]]:
        """Returns (style, sources, unresolved). `sources` items: css:.Class | tipo:Class (inferred) | inline | attr."""
        style: dict = {}
        sources: list[str] = []
        unresolved: list[str] = []
        for key, label, inferred in (("cssclass", "css", False), ("class", "css", False), ("tipo", "tipo", True)):
            for cls_name in str(attrs.get(key, "")).split():
                if cls_name in self.rules:
                    style.update({k: v for k, v in self.rules[cls_name].items() if k not in style or not inferred})
                    sources.append(f"{label}:.{cls_name}" + (" (inferido)" if inferred else ""))
                elif key != "tipo":
                    unresolved.append(cls_name)
        if attrs.get("style"):
            decl = parse_declarations(str(attrs["style"]))
            if decl:
                style.update(decl)
                sources.append("inline")
        for k in ("width", "height"):
            px = _px(str(attrs.get(k, ""))) if attrs.get(k) and not str(attrs.get(k)).endswith("%") else None
            if px:
                style[k] = px
                sources.append(f"attr:{k}")
        return style, sources, unresolved

    def icon(self, view_markup_file: str, image_url: str) -> tuple[str | None, str]:
        """(data URI or None, reason) of an image referenced by a control, from persisted asset evidence."""
        if self.icon_resolver is None:
            return None, "sin imagen"
        return self.icon_resolver(view_markup_file, image_url)


def classify_fidelity(report: dict) -> str:
    """Conservative: HIGH only when nearly every visible control has confirmed (non-inferred) style, icons resolve and no layout is runtime-driven."""
    if not report.get("controls_with_style"):
        return STRUCTURE_ONLY
    visible = max(1, report.get("visible_controls", 1))
    confirmed_ratio = report.get("controls_with_confirmed_style", 0) / visible
    clean = (report.get("icons_total", 0) == report.get("icons_resolved", 0) and not report.get("dynamic_visibility_assignments")
             and not report.get("script_blocks") and report.get("css_sources") and not report.get("classes_unresolved"))
    return STYLE_HIGH if confirmed_ratio >= 0.9 and clean else STYLE_PARTIAL
