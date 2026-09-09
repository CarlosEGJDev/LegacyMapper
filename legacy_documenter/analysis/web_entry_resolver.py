from pathlib import Path

from legacy_documenter.models import Dependency, EntryPoint, EventBinding


class WebEntryResolver:
    def resolve(
        self,
        webforms: list[dict],
        symbols: list[dict],
        web_events: list[dict],
        calls: list[dict],
    ) -> tuple[list[dict], list[dict], list[dict]]:
        symbols_by_file = self._symbols_by_file(symbols)
        methods_by_file_name = self._methods_by_file_name(web_events)
        calls_by_method = self._calls_by_method(calls)
        bindings: dict[tuple, dict] = {}
        entry_points: dict[tuple, dict] = {}
        dependencies: dict[tuple, dict] = {}

        for form in webforms:
            code_file = form.get("codebehind") or form.get("codefile")
            code_path = self._resolve_code_path(form["path"], code_file) if code_file else None
            class_symbol = self._resolve_class(form, code_path, symbols_by_file)
            class_name = self._class_name(class_symbol, form)
            project = class_symbol.get("project_path") if class_symbol else None
            handlers = methods_by_file_name.get(self._norm(code_path), []) if code_path else []
            handlers_by_name = {}
            for handler in handlers:
                handlers_by_name.setdefault(handler["name"].lower(), []).append(handler)

            for handler in handlers:
                for event_handler in handler.get("handlers", []):
                    self._add_binding_and_entry(
                        form,
                        event_handler,
                        class_name,
                        project,
                        handlers_by_name,
                        calls_by_method,
                        bindings,
                        entry_points,
                        dependencies,
                    )

            for markup_event in form.get("markup_events", []):
                self._add_binding_and_entry(
                    form,
                    markup_event,
                    class_name,
                    project,
                    handlers_by_name,
                    calls_by_method,
                    bindings,
                    entry_points,
                    dependencies,
                )

        return list(entry_points.values()), list(bindings.values()), list(dependencies.values())

    def _add_binding_and_entry(
        self,
        form: dict,
        event_data: dict,
        class_name: str | None,
        project: str | None,
        handlers_by_name: dict[str, list[dict]],
        calls_by_method: dict[tuple, list[dict]],
        bindings: dict[tuple, dict],
        entry_points: dict[tuple, dict],
        dependencies: dict[tuple, dict],
    ) -> None:
        handler_name = event_data.get("handler") or event_data.get("name")
        matches = handlers_by_name.get((handler_name or "").lower(), [])
        confidence = "confirmed" if class_name and len(matches) == 1 else "unresolved"
        handler_method = f"{class_name}.{handler_name}" if confidence == "confirmed" else None
        evidence = {
            "file": event_data.get("file") or form["path"],
            "line": event_data.get("line"),
            "expression": event_data.get("evidence"),
            "project": project,
            "class_name": class_name,
            "method": handler_name,
        }
        event_id = self._event_id(form["path"], event_data.get("control"), event_data.get("event"))
        binding_id = self._stable_id("EVB", form["path"], event_data.get("control"), event_data.get("event"), handler_name)
        binding = EventBinding(
            id=binding_id,
            webform=form["path"],
            control=event_data.get("control"),
            control_type=event_data.get("control_type"),
            event=event_data.get("event"),
            handler=handler_name,
            class_name=class_name,
            project=project,
            confidence=confidence,
            evidence=[evidence],
        ).to_dict()
        self._merge(bindings, (form["path"], event_data.get("control"), event_data.get("event"), handler_name), binding)
        entry_type = "web_lifecycle" if event_data.get("event") in {"Load", "Init", "PreRender"} and event_data.get("control") in {"Me", "MyBase", None} else "web_event"
        outgoing = calls_by_method.get((evidence["file"], class_name, handler_name), []) if confidence == "confirmed" else []
        entry = EntryPoint(
            id=self._stable_id("EP", form["path"], event_data.get("control"), event_data.get("event"), handler_name),
            type=entry_type,
            webform=form["path"],
            control=event_data.get("control"),
            event=event_data.get("event"),
            handler=handler_name,
            class_name=class_name,
            project=project,
            confidence=confidence,
            evidence=[evidence],
            handler_method=handler_method,
            outgoing_calls=outgoing,
        ).to_dict()
        self._merge(entry_points, (form["path"], event_data.get("control"), event_data.get("event"), handler_name), entry)
        self._add_dependency(dependencies, form["path"], event_id, "WebForm -> Event", form["path"], event_data.get("evidence") or "", confidence)
        self._add_dependency(dependencies, event_id, handler_name or "", "Event -> Handler", form["path"], event_data.get("evidence") or "", confidence)
        if handler_method:
            self._add_dependency(dependencies, handler_name or "", handler_method, "Handler -> Method", form["path"], event_data.get("evidence") or "", confidence)

    def _symbols_by_file(self, symbols: list[dict]) -> dict[str, list[dict]]:
        result: dict[str, list[dict]] = {}
        for symbol in symbols:
            result.setdefault(self._norm(symbol.get("file")), []).append(symbol)
        return result

    def _methods_by_file_name(self, web_events: list[dict]) -> dict[str, list[dict]]:
        result: dict[str, list[dict]] = {}
        for item in web_events:
            handlers = item.get("handlers", [])
            methods = []
            for method in item.get("methods", []):
                methods.append({**method, "handlers": [h for h in handlers if h.get("name") == method.get("name")]})
            result[self._norm(item.get("file"))] = methods
        return result

    def _calls_by_method(self, calls: list[dict]) -> dict[tuple, list[dict]]:
        result: dict[tuple, list[dict]] = {}
        for item in calls:
            file_name = item.get("file")
            for call in item.get("calls", []):
                key = (file_name, call.get("containing_class"), call.get("containing_method"))
                result.setdefault(key, []).append(
                    {
                        "expression": call.get("expression"),
                        "method_name": call.get("method_name"),
                        "receiver": call.get("receiver"),
                        "receiver_path": call.get("receiver_path"),
                        "resolved_target": call.get("resolved_target"),
                        "confidence": call.get("confidence"),
                        "line": (call.get("evidence") or {}).get("line"),
                    }
                )
        return result

    def _resolve_class(self, form: dict, code_path: str | None, symbols_by_file: dict[str, list[dict]]) -> dict | None:
        candidates = symbols_by_file.get(self._norm(code_path), []) if code_path else []
        inherited = form.get("inherits")
        if inherited:
            matched = [symbol for symbol in candidates if inherited.endswith(symbol.get("name", "")) or inherited == self._full_name(symbol)]
            if len(matched) == 1:
                return matched[0]
        class_candidates = [symbol for symbol in candidates if symbol.get("kind") == "class"]
        return class_candidates[0] if len(class_candidates) == 1 else None

    def _resolve_code_path(self, form_path: str, code_file: str | None) -> str | None:
        if not code_file:
            return None
        return str(Path(form_path).parent / code_file) if str(Path(form_path).parent) != "." else code_file

    def _class_name(self, symbol: dict | None, form: dict) -> str | None:
        if symbol:
            return symbol.get("name")
        inherited = form.get("inherits")
        return inherited.split(".")[-1] if inherited else None

    def _full_name(self, symbol: dict) -> str:
        namespace = symbol.get("effective_namespace") or symbol.get("namespace")
        return f"{namespace}.{symbol['name']}" if namespace else symbol["name"]

    def _event_id(self, webform: str, control: str | None, event: str | None) -> str:
        return f"{webform}::{control or '<page>'}.{event}"

    def _stable_id(self, prefix: str, *parts: object) -> str:
        raw = "|".join("" if part is None else str(part) for part in parts)
        value = 0
        for char in raw:
            value = (value * 33 + ord(char)) % 1000000007
        return f"{prefix}-{value:010d}"

    def _merge(self, bucket: dict[tuple, dict], key: tuple, item: dict) -> None:
        if key not in bucket:
            bucket[key] = item
            return
        existing = bucket[key]
        for evidence in item.get("evidence", []):
            if evidence not in existing["evidence"]:
                existing["evidence"].append(evidence)
        if existing.get("confidence") != "confirmed" and item.get("confidence") == "confirmed":
            existing.update(item)

    def _add_dependency(self, bucket: dict[tuple, dict], source: str, target: str, dependency_type: str, source_file: str, evidence: str, confidence: str) -> None:
        key = (source, target, dependency_type, source_file, confidence)
        if key not in bucket:
            data = Dependency(source, target, dependency_type, source_file, evidence, confidence).to_dict()
            data["evidence_samples"] = [evidence] if evidence else []
            data["evidence_count"] = 1
            bucket[key] = data
            return
        bucket[key]["evidence_count"] += 1
        samples = bucket[key].setdefault("evidence_samples", [])
        if evidence and evidence not in samples and len(samples) < 5:
            samples.append(evidence)

    def _norm(self, value: str | None) -> str:
        return (value or "").replace("\\", "/").strip("./").lower()
