from pathlib import Path
import json


class ContextBuilder:
    def build_project_contexts(self, output_dir: str | Path, indexes: dict) -> list[dict]:
        contexts = []
        symbols_by_file = indexes.get("symbols", [])
        for project in indexes.get("projects", []):
            classes = [s for s in symbols_by_file if s.get("file", "").replace("/", "\\") in project.get("compile_items", [])]
            context = {
                "project": project.get("name"),
                "technology": "ASP.NET Web Forms" if any(p.endswith((".aspx", ".ascx")) for p in project.get("content_items", [])) else ".NET Framework",
                "language": "VB.NET",
                "target_framework": project.get("target_framework"),
                "classes": len([s for s in classes if s.get("kind") == "class"]),
                "aspx": len([p for p in project.get("content_items", []) if p.lower().endswith(".aspx")]),
                "ascx": len([p for p in project.get("content_items", []) if p.lower().endswith(".ascx")]),
                "namespaces": sorted({s.get("namespace") for s in classes if s.get("namespace")}),
                "dependencies": [
                    f"{d['source']} -> {d['target']}"
                    for d in indexes.get("dependencies", [])
                    if d["source"] == project.get("path")
                ],
            }
            contexts.append(context)
        context_dir = Path(output_dir) / "context"
        context_dir.mkdir(parents=True, exist_ok=True)
        (context_dir / "projects.json").write_text(json.dumps(contexts, indent=2, ensure_ascii=False), encoding="utf-8")
        return contexts
