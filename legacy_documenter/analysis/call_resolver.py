from collections import defaultdict

from legacy_documenter.models import Dependency


class CallResolver:
    def resolve(self, call_indexes: list[dict], symbols: list[dict]) -> tuple[list[dict], list[dict]]:
        class_index = self._class_index(symbols)
        method_index = self._method_index(symbols)
        functional_dependencies: dict[tuple, dict] = {}

        for file_calls in call_indexes:
            for instantiation in file_calls.get("instantiations", []):
                resolved = self._resolve_type(instantiation["type_name"], class_index)
                instantiation["resolved_type"] = resolved["target"]
                instantiation["confidence"] = resolved["confidence"]
                source_method = self._method_id(instantiation.get("containing_class"), instantiation.get("containing_method"))
                self._add_dependency(
                    functional_dependencies,
                    source=source_method,
                    target=resolved["target"] or instantiation["type_name"],
                    dependency_type="Method -> InstantiatesClass",
                    source_file=instantiation["evidence"]["file"],
                    evidence=instantiation["evidence"]["expression"] or "",
                    confidence=resolved["confidence"],
                )
                if instantiation.get("containing_class"):
                    self._add_dependency(
                        functional_dependencies,
                        source=instantiation["containing_class"],
                        target=resolved["target"] or instantiation["type_name"],
                        dependency_type="Class -> UsesClass",
                        source_file=instantiation["evidence"]["file"],
                        evidence=instantiation["evidence"]["expression"] or "",
                        confidence=resolved["confidence"],
                    )
            variable_types = {
                inst.get("variable_name", "").lower(): inst.get("resolved_type") or inst.get("type_name")
                for inst in file_calls.get("instantiations", [])
                if inst.get("variable_name")
            }
            for call in file_calls.get("calls", []):
                resolution = self._resolve_call(call, variable_types, class_index, method_index)
                call["resolved_target"] = resolution["target"]
                call["resolved_project"] = resolution.get("project")
                call["confidence"] = resolution["confidence"]
                call["candidates"] = resolution["candidates"]
                self._add_dependency(
                    functional_dependencies,
                    source=self._method_id(call.get("containing_class"), call.get("containing_method")),
                    target=resolution["target"] or call["method_name"],
                    dependency_type="Method -> Method",
                    source_file=call["evidence"]["file"],
                    evidence=call["evidence"]["expression"] or call["expression"],
                    confidence=resolution["confidence"],
                )
        return call_indexes, list(functional_dependencies.values())

    def _class_index(self, symbols: list[dict]) -> dict[str, list[dict]]:
        index: dict[str, list[dict]] = defaultdict(list)
        for symbol in symbols:
            if symbol.get("kind") not in {"class", "module"}:
                continue
            names = {symbol["name"].lower()}
            full = self._full_name(symbol)
            if full:
                names.add(full.lower())
            for name in names:
                if symbol not in index[name]:
                    index[name].append(symbol)
        return index

    def _method_index(self, symbols: list[dict]) -> dict[tuple[str, str], list[dict]]:
        index: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for symbol in symbols:
            class_name = symbol.get("name", "").lower()
            full = (self._full_name(symbol) or "").lower()
            for member in symbol.get("members", []):
                if member.get("kind") in {"sub", "function"}:
                    if symbol not in index[(class_name, member["name"].lower())]:
                        index[(class_name, member["name"].lower())].append(symbol)
                    if full:
                        if symbol not in index[(full, member["name"].lower())]:
                            index[(full, member["name"].lower())].append(symbol)
        return index

    def _resolve_type(self, type_name: str, class_index: dict[str, list[dict]]) -> dict:
        candidates = class_index.get(type_name.lower(), [])
        if len(candidates) == 1:
            return {"target": self._full_name(candidates[0]), "confidence": "confirmed", "candidates": [self._full_name(candidates[0])]}
        return {"target": None, "confidence": "unresolved", "candidates": [self._full_name(item) for item in candidates]}

    def _resolve_call(self, call: dict, variable_types: dict[str, str], class_index: dict[str, list[dict]], method_index: dict[tuple[str, str], list[dict]]) -> dict:
        receiver = call.get("receiver")
        method = call["method_name"].lower()
        if receiver:
            if receiver.lower() in {"me", "mybase"} and call.get("containing_class"):
                return self._resolve_method(call["containing_class"], method, method_index)
            receiver_path = call.get("receiver_path") or receiver
            receiver_type = variable_types.get(receiver.lower()) or (call.get("candidates") or [None])[0] or receiver_path
            resolved = self._resolve_method(receiver_type, method, method_index)
            if resolved["confidence"] == "unresolved" and receiver_path != receiver:
                resolved = self._resolve_method(receiver, method, method_index)
            return resolved
        if call.get("containing_class"):
            return self._resolve_method(call["containing_class"], method, method_index)
        return {"target": None, "project": None, "confidence": "unresolved", "candidates": []}

    def _resolve_method(self, class_name: str, method: str, method_index: dict[tuple[str, str], list[dict]]) -> dict:
        candidates = method_index.get((class_name.lower(), method), [])
        targets = [f"{self._full_name(item)}.{method}" for item in candidates]
        if len(candidates) == 1:
            return {"target": targets[0], "project": candidates[0].get("project_path"), "confidence": "confirmed", "candidates": targets}
        return {"target": None, "project": None, "confidence": "unresolved", "candidates": targets}

    def _full_name(self, symbol: dict) -> str:
        namespace = symbol.get("effective_namespace") or symbol.get("namespace")
        return f"{namespace}.{symbol['name']}" if namespace else symbol["name"]

    def _method_id(self, class_name: str | None, method: str | None) -> str:
        if class_name and method:
            return f"{class_name}.{method}"
        return method or class_name or "<unknown>"

    def _add_dependency(
        self,
        dependencies: dict[tuple, dict],
        source: str,
        target: str,
        dependency_type: str,
        source_file: str,
        evidence: str,
        confidence: str,
    ) -> None:
        key = (source, target, dependency_type, source_file, confidence)
        if key not in dependencies:
            data = Dependency(source, target, dependency_type, source_file, evidence, confidence).to_dict()
            data["evidence_samples"] = [evidence] if evidence else []
            data["evidence_count"] = 1
            dependencies[key] = data
            return
        current = dependencies[key]
        current["evidence_count"] += 1
        samples = current.setdefault("evidence_samples", [])
        if evidence and evidence not in samples and len(samples) < 5:
            samples.append(evidence)
