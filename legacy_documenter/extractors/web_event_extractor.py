import re
from pathlib import Path


METHOD_RE = re.compile(r"^\s*(?:Public|Private|Protected Friend|Protected|Friend)?\s*(?:Overrides\s+)?(?:Shared\s+)?(?P<kind>Sub|Function)\s+(?P<name>[A-Za-z_]\w*)\b(?P<body>.*)", re.IGNORECASE)
HANDLES_RE = re.compile(r"\bHandles\s+(?P<events>.+)$", re.IGNORECASE)
TYPE_RE = re.compile(r"^\s*(?:Public|Private|Protected|Friend|Partial|MustInherit|NotInheritable|\s)+\s*(?:Class|Module|Structure)\s+(?P<name>[A-Za-z_]\w*)", re.IGNORECASE)
END_TYPE_RE = re.compile(r"^\s*End\s+(Class|Module|Structure)\b", re.IGNORECASE)
LIFECYCLE_OVERRIDES = {
    "oninit": "Init",
    "onload": "Load",
    "onprerender": "PreRender",
}


class WebEventExtractor:
    def extract(self, path: str | Path, root: str | Path | None = None) -> dict:
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        current_class: str | None = None
        handlers: list[dict] = []
        methods: list[dict] = []
        for line_no, line in self._logical_lines(file_path):
            type_match = TYPE_RE.match(line)
            if type_match:
                current_class = type_match.group("name")
                continue
            if END_TYPE_RE.match(line):
                current_class = None
                continue
            method = METHOD_RE.match(line)
            if not method:
                continue
            method_name = method.group("name")
            method_info = {
                "name": method_name,
                "class_name": current_class,
                "file": rel,
                "line": line_no,
                "evidence": line,
            }
            methods.append(method_info)
            handles = HANDLES_RE.search(line)
            if handles:
                for item in self._split_handles(handles.group("events")):
                    handlers.append(
                        {
                            **method_info,
                            "control": item["control"],
                            "event": item["event"],
                            "binding_kind": "handles",
                            "confidence": "confirmed",
                        }
                    )
            lifecycle = self._lifecycle_event(method_name, line)
            if lifecycle:
                handlers.append(
                    {
                        **method_info,
                        "control": "MyBase" if "MyBase." in line else "Me" if "Me." in line else None,
                        "event": lifecycle,
                        "binding_kind": "lifecycle",
                        "confidence": "confirmed",
                    }
                )
        return {"file": rel, "methods": methods, "handlers": handlers}

    def _logical_lines(self, path: Path) -> list[tuple[int, str]]:
        result: list[tuple[int, str]] = []
        pending = ""
        start_line = 0
        for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            line = self._remove_comment(raw).strip()
            if not line:
                continue
            if line.endswith("_"):
                if not pending:
                    start_line = idx
                pending += line[:-1].rstrip() + " "
                continue
            result.append((start_line or idx, pending + line))
            pending = ""
            start_line = 0
        if pending:
            result.append((start_line, pending))
        return result

    def _remove_comment(self, line: str) -> str:
        in_string = False
        for idx, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            if char == "'" and not in_string:
                return line[:idx]
        return line

    def _split_handles(self, value: str) -> list[dict]:
        events = []
        for item in value.split(","):
            target = item.strip()
            if "." not in target:
                continue
            control, event = target.rsplit(".", 1)
            events.append({"control": control.strip(), "event": event.strip()})
        return events

    def _lifecycle_event(self, method_name: str, line: str) -> str | None:
        lower = method_name.lower()
        if "Handles " in line:
            return None
        if lower in LIFECYCLE_OVERRIDES and re.search(r"\bOverrides\b", line, re.IGNORECASE):
            return LIFECYCLE_OVERRIDES[lower]
        return None
