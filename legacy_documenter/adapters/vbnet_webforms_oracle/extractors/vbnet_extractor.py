import re
from pathlib import Path

from legacy_documenter.models import Symbol


TYPE_RE = re.compile(
    r"^\s*(?P<access>Public|Private|Protected|Friend|Partial|MustInherit|NotInheritable|Shared|\s)+\s*"
    r"(?P<kind>Class|Interface|Module|Structure|Enum)\s+(?P<name>[A-Za-z_][\w.]*)",
    re.IGNORECASE,
)
MEMBER_RE = re.compile(
    r"^\s*(?P<access>Public|Protected Friend|Protected|Friend)\s+(?P<shared>Shared\s+)?"
    r"(?P<kind>Sub|Function|Property)\s+(?P<name>[A-Za-z_]\w*)",
    re.IGNORECASE,
)
NAMESPACE_RE = re.compile(r"^\s*Namespace\s+(?P<name>[\w.]+)", re.IGNORECASE)
END_NAMESPACE_RE = re.compile(r"^\s*End\s+Namespace\b", re.IGNORECASE)
INHERITS_RE = re.compile(r"^\s*Inherits\s+(?P<names>.+)", re.IGNORECASE)
IMPLEMENTS_RE = re.compile(r"^\s*Implements\s+(?P<names>.+)", re.IGNORECASE)


class VBNetExtractor:
    """Provides the cohesive VBNetExtractor responsibility for this module."""
    def extract(self, path: str | Path, root: str | Path | None = None) -> list[Symbol]:
        """Performs extract while preserving this module's deterministic contract."""
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        lines = self._logical_lines(file_path)
        namespaces: list[str] = []
        symbols: list[Symbol] = []
        current: Symbol | None = None
        for line in lines:
            ns = NAMESPACE_RE.match(line)
            if ns:
                namespaces.append(ns.group("name"))
                continue
            if END_NAMESPACE_RE.match(line):
                if namespaces:
                    namespaces.pop()
                continue
            type_match = TYPE_RE.match(line)
            if type_match:
                prefix = line[: type_match.start("kind")]
                tokens = {token.lower() for token in re.findall(r"\b\w+\b", prefix)}
                access = next((a for a in ["Public", "Private", "Protected", "Friend"] if a.lower() in tokens), None)
                modifiers = [m for m in ["Shared", "MustInherit", "NotInheritable", "Partial"] if m.lower() in tokens]
                current = Symbol(
                    name=type_match.group("name"),
                    kind=type_match.group("kind").lower(),
                    file=rel,
                    namespace=".".join(namespaces) if namespaces else None,
                    declared_namespace=".".join(namespaces) if namespaces else None,
                    effective_namespace=".".join(namespaces) if namespaces else None,
                    namespace_confidence="confirmed" if namespaces else "unresolved",
                    accessibility=access,
                    modifiers=modifiers,
                )
                symbols.append(current)
                continue
            if current:
                inherits = INHERITS_RE.match(line)
                if inherits:
                    current.inherits.extend(self._split_names(inherits.group("names")))
                    continue
                implements = IMPLEMENTS_RE.match(line)
                if implements:
                    current.implements.extend(self._split_names(implements.group("names")))
                    continue
                member = MEMBER_RE.match(line)
                if member:
                    record = {
                        "kind": member.group("kind").lower(),
                        "name": member.group("name"),
                        "accessibility": member.group("access").strip(),
                        "shared": bool(member.group("shared")),
                    }
                    if record["kind"] in ("sub", "function"):
                        record["parameters"] = self._parameters(line[member.end():])      # declared signature: overload arity evidence
                    current.members.append(record)
        return symbols

    @staticmethod
    def _parameters(rest: str) -> list[dict]:
        """Parameters of a Sub/Function declaration from the text after its name: `(ByVal a As T, Optional b As Integer = 0, ParamArray c() As X)`."""
        text = rest.lstrip()
        if not text.startswith("("):
            return []
        depth, end = 0, None
        for idx, char in enumerate(text):
            depth += (char == "(") - (char == ")")
            if depth == 0:
                end = idx
                break
        body = text[1:end] if end is not None else text[1:]
        parts, depth, current = [], 0, ""
        for char in body:
            depth += (char == "(") - (char == ")")
            if char == "," and depth == 0:
                parts.append(current)
                current = ""
            else:
                current += char
        if current.strip():
            parts.append(current)
        modifiers = {"byval", "byref", "optional", "paramarray"}
        result = []
        for part in parts:
            words = re.findall(r"[A-Za-z_][A-Za-z0-9_.]*", part.split("=")[0])
            if not words:
                continue
            lowered = [w.lower() for w in words]
            names = [w for w in words if w.lower() not in modifiers]
            type_name = None
            if "as" in lowered:
                at = lowered.index("as")
                if at + 1 < len(words):
                    type_name = words[at + 1]
                names = [w for w in words[:at] if w.lower() not in modifiers]
            result.append({
                "name": names[0] if names else None,
                "type": type_name,
                "passing": "ByRef" if "byref" in lowered else "ByVal",
                "optional": "optional" in lowered,
                "param_array": "paramarray" in lowered,
            })
        return result

    def _logical_lines(self, path: Path) -> list[str]:
        logical: list[str] = []
        pending = ""
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = self._remove_comment(raw).strip()
            if not line or line.startswith("<"):
                continue
            if line.endswith("_"):
                pending += line[:-1].rstrip() + " "
                continue
            logical.append(pending + line)
            pending = ""
        if pending:
            logical.append(pending)
        return logical

    def _remove_comment(self, line: str) -> str:
        in_string = False
        for idx, char in enumerate(line):
            if char == '"':
                in_string = not in_string
            if char == "'" and not in_string:
                return line[:idx]
        return line

    def _split_names(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]
