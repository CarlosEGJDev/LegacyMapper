import re
from pathlib import Path

from legacy_documenter.utils import sanitize_text


TYPE_RE = re.compile(r"^\s*(?:Public|Private|Protected|Friend|Partial|MustInherit|NotInheritable|\s)+\s*(?:Class|Module|Structure)\s+(?P<name>[A-Za-z_]\w*)", re.IGNORECASE)
END_TYPE_RE = re.compile(r"^\s*End\s+(Class|Module|Structure)\b", re.IGNORECASE)
METHOD_RE = re.compile(r"^\s*(?:<[^>]+>\s*)?(?:(?:Public|Private|Protected Friend|Protected|Friend|Shared|Overrides|Overloads|MustOverride|Async|Static)\s+)*(?:Sub|Function)\s+(?P<name>[A-Za-z_]\w*)\s*(?:\((?P<params>.*)\))?", re.IGNORECASE)
END_METHOD_RE = re.compile(r"^\s*End\s+(Sub|Function)\b", re.IGNORECASE)
VAR_RE = re.compile(r"\bDim\s+(?P<var>[A-Za-z_]\w*)\s+As\s+(?:New\s+)?(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
STRING_ASSIGN_RE = re.compile(r"\b(?:Dim\s+)?(?P<var>[A-Za-z_]\w*)\s*(?:As\s+String\s*)?=\s*(?P<expr>.+)", re.IGNORECASE)
FIELD_RE = re.compile(r"^\s*(?:Public|Private|Protected Friend|Protected|Friend|Dim)\s+(?P<var>[A-Za-z_]\w*)\s+As\s+(?:New\s+)?(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
PARAM_RE = re.compile(r"\b(?:ByRef|ByVal|Optional|ParamArray)?\s*(?P<var>[A-Za-z_]\w*)\s+As\s+(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
NEW_ASSIGN_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\s*=\s*New\s+(?P<type>[A-Za-z_][\w.]*)", re.IGNORECASE)
COMMAND_NEW_RE = re.compile(r"\b(?:Dim\s+)?(?P<var>[A-Za-z_]\w*)\s*(?:As\s+New\s+(?P<type1>[A-Za-z_][\w.]*Command)|As\s+(?P<type2>[A-Za-z_][\w.]*Command)\s*=\s*New\s+[A-Za-z_][\w.]*Command|=\s*New\s+(?P<type3>[A-Za-z_][\w.]*Command)|New\s+(?P<type4>[A-Za-z_][\w.]*Command))\s*\((?P<args>.*)\)", re.IGNORECASE)
ADAPTER_NEW_RE = re.compile(r"\b(?:Dim\s+)?(?P<var>[A-Za-z_]\w*)\s*(?:As\s+New\s+(?P<type1>[A-Za-z_][\w.]*DataAdapter)|As\s+(?P<type2>[A-Za-z_][\w.]*DataAdapter)\s*=\s*New\s+[A-Za-z_][\w.]*DataAdapter|=\s*New\s+(?P<type3>[A-Za-z_][\w.]*DataAdapter)|New\s+(?P<type4>[A-Za-z_][\w.]*DataAdapter))\s*\((?P<args>.*)\)", re.IGNORECASE)
COMMAND_TEXT_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.CommandText\s*=\s*(?P<expr>.+)", re.IGNORECASE)
COMMAND_TYPE_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.CommandType\s*=\s*CommandType\.(?P<type>StoredProcedure|Text)", re.IGNORECASE)
EXECUTE_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.(?P<method>ExecuteNonQuery|ExecuteReader|ExecuteScalar)\s*\(", re.IGNORECASE)
FILL_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.Fill\s*\(", re.IGNORECASE)
PARAM_ADD_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.Parameters\.(?P<method>Add|AddWithValue)\s*\((?P<args>.*)\)", re.IGNORECASE)
ORACLE_PARAM_RE = re.compile(r"\b(?:Dim\s+)?(?P<var>[A-Za-z_]\w*)?\s*(?:As\s+OracleParameter\s*=\s*)?New\s+OracleParameter\s*\((?P<args>.*)\)", re.IGNORECASE)
DIRECTION_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.Direction\s*=\s*ParameterDirection\.(?P<direction>[A-Za-z_]\w*)", re.IGNORECASE)
WRAPPER_EXEC_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.(?P<method>ExecProc|ExecProcDS)\s*\((?P<args>.*)\)", re.IGNORECASE)
TRANSACTION_RE = re.compile(r"\b(?P<var>[A-Za-z_]\w*)\.(?P<method>BeginTransaction|BeginTrans|Commit|Rollback)\s*\(", re.IGNORECASE)
CONNECTION_NAME_RE = re.compile(r'ConnectionStrings\s*\(\s*"(?P<name>[^"]+)"\s*\)', re.IGNORECASE)
SQL_RE = re.compile(r"^\s*(SELECT|INSERT|UPDATE|DELETE|MERGE)\b", re.IGNORECASE)


class DatabaseExtractor:
    def extract(self, path: str | Path, root: str | Path | None = None) -> dict:
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        current_class: str | None = None
        current_method: str | None = None
        variables: dict[str, str] = {}
        class_fields: dict[str, str] = {}
        commands: dict[str, dict] = {}
        adapters: dict[str, dict] = {}
        parameters: dict[str, dict] = {}
        string_values: dict[str, dict] = {}
        operations: list[dict] = []
        data_parameters: list[dict] = []

        for line_no, line in self._logical_lines(file_path):
            scan_line = self._strip_string_literals(line)
            type_match = TYPE_RE.match(line)
            if type_match:
                current_class = type_match.group("name")
                class_fields = {}
                continue
            if END_TYPE_RE.match(line):
                current_class = None
                variables = {}
                class_fields = {}
                commands = {}
                adapters = {}
                parameters = {}
                string_values = {}
                continue
            method = METHOD_RE.match(line)
            if method:
                current_method = method.group("name")
                variables = dict(class_fields)
                variables.update(self._method_parameters(method.group("params") or ""))
                commands = {}
                adapters = {}
                parameters = {}
                string_values = {}
                continue
            if END_METHOD_RE.match(line):
                current_method = None
                variables = dict(class_fields)
                commands = {}
                adapters = {}
                parameters = {}
                string_values = {}
                continue

            for match in VAR_RE.finditer(line):
                variables[match.group("var").lower()] = match.group("type")
            string_assignment = STRING_ASSIGN_RE.match(line)
            if string_assignment and '"' in string_assignment.group("expr") and not re.search(r"\bNew\s+", string_assignment.group("expr"), re.IGNORECASE):
                string_values[string_assignment.group("var").lower()] = self._text_state(string_assignment.group("expr"))
            if current_class and not current_method:
                field = FIELD_RE.match(line)
                if field:
                    class_fields[field.group("var").lower()] = field.group("type")
                    variables[field.group("var").lower()] = field.group("type")
            for match in NEW_ASSIGN_RE.finditer(line):
                variables[match.group("var").lower()] = match.group("type")

            cmd_match = COMMAND_NEW_RE.search(line)
            if cmd_match:
                var = cmd_match.group("var")
                command_type_name = self._matched_type(cmd_match) or "OracleCommand"
                variables[var.lower()] = command_type_name
                commands[var.lower()] = self._command_state(var, cmd_match.group("args"), rel, line_no, line, current_class, current_method)
                operations.append(self._operation("command", "direct_provider", self._provider(command_type_name), var, commands[var.lower()], rel, line_no, line, current_class, current_method))
                continue

            adapter_match = ADAPTER_NEW_RE.search(line)
            if adapter_match:
                var = adapter_match.group("var")
                adapter_type_name = self._matched_type(adapter_match) or "OracleDataAdapter"
                variables[var.lower()] = adapter_type_name
                adapters[var.lower()] = self._command_state(var, adapter_match.group("args"), rel, line_no, line, current_class, current_method)
                operations.append(self._operation("adapter", "direct_provider", self._provider(adapter_type_name), var, adapters[var.lower()], rel, line_no, line, current_class, current_method))
                continue

            text_match = COMMAND_TEXT_RE.search(line)
            if text_match and self._is_command(text_match.group("var"), variables):
                state = commands.setdefault(text_match.group("var").lower(), self._empty_state(text_match.group("var")))
                state.update(string_values.get(text_match.group("expr").strip().lower(), self._text_state(text_match.group("expr"))))
                operations.append(self._operation("command_text", "direct_provider", self._provider(variables[text_match.group("var").lower()]), text_match.group("var"), state, rel, line_no, line, current_class, current_method))
                continue

            type_match = COMMAND_TYPE_RE.search(line)
            if type_match and self._is_command(type_match.group("var"), variables):
                state = commands.setdefault(type_match.group("var").lower(), self._empty_state(type_match.group("var")))
                state["command_type"] = type_match.group("type")
                operations.append(self._operation("command_type", "direct_provider", "Oracle", type_match.group("var"), state, rel, line_no, line, current_class, current_method))
                continue

            exec_match = EXECUTE_RE.search(scan_line)
            if exec_match and self._is_command(exec_match.group("var"), variables):
                state = commands.get(exec_match.group("var").lower(), self._empty_state(exec_match.group("var")))
                operations.append(self._operation(exec_match.group("method"), "direct_provider", self._provider(variables[exec_match.group("var").lower()]), exec_match.group("var"), state, rel, line_no, line, current_class, current_method))
                continue

            fill_match = FILL_RE.search(scan_line)
            if fill_match and self._is_adapter(fill_match.group("var"), variables):
                state = adapters.get(fill_match.group("var").lower(), self._empty_state(fill_match.group("var")))
                operations.append(self._operation("Fill", "direct_provider", self._provider(variables[fill_match.group("var").lower()]), fill_match.group("var"), state, rel, line_no, line, current_class, current_method))
                continue

            for param_match in PARAM_ADD_RE.finditer(line):
                if not self._is_command(param_match.group("var"), variables):
                    continue
                param = self._parameter(param_match.group("var"), param_match.group("args"), rel, line_no, line, current_class, current_method)
                data_parameters.append(param)
            oracle_param = ORACLE_PARAM_RE.search(line)
            if oracle_param and "OracleParameter" in line:
                var = oracle_param.group("var")
                param = self._parameter(None, oracle_param.group("args"), rel, line_no, line, current_class, current_method, variable=var)
                if var:
                    parameters[var.lower()] = param
                data_parameters.append(param)
            direction = DIRECTION_RE.search(line)
            if direction and direction.group("var").lower() in parameters:
                parameters[direction.group("var").lower()]["direction"] = direction.group("direction")

            wrapper = WRAPPER_EXEC_RE.search(line)
            if wrapper and self._is_oraconn(wrapper.group("var"), variables):
                state = self._text_state(self._first_arg(wrapper.group("args")) or "")
                op = self._operation(wrapper.group("method"), "repository_wrapper", "OraConn", wrapper.group("var"), state, rel, line_no, line, current_class, current_method)
                op["command_type"] = "StoredProcedure" if op.get("stored_procedure") else "unresolved"
                operations.append(op)
                data_parameters.extend(self._wrapper_parameters(wrapper.group("var"), wrapper.group("method"), wrapper.group("args"), rel, line_no, line, current_class, current_method))
                continue

            tx = TRANSACTION_RE.search(scan_line)
            if tx and (self._is_command(tx.group("var"), variables) or self._is_oraconn(tx.group("var"), variables)):
                operations.append(self._operation(tx.group("method"), "repository_wrapper" if self._is_oraconn(tx.group("var"), variables) else "direct_provider", "OraConn" if self._is_oraconn(tx.group("var"), variables) else "Oracle", tx.group("var"), self._empty_state(tx.group("var")), rel, line_no, line, current_class, current_method))

        return {"file": rel, "operations": operations, "parameters": data_parameters}

    def _operation(self, kind: str, access_kind: str, provider: str, variable: str | None, state: dict, rel: str, line_no: int, line: str, class_name: str | None, method: str | None) -> dict:
        command_type = state.get("command_type")
        stored = state.get("stored_procedure")
        sql_kind = state.get("sql_operation")
        if not command_type:
            command_type = "StoredProcedure" if stored else "Text" if sql_kind else "unresolved"
        confidence = "confirmed" if stored or sql_kind or kind in {"BeginTransaction", "BeginTrans", "Commit", "Rollback"} else "unresolved"
        return {
            "id": None,
            "operation_kind": self._operation_kind(kind, stored, sql_kind),
            "access_kind": access_kind,
            "provider": provider,
            "command_variable": variable,
            "command_type": command_type,
            "command_text": state.get("command_text"),
            "stored_procedure": stored,
            "sql_operation": sql_kind,
            "connection": state.get("connection"),
            "connection_name": state.get("connection_name"),
            "dynamic_sql": state.get("dynamic_sql", False),
            "class": class_name,
            "method": method,
            "project": None,
            "confidence": confidence,
            "evidence": [{"file": rel, "line": line_no, "expression": self._sanitize(line), "class_name": class_name, "method": method, "project": None}],
        }

    def _operation_kind(self, kind: str, stored: str | None, sql_kind: str | None) -> str:
        if kind in {"BeginTransaction", "BeginTrans", "Commit", "Rollback"}:
            return "transaction"
        if kind == "Fill":
            return "fill"
        if stored:
            return "stored_procedure"
        if sql_kind:
            return "sql"
        return "execute" if kind.startswith("Execute") else "command"

    def _command_state(self, var: str, args: str, rel: str, line_no: int, line: str, class_name: str | None, method: str | None) -> dict:
        parts = self._split_args(args)
        state = self._empty_state(var)
        if parts:
            state.update(self._text_state(parts[0]))
        if len(parts) > 1:
            state["connection"] = parts[1].strip()
            state["connection_name"] = self._connection_name(parts[1])
        return state

    def _empty_state(self, var: str | None) -> dict:
        return {"command_variable": var, "command_type": None, "command_text": None, "stored_procedure": None, "sql_operation": None, "connection": None, "connection_name": None, "dynamic_sql": False}

    def _text_state(self, expr: str) -> dict:
        literal = self._literal(expr)
        text = literal if literal is not None else self._sanitize(expr.strip())
        sql_kind = self._sql_kind(literal)
        dynamic = literal is None and any(f'"{kw}' in expr.upper() for kw in ("SELECT", "INSERT", "UPDATE", "DELETE", "MERGE"))
        if not sql_kind and dynamic:
            sql_kind = self._first_sql_keyword(expr)
        stored = None if sql_kind else literal
        return {"command_text": text, "stored_procedure": stored, "sql_operation": sql_kind, "dynamic_sql": dynamic}

    def _parameter(self, command_var: str | None, args: str, rel: str, line_no: int, line: str, class_name: str | None, method: str | None, variable: str | None = None) -> dict:
        parts = self._split_args(args)
        name = self._literal(parts[0]) if parts else None
        return {
            "id": None,
            "command_variable": command_var,
            "variable": variable,
            "name": name,
            "direction": None,
            "db_type": parts[1].strip() if len(parts) > 1 else None,
            "data_type": parts[1].strip() if len(parts) > 1 else None,
            "size": self._explicit_size(parts),
            "source_expression": self._sanitize(parts[-1].strip()) if len(parts) > 1 else None,
            "class": class_name,
            "method": method,
            "project": None,
            "confidence": "confirmed" if name else "unresolved",
            "evidence": [{"file": rel, "line": line_no, "expression": self._sanitize(line), "class_name": class_name, "method": method, "project": None}],
        }

    def _wrapper_parameters(self, command_var: str, wrapper_method: str, args: str, rel: str, line_no: int, line: str, class_name: str | None, method: str | None) -> list[dict]:
        parts = self._split_args(args)
        if len(parts) < 2:
            return []
        raw_names = self._literal(parts[1])
        if not raw_names:
            return []
        params = []
        directions = self._csv_literal(parts[3]) if len(parts) > 3 else []
        db_types = self._csv_literal(parts[4]) if len(parts) > 4 else []
        for idx, name in enumerate([part.strip() for part in raw_names.split(",") if part.strip()]):
            param = self._parameter(command_var, f'"{name}"', rel, line_no, line, class_name, method)
            if idx < len(directions):
                param["direction"] = self._direction(directions[idx])
            if idx < len(db_types):
                param["db_type"] = db_types[idx]
                param["data_type"] = db_types[idx]
            param["wrapper"] = wrapper_method
            params.append(param)
        return params

    def _logical_lines(self, path: Path) -> list[tuple[int, str]]:
        result = []
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
        idx = 0
        while idx < len(line):
            if line[idx] == '"':
                if idx + 1 < len(line) and line[idx + 1] == '"':
                    idx += 2
                    continue
                in_string = not in_string
            if line[idx] == "'" and not in_string:
                return line[:idx]
            idx += 1
        return line

    def _strip_string_literals(self, line: str) -> str:
        result = []
        in_string = False
        idx = 0
        while idx < len(line):
            if line[idx] == '"':
                in_string = not in_string
                result.append(" ")
            elif in_string:
                result.append(" ")
            else:
                result.append(line[idx])
            idx += 1
        return "".join(result)

    def _split_args(self, args: str) -> list[str]:
        parts = []
        current = []
        depth = 0
        in_string = False
        idx = 0
        while idx < len(args):
            char = args[idx]
            if char == '"':
                in_string = not in_string
            elif not in_string:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth = max(0, depth - 1)
                elif char == "," and depth == 0:
                    parts.append("".join(current).strip())
                    current = []
                    idx += 1
                    continue
            current.append(char)
            idx += 1
        if current or args.strip():
            parts.append("".join(current).strip())
        return parts

    def _method_parameters(self, params: str) -> dict[str, str]:
        variables: dict[str, str] = {}
        for param in PARAM_RE.finditer(params):
            variables[param.group("var").lower()] = param.group("type")
        return variables

    def _matched_type(self, match) -> str | None:
        for name in ("type1", "type2", "type3", "type4"):
            value = match.groupdict().get(name)
            if value:
                return value
        return None

    def _literal(self, expr: str | None) -> str | None:
        if not expr:
            return None
        match = re.match(r'^\s*"(?P<value>(?:""|[^"])*)"\s*$', expr.strip())
        return match.group("value").replace('""', '"') if match else None

    def _sql_kind(self, text: str | None) -> str | None:
        if not text:
            return None
        match = SQL_RE.match(text)
        return match.group(1).upper() if match else None

    def _first_sql_keyword(self, expr: str) -> str | None:
        match = re.search(r'"(?:\s*)(SELECT|INSERT|UPDATE|DELETE|MERGE)\b', expr, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _first_arg(self, args: str) -> str | None:
        parts = self._split_args(args)
        return parts[0] if parts else None

    def _csv_literal(self, expr: str | None) -> list[str]:
        value = self._literal(expr)
        if not value:
            return []
        return [part.strip() for part in value.split(",")]

    def _direction(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized in {"out", "output"}:
            return "Output"
        if normalized in {"inout", "inputoutput"}:
            return "InputOutput"
        if normalized in {"return", "returnvalue"}:
            return "ReturnValue"
        return "Input" if normalized == "in" else value.strip()

    def _explicit_size(self, parts: list[str]) -> str | None:
        for part in parts[2:]:
            if re.fullmatch(r"\d+", part.strip()):
                return part.strip()
        return None

    def _connection_name(self, expr: str) -> str | None:
        match = CONNECTION_NAME_RE.search(expr)
        return match.group("name") if match else None

    def _is_command(self, var: str, variables: dict[str, str]) -> bool:
        return variables.get(var.lower(), "").lower().endswith("command")

    def _is_adapter(self, var: str, variables: dict[str, str]) -> bool:
        return variables.get(var.lower(), "").lower().endswith("dataadapter")

    def _is_oraconn(self, var: str, variables: dict[str, str]) -> bool:
        return variables.get(var.lower(), "").lower().endswith("oraconn")

    def _sanitize(self, text: str) -> str:
        return sanitize_text(text).strip()

    def _provider(self, type_name: str) -> str:
        lowered = type_name.lower()
        if "oracle" in lowered:
            return "Oracle"
        if "oledb" in lowered:
            return "OleDb"
        return type_name.rsplit(".", 1)[-1]
