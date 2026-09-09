import re
from pathlib import Path

from legacy_documenter.models import WebForm


DIRECTIVE_RE = re.compile(r"<%@\s*(?P<name>\w+)\s+(?P<body>.*?)%>", re.IGNORECASE | re.DOTALL)
ATTR_RE = re.compile(r"(?P<key>[\w:.-]+)\s*=\s*\"(?P<value>[^\"]*)\"", re.IGNORECASE)
SCRIPT_RE = re.compile(r"<script[^>]+src\s*=\s*\"(?P<src>[^\"]+)\"", re.IGNORECASE)
CSS_RE = re.compile(r"<link[^>]+href\s*=\s*\"(?P<href>[^\"]+)\"[^>]*rel\s*=\s*\"stylesheet\"|<link[^>]+rel\s*=\s*\"stylesheet\"[^>]+href\s*=\s*\"(?P<href2>[^\"]+)\"", re.IGNORECASE)
TAG_RE = re.compile(r"<(?P<tag>(?:asp|uc\d*|cc\d*|[A-Za-z_][\w-]*):?[A-Za-z_][\w.-]*)\b(?P<body>[^<>]*?)>", re.IGNORECASE | re.DOTALL)


class WebFormsExtractor:
    def extract(self, path: str | Path, root: str | Path | None = None) -> WebForm:
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        kind = file_path.suffix.lower().lstrip(".")
        text = file_path.read_text(encoding="utf-8", errors="replace")
        form = WebForm(path=rel, kind=kind)
        for match in DIRECTIVE_RE.finditer(text):
            attrs = {m.group("key"): m.group("value") for m in ATTR_RE.finditer(match.group("body"))}
            normalized = {key.lower(): value for key, value in attrs.items()}
            directive = {"name": match.group("name"), "attributes": attrs}
            form.directives.append(directive)
            lower_name = match.group("name").lower()
            if lower_name in {"page", "control", "master"}:
                form.codebehind = normalized.get("codebehind") or form.codebehind
                form.codefile = normalized.get("codefile") or form.codefile
                form.inherits = normalized.get("inherits") or form.inherits
                form.master_page = normalized.get("masterpagefile") or form.master_page
            if lower_name == "register":
                form.registers.append({**attrs, "_normalized": normalized})
        form.scripts = [m.group("src") for m in SCRIPT_RE.finditer(text)]
        form.stylesheets = [m.group("href") or m.group("href2") for m in CSS_RE.finditer(text)]
        form.markup_events = self._extract_markup_events(text)
        return form

    def _extract_markup_events(self, text: str) -> list[dict]:
        events: list[dict] = []
        for match in TAG_RE.finditer(text):
            attrs = {m.group("key"): m.group("value") for m in ATTR_RE.finditer(match.group("body"))}
            normalized = {key.lower(): value for key, value in attrs.items()}
            control_id = normalized.get("id")
            for key, value in attrs.items():
                if not key.lower().startswith("on") or len(key) <= 2:
                    continue
                if not re.match(r"^[A-Za-z_]\w*$", value):
                    continue
                events.append(
                    {
                        "control": control_id,
                        "control_type": match.group("tag"),
                        "event": key[2:],
                        "handler": value,
                        "line": text.count("\n", 0, match.start()) + 1,
                        "evidence": match.group(0).strip(),
                        "binding_kind": "markup",
                    }
                )
        return events
