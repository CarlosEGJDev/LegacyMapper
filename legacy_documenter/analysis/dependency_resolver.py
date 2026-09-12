from pathlib import Path

from legacy_documenter.models import Dependency


class DependencyResolver:
    """Provides the cohesive DependencyResolver responsibility for this module."""
    def resolve(self, solutions: list[dict], projects: list[dict], symbols: list[dict], webforms: list[dict]) -> list[Dependency]:
        """Performs resolve while preserving this module's deterministic contract."""
        deps: list[Dependency] = []
        deps.extend(self._solution_deps(solutions))
        deps.extend(self._project_deps(projects))
        deps.extend(self._symbol_deps(symbols))
        deps.extend(self._webform_deps(webforms, symbols))
        return deps

    def _solution_deps(self, solutions: list[dict]) -> list[Dependency]:
        deps = []
        for solution in solutions:
            for project in solution.get("projects", []):
                deps.append(Dependency(solution["name"], project["path"], "Solution -> Project", solution["path"], project["name"]))
        return deps

    def _project_deps(self, projects: list[dict]) -> list[Dependency]:
        deps = []
        for project in projects:
            for ref in project.get("project_references", []):
                deps.append(Dependency(project["path"], ref.get("include", ""), "Project -> Project", project["path"], str(ref)))
            for ref in project.get("assembly_references", []):
                deps.append(Dependency(project["path"], ref.get("include", ""), "Project -> DLL", project["path"], str(ref)))
            for item in project.get("compile_items", []):
                deps.append(Dependency(project["path"], item, "Project -> SourceFile", project["path"], item))
        return deps

    def _symbol_deps(self, symbols: list[dict]) -> list[Dependency]:
        deps = []
        for symbol in symbols:
            full = self._full_name(symbol)
            if symbol.get("namespace"):
                deps.append(Dependency(symbol["namespace"], full, "Namespace -> Class", symbol["file"], symbol["kind"]))
            for base in symbol.get("inherits", []):
                deps.append(Dependency(full, base, "Class -> BaseClass", symbol["file"], "Inherits " + base))
            for interface in symbol.get("implements", []):
                deps.append(Dependency(full, interface, "Class -> Interface", symbol["file"], "Implements " + interface))
        return deps

    def _webform_deps(self, webforms: list[dict], symbols: list[dict]) -> list[Dependency]:
        symbol_names = {self._full_name(symbol): symbol for symbol in symbols}
        deps = []
        for form in webforms:
            source = form["path"]
            if form.get("codebehind"):
                deps.append(Dependency(source, form["codebehind"], f"{form['kind'].upper()} -> CodeBehind", source, "CodeBehind"))
            if form.get("codefile"):
                deps.append(Dependency(source, form["codefile"], f"{form['kind'].upper()} -> CodeBehind", source, "CodeFile"))
            if form.get("master_page"):
                deps.append(Dependency(source, form["master_page"], "ASPX -> MasterPage", source, "MasterPageFile"))
            for reg in form.get("registers", []):
                normalized = self._normalized_attrs(reg)
                if normalized.get("src"):
                    deps.append(Dependency(source, normalized["src"], f"{form['kind'].upper()} -> ASCX", source, "Register Src"))
                elif normalized.get("namespace"):
                    target = normalized["namespace"] + ("," + normalized.get("assembly", "") if normalized.get("assembly") else "")
                    deps.append(Dependency(source, target, "WebForm -> RegisteredNamespace", source, "Register Namespace/Assembly"))
            for script in form.get("scripts", []):
                deps.append(Dependency(source, script, "WebForm -> JavaScript", source, "script src"))
            for css in form.get("stylesheets", []):
                deps.append(Dependency(source, css, "WebForm -> CSS", source, "stylesheet href"))
            inherited = form.get("inherits")
            if inherited:
                confidence = "confirmed" if inherited in symbol_names or inherited.split(".")[-1] in {s["name"] for s in symbols} else "unresolved"
                deps.append(Dependency(source, inherited, "WebForm -> VBClass", source, "Inherits", confidence))
        return deps

    def _full_name(self, symbol: dict) -> str:
        namespace = symbol.get("effective_namespace") or symbol.get("namespace")
        return f"{namespace}.{symbol['name']}" if namespace else symbol["name"]

    def _normalized_attrs(self, attrs: dict) -> dict:
        normalized = dict(attrs.get("_normalized", {}))
        normalized.update({key.lower(): value for key, value in attrs.items() if not key.startswith("_")})
        return normalized
