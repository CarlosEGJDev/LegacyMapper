"""AI behavioral interpretation over a bounded behavioral context (post-V5 H4-R5).

    deterministic evidence -> bounded behavioral context (facts with real refs) -> provider (structured JSON) -> deterministic
    validation -> `AI_INTERPRETATION` narrative attached to the view

The model never receives the repository: only the facts of one view (controls, events, paths, data operations, invocations, messages,
usage evidence), each with a reference the validator can resolve. Anything the model says that cites a reference it was not given, a
symbol that does not exist, or that calls a component obsolete/unused is REJECTED; the rest of its answer is kept and always labelled
`AI_INTERPRETATION` (never confirmed, never canonical).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field

from .model import AI_INTERPRETATION, Claim
from .usage import FORBIDDEN_WORDS, USAGE_STATES
from .validate import ReferenceIndex, Violation

ENTITY_TYPES = ("control", "event", "method", "class", "procedure", "view", "parameter", "message")
_QUOTED = re.compile(r"«([^»]{1,120})»|`([^`]{1,120})`")

ITEM = {"type": "object", "required": ["text", "source_refs", "reasoning_basis"],
        "properties": {"text": {"type": "string"}, "source_refs": {"type": "array", "items": {"type": "string"}},
                       "reasoning_basis": {"type": "string"},
                       "entities": {"type": "array", "items": {"type": "object", "required": ["type", "name"],
                                                               "properties": {"type": {"enum": list(ENTITY_TYPES)}, "name": {"type": "string"}}}}}}
VIEW_SCHEMA = {
    "type": "object",
    "required": ["view_id", "simple_summary", "observable_purpose", "usage_reasoning", "main_actions", "data_behavior"],
    "properties": {
        "view_id": {"type": "string"}, "simple_summary": ITEM, "observable_purpose": ITEM,
        "usage_status": {"enum": list(USAGE_STATES)}, "usage_reasoning": ITEM,
        "inputs": {"type": "array", "items": ITEM},
        "main_actions": {"type": "array", "items": {"type": "object", "required": ["action_key", "explanation"],
                                                    "properties": {"action_key": {"type": "string"}, "explanation": ITEM}}},
        "data_behavior": ITEM,
        "related_classes": {"type": "array", "items": {"type": "object", "required": ["name", "role_note"],
                                                       "properties": {"name": {"type": "string"}, "role_note": ITEM}}},
        "messages_popups": {"type": "array", "items": ITEM},
        "known": {"type": "array", "items": ITEM}, "inferred": {"type": "array", "items": ITEM}, "unresolved": {"type": "array", "items": ITEM},
    },
}
PROJECT_SCHEMA = {
    "type": "object", "required": ["project_summary", "role_in_solution", "how_it_is_used", "unresolved"],
    "properties": {"project_summary": ITEM, "role_in_solution": ITEM, "how_it_is_used": ITEM, "unresolved": {"type": "array", "items": ITEM}},
}

SYSTEM = (
    "Eres un analista que explica a personas no técnicas cómo funciona una pantalla de un sistema legado, a partir de hechos estáticos "
    "extraídos por un analizador determinista. Tu trabajo es EXPLICAR EL COMPORTAMIENTO, no resumir archivos. Escribe en español claro y "
    "sencillo (frases como «Esta pantalla…», «Al abrirse…», «Al pulsar…», «Después…»). Usa SOLO los hechos del contexto. No inventes "
    "actores, requisitos, casos de uso, módulos, sistemas externos, semántica de base de datos ni uso en producción. No llames obsoleto, "
    "muerto ni «sin uso» a un componente: la ausencia de evidencia de uso no es evidencia de obsolescencia. Marca con claridad lo que sea "
    "inferencia. Explica el sistema para una persona: qué se sabe, qué hace el componente, cómo se comporta, qué llama, qué abre y a qué datos "
    "llega. Prefiere nombres y relaciones concretos a conteos; no uses estadísticas del análisis (número de llamadas, hechos, controles, "
    "afirmaciones, referencias, solicitudes) ni identificadores de Evidence en la prosa. Sé breve: 1–3 frases por afirmación. Si algo no se "
    "sabe, menciónalo brevemente solo cuando cambie la comprensión; la incertidumbre no es la narrativa principal. Rutas técnicas con símbolos "
    "reales: vista → evento → manejador → método de negocio → método entre proyectos → método de datos → procedimiento / SQL → base de datos o "
    "frontera. Si el contexto trae `human_confirmed_domain_knowledge`, son términos confirmados por una persona: úsalos para nombrar y "
    "explicar, sin presentarlos como evidencia del código. Responde únicamente con un objeto JSON que cumpla el esquema."
)
INSTRUCTION = (
    "Explica la vista descrita en `context`. Cada afirmación debe ser un objeto con `text` (1–3 frases), `source_refs` (SOLO valores del campo "
    "`ref` de `facts`; use [] si ninguno aplica), `reasoning_basis` (por qué lo afirmas) y `entities` (controles, eventos, métodos, clases, "
    "procedimientos o vistas del contexto en los que se apoya el texto). Entre «» escribe únicamente nombres exactos del contexto "
    "(controles, manejadores, clases, procedimientos, etiquetas visibles). Responde: ¿para qué sirve la vista según la evidencia observable?, "
    "¿qué puede hacer el usuario?, ¿qué pasa al abrirse y en las acciones principales (usa `action_key` = el nombre del manejador)?, "
    "¿qué información entra, se muestra, se selecciona o cambia?, ¿a dónde van los datos?, ¿qué clases participan?, ¿qué otras vistas o "
    "ventanas intervienen?, ¿qué evidencia sugiere que se usa (explica `usage_reasoning` sin contradecir `usage.deterministic_status`)? "
    "y ¿qué permanece incierto? Si el contexto no sustenta algo, dilo en `unresolved` en lugar de suponerlo. Redacta simple y corto, con "
    "nombres reales de vistas, acciones, clases y procedimientos; sin conteos ni identificadores de Evidence en el texto."
)


@dataclass
class AiRun:
    provider_id: str = ""
    model_id: str = ""
    requests: list[dict] = field(default_factory=list)
    raw: list[dict] = field(default_factory=list)      # provider answers as received (for audit / re-validation)


def make_provider(max_output_tokens: int = 4500, timeout_s: float = 240):
    """Existing provider architecture only (COPILOT unless LEGACYMAPPER_LLM_PROVIDER says otherwise). No new provider."""
    import asyncio

    from legacy_documenter.llm.registry import ProviderRegistry, config_from_environment
    config = config_from_environment(max_output_tokens=max_output_tokens, timeout_s=timeout_s)
    if config.provider_type.upper() == "COPILOT" and not config.model_id:
        from legacy_documenter.llm.copilot_pilot import discover_model
        config.model_id = asyncio.run(discover_model())
    return ProviderRegistry().create(config)


class ReplayProvider:
    """Replays the answers of an earlier REAL provider run (saved by this prototype) so the deterministic validation can be re-applied
    after validator changes without new provider calls. It never invents content: a missing answer yields no output."""

    def __init__(self, raw_path, manifest_path=None) -> None:
        from pathlib import Path
        self.answers = {(r["kind"], r["target"]): r for r in json.loads(Path(raw_path).read_text(encoding="utf-8"))}
        meta = {}
        if manifest_path and Path(manifest_path).is_file():
            meta = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        self.provider_id, self.model_id = meta.get("provider_id", "replay"), meta.get("model_id", "replay")
        self.original_requests = meta.get("requests", [])

    def model_info(self):
        from legacy_documenter.llm.contracts import LLMModelInfo
        return LLMModelInfo(self.provider_id, self.model_id, self.model_id, "REPLAY", self.capabilities())

    def capabilities(self):
        from legacy_documenter.llm.contracts import LLMCapabilities
        return LLMCapabilities(structured_output=True, json_mode=True)

    def structured_generate(self, request, schema):
        from legacy_documenter.llm.contracts import LLMResponse, Usage
        cid = request.context_package_id          # CTX-BEHAVIOR-<kind>-<name>
        _, _, kind, name = cid.split("-", 3)
        saved = self.answers.get((kind, name))
        content = (saved or {}).get("content") or ""
        parsed = None
        try:
            value = json.loads(content, strict=False)
            parsed = value if isinstance(value, dict) else None
        except ValueError:
            parsed = None
        return LLMResponse(request.request_id, "REPLAY-" + request.request_id, self.provider_id, self.model_id, "SUCCESS" if parsed is not None else "INVALID_STRUCTURED_OUTPUT",
                           content=content, usage=Usage(), parsed_output=parsed,
                           schema_validation_status="VALID_STRUCTURED_OUTPUT" if parsed is not None else "INVALID_STRUCTURED_OUTPUT")


# ---------------------------------------------------------------- bounded behavioral context
def _trim(text: str, n: int = 160) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def fact_tokens(facts: list[dict]) -> set[str]:
    """Identifier-like tokens (and their dotted prefixes/parts) and «quoted» strings that appear in the facts given to the model."""
    out: set[str] = set()
    for f in facts:
        for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", f["fact"]):
            parts = tok.split(".")
            out.update(p.lower() for p in parts)
            for i in range(1, len(parts) + 1):
                out.add(".".join(parts[:i]).lower())
        out.update(m.strip().lower() for m in re.findall(r"«([^»]{1,160})»", f["fact"]))
    return out


def view_context(bc, view, project: dict) -> tuple[dict, dict]:
    """Returns (context, universe). `facts` carry real refs; `universe` holds the names the validator will accept."""
    ev = bc.view(view.view)
    facts: list[dict] = []
    uni: dict[str, set] = {t: set() for t in ENTITY_TYPES}
    allowed_refs: set[str] = set()

    def fact(ref: str, kind: str, text: str) -> None:
        facts.append({"ref": ref, "kind": kind, "fact": _trim(text, 220)})
        allowed_refs.add(ref)

    uni["view"].update({view.name.lower(), view.view.lower()})
    if view.title:
        uni["message"].add(view.title.lower())
        fact(f"src:{ev.markup_file}:1", "view_title", f"Título visible de la pantalla: «{view.title}»")
    controls = []
    if view.ui and view.ui.status == "DOCUMENTARY_RECONSTRUCTION":
        for c in view.ui.controls[:70]:
            uni["control"].add(c.id.lower())
            if c.label:
                uni["message"].add(c.label.lower())
            entry = {"id": c.id, "kind": c.kind, "label": c.label, "hidden": not c.visible_initially, "event_bound": c.event_bound}
            if c.columns:
                entry["grid_columns"] = c.columns[:10]
                uni["message"].update(x.lower() for x in c.columns)
            if c.bound_to:
                entry["bound_to"] = c.bound_to
            controls.append(entry)
    for e in ev.events:
        ref = e.ep_id
        label = f"{e.control}.{e.event}" if e.control else e.event
        uni["event"].add(label.lower())
        uni["method"].add(e.handler.lower())
        if e.control:
            uni["control"].add(e.control.lower())
        fact(ref, "event", f"Evento {label} → manejador {e.handler} (código en {ev.code_file or 'n/d'}:{e.line})")
        if e.chains:
            best = max(e.chains, key=lambda c: (any(s["kind"] == "procedure" for s in c), len(c)))
            steps = " → ".join(s["label"] for s in best)
            for s in best:
                uni["method"].add(s["label"].lower())
                for part in s["label"].split("."):
                    uni["method"].add(part.lower())
                    uni["class"].add(part.lower())
            fact(e.flow_id or ref, "technical_path", f"Ruta confirmada de {e.handler}: {_trim(steps, 300)}")
        for o in e.data_ops[:6]:
            for key in ("class",):
                if o[key]:
                    uni["class"].add(str(o[key]).lower())
            if o["method"]:
                uni["method"].add(str(o["method"]).lower())
            if o["procedure"]:
                uni["procedure"].add(o["procedure"].lower())
            fact(o["dao_id"] or e.flow_id or ref, "data_operation",
                 f"{e.handler} alcanza la operación de datos {o['class']}.{o['method']}" + (f" → procedimiento {o['procedure']}" if o["procedure"] else "")
                 + f" (tipo deducido del nombre: {o['effect']})")
        biz = [u for u in e.unresolved if u["label"] and not u["label"].lower().startswith(("dbc.", "me.", "values"))]
        seen = set()
        for u in biz:
            if u["label"] in seen or len(seen) >= 6:
                continue
            seen.add(u["label"])
            uni["method"].add(u["label"].lower())
            m = re.match(r"^(?:[A-Za-z_]\w*\.)*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(", u["label"])
            if m:
                uni["class"].add(m.group(1).lower())
                uni["method"].add(m.group(2).lower())
            fact(u["refs"][0] if u["refs"] else e.flow_id, "unresolved_call", f"{e.handler} llama a {_trim(u['label'], 90)} y el análisis no resolvió su destino")
    for cls in view.classes:
        uni["class"].add(cls.name.lower())
    if ev.code:
        for r in ev.code.receives[:12]:
            uni["parameter"].add(r["name"].lower())
            fact(f"src:{ev.code_file}:{r['line']}", "parameter", f"Recibe el parámetro «{r['name']}» (vía {r['via']})")
        for k in ev.code.session_keys[:8]:
            uni["parameter"].add(k.lower())
        if ev.code.session_keys:
            fact(f"src:{ev.code_file}:1", "session", "Usa claves de sesión: " + ", ".join(ev.code.session_keys[:8]))
        for m in ev.code.messages[:10]:
            if m["text"]:
                uni["message"].add(m["text"].lower())
                fact(f"src:{ev.code_file}:{m['line']}", "message", f"En {m['event']} muestra el mensaje literal «{_trim(m['text'], 100)}»")
            elif m["kind"] == "error_display":
                fact(f"src:{ev.code_file}:{m['line']}", "message", f"En {m['event']} muestra un error al usuario (texto no estático)")
    class_short = (view.name or "").lower()
    own = [r for r in bc.cross_project_calls if str(r.get("source_symbol", "")).split(".")[0].lower() == class_short
           and (r["status"] != "CONFIRMED" or r.get("source_project") != r.get("target_project"))]
    for rec in sorted(own, key=lambda r: (r["status"] != "UNRESOLVED", r.get("line") or 0))[:6]:
        target = rec.get("target_symbol") or ", ".join((rec.get("candidates") or [])[:2]) or rec.get("expression")
        fact(f"src:{ev.code_file}:{rec.get('line') or 1}", "cross_project_call",
             f"La llamada {_trim(str(rec.get('expression')), 60)} entre proyectos: estado {rec['status']} ({rec.get('resolution_code')}; base {rec.get('resolution_basis')}); destino {target}")
    doc = bc.ui.document(view.view)
    if doc is not None:                                    # persisted UI Evidence: host chain, assets and style references (bounded)
        summary = bc.ui.view_summary(doc)
        base_ref = f"src:{ev.markup_file}:1"
        if summary["hosts"] or view.kind == "user_control":
            names = [h.rsplit("/", 1)[-1] for h in summary["hosts"][:6]]
            for n in names:
                uni["view"].update({n.lower(), n.rsplit(".", 1)[0].lower()})
            fact(base_ref, "host_chain", ("Contenida por: " + ", ".join(names) + f" (resolución del anfitrión: {summary['host_resolution']})")
                 if names else "Ningún anfitrión que la registre fue encontrado en la evidencia (anfitrión no resuelto)")
        for entry in bc.ui.menu_entries_for(doc)[:5]:
            props = entry["properties"]
            fact(f"src:{entry['logical_source_path']}:{props['line']}", "menu_entry",
                 f"Referenciada desde la configuración/menú «{props['label'] or props['target_literal']}» ({entry['logical_source_path']}:{props['line']}; estado {entry['status']})")
        if summary["master_literal"]:
            fact(base_ref, "master_page", f"Declara la página maestra «{summary['master_literal']}» (estado: {summary['master_status']})")
        if summary["assets_total"]:
            fact(base_ref, "assets", f"Referencia {summary['assets_total']} imagen(es); sin resolver: {', '.join(summary['assets_unresolved'][:5]) or 'ninguna'}")
        if summary["stylesheets"] or summary["css_classes"]:
            fact(base_ref, "styles", f"Hojas de estilo enlazadas: {', '.join(summary['stylesheets'][:4]) or 'ninguna'}; clases CSS declaradas: "
                 f"{len(summary['css_classes'])}; sin definición en las hojas persistidas: {', '.join(summary['css_classes_undefined'][:6]) or 'ninguna'}")
    seen_src = set()
    for i in view.reached_by:
        name = i.source_view.rsplit("\\", 1)[-1]
        uni["view"].add(name.lower())
        uni["view"].add(name.rsplit(".", 1)[0].lower())
        if (i.file, i.line) in seen_src or len(seen_src) >= 10:
            continue
        seen_src.add((i.file, i.line))
        fact(i.source_refs[0], "incoming_invocation", f"La vista {name} la abre como {i.mechanism} con parámetros {', '.join(i.parameters) or 'ninguno'}")
    for i in view.reaches[:10]:
        name = i.target_view.rsplit("\\", 1)[-1]
        uni["view"].add(name.lower())
        uni["view"].add(name.rsplit(".", 1)[0].lower())
        fact(i.source_refs[0], "outgoing_invocation",
             f"Esta vista abre {name} ({i.mechanism}; parámetros {', '.join(i.parameters) or 'ninguno'})" + ("" if i.target_exists else " — destino inexistente en el repositorio"))
    usage = view.usage
    for c in usage.get("reasons", []):
        fact(c.source_refs[0] if c.source_refs else f"src:{ev.markup_file}:1", "usage_evidence", c.text)
    allowed_refs.add(f"src:{ev.markup_file}:1")
    context = {
        "solution": project["solution"], "project": project["project"],
        "view": {"id": view.view, "name": view.name, "type": view.kind, "visible_title": view.title},
        "usage": {"deterministic_status": usage.get("status"), "wording_guidance": usage.get("wording")},
        "controls": controls, "facts": facts,
        "note": "Solo existen los controles, eventos y símbolos listados; las referencias (`ref`) de `facts` son las únicas válidas.",
    }
    terms = relevant_terms(project.get("domain_knowledge") or [], [view.name, view.title])
    if terms:
        context["human_confirmed_domain_knowledge"] = terms
    tokens: set[str] = fact_tokens(facts)
    for c in controls:
        tokens.update({str(c["id"]).lower(), str(c.get("label", "")).lower()} | {x.lower() for x in c.get("grid_columns", [])})
        bound = str(c.get("bound_to", ""))
        if bound:
            parts = bound.split(".")
            tokens.update(".".join(parts[:i]).lower() for i in range(1, len(parts) + 1))
            tokens.update(p.lower() for p in parts)
    for r in ev.code.receives if ev.code else []:
        tokens.add(r["name"].lower())
    for i in list(view.reached_by) + list(view.reaches):
        tokens.update(p.lower() for p in i.parameters)
        uni["parameter"].update(p.lower() for p in i.parameters)
    tokens.update(x.lower() for x in USAGE_STATES)
    tokens.update({"window_open", "navigate_url", "url_literal", "default.aspx"})
    uni["_labels_all"] = set().union(*[uni[t] for t in ENTITY_TYPES]) | tokens
    return context, {"universe": uni, "allowed_refs": allowed_refs}


def relevant_terms(terms: list[dict], texts: list[str]) -> list[dict]:
    """Human-confirmed terms that appear as a word / camel-case token of the given names (never inferred from the code)."""
    import re as _re
    tokens: set[str] = set()
    for t in texts:
        for part in _re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", t or ""):
            tokens.add(part.lower())
        tokens.update(w.lower() for w in _re.findall(r"\w+", t or ""))
    return [dict(t) for t in terms if str(t.get("term", "")).lower() in tokens]


def project_context(doc_views: list, project: dict, module, measurements: dict, usage_summary: dict) -> tuple[dict, dict]:
    facts, allowed, names = [], set(), set()

    def fact(ref, kind, text):
        facts.append({"ref": ref, "kind": kind, "fact": _trim(text, 260)})
        allowed.add(ref)
    fact(f"project:{project['path']}", "project", f"Proyecto web «{project['project']}» de la solución «{project['solution']}»; referencias de proyecto: "
         + ", ".join(project.get("refs") or ["ninguna"]))
    fact(f"project:{project['path']}", "module_decision", f"Clasificación de módulos: {module.classification}. {module.claim.text}")
    names.update({project["project"].lower(), project["solution"].lower()})
    for v in doc_views:
        names.update({v.name.lower(), v.view.lower()})
        ref = (v.actions[0].source_refs[0] if v.actions and v.actions[0].source_refs else f"project:{project['path']}")
        data = sorted({d.object_name for a in v.actions for d in a.data})
        openers = sorted({i.source_view.rsplit("\\", 1)[-1] for i in v.reached_by})[:5]
        fact(ref, "view_summary", f"Vista {v.name} («{v.title or 'sin título'}»): uso={v.usage.get('status')}; "
             f"acciones: {', '.join(a.action for a in v.actions[:6]) or 'ninguna propia'}; "
             f"datos: {', '.join(data[:4]) or 'destino posterior indeterminado'}; la abren: {', '.join(openers) or 'ninguna vista confirmada'}")
        names.update(x.lower() for x in data)
    names_by_status: dict[str, list[str]] = {}
    for v in doc_views:
        names_by_status.setdefault(str(v.usage.get("status")), []).append(v.name)
    fact(f"project:{project['path']}", "usage_summary", "Uso observable de las vistas explicadas: " +
         "; ".join(f"{k}: {', '.join(sorted(vs))}" for k, vs in sorted(names_by_status.items())))
    names.update(fact_tokens(facts))
    ctx = {"solution": project["solution"], "project": project["project"], "facts": facts,
           "note": "Explica el proyecto en términos de comportamiento observable; no inventes propósito de negocio."}
    if project.get("domain_knowledge"):
        ctx["human_confirmed_domain_knowledge"] = [dict(t) for t in project["domain_knowledge"]]
    return ctx, {"allowed_refs": allowed, "names": names}


# ---------------------------------------------------------------- request / call
def _request(kind: str, name: str, context: dict, snapshot: str, schema: dict, max_tokens: int):
    from legacy_documenter.llm.contracts import LLMRequest
    return LLMRequest(
        purpose="FUNCTIONAL_INTERPRETATION", system_instruction=SYSTEM, user_instruction=INSTRUCTION if kind == "view" else (
            "Explica el proyecto descrito en `context` para una persona no técnica: qué hace en términos observables, qué papel cumple en la solución "
            "y cómo se usa (a partir de las vistas resumidas), con `source_refs` tomadas solo de `facts`. Declara lo incierto en `unresolved`. "
            "Sé breve y nombra las vistas y relaciones concretas; no cites conteos del análisis ni identificadores de Evidence."),
        context=context, context_package_id=f"CTX-BEHAVIOR-{kind}-{name}", context_schema_version="behavior-context-1", source_snapshot=snapshot[:32],
        max_output_tokens=max_tokens, structured_output=True, output_contract=schema,
        metadata={"evidence_policy": {"use_only": "facts[].fact", "refs": "facts[].ref only"},
                  "claim_policy": {"status": "all output is AI_INTERPRETATION", "forbidden": ["obsolete", "unused", "invented actors/use cases/modules"]}})


def _tolerant_json(text: str) -> dict | None:
    """Parses the provider's answer allowing raw control characters inside strings. The content is never rewritten."""
    body = text.strip()
    if body.startswith("```"):
        body = body.strip("`")
        body = body[body.find("{"):]
    try:
        value = json.loads(body, strict=False)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def call(provider, kind: str, name: str, context: dict, snapshot: str, schema: dict, run: AiRun, max_tokens: int = 4500) -> dict | None:
    from legacy_documenter.llm.payload import render_request_payload
    req = _request(kind, name, context, snapshot, schema, max_tokens)
    payload = render_request_payload(req, schema)
    started = time.perf_counter()
    resp = provider.structured_generate(req, schema)
    info = provider.model_info()
    run.provider_id, run.model_id = info.provider_id, (resp.model_id or info.model_id)
    run.requests.append({"kind": kind, "target": name, "request_id": req.request_id, "status": resp.status,
                         "schema_validation": resp.schema_validation_status, "input_chars": len(payload), "context_chars": len(json.dumps(context, ensure_ascii=False)),
                         "output_chars": len(resp.content or ""), "seconds": round(time.perf_counter() - started, 1),
                         "output_tokens": getattr(resp.usage, "output_tokens", None) if resp.usage else None,
                         "error": (resp.error.details.get("sanitized_message") or resp.error.message) if resp.error else None})
    run.raw.append({"kind": kind, "target": name, "request_id": req.request_id, "status": resp.status, "content": resp.content})
    parsed = resp.parsed_output if isinstance(resp.parsed_output, dict) else None
    if parsed is None and resp.content:
        parsed = _tolerant_json(resp.content)
        if parsed is not None:
            run.requests[-1]["parse_recovery"] = "json strict=False (control characters inside strings); content unchanged"
    return parsed


# ---------------------------------------------------------------- deterministic validation of the AI narrative
def _symbols(text: str) -> list[str]:
    out = []
    for a, b in _QUOTED.findall(text):
        sym = (a or b).strip()
        if sym:
            out.append(sym)
    return out


def check_item(raw: object, where: str, allowed_refs: set[str], universe: dict, refs: ReferenceIndex) -> tuple[Claim | None, list[Violation]]:
    if not isinstance(raw, dict):
        return None, [Violation("AI_MALFORMED_ITEM", where, type(raw).__name__, "rejected")]
    text = str(raw.get("text") or "").strip()
    if not text:
        return None, [Violation("AI_EMPTY_CLAIM", where, "", "rejected")]
    if len(text) > 1200:
        return None, [Violation("AI_TEXT_TOO_LONG", where, str(len(text)), "rejected")]
    m = FORBIDDEN_WORDS.search(text)
    if m:
        return None, [Violation("AI_OBSOLESCENCE_CLAIM", where, m.group(0), "rejected")]
    source_refs = [str(r) for r in (raw.get("source_refs") or []) if str(r).strip()]
    for r in source_refs:
        if r not in allowed_refs:
            return None, [Violation("AI_REF_NOT_PROVIDED", where, r, "rejected")]
        if not refs.ref_ok(r):
            return None, [Violation("AI_UNRESOLVED_SOURCE_REF", where, r, "rejected")]
    entities = []
    for ent in raw.get("entities") or []:
        if not isinstance(ent, dict):
            continue
        t, n = str(ent.get("type")), str(ent.get("name") or "")
        known = n.lower() in universe.get(t, set()) or (t != "control" and n.lower() in universe.get("_labels_all", set()))   # controls: wireframe/evidence only
        if t not in ENTITY_TYPES or not known:
            return None, [Violation("AI_UNKNOWN_ENTITY", where, f"{t}:{n}", "rejected")]
        entities.append({"type": t, "name": n})
    universe_all = universe.get("_labels_all", set())
    for sym in _symbols(text):
        sym_n = re.sub(r"[(?].*$", "", sym).strip()           # «metodo()» / «metodo(x)» -> «metodo»
        key = sym_n.lower()
        parts = [p.lower() for p in re.split(r"[.\s]+", sym_n) if p]
        if key not in universe_all and not (parts and all(p in universe_all for p in parts)):
            return None, [Violation("AI_UNKNOWN_SYMBOL", where, sym, "rejected")]
    claim = Claim(text=text, status=AI_INTERPRETATION, source_refs=sorted(set(source_refs)), basis=_trim(raw.get("reasoning_basis") or "", 300),
                  origin="ai", entities=entities)
    return claim, []


def merge_view(view, parsed: dict | None, scope: dict, refs: ReferenceIndex, run_index: int = 0) -> list[Violation]:
    """Validates one parsed AI answer and attaches the surviving claims to the view (never as CONFIRMED)."""
    violations: list[Violation] = []
    if parsed is None:
        return [Violation("AI_NO_USABLE_OUTPUT", view.name, "provider returned no structured output", "rejected")]
    allowed, uni = scope["allowed_refs"], scope["universe"]
    sections: dict[str, list[Claim]] = {}

    def take(section: str, raw, where: str) -> None:
        claim, vs = check_item(raw, f"{view.name}:{where}", allowed, uni, refs)
        violations.extend(vs)
        if claim is not None:
            sections.setdefault(section, []).append(claim)

    if str(parsed.get("view_id") or "") not in (view.view, view.name):
        violations.append(Violation("AI_VIEW_ID_MISMATCH", view.name, str(parsed.get("view_id")), "noted"))
    for key in ("simple_summary", "observable_purpose", "usage_reasoning", "data_behavior"):
        take(key, parsed.get(key), key)
    for sec in ("inputs", "messages_popups", "known", "inferred", "unresolved"):
        for i, raw in enumerate(parsed.get(sec) or []):
            take(sec, raw, f"{sec}[{i}]")
    for i, rc in enumerate(parsed.get("related_classes") or []):
        if isinstance(rc, dict) and (str(rc.get("name", "")).lower() in uni["class"] or str(rc.get("name", "")).lower() in uni.get("_labels_all", set())):
            take("related_classes", rc.get("role_note"), f"related_classes[{i}]")
        else:
            violations.append(Violation("AI_UNKNOWN_ENTITY", f"{view.name}:related_classes[{i}]", f"class:{(rc or {}).get('name') if isinstance(rc, dict) else rc}", "rejected"))
    handlers = {a.handler.lower(): a.handler for a in view.actions}
    for i, ma in enumerate(parsed.get("main_actions") or []):
        key = str((ma or {}).get("action_key", "")).lower() if isinstance(ma, dict) else ""
        if key not in handlers:
            if key in scope["universe"]["method"]:
                violations.append(Violation("AI_ACTION_NOT_DOCUMENTED", f"{view.name}:main_actions[{i}]", f"method:{key}", "noted"))
            else:
                violations.append(Violation("AI_UNKNOWN_ENTITY", f"{view.name}:main_actions[{i}]", f"method:{key}", "rejected"))
            continue
        claim, vs = check_item(ma.get("explanation"), f"{view.name}:main_actions[{i}]", allowed, uni, refs)
        violations.extend(vs)
        if claim is not None:
            view.ai_action_notes.setdefault(handlers[key], []).append(claim)
    proposed = parsed.get("usage_status")
    if proposed and proposed != view.usage.get("status"):
        violations.append(Violation("AI_USAGE_STATUS_OVERRIDDEN", view.name, f"{proposed} -> {view.usage.get('status')}", "noted"))
    view.ai_narrative = sections
    del run_index
    return violations


def merge_project(project_expl, parsed: dict | None, scope: dict, refs: ReferenceIndex) -> list[Violation]:
    violations: list[Violation] = []
    if parsed is None:
        return [Violation("AI_NO_USABLE_OUTPUT", "project", "provider returned no structured output", "rejected")]
    uni = {t: set() for t in ENTITY_TYPES}
    uni["view"] = set(scope["names"])
    uni["_labels_all"] = set(scope["names"])
    for key in ("project_summary", "role_in_solution", "how_it_is_used"):
        claim, vs = check_item(parsed.get(key), f"project:{key}", scope["allowed_refs"], uni, refs)
        violations += vs
        if claim is not None:
            project_expl.ai_summary.append(claim)
    for i, raw in enumerate(parsed.get("unresolved") or []):
        claim, vs = check_item(raw, f"project:unresolved[{i}]", scope["allowed_refs"], uni, refs)
        violations += vs
        if claim is not None:
            project_expl.ai_summary.append(claim)
    return violations
