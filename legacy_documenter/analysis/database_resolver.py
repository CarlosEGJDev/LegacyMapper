from pathlib import Path

from legacy_documenter.models import Dependency


class DatabaseResolver:
    def resolve(self, data_access_indexes: list[dict], projects: list[dict]) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
        project_by_file = self._project_by_file(projects)
        operations: dict[tuple, dict] = {}
        stored_procedures: dict[str, dict] = {}
        sql_operations: dict[tuple, dict] = {}
        parameters: dict[tuple, dict] = {}
        dependencies: dict[tuple, dict] = {}
        command_operation_ids: dict[tuple, str] = {}

        for file_index in data_access_indexes:
            file_name = file_index.get("file")
            project = project_by_file.get(self._norm(file_name))
            for operation in file_index.get("operations", []):
                operation = self._with_project(operation, project)
                key = self._operation_key(operation)
                operation["id"] = self._stable_id("DAO", *key)
                self._merge(operations, key, operation)
                method_id = self._method_id(operation)
                if method_id:
                    dep_type = "Method -> TransactionOperation" if operation.get("operation_kind") == "transaction" else "Method -> DataAccessOperation"
                    self._add_dependency(dependencies, method_id, operation["id"], dep_type, file_name, self._evidence_text(operation), operation.get("confidence", "unresolved"))
                if operation.get("command_variable") and operation.get("operation_kind") != "transaction":
                    command_key = (operation.get("project"), operation.get("class"), operation.get("method"), operation.get("command_variable"))
                    command_operation_ids.setdefault(command_key, operation["id"])
                if operation.get("stored_procedure"):
                    proc_name = operation["stored_procedure"]
                    proc_id = self._stable_id("SP", proc_name)
                    stored_procedures.setdefault(
                        proc_id,
                        {
                            "id": proc_id,
                            "name": proc_name,
                            "package": proc_name.rsplit(".", 1)[0] if "." in proc_name else None,
                            "procedure": proc_name.rsplit(".", 1)[-1],
                            "confidence": operation.get("confidence", "confirmed"),
                            "evidence": [],
                        },
                    )
                    self._extend_evidence(stored_procedures[proc_id], operation.get("evidence", []))
                    self._add_dependency(dependencies, operation["id"], proc_id, "DataAccessOperation -> StoredProcedure", file_name, self._evidence_text(operation), operation.get("confidence", "confirmed"))
                if operation.get("sql_operation"):
                    sql_key = (operation.get("sql_operation"), operation.get("command_text"), operation.get("dynamic_sql"))
                    sql_id = self._stable_id("SQL", *sql_key)
                    sql_operations.setdefault(
                        sql_key,
                        {
                            "id": sql_id,
                            "operation": operation.get("sql_operation"),
                            "command_text": operation.get("command_text"),
                            "dynamic_sql": operation.get("dynamic_sql", False),
                            "confidence": operation.get("confidence", "confirmed"),
                            "evidence": [],
                        },
                    )
                    self._extend_evidence(sql_operations[sql_key], operation.get("evidence", []))
                    self._add_dependency(dependencies, operation["id"], sql_id, "DataAccessOperation -> SQL", file_name, self._evidence_text(operation), operation.get("confidence", "confirmed"))
                if operation.get("connection") or operation.get("connection_name"):
                    connection_id = self._stable_id("CONN", operation.get("connection_name") or operation.get("connection"))
                    self._add_dependency(dependencies, operation["id"], connection_id, "DataAccessOperation -> Connection", file_name, self._evidence_text(operation), "confirmed")

            for parameter in file_index.get("parameters", []):
                parameter = self._with_project(parameter, project)
                key = (parameter.get("project"), parameter.get("class"), parameter.get("method"), parameter.get("command_variable"), parameter.get("name"), parameter.get("source_expression"))
                parameter["id"] = self._stable_id("PAR", *key)
                self._merge(parameters, key, parameter)
                command_key = (parameter.get("project"), parameter.get("class"), parameter.get("method"), parameter.get("command_variable"))
                operation_id = command_operation_ids.get(command_key)
                if operation_id:
                    self._add_dependency(dependencies, operation_id, parameter["id"], "DataAccessOperation -> Parameter", file_name, self._evidence_text(parameter), parameter.get("confidence", "unresolved"))

        return list(operations.values()), list(stored_procedures.values()), list(sql_operations.values()), list(parameters.values()), list(dependencies.values())

    def _project_by_file(self, projects: list[dict]) -> dict[str, str]:
        result: dict[str, str] = {}
        for project in projects:
            project_dir = Path(project["path"]).parent
            for item in project.get("compile_items", []):
                result[self._norm(str(project_dir / item))] = project.get("path")
        return result

    def _with_project(self, item: dict, project: str | None) -> dict:
        item = {**item, "project": project}
        for evidence in item.get("evidence", []):
            evidence["project"] = project
        return item

    def _operation_key(self, operation: dict) -> tuple:
        return (
            operation.get("project"),
            operation.get("class"),
            operation.get("method"),
            operation.get("operation_kind"),
            operation.get("access_kind"),
            operation.get("provider"),
            operation.get("command_variable"),
            operation.get("command_type"),
            operation.get("stored_procedure"),
            operation.get("sql_operation"),
            operation.get("command_text"),
        )

    def _method_id(self, item: dict) -> str | None:
        if not item.get("class") or not item.get("method"):
            return None
        return f"{item.get('project') or '<unknown>'}::{item['class']}.{item['method']}"

    def _merge(self, bucket: dict[tuple, dict], key: tuple, item: dict) -> None:
        if key not in bucket:
            item["evidence_count"] = len(item.get("evidence", [])) or 1
            bucket[key] = item
            return
        bucket[key]["evidence_count"] += len(item.get("evidence", [])) or 1
        self._extend_evidence(bucket[key], item.get("evidence", []))
        if bucket[key].get("confidence") != "confirmed" and item.get("confidence") == "confirmed":
            bucket[key]["confidence"] = "confirmed"

    def _extend_evidence(self, item: dict, evidence_items: list[dict]) -> None:
        evidence = item.setdefault("evidence", [])
        for sample in evidence_items:
            if sample not in evidence and len(evidence) < 10:
                evidence.append(sample)

    def _add_dependency(self, bucket: dict[tuple, dict], source: str, target: str, dependency_type: str, source_file: str | None, evidence: str, confidence: str) -> None:
        key = (source, target, dependency_type, source_file, confidence)
        if key not in bucket:
            data = Dependency(source, target, dependency_type, source_file or "", evidence, confidence).to_dict()
            data["evidence_samples"] = [evidence] if evidence else []
            data["evidence_count"] = 1
            bucket[key] = data
            return
        bucket[key]["evidence_count"] += 1
        samples = bucket[key].setdefault("evidence_samples", [])
        if evidence and evidence not in samples and len(samples) < 5:
            samples.append(evidence)

    def _evidence_text(self, item: dict) -> str:
        evidence = item.get("evidence") or []
        return evidence[0].get("expression", "") if evidence else ""

    def _stable_id(self, prefix: str, *parts: object) -> str:
        raw = "|".join("" if part is None else str(part) for part in parts)
        value = 0
        for char in raw:
            value = (value * 33 + ord(char)) % 1000000007
        return f"{prefix}-{value:010d}"

    def _norm(self, value: str | None) -> str:
        return (value or "").replace("\\", "/").strip("./").lower()
