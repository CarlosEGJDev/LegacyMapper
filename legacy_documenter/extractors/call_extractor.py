import re
from pathlib import Path

from legacy_documenter.models import Call, Evidence, Instantiation, TypeReference


IMPORT_RE = re.compile(r"^\s*Imports\s+(?:(?P<alias>[A-Za-z_]\w*)\s*=\s*)?(?P<name>[\w.]+)", re.IGNORECASE)
TYPE_RE = re.compile(r"^\s*(?:Public|Private|Protected|Friend|Partial|MustInherit|NotInheritable|\s)+\s*(?P<kind>Class|Interface|Module|Structure)\s+(?P<name>[A-Za-z_]\w*)", re.IGNORECASE)
END_TYPE_RE = re.compile(r"^\s*End\s+(Class|Interface|Module|Structure)\b", re.IGNORECASE)
METHOD_RE = re.compile(r"^\s*(?:Public|Private|Protected Friend|Protected|Friend)?\s*(?:Shared\s+)?(?P<kind>Sub|Function)\s+(?P<name>[A-Za-z_]\w*)", re.IGNORECASE)
END_METHOD_RE = re.compile(r"^\s*End\s+(Sub|Function)\b", re.IGNORECASE)
VAR_RE = re.compile(r"\bDim\s+(?P<var>[A-Za-z_]\w*)\s+As\s+(?:New\s+)?(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
ASSIGN_NEW_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\s*(?:=\s*New\s+|As\s+(?:New\s+|[A-Za-z_][\w.]*\s*=\s*New\s+))(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
NEW_RE = re.compile(r"\bNew\s+(?P<type>[A-Za-z_][\w.]*)\s*\(", re.IGNORECASE)
QUALIFIED_CALL_RE = re.compile(r"\b(?P<receiver_path>(?:[A-Za-z_]\w*|Me|MyBase)(?:\.[A-Za-z_]\w*)*)\.(?P<method>[A-Za-z_]\w*)\s*\((?P<args>[^)]*)\)", re.IGNORECASE)
INTERNAL_CALL_RE = re.compile(r"(?<!\.)\b(?P<method>[A-Za-z_]\w*)\s*\((?P<args>[^)]*)\)")
KEYWORDS = {
    "If",
    "For",
    "While",
    "Select",
    "Return",
    "New",
    "CType",
    "DirectCast",
    "TryCast",
    "GetType",
    "Throw",
}
VB_INTRINSICS = {
    "isnothing",
    "cstr",
    "cint",
    "cdate",
    "cdbl",
    "cdec",
    "iif",
    "format",
    "dateadd",
    "ctype",
    "directcast",
    "trycast",
    "gettype",
    "clng",
    "cbool",
    "csng",
    "cshort",
    "cbyte",
    "isdate",
    "isnumeric",
    "now",
}
DEFAULT_PROPERTY_ACCESSORS = {
    "tables",
    "rows",
    "item",
    "items",
    "attributes",
    "session",
    "querystring",
    "cells",
    "columns",
    "viewstate",
    "application",
    "cache",
    "cookies",
    "form",
    "servervariables",
}


class CallExtractor:
    """Provides the cohesive CallExtractor responsibility for this module."""
    def extract(self, path: str | Path, root: str | Path | None = None) -> dict:
        """Performs extract while preserving this module's deterministic contract."""
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        imports: list[TypeReference] = []
        instantiations: list[Instantiation] = []
        calls: list[Call] = []
        variables: dict[str, str] = {}
        current_class: str | None = None
        current_method: str | None = None

        for line_no, line in self._logical_lines(file_path):
            scan_line = self._strip_string_literals(line)
            imp = IMPORT_RE.match(line)
            if imp:
                imports.append(
                    TypeReference(
                        name=imp.group("name"),
                        alias=imp.group("alias"),
                        evidence=Evidence(file=rel, line=line_no, expression=line),
                    )
                )
                continue
            type_match = TYPE_RE.match(line)
            if type_match:
                current_class = type_match.group("name")
                continue
            if END_TYPE_RE.match(line):
                current_class = None
                variables = {}
                continue
            method = METHOD_RE.match(line)
            if method:
                current_method = method.group("name")
                variables = {}
                continue
            if END_METHOD_RE.match(line):
                current_method = None
                variables = {}
                continue

            for var_match in VAR_RE.finditer(line):
                variables[var_match.group("var").lower()] = var_match.group("type")
            for new_match in self._instantiation_matches(line):
                variable = new_match.groupdict().get("var")
                type_name = new_match.group("type")
                if variable:
                    variables[variable.lower()] = type_name
                instantiations.append(
                    Instantiation(
                        type_name=type_name,
                        variable_name=variable,
                        containing_class=current_class,
                        containing_method=current_method,
                        evidence=Evidence(rel, line_no, line, class_name=current_class, method=current_method),
                    )
                )
            seen: set[tuple[str | None, str, str]] = set()
            for call_match in QUALIFIED_CALL_RE.finditer(scan_line):
                if self._should_skip_call(call_match.group("method"), call_match.group("receiver_path")):
                    continue
                key = (self._short_receiver(call_match.group("receiver_path")), call_match.group("method"), call_match.group(0))
                seen.add(key)
                calls.append(self._call_from_match(call_match, rel, line_no, line, current_class, current_method, variables))
            for call_match in INTERNAL_CALL_RE.finditer(scan_line):
                method_name = call_match.group("method")
                prefix = scan_line[max(0, call_match.start() - 8) : call_match.start()]
                if re.search(r"\bNew\s+$", prefix, re.IGNORECASE):
                    continue
                if self._should_skip_call(method_name, None) or (None, method_name, call_match.group(0)) in seen:
                    continue
                if re.search(r"\b(Sub|Function|Class|Interface|Module|Structure)\s+" + re.escape(method_name) + r"\b", scan_line, re.IGNORECASE):
                    continue
                calls.append(self._call_from_match(call_match, rel, line_no, line, current_class, current_method, variables))
        return {
            "file": rel,
            "imports": [item.to_dict() for item in imports],
            "instantiations": [item.to_dict() for item in instantiations],
            "calls": [item.to_dict() for item in calls],
        }

    def _logical_lines(self, path: Path) -> list[tuple[int, str]]:
        result: list[tuple[int, str]] = []
        pending = ""
        start_line = 0
        for idx, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            line = self._remove_comment(raw).strip()
            if not line or line.startswith("<"):
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

    def _strip_string_literals(self, line: str) -> str:
        result = []
        in_string = False
        idx = 0
        while idx < len(line):
            char = line[idx]
            if char == '"':
                in_string = not in_string
                result.append(" ")
            elif in_string:
                result.append(" ")
            else:
                result.append(char)
            idx += 1
        return "".join(result)

    def _instantiation_matches(self, line: str):
        yielded_spans = []
        for match in ASSIGN_NEW_RE.finditer(line):
            yielded_spans.append(match.span())
            yield match
        for match in NEW_RE.finditer(line):
            if not any(match.start() < end and match.end() > start for start, end in yielded_spans):
                yield match

    def _call_from_match(self, match, rel: str, line_no: int, line: str, current_class: str | None, current_method: str | None, variables: dict[str, str]) -> Call:
        receiver_path = match.groupdict().get("receiver_path")
        receiver = self._short_receiver(receiver_path)
        call = Call(
            expression=match.group(0),
            method_name=match.group("method"),
            receiver=receiver,
            receiver_path=receiver_path,
            arguments_count=self._argument_count(match.group("args")),
            containing_class=current_class,
            containing_method=current_method,
            evidence=Evidence(rel, line_no, line, class_name=current_class, method=current_method),
        )
        if receiver and receiver.lower() in variables:
            call.candidates.append(variables[receiver.lower()])
        return call

    def _short_receiver(self, receiver_path: str | None) -> str | None:
        if not receiver_path:
            return None
        return receiver_path.split(".")[-1]

    def _should_skip_call(self, method_name: str, receiver_path: str | None) -> bool:
        method = method_name.lower()
        if method_name in KEYWORDS or method in VB_INTRINSICS:
            return True
        if method in DEFAULT_PROPERTY_ACCESSORS:
            return True
        if receiver_path and receiver_path.split(".")[-1].lower() in DEFAULT_PROPERTY_ACCESSORS:
            return True
        return False

    def _argument_count(self, args: str) -> int:
        value = args.strip()
        if not value:
            return 0
        return len([part for part in value.split(",") if part.strip()])
