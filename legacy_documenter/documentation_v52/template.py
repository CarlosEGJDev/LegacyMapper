"""Template engine: applies declarative templates to a profile-filtered view of the
`AudienceDocumentModel` and yields renderer-neutral `StructuredDocument`s.

Templates are JSON data (no code execution). The engine gives them a *read-only
view*: `ProfileView` filters items by the profile's visible categories/level and
applies the profile's noise visibility; templates never see internal ids, the
Evidence Core or the noise policy itself.
"""
from __future__ import annotations

from collections import defaultdict

from .categories import DETAIL_ON_DEMAND, INTERPRETED, AudienceDocumentModel, Item
from .config import Catalog, OutputProfile
from .noise import NoisePolicy
from .structure import (
    Bullets, Code, Heading, Link, LinkRef, Note, Paragraph, PartitionedTable, StructuredDocument, Table, Text,
)

# Table-cell/link-block target template ids per scope (V5.2 R3.3: Solution ->
# Project -> Component/Archivo -> Método navigation).
_LINK_TEMPLATES = {
    "module": "dev.module", "solution": "dev.solution", "file": "dev.file", "component": "dev.component",
    "method": "dev.method",
}


class ProfileView:
    """What a profile lets a template see."""

    def __init__(self, model: AudienceDocumentModel, profile: OutputProfile, policy: NoisePolicy) -> None:
        self.model = model
        self.profile = profile
        self.policy = policy

    def _noise_visibility(self, item: Item) -> str | None:
        if item.noise_category is None:
            return None
        return self.policy.visibility(item.noise_category, self.profile.noise_visibility_overrides)

    def visible(self, items: list[Item]) -> list[Item]:
        out = []
        for item in items:
            category = item.category
            if self._noise_visibility(item) in ("hide", "summarize"):
                category = DETAIL_ON_DEMAND
            if category in self.profile.visible_categories and item.level <= self.profile.max_detail_level:
                out.append(item)
        return out

    def detail(self, items: list[Item]) -> list[Item]:
        """Everything a detail document may list (never INTERNAL_ONLY, never a
        noise category whose policy says it is not available in detail)."""
        if self.profile.detail_on_demand != "documents":
            return []
        out = []
        for item in items:
            if item.noise_category is not None and not self.policy.categories[item.noise_category].get("detail_availability", True):
                continue
            out.append(item)
        return out

    def noise(self, items: list[Item]) -> tuple[int, dict[str, int]]:
        """(total weight of hidden+summarized noise, {category: weight} of `summarize` ones)."""
        total = 0
        named: dict[str, int] = defaultdict(int)
        for item in items:
            visibility = self._noise_visibility(item)
            if visibility in ("hide", "summarize"):
                weight = int(item.values.get("count", 1))
                total += weight
                if visibility == "summarize":
                    named[item.noise_category] += weight
        return total, dict(named)


class TemplateEngine:
    def __init__(self, model: AudienceDocumentModel, profile: OutputProfile, policy: NoisePolicy,
                 catalog: Catalog, templates: dict[str, dict]) -> None:
        self.model = model
        self.profile = profile
        self.catalog = catalog
        self.templates = templates
        self.view = ProfileView(model, profile, policy)
        self._modules = {m.slug: m for m in model.modules}
        self._module_by_path = {m.values["path"]: m for m in model.modules}
        self._solutions = {s.slug: s for s in model.solutions}
        self._files = {f.slug: f for f in model.files}
        self._components = {c.slug: c for c in model.components}
        self._methods = {m.slug: m for m in model.methods}
        self.paths: dict[tuple[str, str], str] = {}  # (template id, scope key) -> doc path

    # ------------------------------------------------------------------ public
    def build(self) -> list[StructuredDocument]:
        planned: dict[str, list[tuple[dict, str]]] = defaultdict(list)
        ordered = sorted(self.templates.values(), key=lambda t: (t.get("order", 100), t["id"]))
        for template in ordered:
            if template.get("detail") and self.profile.detail_on_demand != "documents":
                continue
            for scope_key, ctx in self._contexts(template):
                if "when" in template and not self._cond(template["when"], ctx):
                    continue
                path = template["file"].replace("{slug}", scope_key)
                self.paths[(template["id"], scope_key)] = path
                planned[path].append((template, scope_key))
        documents = []
        for path in sorted(planned):
            entries = planned[path]
            first_template, scope_key = entries[0]
            ctx = self._context(first_template["scope"], scope_key)
            title_source = next((t for t, _ in entries if t.get("title_key")), first_template)
            title = self._text(title_source.get("title_key", ""), {"name": self._name(ctx)}) if title_source.get("title_key") else Text.of("")
            doc = StructuredDocument(path=path, title=title)
            for template, key in entries:
                if template.get("disclaimer") == "top":
                    doc.blocks.append(Note(Text.of(self.catalog.text("generated_note"))))
                    break
            for template, key in entries:
                ctx = self._context(template["scope"], key)
                for block in template["blocks"]:
                    doc.blocks.extend(self._block(block, ctx, template, key, path))
            for template, key in entries:
                if template.get("disclaimer") == "bottom":
                    doc.blocks.append(Note(Text.of(self.catalog.text("generated_note"))))
                    break
            documents.append(doc)
        return documents

    # ------------------------------------------------------------------ contexts
    def _contexts(self, template: dict):
        scope = template["scope"]
        if scope == "system":
            yield "", self._context("system", "")
        elif scope == "module":
            for module in self.model.modules:
                yield module.slug, self._context("module", module.slug)
        elif scope == "solution":
            for solution in self.model.solutions:
                yield solution.slug, self._context("solution", solution.slug)
        elif scope == "file":
            for file in self.model.files:
                yield file.slug, self._context("file", file.slug)
        elif scope == "component":
            for component in self.model.components:
                yield component.slug, self._context("component", component.slug)
        elif scope == "method":
            for method in self.model.methods:
                yield method.slug, self._context("method", method.slug)

    def _context(self, scope: str, key: str) -> dict:
        ctx = {"system": self.model.system, "slots": self.model.slots, "scope": scope}
        if scope == "module":
            module = self._modules[key]
            ctx["module"] = module.values
            ctx["module_slots"] = module.slots
            ctx["module_obj"] = module
        elif scope == "solution":
            solution = self._solutions[key]
            ctx["solution"] = solution.values
            ctx["solution_slots"] = solution.slots
        elif scope == "file":
            file = self._files[key]
            ctx["file"] = file.values
            ctx["file_slots"] = file.slots
        elif scope == "component":
            component = self._components[key]
            ctx["component"] = component.values
            ctx["component_slots"] = component.slots
        elif scope == "method":
            method = self._methods[key]
            ctx["method"] = method.values
            ctx["method_slots"] = method.slots
        return ctx

    @staticmethod
    def _name(ctx: dict) -> str:
        for scope in ("module", "solution", "file", "component", "method"):
            if ctx["scope"] == scope:
                return str(ctx[scope]["name"])
        return str(ctx["system"]["name"])

    # ------------------------------------------------------------------ data access
    @staticmethod
    def _all(source: str, ctx: dict) -> list[Item]:
        parts = source.split(".")
        if parts[0] == "slots":
            return ctx["slots"][parts[1]]
        return ctx[f"{parts[0]}_slots"][parts[2]]

    def _visible(self, source: str, ctx: dict, detail: bool) -> list[Item]:
        items = self._all(source, ctx)
        return self.view.detail(items) if detail else self.view.visible(items)

    def _param(self, path: str, ctx: dict) -> object:
        if path.startswith("const:"):
            return path[6:]
        head, _, rest = path.partition(":")
        if rest and head in ("count", "total", "shown", "noise", "noise_count"):
            items = self._all(rest, ctx)
            if head == "total":
                return len(items)
            visible = self.view.visible(items)
            if head == "count":
                return len(visible)
            if head == "shown":
                return min(self.profile.body_row_limit, len(visible))
            total, named = self.view.noise(items)
            if head == "noise_count":
                return total
            return ", ".join(f"{self.catalog.text('noise.' + c)} ({n})" for c, n in sorted(named.items()))
        if path.startswith("system."):
            return ctx["system"][path[7:]]
        for scope in ("module", "solution", "file", "component", "method"):
            if path.startswith(f"{scope}."):
                return ctx[scope][path[len(scope) + 1:]]
        if path.startswith("profile."):
            return getattr(self.profile, path[8:])
        raise KeyError(path)

    def _text(self, key: str, params: dict | None) -> Text:
        # unformatted catalog string: the renderer formats it and escapes parameters
        return Text.of(self.catalog.raw(key), params)

    def _params(self, spec: dict | None, ctx: dict) -> dict:
        return {name: str(self._param(path, ctx)) for name, path in (spec or {}).items()}

    # ------------------------------------------------------------------ conditions
    def _cond(self, cond: str, ctx: dict) -> bool:
        return all(self._clause(clause, ctx) for clause in cond.split("&&"))

    def _clause(self, clause: str, ctx: dict) -> bool:
        head, _, arg = clause.partition(":")
        if head == "nonempty":
            return bool(self._visible(arg, ctx, False))
        if head == "empty":
            return not self._visible(arg, ctx, False)
        if head == "nonempty_total":
            return any(self._all(source, ctx) for source in arg.split("|"))
        if head == "empty_total":
            return not any(self._all(source, ctx) for source in arg.split("|"))
        if head == "zero":
            return not self._param(arg, ctx)
        if head == "positive":
            return bool(self._param(arg, ctx))
        if head == "value":
            return bool(self._param(arg, ctx))
        if head == "empty_value":
            return not self._param(arg, ctx)
        if head == "has_noise":
            return self.view.noise(self._all(arg, ctx))[0] > 0
        if head == "has_noise_text":
            return bool(self.view.noise(self._all(arg, ctx))[1])
        if head == "interpreted":
            return self._interpreted(ctx) is not None
        if head == "no_interpreted":
            return self._interpreted(ctx) is None
        if head == "gap":
            return arg in self.model.gaps
        if head == "more_than_limit":
            return len(self._visible(arg, ctx, False)) > self.profile.body_row_limit
        raise ValueError(clause)

    def _interpreted(self, ctx: dict):
        if ctx["scope"] == "module":
            return self.model.interpreted.get(f"module:{ctx['module']['path']}")
        return self.model.interpreted.get("system")

    # ------------------------------------------------------------------ blocks
    def _block(self, block: dict, ctx: dict, template: dict, key: str, doc_path: str) -> list:
        if "when" in block and not self._cond(block["when"], ctx):
            return []
        kind = block["type"]
        if kind == "heading":
            return [Heading(block.get("level", 2), self._text(block["text_key"], self._params(block.get("params"), ctx)))]
        if kind == "paragraph":
            return [Paragraph(self._text(block["text_key"], self._params(block.get("params"), ctx)))]
        if kind == "note":
            return [Note(self._text(block["text_key"], self._params(block.get("params"), ctx)))]
        if kind == "bullets":
            items = [
                self._text(item["text_key"], self._params(item.get("params"), ctx))
                for item in block["items"] if "when" not in item or self._cond(item["when"], ctx)
            ]
            return [Bullets(items)] if items else []
        if kind == "link":
            target = self._link_target(block["target"], ctx)
            return [Link(self._text(block["text_key"], self._params(block.get("params"), ctx)), target)] if target else []
        if kind == "interpreted":
            section = self._interpreted(ctx)
            if section is None or section.origin.strip() == "":
                return []
            label = self.catalog.text("interpreted_label", origin=section.origin, created_at=section.created_at)
            return [Note(Text.of(label)), Note(Text.of("{content}", {"content": section.content}))]
        if kind == "table":
            return self._table(block, ctx, key, doc_path)
        if kind == "partitioned_table":
            return self._partitioned(block, ctx, key, template)
        raise ValueError(kind)

    def _link_target(self, ref: str, ctx: dict) -> str | None:
        """Resolves a `link` BLOCK's target (a single, fixed navigation link, not
        a per-row table link -- see `_cell` for that). The target key depends on
        the *target* template's own scope, derived from the current document's
        context (V5.2 R3.3: Método -> Componente -> Archivo -> Proyecto -> Solution)."""
        template_id = ref.split(":", 1)[1]
        target_scope = self.templates.get(template_id, {}).get("scope")
        if target_scope == "module":
            key = {"module": lambda: ctx["module"]["slug"], "file": lambda: ctx["file"]["module_slug"],
                   "component": lambda: ctx["component"]["module_slug"],
                   "method": lambda: ctx["method"]["module_slug"]}.get(ctx["scope"], lambda: "")()
        elif target_scope == "file":
            key = {"file": lambda: ctx["file"]["slug"], "component": lambda: ctx["component"]["file_slug"],
                   "method": lambda: ctx["method"]["file_slug"]}.get(ctx["scope"], lambda: "")()
        elif target_scope == "component":
            key = {"component": lambda: ctx["component"]["slug"],
                   "method": lambda: ctx["method"]["component_slug"]}.get(ctx["scope"], lambda: "")()
        elif target_scope == "method":
            key = ctx["method"]["slug"] if ctx["scope"] == "method" else ""
        elif target_scope == "solution":
            key = ctx["solution"]["slug"] if ctx["scope"] == "solution" else ""
        else:
            key = ""
        return self.paths.get((template_id, key))

    def _cell(self, column: dict, item: Item, detail: bool = False):
        value = item.values.get(column["field"], "")
        text = str(value)
        if column.get("translate") and text != "":
            key = f"{column['translate']}.{text}"
            text = self.catalog.text(key) if self.catalog.has(key) else text
        elif column.get("translate"):
            text = ""
        limit = column.get("max_chars")
        if limit and len(text) > limit and not detail:
            text = text[: limit - 1].rstrip() + "…"
        if column.get("format_key"):
            text = self.catalog.text(column["format_key"], value=text) if text else ""
        link_type = column.get("link")
        if link_type in _LINK_TEMPLATES:
            target = self.paths.get((_LINK_TEMPLATES[link_type], str(item.values.get("slug", ""))))
            if target:
                return LinkRef(text, target, code=bool(column.get("code")))
        if column.get("code") and text:
            return Code(text)
        return text

    def _rows(self, block: dict, items: list[Item], detail: bool = False) -> list[list]:
        return [[self._cell(column, item, detail) for column in block["columns"]] for item in items]

    def _headers(self, block: dict) -> list[str]:
        return [self.catalog.text(column["header_key"]) for column in block["columns"]]

    def _table(self, block: dict, ctx: dict, key: str, doc_path: str) -> list:
        items = self._visible(block["source"], ctx, False)
        if not items:
            return []
        limit = block.get("limit")
        limit = self.profile.body_row_limit if limit == "profile.body_row_limit" else limit
        shown = items if limit is None else items[:limit]
        out: list = [Table(self._headers(block), self._rows(block, shown))]
        if block.get("overflow") == "detail" and len(items) > len(shown):
            detail_template = block.get("detail_template", "dev.technical_detail")
            target = self.paths.get((detail_template, key))
            if target:
                out.append(Link(self._text("dev.module.more", {"shown": str(len(shown)), "total": str(len(items))}), target))
        return out

    def _partitioned(self, block: dict, ctx: dict, key: str, template: dict) -> list:
        detail = bool(template.get("detail"))
        items = self._visible(block["source"], ctx, detail)
        if not items:
            return []
        title = self.catalog.text(block["title_key"], name=self._name(ctx))
        stem = block.get("file_stem")
        return [
            Heading(2, Text.of(title)),
            PartitionedTable(block["name"], stem or "", title, self._headers(block), self._rows(block, items, detail=True),
                             separate=bool(block.get("separate"))),
        ]
