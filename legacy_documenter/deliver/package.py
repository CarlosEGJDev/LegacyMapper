"""Final human package (post-V5 H4): HTML site + PDFs composed from the H2 narrative and the H3 visuals of a persisted baseline.

Order (the order is the contract): baseline gate (H1) -> H2 documentation + H3 visual package (generated from the persisted
baseline into a staging directory, or consumed from existing directories) -> block model -> HTML/PDF -> manifest. Nothing scans a
source tree, rebuilds Evidence or resolves an AI provider; the package is a pure function of the persisted baseline and options.
"""
from __future__ import annotations

import hashlib
import json
import posixpath
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from legacy_documenter.documentation_v52.audience import load_knowledge_overlay
from legacy_documenter.documentation_v52.engine import AUDIENCE_PROFILES, generate_documentation_v52
from legacy_documenter.orchestration.ai_only import BaselineInvalid
from legacy_documenter.visuals.model import KINDS
from legacy_documenter.visuals.package import generate_visuals, load_context, load_knowledge_refs, representative_flow

from . import html as H
from .markdown import (
    Bullets, Callout, Details, Figure, Heading, Para, Quote, Run, Table, demote, map_runs, parse_markdown, plain, section, title_of, walk_runs,
)
from .pdf import PdfDocument

CONTRACT = "LegacyMapperDeliverablesManifest"
CONTRACT_VERSION = "1.0"
LEGEND_VERSION = "1.0"
MANIFEST_NAME = "DELIVERABLES_MANIFEST.json"
SITE_DIR = {"executive": "executive", "functional": "functional", "technical_overview": "technical"}
AUDIENCE_LABEL = {"executive": "Ejecutivo", "functional": "Funcional", "technical_overview": "Técnico"}
AUDIENCE_BLURB = {
    "executive": "¿Qué sistema es, qué tan grande es, cómo se organiza y qué no se sabe? Sin métodos, clases ni identificadores crudos.",
    "functional": "Áreas, procesos observables (pantalla → evento → dato), pantallas, datos y comportamiento no resuelto.",
    "technical_overview": "Proyectos, capas inferidas, dependencias, pantallas, interacciones con datos y límites no resueltos.",
}
DELIVERABLES = (
    ("SYSTEM_OVERVIEW", "Resumen del sistema", "Qué sistema es, su tamaño y cómo se organiza (narrativa ejecutiva + mapa del sistema)."),
    ("MODULE_MAP", "Mapa de módulos", "Agrupaciones que el código demuestra: solución (área), proyecto y capa inferida."),
    ("FUNCTIONAL_AREAS", "Áreas funcionales", "Las áreas del sistema (cada una es una solución real, no una función de negocio confirmada)."),
    ("USE_CASES", "Casos de uso", "Casos de uso respaldados por evidencia o conocimiento aprobado; si no los hay, se dice."),
    ("BUSINESS_FLOWS", "Flujos de negocio / flujos observables", "Recorridos pantalla → evento → dato que el código demuestra."),
    ("ARCHITECTURE_OVERVIEW", "Visión de arquitectura", "Proyectos, capas y dependencias."),
    ("PROJECT_LAYER_MAP", "Mapa de proyectos y capas", "Qué proyecto pertenece a qué capa (capa inferida por reglas estructurales)."),
    ("DATA_INTERACTIONS", "Interacciones con datos", "Qué operaciones de datos se observan y desde qué pantallas."),
    ("EXTERNAL_INTEGRATIONS", "Integraciones externas", "Qué es confirmado, qué es de plataforma, qué no está clasificado y qué no se resolvió."),
    ("KNOWN_UNRESOLVED_AREAS", "Áreas no resueltas conocidas", "Lo que el análisis no pudo determinar. No significa ausencia."),
)
DELIVERABLE_IDS = tuple(d[0] for d in DELIVERABLES)
PDF_FILES = {
    "overview": "LegacyMapper_System_Overview.pdf", "executive": "LegacyMapper_Executive.pdf",
    "functional": "LegacyMapper_Functional.pdf", "technical_overview": "LegacyMapper_Technical_Overview.pdf",
}
NOTICE_PREFIXES = ("Documentación generada automáticamente", "Cómo leer las etiquetas")
PDF_MAX_ENTITY_PAGES = 5    # area / project pages with diagrams included in an audience PDF (the HTML has all of them)


class DeliveryInvalid(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason, self.detail = reason, detail


@dataclass
class Page:
    path: str                      # site-relative, e.g. functional/areas/x.html
    title: str
    blocks: list
    section: str                   # nav key
    audience: str = ""
    crumbs: list = field(default_factory=list)
    toc: bool = True
    source: str = ""               # H2 documentation-relative source (or "" for composed pages)


@dataclass
class DeliveryResult:
    output: Path
    manifest: dict
    seconds: float = 0.0
    pdfs: dict = field(default_factory=dict)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _site_path(h2_rel: str) -> str:
    """`technical_overview/modules/x.md` -> `technical/modules/x.html` (README -> index)."""
    head, _, rest = h2_rel.partition("/")
    rest = rest[:-3] if rest.endswith(".md") else rest
    if rest == "README" or rest.endswith("/README"):
        rest = rest[:-6] + "index"
    return f"{SITE_DIR.get(head, head)}/{rest}.html"


def strip_boilerplate(blocks: list) -> list:
    """Removes the per-page generic notice and the per-page copy of the label legend (one shared legend per package)."""
    out = []
    for b in blocks:
        if isinstance(b, Quote) and b.blocks:
            first = plain(b.blocks[0].runs) if isinstance(b.blocks[0], Para) else ""
            if first.startswith(NOTICE_PREFIXES):
                continue
        out.append(b)
    return out


def _anchor_unique(blocks: list) -> list:
    return blocks


class Builder:
    def __init__(self, ctx, info, docs_root: Path, vis_root: Path, vis_manifest: dict, audiences: tuple[str, ...], knowledge_run: Path | None,
                 include_ai: bool) -> None:
        self.ctx, self.info, self.docs_root, self.vis_root, self.vis = ctx, info, docs_root, vis_root, vis_manifest
        self.audiences = audiences
        self.knowledge_run = knowledge_run
        self.include_ai = include_ai
        self.system = ctx.model.system
        self.pages: dict[str, Page] = {}
        self.missing_refs: dict[str, list[str]] = {}
        self.diagram_entries = {d["svg"]: d for d in vis_manifest.get("diagrams", [])}
        self.children: dict[str, list[dict]] = {}
        for d in vis_manifest.get("diagrams", []):
            if d.get("parent_id"):
                self.children.setdefault(d["parent_id"], []).append(d)
        self.by_id = {d["id"]: d for d in vis_manifest.get("diagrams", [])}

    # ------------------------------------------------------------ visuals helpers
    def figure(self, entry: dict, *, with_children: bool = True) -> Figure:
        dec = entry.get("decomposition") or {}
        kids = []
        if with_children:
            for c in sorted(self.children.get(entry["id"], []), key=lambda e: e["svg"]):
                kids.append((c["title"], f"visuals/{c['svg'][:-4]}.html"))
        m = entry.get("metrics", {})
        return Figure(title=entry["title"], svg=f"visuals/{entry['svg']}", model=f"visuals/{entry['model']}", page=f"visuals/{entry['svg'][:-4]}.html",
                      kind=entry["kind"], scope_label=str(entry["scope"].get("label", "")), nodes=entry["nodes"], edges=entry["edges"],
                      width=int(m.get("canvas_width", 820)), height=int(m.get("canvas_height", 400)), status_counts=entry.get("status_counts", {}),
                      partial=entry.get("partial", {}), unresolved_nodes=entry.get("unresolved_nodes", 0), role=dec.get("role", ""), children=kids)

    def top_entries(self, prefix: str, kinds: tuple[str, ...] | None = None) -> list[dict]:
        """Summary-level (non-detail) diagrams whose svg path starts with `prefix`."""
        out = [d for d in self.vis.get("diagrams", []) if d["svg"].startswith(prefix) and d.get("decomposition", {}).get("role") != "detail"
               and (kinds is None or d["kind"] in kinds)]
        return sorted(out, key=lambda d: d["svg"])

    def kind_entries(self, kind: str, scope_types: tuple[str, ...] = ("system", "area", "project")) -> list[dict]:
        out = [d for d in self.vis.get("diagrams", []) if d["kind"] == kind and d.get("decomposition", {}).get("role") != "detail"
               and (d["scope"].get("type") in scope_types)]
        return sorted(out, key=lambda d: d["svg"])

    # ------------------------------------------------------------ H2 pages
    def load_h2_pages(self) -> None:
        known: dict[str, str] = {}
        sources: list[tuple[str, Path]] = []
        for audience in self.audiences:
            base = self.docs_root / audience
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*.md")):
                rel = f"{audience}/{path.relative_to(base).as_posix()}"
                known[rel] = _site_path(rel)
                sources.append((rel, path))
        for rel, path in sources:
            blocks = parse_markdown(path.read_text(encoding="utf-8"))
            site = known[rel]
            blocks = map_runs(blocks, lambda run, rel=rel, known=known: self._resolve_link(run, rel, known))
            audience = rel.split("/", 1)[0]
            self.pages[site] = Page(site, title_of(blocks, site), blocks, SITE_DIR[audience], audience, source=rel)

    def _resolve_link(self, run, src_rel: str, known: dict[str, str]):
        if not run.href:
            return run
        href = run.href
        if "://" in href or href.startswith("mailto:"):
            return run
        target, _, frag = href.partition("#")
        if not target:
            return run
        joined = posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), target))
        site = known.get(joined)
        if site is None:
            self.missing_refs.setdefault(src_rel, []).append(target)
            return Run(run.text, run.bold, run.italic, run.code, None, True)
        return Run(run.text, run.bold, run.italic, run.code, site + (f"#{frag}" if frag else ""), False)

    # ------------------------------------------------------------ composition helpers
    def h2_blocks(self, site: str) -> list:
        p = self.pages.get(site)
        return strip_boilerplate(p.blocks) if p else []

    def embed(self, site: str, *, drop_title: bool = True, demote_by: int = 1) -> list:
        blocks = self.h2_blocks(site)
        if drop_title:
            blocks = [b for b in blocks if not (isinstance(b, Heading) and b.level == 1)]
        return demote(blocks, demote_by)

    def source_note(self, *sites: str) -> list:
        links = []
        for s in sites:
            if s in self.pages:
                links.append([Run(self.pages[s].title, href=s)])
        if not links:
            return []
        return [Para([Run("Fuentes de esta superficie (narrativa H2): ", italic=True)]), Bullets(links)]

    def numbers(self, *keys: str) -> dict:
        return {k: self.system.get(k, 0) for k in keys}

    def counts_paragraph(self, text: str, status: str = "Confirmado") -> list:
        return [Para(parse_inline_simple(text)), Para([Run(f"Estado: {status.lower()}.", italic=True)])]

    # ------------------------------------------------------------ deliverables
    def build_deliverables(self) -> dict[str, dict]:
        sysm = self.system
        have = lambda s: s in self.pages  # noqa: E731
        out: dict[str, dict] = {}

        def add(did: str, blocks: list, *, semantic: str, support: str, sources: list[str], kinds: list[str]) -> None:
            title = next(t for i, t, _ in DELIVERABLES if i == did)
            body = [Heading(1, [Run(title)], "titulo"), Callout("semantic", "Qué es (y qué no es) esta superficie", [Para([Run(semantic)])])]
            body += blocks
            out[did] = {"id": did, "title": title, "blocks": body, "support": support, "sources": sources, "visual_kinds": kinds}

        def gallery(heading: str, entries: list[dict], *, limit: int = 12) -> list:
            if not entries:
                return []
            shown = entries[:limit]
            blocks: list = [Heading(2, [Run(heading)], "")]
            for e in shown:
                blocks.append(self.figure(e))
            if len(entries) > limit:
                blocks.append(Para([Run(f"Se muestran {limit} de {len(entries)} diagramas; el resto está en el índice de diagramas.", italic=True)]))
            return blocks

        # SYSTEM_OVERVIEW
        sys_map = self.kind_entries("system-map", ("system",))
        blocks = self.embed("executive/index.html") if have("executive/index.html") else []
        if not blocks:
            blocks = [Para([Run(f"Sistema «{sysm.get('name', '')}». Áreas (soluciones): {sysm.get('areas', 0)}. Proyectos: {sysm.get('projects', 0)}. "
                                f"Pantallas web: {sysm.get('screens', 0)}.")]), Para([Run("Estado: confirmado por evidencia.", italic=True)])]
        blocks = blocks + gallery("Mapa del sistema", sys_map)
        add("SYSTEM_OVERVIEW", blocks, support="SUPPORTED" if have("executive/index.html") else "PARTIAL_NO_EXECUTIVE_AUDIENCE",
            semantic="Composición del resumen ejecutivo (H2) con el mapa del sistema (H3). No añade significado: el propósito de negocio del sistema "
                     "no puede deducirse del código y se declara como no resuelto.",
            sources=["executive/index.html"], kinds=["system-map"])

        # MODULE_MAP
        layer_section = section(self.h2_blocks("executive/index.html"), "Cómo está organizado")
        blocks = []
        if layer_section:
            blocks += [Heading(2, [Run("Capas (inferidas)")], "")] + layer_section
        else:
            blocks += [Para([Run("Capas inferidas: presentación "
                                 f"{sysm.get('layer_presentation', 0)}, lógica/servicios {sysm.get('layer_logic', 0)}, acceso a datos "
                                 f"{sysm.get('layer_data_access', 0)}, sin clasificar {sysm.get('layer_unclassified', 0)}.")]),
                       Para([Run("Estado: inferido con una regla estructural.", italic=True)])]
        links = []
        for site, label in (("functional/areas.html", "Áreas (soluciones) del sistema"), ("technical/layers.html", "Proyectos por capa"),
                            ("technical/dependencies.html", "Dependencias entre proyectos")):
            if have(site):
                links.append([Run(label, href=site)])
        if links:
            blocks += [Heading(2, [Run("Dónde ver cada agrupación")], ""), Bullets(links)]
        blocks += gallery("Mapas del sistema y de capas", self.kind_entries("system-map", ("system",)) + self.kind_entries("project-layer-map", ("area", "project")))
        add("MODULE_MAP", blocks, support="SUPPORTED_AS_SOLUTION_PROJECT_LAYER",
            semantic="En LegacyMapper un «módulo» solo puede representarse con tres agrupaciones que el código demuestra: solución (área), proyecto y capa "
                     "inferida. No se inventan módulos de negocio; si «módulo» significara una función de negocio, ese dato no está en la evidencia.",
            sources=["executive/index.html", "technical/layers.html"], kinds=["system-map", "project-layer-map"])

        # FUNCTIONAL_AREAS
        blocks = self.embed("functional/areas.html") if have("functional/areas.html") else (
            self.embed("executive/areas.html") if have("executive/areas.html") else [])
        blocks += gallery("Mapas de las áreas generadas", self.kind_entries("system-map", ("area",)))
        add("FUNCTIONAL_AREAS", blocks, support="SUPPORTED_AS_SOLUTION" if blocks else "NO_AUDIENCE_SOURCE",
            semantic="Un área es aquí una solución real (archivo .sln) y los proyectos que contiene. No es una función de negocio confirmada: "
                     "esa agrupación no puede deducirse del código.",
            sources=["functional/areas.html", "executive/areas.html"], kinds=["system-map"])

        # USE_CASES
        canon, proposals = self._use_case_records()
        blocks = [
            Callout("unresolved", "Resultado", [Para([Run("No hay casos de uso confirmados derivables de la evidencia estática. "
                                                          "Los actores y los objetivos de negocio no pueden deducirse del código y no se fabrican.")]),
                                                Para([Run("Estado: no resuelto.", italic=True)])]) if not canon else
            Callout("note", "Resultado", [Para([Run(f"Hay {len(canon)} caso(s) de uso aprobado(s) por una persona (canónico). "
                                                    "No hay casos de uso confirmados derivados de la evidencia estática.")])]),
            Heading(2, [Run("La representación respaldada por evidencia más cercana")], ""),
            Para([Run(f"Interacciones observadas en las que una acción del usuario llega a una operación real de datos: {sysm.get('interactions', 0)}, "
                      f"en {sysm.get('interaction_screens', 0)} pantallas de {sysm.get('interaction_projects', 0)} proyectos. "
                      "Son flujos observables (pantalla → evento → operación de datos), no casos de uso.")]),
            Para([Run("Estado: confirmado por evidencia.", italic=True)]),
        ]
        nav = []
        for site, label in (("deliverables/BUSINESS_FLOWS.html", "Flujos observables"), ("functional/processes.html", "Procesos que llegan a datos")):
            if have(site) or site.startswith("deliverables/"):
                nav.append([Run(label, href=site)])
        blocks.append(Bullets(nav))
        blocks.append(Heading(2, [Run("Conocimiento aprobado por una persona (canónico)")], ""))
        if canon:
            blocks.append(Table([[Run("Afirmación")], [Run("Estado")]], [[[Run(c)], [Run("Canónico (aprobado por una persona)")]] for c in canon]))
        else:
            blocks.append(Para([Run("No hay casos de uso aprobados registrados" + ("." if self.knowledge_run else " (no se proporcionó una corrida de IA/conocimiento a este paquete)."))]))
        if proposals:
            blocks.append(Heading(2, [Run("Propuestas de IA (no aprobadas)")], ""))
            blocks.append(Para([Run("Ninguna persona las ha aprobado: no son hechos ni casos de uso confirmados.")]))
            blocks.append(Table([[Run("Afirmación")], [Run("Estado")]], [[[Run(p)], [Run("Interpretación de IA (no aprobada)")]] for p in proposals]))
        add("USE_CASES", blocks, support="CANONICAL_ONLY" if canon else "NO_CONFIRMED_USE_CASES",
            semantic="No se fabrican casos de uso. Solo se muestran los que una persona aprobó explícitamente (canónico); las propuestas de IA "
                     "permanecen separadas y no aprobadas.",
            sources=["knowledge:canonical"] if canon else [], kinds=[])

        # BUSINESS_FLOWS
        blocks = []
        if have("functional/processes.html"):
            blocks += self.embed("functional/processes.html")
        else:
            blocks += [Para([Run(f"Interacciones observadas que llegan a datos: {sysm.get('interactions', 0)}.")]), Para([Run("Estado: confirmado por evidencia.", italic=True)])]
        blocks += gallery("Diagramas de flujos observables", self.kind_entries("observable-flow", ("flow",)))
        add("BUSINESS_FLOWS", blocks, support="OBSERVABLE_FLOWS_ONLY",
            semantic="Se llaman «flujos observables»: recorridos pantalla → evento → operación de datos que el código demuestra. No se afirma que "
                     "representen un flujo de negocio; el propósito de cada uno no puede deducirse del código.",
            sources=["functional/processes.html"], kinds=["observable-flow"])

        # ARCHITECTURE_OVERVIEW
        blocks = self.embed("technical/index.html") if have("technical/index.html") else []
        if not blocks:
            blocks = [Para([Run(f"Proyectos: {sysm.get('projects', 0)}; capas inferidas y dependencias en las vistas técnicas.")])]
        blocks += gallery("Mapas de dependencias y capas", self.kind_entries("dependency-map", ("area", "project")) + self.kind_entries("project-layer-map", ("area",)))
        add("ARCHITECTURE_OVERVIEW", blocks, support="SUPPORTED" if have("technical/index.html") else "PARTIAL_NO_TECHNICAL_AUDIENCE",
            semantic="Vista de proyectos, capas y dependencias. La capa de un proyecto es una inferencia estructural, no una afirmación arquitectónica.",
            sources=["technical/index.html"], kinds=["dependency-map", "project-layer-map"])

        # PROJECT_LAYER_MAP
        blocks = self.embed("technical/layers.html") if have("technical/layers.html") else layer_section
        blocks += gallery("Mapas de proyectos y capas", self.kind_entries("project-layer-map", ("area", "project")))
        add("PROJECT_LAYER_MAP", blocks, support="SUPPORTED_INFERRED_LAYERS",
            semantic="La capa se infiere con reglas estructurales sobre la evidencia (pantallas propias, accesos directos a datos, referencias); "
                     "los nombres de los proyectos no se usan. Un proyecto sin regla aplicable queda «no resuelto».",
            sources=["technical/layers.html"], kinds=["project-layer-map"])

        # DATA_INTERACTIONS
        blocks = []
        summary = section(self.h2_blocks("functional/index.html"), "Resumen funcional observable")
        if summary:
            blocks += [Heading(2, [Run("Resumen de interacciones observadas")], "")] + summary
        blocks += self.embed("functional/data.html") if have("functional/data.html") else self.embed("technical/data.html") if have("technical/data.html") else []
        blocks += gallery("Mapas de interacción con datos", self.kind_entries("data-interaction-map", ("area", "project")))
        add("DATA_INTERACTIONS", blocks, support="SUPPORTED" if blocks else "NO_AUDIENCE_SOURCE",
            semantic="El tipo de interacción (consulta, registro, modificación, eliminación) se infiere solo del nombre técnico de la operación; "
                     "no describe el propósito de negocio.",
            sources=["functional/index.html", "functional/data.html"], kinds=["data-interaction-map"])

        # EXTERNAL_INTEGRATIONS
        slots = self.ctx.model.slots
        n = lambda key: len(slots.get(key, []))  # noqa: E731
        rows = [
            ("Externa confirmada", "Conexiones a base de datos identificadas. No se identifican servicios externos (por ejemplo, servicios web).",
             n("integrations"), "Confirmado"),
            ("Plataforma", "Bibliotecas reconocidas como de la plataforma (no son integraciones de negocio).", n("platform_libraries"), "Inferido (regla estructural)"),
            ("Sin clasificar", "Bibliotecas referenciadas cuya naturaleza (propia o de terceros) no se determina. No son integraciones confirmadas.",
             n("unclassified_libraries"), "No resuelto"),
            ("No resuelto (límites de flujo)", "Destinos de llamadas que el análisis no pudo seguir hasta código del repositorio.",
             sysm.get("unresolved_distinct", 0), "No resuelto"),
        ]
        blocks = [
            Table([[Run("Categoría")], [Run("Qué incluye")], [Run("Cantidad")], [Run("Estado")]],
                  [[[Run(a, bold=True)], [Run(b)], [Run(str(c))], [Run(d)]] for a, b, c, d in rows]),
            Para([Run("Una biblioteca sin clasificar no es una integración externa confirmada: el análisis no demuestra que sea un sistema o servicio externo.", bold=True)]),
        ]
        blocks += (self.embed("functional/integrations.html") if have("functional/integrations.html")
                   else self.embed("technical/integrations.html") if have("technical/integrations.html") else [])
        add("EXTERNAL_INTEGRATIONS", blocks, support="CLASSIFIED_BY_EVIDENCE",
            semantic="Se distinguen cuatro categorías y ninguna se promueve: lo desconocido no se convierte en integración confirmada.",
            sources=["functional/integrations.html"], kinds=[])

        # KNOWN_UNRESOLVED_AREAS
        flows, unresolved = sysm.get("flows", 0), sysm.get("unresolved_flows", 0)
        blocks = [
            Callout("unresolved", "Cuánto no se sabe", [Para([Run(
                f"Recorridos observados: {flows}. Se detienen ante un límite no resuelto: {unresolved} ({sysm.get('unresolved_share', 0)}%). "
                f"Destinos no resueltos distintos: {sysm.get('unresolved_distinct', 0)}. Proyectos afectados: {sysm.get('unresolved_projects', 0)}.")]),
                Para([Run("Estado: no resuelto. «No resuelto» no significa que falle ni que no exista: el análisis estático no puede afirmar a dónde va.", italic=True)])]),
        ]
        blocks += self.embed("functional/unresolved.html") if have("functional/unresolved.html") else (
            self.embed("technical/unresolved.html") if have("technical/unresolved.html") else [])
        if have("technical/unresolved.html") and have("functional/unresolved.html"):
            blocks.append(Para([Run("Detalle técnico completo: ", italic=True), Run("Áreas no resueltas (vista técnica)", href="technical/unresolved.html")]))
        cues = sorted((d for d in self.vis.get("diagrams", []) if d.get("unresolved_nodes", 0) and d.get("decomposition", {}).get("role") != "detail"),
                      key=lambda d: (-d["unresolved_nodes"], d["svg"]))
        if cues:
            blocks.append(Heading(2, [Run("Señales de lo no resuelto en los diagramas")], ""))
            blocks.append(Para([Run("Diagramas generados que contienen nodos «no resueltos» (borde punteado y marca «!»).")]))
            blocks.append(Table([[Run("Diagrama")], [Run("Tipo")], [Run("Nodos no resueltos")], [Run("Estado")]],
                                [[[Run(d["title"], href=f"visuals/{d['svg'][:-4]}.html")], [Run(d["kind"])], [Run(str(d["unresolved_nodes"]))], [Run("No resuelto")]]
                                 for d in cues[:25]]))
        add("KNOWN_UNRESOLVED_AREAS", blocks, support="SUPPORTED",
            semantic="Lo no resuelto se muestra de forma destacada y nunca como ausencia: es lo que el análisis estático no pudo determinar.",
            sources=["functional/unresolved.html", "technical/unresolved.html"], kinds=["system-map", "observable-flow"])
        return out

    def _use_case_records(self) -> tuple[list[str], list[str]]:
        """(canonical statements, unapproved AI statements) whose recorded kind is a use case. Nothing else is called a use case."""
        if not self.knowledge_run:
            return [], []
        import re

        def is_use_case(kind: object) -> bool:
            return bool(re.search(r"use[_ -]?case|caso[_ -]?de[_ -]?uso", str(kind or ""), re.IGNORECASE))

        def read(path: Path):
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return None

        run = self.knowledge_run
        decisions = [d for d in (read(p) for p in sorted((run / "knowledge" / "decisions").glob("*.json"))) if isinstance(d, dict)]
        rejected = {d.get("proposal_id") for d in decisions if d.get("action") == "REJECT"}
        canon_records = [r for r in (read(p) for p in sorted((run / "knowledge" / "canonical").glob("*.json")))
                         if isinstance(r, dict) and r.get("status", "ACTIVE") == "ACTIVE"]
        canonical_ids = {r.get("source_proposal_id") for r in canon_records}
        canon = [str((r.get("content") or {}).get("statement", "")) for r in canon_records if is_use_case((r.get("content") or {}).get("kind"))]
        envelope = read(run / "proposals" / "AI_PROPOSALS.json") or {}
        proposals = [str(p.get("statement", "")) for p in (envelope.get("proposals") or [])
                     if isinstance(p, dict) and is_use_case(p.get("proposal_kind")) and p.get("proposal_id") not in canonical_ids | rejected]
        return [c for c in canon if c], [p for p in proposals if p]


def parse_inline_simple(text: str) -> list[Run]:
    return [Run(text)]


# ====================================================================== site assembly
def _crumbs(page: Page, pages: dict[str, Page]) -> list[tuple[str, str | None]]:
    home = ("Inicio", "index.html")
    if page.path == "index.html":
        return [("Inicio", None)]
    parts = page.path.split("/")
    if parts[0] in ("deliverables",):
        trail = [home, ("Entregables", "deliverables/index.html")]
        if page.path != "deliverables/index.html":
            trail.append((page.title, None))
        else:
            trail[-1] = ("Entregables", None)
        return trail
    if parts[0] == "visuals":
        trail = [home, ("Diagramas", "visuals/index.html")]
        if page.path != "visuals/index.html":
            trail.append((page.title, None))
        else:
            trail[-1] = ("Diagramas", None)
        return trail
    if parts[0] in SITE_DIR.values():
        label = {"executive": "Ejecutivo", "functional": "Funcional", "technical": "Técnico"}[parts[0]]
        landing = f"{parts[0]}/index.html"
        trail: list[tuple[str, str | None]] = [home]
        if page.path == landing:
            return trail + [(label, None)]
        trail.append((label, landing))
        name = parts[-1][:-5]
        parent = None
        if len(parts) > 2 and parts[1] == "areas":
            parent = f"{parts[0]}/areas.html"
        elif len(parts) > 2 and parts[1] == "modules":
            parent = f"{parts[0]}/layers.html"
        elif "-part-" in name:
            parent = f"{parts[0]}/{name.split('-part-')[0]}.html"
        if parent and parent in pages and parent != page.path:
            trail.append((pages[parent].title, parent))
        trail.append((page.title, None))
        return trail
    return [home, (page.title, None)]


def _unique_anchors(blocks: list) -> None:
    """Gives every top-level heading a stable, page-unique id (composed pages embed several H2 pages)."""
    from .markdown import slugify
    seen: dict[str, int] = {}
    for b in blocks:
        if isinstance(b, Heading):
            base = b.anchor or slugify(plain(b.runs))
            seen[base] = seen.get(base, 0) + 1
            b.anchor = base if seen[base] == 1 else f"{base}-{seen[base]}"


def _toc(blocks: list) -> list[tuple[str, str, int]]:
    out = []
    for b in blocks:
        if isinstance(b, Heading) and b.level in (2, 3) and b.anchor:
            out.append((b.anchor, plain(b.runs), b.level))
    return out[:40]


def _write(root: Path, rel: str, data: str | bytes, files: dict[str, dict]) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = data.encode("utf-8") if isinstance(data, str) else data
    target.write_bytes(raw)
    files[rel] = {"sha256": _sha(raw), "bytes": len(raw)}


def _kpi(label: str, value: object, status: str) -> list:
    return [Run(label, bold=True), Run(f": {value} ({status})")]


def build_package(builder: Builder, output: Path, *, make_pdf: bool, row_cap: int, options: dict) -> tuple[dict, dict]:
    ctx, sysm = builder.ctx, builder.system
    name = str(sysm.get("name", "sistema"))
    pages = builder.pages
    present = [a for a in builder.audiences if any(p.audience == a for p in pages.values())]
    deliverables = builder.build_deliverables()

    # ---- diagram pages (summary -> detail navigation) and visuals index
    diagram_pages: dict[str, Page] = {}
    for entry in builder.vis.get("diagrams", []):
        site = f"visuals/{entry['svg'][:-4]}.html"
        fig = builder.figure(entry)
        model = json.loads((builder.vis_root / entry["model"]).read_text(encoding="utf-8"))
        node_rows = [[[Run(n["label"])], [Run(n["type"])], [Run(H.STATUS_TEXT.get(n["status"], n["status"]))],
                      [Run(", ".join(n.get("source_refs", [])[:3]) or "—", code=bool(n.get("source_refs")))]] for n in model.get("nodes", [])]
        edge_rows = []
        labels = {n["id"]: n["label"] for n in model.get("nodes", [])}
        for e in model.get("edges", []):
            edge_rows.append([[Run(labels.get(e["source"], e["source"]))], [Run(e.get("relation", ""))], [Run(labels.get(e["target"], e["target"]))],
                              [Run(H.STATUS_TEXT.get(e["status"], e["status"]))]])
        blocks: list = [Heading(1, [Run(entry["title"])], "titulo")]
        dec = entry.get("decomposition") or {}
        if entry.get("parent_id") and entry["parent_id"] in builder.by_id:
            parent = builder.by_id[entry["parent_id"]]
            blocks.append(Para([Run("Este es un diagrama de detalle. Resumen: "), Run(parent["title"], href=f"visuals/{parent['svg'][:-4]}.html")]))
        blocks.append(fig)
        blocks.append(Callout("note", "Cómo leerlo", [Para([Run("Cada nodo y relación indica su estado en texto y con un patrón de borde distinto "
                                                                "(leyenda dentro del diagrama y en «Sobre la evidencia»). Abra el SVG para ampliarlo.")])]))
        if dec:
            blocks.append(Para([Run(f"Descomposición: rol «{dec.get('role', '')}»; elementos incluidos {dec.get('included_count', 0)}, "
                                    f"agregados {dec.get('omitted_count', 0)}.")]))
        blocks.append(Heading(2, [Run("Nodos (alternativa textual)")], "nodos"))
        blocks.append(Table([[Run("Nodo")], [Run("Tipo")], [Run("Estado")], [Run("Referencias de evidencia")]], node_rows) if node_rows
                      else Para([Run("Sin nodos.")]))
        if edge_rows:
            blocks.append(Heading(2, [Run("Relaciones")], "relaciones"))
            blocks.append(Table([[Run("Origen")], [Run("Relación")], [Run("Destino")], [Run("Estado")]], edge_rows))
        diagram_pages[site] = Page(site, entry["title"], blocks, "visuals", toc=True)

    # ---- landing pages and composed pages
    deliv_links = {d: f"deliverables/{d}.html" for d in DELIVERABLE_IDS}
    index_blocks: list = [Heading(1, [Run(f"LegacyMapper — {name}")], "titulo"),
                          Para([Run("Paquete de entregables humanos generado a partir de una línea base determinista ya persistida. "
                                    "Cada afirmación conserva su estado epistémico: confirmado, inferido, no resuelto, interpretación de IA o canónico.")])]
    index_blocks.append(Heading(2, [Run("El sistema en cifras")], "cifras"))
    index_blocks.append(Table(
        [[Run("Medida")], [Run("Valor")], [Run("Estado")]],
        [[[Run("Áreas (soluciones con proyectos identificados)")], [Run(str(sysm.get("areas", 0)))], [Run("Confirmado")]],
         [[Run("Proyectos")], [Run(str(sysm.get("projects", 0)))], [Run("Confirmado")]],
         [[Run("Pantallas web")], [Run(str(sysm.get("screens", 0)))], [Run("Confirmado")]],
         [[Run("Recorridos observados")], [Run(str(sysm.get("flows", 0)))], [Run("Confirmado")]],
         [[Run("Recorridos que llegan a una operación real de datos")], [Run(str(sysm.get("real_flows", 0)))], [Run("Confirmado")]],
         [[Run("Recorridos que se detienen ante un límite no resuelto")], [Run(f"{sysm.get('unresolved_flows', 0)} ({sysm.get('unresolved_share', 0)}%)")],
          [Run("No resuelto")]]]))
    index_blocks.append(Callout("unresolved", "Lo que no se sabe", [Para([Run(
        "El propósito de negocio del sistema, la agrupación por función de negocio y los servicios externos no pueden deducirse del código. "
        f"El {sysm.get('unresolved_share', 0)}% de los recorridos observados se detiene ante algo que el análisis estático no pudo seguir. ")]),
        Para([Run("Ver las áreas no resueltas conocidas", href="deliverables/KNOWN_UNRESOLVED_AREAS.html")])]))
    index_blocks.append(Heading(2, [Run("Elija su ruta de lectura")], "rutas"))
    for audience in present:
        landing = f"{SITE_DIR[audience]}/index.html"
        if landing in pages:
            index_blocks.append(Para([Run(AUDIENCE_LABEL[audience], bold=True, href=landing), Run(f" — {AUDIENCE_BLURB[audience]}")]))
    index_blocks.append(Heading(2, [Run("Entregables")], "entregables"))
    index_blocks.append(Bullets([[Run(title, href=deliv_links[i]), Run(f" — {desc}")] for i, title, desc in DELIVERABLES]))
    index_blocks.append(Para([Run("Índice de diagramas", href="visuals/index.html"), Run(" · "), Run("Sobre la evidencia y las etiquetas", href="about.html")]))
    composed: dict[str, Page] = {"index.html": Page("index.html", f"LegacyMapper — {name}", index_blocks, "", toc=False)}

    route = {"executive": ["SYSTEM_OVERVIEW", "FUNCTIONAL_AREAS", "MODULE_MAP", "DATA_INTERACTIONS", "EXTERNAL_INTEGRATIONS", "KNOWN_UNRESOLVED_AREAS"],
             "functional": ["FUNCTIONAL_AREAS", "BUSINESS_FLOWS", "USE_CASES", "DATA_INTERACTIONS", "EXTERNAL_INTEGRATIONS", "KNOWN_UNRESOLVED_AREAS"],
             "technical_overview": ["ARCHITECTURE_OVERVIEW", "PROJECT_LAYER_MAP", "MODULE_MAP", "DATA_INTERACTIONS", "EXTERNAL_INTEGRATIONS", "KNOWN_UNRESOLVED_AREAS"]}
    for audience in present:
        landing = f"{SITE_DIR[audience]}/index.html"
        page = pages.get(landing)
        if page is None:
            continue
        intro = [Callout("note", "Ruta sugerida para esta audiencia", [Bullets([[Run(dict((i, t) for i, t, _ in DELIVERABLES)[d], href=deliv_links[d])] for d in route[audience]])]),
                 Callout("unresolved", "Qué no se sabe", [Para([Run("Lo no resuelto no es ausencia. "), Run("Ver áreas no resueltas conocidas", href="deliverables/KNOWN_UNRESOLVED_AREAS.html")])])]
        head = [b for b in page.blocks if isinstance(b, Heading) and b.level == 1][:1]
        rest = [b for b in page.blocks if b not in head]
        page.blocks = head + intro + rest

    # ---- visual injection on area / project pages
    for path, page in pages.items():
        parts = path.split("/")
        if len(parts) == 3 and parts[1] in ("areas", "modules"):
            slug = parts[2][:-5]
            entries = builder.top_entries(f"areas/{slug}/") if parts[1] == "areas" else builder.top_entries(f"projects/{slug}/")
            if entries:
                page.blocks += [Heading(2, [Run("Diagramas")], "diagramas")] + [builder.figure(e) for e in entries]

    # ---- deliverable pages
    for did, title, desc in DELIVERABLES:
        d = deliverables[did]
        composed[f"deliverables/{did}.html"] = Page(f"deliverables/{did}.html", d["title"], d["blocks"], "unresolved" if did == "KNOWN_UNRESOLVED_AREAS" else "deliverables")
    drows = []
    for did, title, desc in DELIVERABLES:
        d = deliverables[did]
        drows.append([[Run(title, bold=True, href=f"deliverables/{did}.html")], [Run(did, code=True)], [Run(desc)], [Run(d["support"].replace("_", " ").lower())]])
    composed["deliverables/index.html"] = Page("deliverables/index.html", "Entregables", [
        Heading(1, [Run("Entregables")], "titulo"),
        Para([Run("Diez superficies de entrega. Algunas son superficies de entrega, no una promesa de que exista toda la semántica: "
                  "donde la evidencia no la sostiene, el entregable lo dice.")]),
        Table([[Run("Entregable")], [Run("Identificador")], [Run("Contenido")], [Run("Soporte de evidencia")]], drows),
        Heading(2, [Run("Documentos PDF")], "pdf"),
        Bullets([[Run(PDF_FILES[k], code=True)] for k in ("overview", *[a for a in present])]) if make_pdf else Para([Run("No se generaron PDF (--no-pdf).")]),
    ], "deliverables")

    # ---- visuals index
    vrows = []
    for e in sorted(builder.vis.get("diagrams", []), key=lambda d: d["svg"]):
        vrows.append([[Run(e["title"], href=f"visuals/{e['svg'][:-4]}.html")], [Run(e["kind"])], [Run(str(e["scope"].get("type", "")))],
                      [Run(str(e["nodes"]))], [Run(str(e["edges"]))], [Run("parcial" if e["partial"].get("partial") else (e.get("decomposition", {}).get("role", "") or "completo"))]])
    composed["visuals/index.html"] = Page("visuals/index.html", "Índice de diagramas", [
        Heading(1, [Run("Índice de diagramas")], "titulo"),
        Para([Run(f"{len(vrows)} diagramas estructurados (SVG + modelo JSON). Todos conservan el estado epistémico de cada nodo y relación.")]),
        Table([[Run("Diagrama")], [Run("Tipo")], [Run("Alcance")], [Run("Nodos")], [Run("Relaciones")], [Run("Forma")]], vrows) if vrows
        else Para([Run("No se generaron diagramas para este paquete.")]),
    ], "visuals")

    # ---- about
    about_blocks = [
        Heading(1, [Run("Sobre la evidencia y las etiquetas")], "titulo"),
        Para([Run("Este paquete presenta y empaqueta conocimiento ya producido; no infiere significado nuevo. Cada afirmación lleva uno de estos estados:")]),
        Bullets([[Run(H.STATUS_TEXT[s], bold=True), Run(f" — {H.STATUS_MEANING[s]} En diagramas: {H.STATUS_PATTERN[s]}.")] for s in H.STATUS_ORDER]),
        Callout("semantic", "Regla permanente", [Para([Run("La presentación puede simplificar el lenguaje, pero no puede reforzar la certeza: "
                                                            "inferido no se vuelve confirmado, una interpretación de IA no se vuelve confirmada y lo no resuelto no se lee como ausencia.")])]),
        Heading(2, [Run("Qué significan los términos")], "terminos"),
        Bullets([[Run("Área", bold=True), Run(" — una solución real (.sln) y sus proyectos; no es una función de negocio confirmada.")],
                 [Run("Capa", bold=True), Run(" — inferencia estructural (presentación, lógica/servicios, acceso a datos); no es una afirmación de arquitectura.")],
                 [Run("Flujo observable", bold=True), Run(" — recorrido pantalla → evento → operación de datos demostrado por el código; no es un flujo de negocio confirmado.")],
                 [Run("No resuelto", bold=True), Run(" — el análisis estático no pudo seguirlo hasta código del repositorio; no significa ausencia.")]]),
        Heading(2, [Run("Procedencia")], "procedencia"),
        Para([Run("Línea base: huella del manifiesto de evidencia "), Run(builder.info.portable_evidence_sha256 or builder.info.evidence_manifest_sha256, code=True), Run(".")]),
        Para([Run("El paquete se genera sin volver a analizar el código fuente y sin llamar a ningún proveedor de IA. "
                  "La interpretación de IA, cuando existe, se muestra siempre aparte y etiquetada; el conocimiento canónico es el aprobado por una persona.")]),
        Heading(2, [Run("Uso sin conexión")], "offline"),
        Para([Run("Todo el contenido es estático: abra index.html desde el disco. No requiere servidor, red ni bibliotecas externas. "
                  "La búsqueda y el filtro de tablas son opcionales (un script local pequeño); sin él la navegación completa sigue funcionando.")]),
    ]
    composed["about.html"] = Page("about.html", "Sobre la evidencia y las etiquetas", about_blocks, "about", toc=True)

    # ---- assemble, render HTML
    all_pages: dict[str, Page] = {}
    all_pages.update(pages)
    all_pages.update(composed)
    all_pages.update(diagram_pages)
    for p in all_pages.values():
        p.crumbs = _crumbs(p, all_pages)
    files: dict[str, dict] = {}
    known = set(all_pages)
    visual_files = {f"visuals/{d['svg']}" for d in builder.vis.get("diagrams", [])} | {f"visuals/{d['model']}" for d in builder.vis.get("diagrams", [])}
    broken: list[tuple[str, str]] = []
    nav_present = set(known)
    for site, page in sorted(all_pages.items()):
        # integrity: every resolved link / figure target exists in the package
        for run in walk_runs(page.blocks):
            if run.href and "://" not in run.href and not run.missing:
                tgt = run.href.partition("#")[0]
                if tgt and tgt not in known and tgt not in visual_files:
                    broken.append((site, run.href))
        for b in page.blocks:
            if isinstance(b, Figure):
                for tgt in (b.svg, b.model, b.page):
                    if tgt not in known and tgt not in visual_files:
                        broken.append((site, tgt))
        _unique_anchors(page.blocks)
        body = H.render_blocks(page.blocks, site)
        shell = H.page_shell(title=page.title, body=body, page=site, section_key=page.section, crumbs=page.crumbs,
                             toc=_toc(page.blocks) if page.toc else [], system_name=name, available=known)
        _write(output, site, shell, files)
    if broken:
        raise DeliveryInvalid("BROKEN_LINKS", "; ".join(f"{a} -> {b}" for a, b in broken[:10]))

    # ---- visuals + assets
    for entry in builder.vis.get("diagrams", []):
        for rel in (entry["svg"], entry["model"]):
            _write(output, f"visuals/{rel}", (builder.vis_root / rel).read_bytes(), files)
    _write(output, "visuals/VISUALS_MANIFEST.json", (builder.vis_root / "VISUALS_MANIFEST.json").read_bytes(), files)
    _write(output, "assets/style.css", H.CSS, files)
    _write(output, "assets/site.js", H.JS, files)
    index = [[site, p.title, " | ".join(plain(b.runs) for b in p.blocks if isinstance(b, Heading) and b.level in (2, 3))[:300]]
             for site, p in sorted(all_pages.items()) if not site.startswith("visuals/") or site == "visuals/index.html"]
    _write(output, "assets/search-index.js", "var LM_SEARCH=" + json.dumps(index, ensure_ascii=False, separators=(",", ":")) + ";\n", files)

    # ---- PDFs
    pdfs: dict[str, dict] = {}
    if make_pdf:
        (output / "pdf").mkdir(parents=True, exist_ok=True)
        meta = [f"Línea base (huella de evidencia): {builder.info.portable_evidence_sha256 or builder.info.evidence_manifest_sha256}",
                "Generado sin volver a analizar el código fuente ni llamar a un proveedor de IA."]
        specs = _pdf_specs(builder, all_pages, deliverables, present, name)
        for key, (title, subtitle, sections) in specs.items():
            doc = PdfDocument(title, footer_title=title, row_cap=row_cap)
            doc.assets_root = output
            doc.reserve_front()
            for blocks in sections:
                doc.blocks(strip_boilerplate(blocks))
                doc._cur = None  # every section starts on a fresh page
            doc.fill_front(subtitle, meta)
            data, stats = doc.render()
            rel = f"pdf/{PDF_FILES[key]}"
            _write(output, rel, data, files)
            pdfs[rel] = {"sha256": files[rel]["sha256"], "bytes": len(data), **stats}

    # ---- manifest
    statuses = {k: 0 for k in H.STATUS_ORDER}
    for e in builder.vis.get("diagrams", []):
        for k, v in e.get("status_counts", {}).items():
            statuses[k] = statuses.get(k, 0) + v
    diagrams = builder.vis.get("diagrams", [])
    manifest = {
        "contract": CONTRACT, "contract_version": CONTRACT_VERSION,
        "baseline": {"evidence_manifest_sha256": builder.info.evidence_manifest_sha256, "portable_evidence_sha256": builder.info.portable_evidence_sha256,
                     "logical_snapshot_sha256": builder.info.logical_snapshot_sha256, "evidence_schema_version": builder.info.evidence_schema_version,
                     "analyzer": builder.info.analyzer, "system": name,
                     "repository": {k: builder.info.repository.get(k) for k in ("repository_id", "source_snapshot_sha256", "logical_snapshot_sha256", "portable_evidence_sha256", "source_file_count")}},
        "epistemic_legend": {"version": LEGEND_VERSION, "statuses": [{"status": s, "label": H.STATUS_TEXT[s], "meaning": H.STATUS_MEANING[s],
                                                                         "diagram_pattern": H.STATUS_PATTERN[s]} for s in H.STATUS_ORDER]},
        "profiles": [{"audience": a, "site_dir": SITE_DIR[a], "pages": sum(1 for p in pages.values() if p.audience == a)} for a in present],
        "deliverables": [{"id": d, "title": deliverables[d]["title"], "path": f"deliverables/{d}.html", "support": deliverables[d]["support"],
                          "sources": deliverables[d]["sources"], "visual_kinds": deliverables[d]["visual_kinds"]} for d in DELIVERABLE_IDS],
        "visual_package": {"manifest": "visuals/VISUALS_MANIFEST.json", "evidence_manifest_sha256": builder.vis.get("evidence_manifest_sha256"),
                           "diagrams": len(diagrams), "partial_diagrams": sum(1 for d in diagrams if d.get("partial", {}).get("partial")),
                           "decomposed_summaries": sum(1 for d in diagrams if d.get("decomposition", {}).get("role") == "summary"),
                           "detail_diagrams": sum(1 for d in diagrams if d.get("decomposition", {}).get("role") == "detail"),
                           "status_counts": dict(sorted(statuses.items()))},
        "pdfs": dict(sorted(pdfs.items())),
        "pdf_determinism": ("PDF streams are deflated with the local zlib: bytes are stable for one Python/zlib build; `content_sha256` hashes the "
                            "uncompressed page streams and is toolchain independent. No timestamps are written."),
        "unresolvable_references": {"count": sum(len(v) for v in builder.missing_refs.values()),
                                    "note": "References to documents outside this package are shown as plain text, never as dead links.",
                                    "by_source": {k: sorted(set(v)) for k, v in sorted(builder.missing_refs.items())}},
        "provider_calls": 0, "source_scan_invocations": 0, "analyzer_invocations": 0, "options": options,
        "counts": {"html_files": sum(1 for f in files if f.endswith(".html")), "svg_files": sum(1 for f in files if f.endswith(".svg")),
                   "json_models": len(diagrams),
                   "pdf_files": len(pdfs), "files_total": len(files) + 1},
        "files": {k: files[k] for k in sorted(files)},
    }
    return manifest, pdfs


def _limit_figures(blocks: list, keep: int) -> list:
    """PDF only: a deliverable shows its first `keep` diagrams; the rest are declared (they are all in the HTML package)."""
    out, seen, dropped = [], 0, 0
    for b in blocks:
        if isinstance(b, Figure):
            seen += 1
            if seen > keep:
                dropped += 1
                continue
        out.append(b)
    if dropped:
        out.append(Para([Run(f"Este PDF muestra {keep} de {seen} diagramas de esta superficie; los {dropped} restantes están en el paquete HTML.", italic=True)]))
    return out


def _omitted_note(what: str, total: int, shown: int) -> list[list]:
    if total <= shown:
        return []
    return [[Para([Run(f"Este PDF incluye las páginas de {shown} de {total} {what} con diagramas; el resto está en el paquete HTML.", italic=True)])]]


def _pdf_specs(builder: Builder, pages: dict[str, Page], deliverables: dict[str, dict], present: list[str], name: str) -> dict:
    def pg(*sites: str) -> list[list]:
        return [pages[s].blocks for s in sites if s in pages]

    specs: dict = {}
    specs["overview"] = (f"Resumen del sistema {name}", "Visión general: resumen, módulos, áreas, flujos observables, arquitectura, datos, integraciones y lo no resuelto.",
                         [_limit_figures(deliverables[d]["blocks"], 3) for d in DELIVERABLE_IDS])
    if "executive" in present:
        system_map = [builder.figure(e) for e in builder.kind_entries("system-map", ("system",))][:1]
        specs["executive"] = (f"Resumen ejecutivo — {name}", "Vista ejecutiva: qué es, cómo se organiza y qué no se sabe.",
                              pg("executive/index.html") + ([[Heading(2, [Run("Mapa del sistema")], ""), *system_map]] if system_map else [])
                              + pg("executive/areas.html") + [_limit_figures(deliverables["KNOWN_UNRESOLVED_AREAS"]["blocks"], 2)])
    if "functional" in present:
        areas = [s for s in sorted(pages) if s.startswith("functional/areas/")]
        with_visuals = [s for s in areas if builder.top_entries(f"areas/{s.split('/')[-1][:-5]}/")]
        shown = with_visuals[:PDF_MAX_ENTITY_PAGES]
        specs["functional"] = (f"Vista funcional — {name}", "Áreas, procesos observables, pantallas, datos, integraciones y comportamiento no resuelto.",
                               pg("functional/index.html", "functional/areas.html", "functional/processes.html", "functional/screens.html", "functional/data.html",
                                  "functional/integrations.html", "functional/interpretation.html", "functional/unresolved.html", *shown)
                               + _omitted_note("áreas", len(with_visuals), len(shown)))
    if "technical_overview" in present:
        mods = [s for s in sorted(pages) if s.startswith("technical/modules/")]
        with_visuals = [s for s in mods if builder.top_entries(f"projects/{s.split('/')[-1][:-5]}/")]
        shown = with_visuals[:PDF_MAX_ENTITY_PAGES]
        specs["technical_overview"] = (f"Visión técnica general — {name}", "Proyectos, capas inferidas, dependencias, datos, integraciones y límites no resueltos.",
                                       pg("technical/index.html", "technical/layers.html", "technical/dependencies.html", "technical/data.html",
                                          "technical/integrations.html", "technical/interpretation.html", "technical/unresolved.html", *shown)
                                       + [_limit_figures(deliverables["ARCHITECTURE_OVERVIEW"]["blocks"], 4), _limit_figures(deliverables["PROJECT_LAYER_MAP"]["blocks"], 4)]
                                       + _omitted_note("proyectos", len(with_visuals), len(shown)))
    return specs


# ====================================================================== entry point
def _clear_previous(output: Path) -> None:
    if not output.exists():
        return
    if not output.is_dir():
        raise DeliveryInvalid("DELIVER_OUTPUT_NOT_A_DIRECTORY", str(output))
    entries = list(output.iterdir())
    if not entries:
        return
    manifest = output / MANIFEST_NAME
    try:
        old = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else None
    except (OSError, ValueError):
        old = None
    if not old or old.get("contract") != CONTRACT:
        raise DeliveryInvalid("DELIVER_OUTPUT_NOT_EMPTY", "choose an empty directory or a previous H4 package")
    for rel in list(old.get("files", {})) + [MANIFEST_NAME]:
        try:
            (output / rel).unlink()
        except OSError:
            pass
    for sub in sorted((p for p in output.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            sub.rmdir()
        except OSError:
            pass


def default_visual_scope(ctx, top_areas: int, all_areas: bool) -> tuple[list[str], list[str], list[str]]:
    """Default diagram scope: the N most active areas, every project of those areas (so area -> project pages carry diagrams) and one
    representative flow per area; `all_areas` extends the same rule to every area."""
    ranked = [i.values["slug"] for i in ctx.model.slots["areas"]]
    chosen = ranked if all_areas else ranked[:top_areas]
    projects = sorted({m.slug for a in chosen for m in ctx.area_modules(a)})
    flows = [f for f in (representative_flow(ctx, a) for a in chosen) if f]
    return chosen, projects, flows


def _find_docs_root(path: Path) -> Path:
    for candidate in (path / "documentation_v52", path):
        if any((candidate / a).is_dir() for a in AUDIENCE_PROFILES):
            return candidate
    raise DeliveryInvalid("DOCS_DIR_INVALID", f"no audience profiles under {path}")


def generate_delivery(baseline: str | Path, output: str | Path, *, audiences: tuple[str, ...] = AUDIENCE_PROFILES, docs_dir: str | Path | None = None,
                      visuals_dir: str | Path | None = None, ai_run: str | Path | None = None, include_ai: bool = False, areas: list[str] | None = None,
                      projects: list[str] | None = None, flows: list[str] | None = None, top_areas: int = 10, all_areas: bool = False,
                      max_nodes: int = 40, max_children: int = 30, make_pdf: bool = True, row_cap: int = 30, verify_evidence: str = "fast") -> DeliveryResult:
    started = perf_counter()
    out = Path(output)
    baseline_path = Path(baseline)
    if include_ai and not ai_run:
        raise DeliveryInvalid("INCLUDE_AI_REQUIRES_AI_RUN")
    if ai_run and not Path(ai_run).is_dir():
        raise DeliveryInvalid("AI_RUN_NOT_FOUND", str(ai_run))
    if out.resolve() == baseline_path.resolve():
        raise DeliveryInvalid("DELIVER_OUTPUT_IS_BASELINE")
    knowledge_refs = load_knowledge_refs(ai_run) if ai_run and include_ai else None
    ctx = load_context(baseline_path, knowledge_refs, verify_evidence, max_nodes, max_children)  # H1 baseline gate + audience model (no scan, no provider)
    info = _info(baseline_path, verify_evidence)
    _clear_previous(out)
    staging = Path(tempfile.mkdtemp(prefix="lm_h4_"))
    try:
        # --- H2 narrative
        if docs_dir:
            docs_root = _find_docs_root(Path(docs_dir))
            missing = [a for a in audiences if not (docs_root / a).is_dir()]
            if missing:
                raise DeliveryInvalid("DOCS_AUDIENCE_MISSING", ",".join(missing))
        else:
            knowledge = load_knowledge_overlay(ai_run) if ai_run else None
            generate_documentation_v52(ctx.source, staging / "docs", profiles=tuple(audiences), knowledge=knowledge,
                                       deep_reference=(baseline_path / "documentation_v52" / "developer").is_dir())
            docs_root = staging / "docs" / "documentation_v52"
        # --- H3 visuals
        if visuals_dir:
            vis_root = Path(visuals_dir)
            manifest_path = vis_root / "VISUALS_MANIFEST.json"
            try:
                vis_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise DeliveryInvalid("VISUALS_MANIFEST_INVALID", str(manifest_path)) from None
            if vis_manifest.get("evidence_manifest_sha256") != ctx.manifest_sha256:
                raise DeliveryInvalid("VISUALS_STALE", "visual package was generated from a different baseline")
        else:
            vis_root = staging / "visuals"
            sel_areas, sel_projects, sel_flows = areas, projects, flows
            if not (areas or projects or flows):
                sel_areas, sel_projects, sel_flows = default_visual_scope(ctx, top_areas, all_areas)
            generate_visuals(ctx, vis_root, areas=sel_areas, projects=sel_projects, flows=sel_flows, top_areas=top_areas, all_areas=False,
                             include_ai=include_ai)
            vis_manifest = json.loads((vis_root / "VISUALS_MANIFEST.json").read_text(encoding="utf-8"))
        builder = Builder(ctx, info, docs_root, vis_root, vis_manifest, tuple(audiences), Path(ai_run) if ai_run else None, include_ai)
        builder.load_h2_pages()
        if not builder.pages:
            raise DeliveryInvalid("NO_AUDIENCE_PAGES")
        options = {"audiences": list(audiences), "docs_dir": "consumed" if docs_dir else "generated", "visuals_dir": "consumed" if visuals_dir else "generated",
                   "ai_run": bool(ai_run), "include_ai": bool(include_ai), "areas": sorted(areas or []), "projects": sorted(projects or []),
                   "flows": sorted(flows or []), "top_areas": top_areas, "all_areas": bool(all_areas), "max_nodes": max_nodes,
                   "max_children": max_children, "pdf": bool(make_pdf), "pdf_row_cap": row_cap}
        out.mkdir(parents=True, exist_ok=True)
        manifest, pdfs = build_package(builder, out, make_pdf=make_pdf, row_cap=row_cap, options=options)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    (out / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return DeliveryResult(out, manifest, round(perf_counter() - started, 3), pdfs)


def _info(baseline: Path, verify_evidence: str):
    from legacy_documenter.orchestration.ai_only import validate_baseline
    return validate_baseline(baseline, verify_evidence)


__all__ = ["generate_delivery", "DeliveryInvalid", "DeliveryResult", "BaselineInvalid", "KINDS", "DELIVERABLE_IDS", "MANIFEST_NAME", "PDF_FILES"]
