"""Deterministic behavioral explainer (post-V5 H4-R4).

Turns the behavioral context (persisted baseline + view sources) into the structured explanation model. It plays the role of the
"interpretation" layer WITHOUT an AI provider: every sentence is a template over evidence, and its status says how it was obtained.
An AI layer would fill the same model through `validate.apply_ai_overlay`; nothing it says can be CONFIRMED.

Wording rules: view-centred, plain language first ("Esta pantalla…", "Al pulsar…"), counts only in facts boxes, no invented business
purpose / actors / use cases / modules / external systems.
"""
from __future__ import annotations

import posixpath
import re
from collections import Counter

from . import wireframe
from .evidence import BehaviorContext, EventEvidence, ViewEvidence
from .model import (
    CONFIRMED, INFERRED, MODULE_CONFIRMED, MODULE_INFERRED, MODULE_NONE, UNRESOLVED, ActionExplanation, BehaviorPath, ClassRole, Claim,
    DataInteractionExplanation, ModuleExplanation, ProjectExplanation, SolutionExplanation, UnresolvedExplanation, ViewExplanation, ViewInvocation,
    ViewMessage,
)

EFFECT_ES = {"read": "consulta", "create": "registro / creación", "update": "modificación", "delete": "eliminación", "mixed": "operación mixta",
             "unknown": "tipo no determinado"}
INFRA = re.compile(r"(?i)^(dbc\.|me\.\w+\.(visible|enabled)|initializecomponent|values\(\)|desplegarerror|setfocus|campos_habilitados|enabledhyperlink)")
_CAMEL = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


def family_of(name: str) -> str:
    tokens = _CAMEL.findall(name)
    if len(tokens) >= 3 and tokens[0].lower() == "uc" and tokens[1].lower() == "pre":
        return "".join(tokens[:3])
    return "".join(tokens[:2]) if len(tokens) >= 2 else name


def src_ref(file: str, line: int) -> str:
    return f"src:{file.replace('/', chr(92))}:{line}"


def _title(v: ViewEvidence) -> tuple[str, str]:
    if v.markup is None:
        return "", ""
    labels = [c for c in v.markup.controls if c.kind == "label" and c.label]
    for c in labels:
        if c.attrs.get("tipo", "").lower() == "titulo":
            return c.label, src_ref(v.markup_file, c.line)
    return "", ""


def _control_label(v: ViewEvidence, control_id: str) -> str:
    if v.markup is not None:
        for c in v.markup.controls:
            if c.id == control_id:
                return wireframe._label_of(c)
    return control_id


def _pretty(label: str, names: dict[str, str]) -> str:
    return ".".join(names.get(p.lower(), p) for p in label.split("."))


def _case_map(v: ViewEvidence, bc: BehaviorContext) -> dict[str, str]:
    names: dict[str, str] = {}
    for d in bc.dao.values():
        for key in (d.get("class"), d.get("method")):
            if key:
                names[str(key).lower()] = str(key)
    if v.code:
        for s in v.code.subs:
            names[s["name"].lower()] = s["name"]
    for e in v.events:
        for key in (e.handler, e.control):
            if key:
                names[key.lower()] = key
        if e.handler_method:
            for part in e.handler_method.split("."):
                names[part.lower()] = part
    names[v.name.lower()] = v.name
    return names


def _sub_range(v: ViewEvidence, handler: str) -> tuple[int, int] | None:
    if not v.code:
        return None
    for s in v.code.subs:
        if s["name"].lower() == handler.lower():
            return s["line"], s.get("end", s["line"] + 400)
    return None


def _effects_phrase(effects: list[str]) -> str:
    uniq = [EFFECT_ES[e] for e in dict.fromkeys(effects)]
    return ", ".join(uniq) if uniq else ""


def _best_chain(e: EventEvidence) -> list[dict]:
    def score(chain):
        return (any(s["kind"] == "procedure" for s in chain), sum(1 for s in chain if s["kind"] in ("data_operation", "procedure")), len(chain))
    return max(e.chains, key=score) if e.chains else []


_CALL = re.compile(r"^((?:[A-Za-z_]\w*\.)*)([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*\(")
_NOT_BUSINESS = {"me", "dbc", "session", "page", "request", "response", "server", "convert", "string", "math", "cstr", "cint", "ds", "dt", "ex", "err",
                 "application", "datetime", "system", "mybase", "viewstate", "cache", "context", "trace", "debug", "int32", "double", "decimal"}


def _business_call(label: str) -> tuple[str, str] | None:
    m = _CALL.match(label.strip())
    if not m:
        return None
    receiver, method = m.group(2), m.group(3)
    first = (m.group(1).split(".")[0] or receiver).lower()
    if first in _NOT_BUSINESS or receiver.lower() in _NOT_BUSINESS or INFRA.match(label.strip()):
        return None
    return receiver, method


def _group_unresolved(e: EventEvidence) -> list[dict]:
    counts: Counter = Counter()
    for u in e.unresolved:
        counts[u["label"]] += 1
    out = []
    for label, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        biz = _business_call(label)
        out.append({"label": label, "count": n, "infrastructure": bool(INFRA.match(label.strip())),
                    "business_call": f"{biz[0]}.{biz[1]}" if biz else ""})
    return out


def _press_label(label: str) -> str:
    if label.startswith("[icono ") and label.endswith("]"):
        return f"Al pulsar el ícono «{label[7:-1]}»"
    return f"Al pulsar «{label}»"


def explain_event(bc: BehaviorContext, v: ViewEvidence, e: EventEvidence, names: dict[str, str]) -> ActionExplanation | None:
    lifecycle = e.kind == "web_lifecycle"
    ops = [o for o in e.data_ops if o["procedure"] or o["method"]]
    if lifecycle and e.event.lower() == "init" and not ops and not any(not INFRA.match(u["label"]) for u in e.unresolved):
        return None  # designer-generated initialisation: not behavior worth documenting
    label = "Al abrirse la vista" if lifecycle and e.event.lower() == "load" else (
        "Al inicializarse la vista" if lifecycle else _press_label(_control_label(v, e.control)))
    refs = [e.ep_id] + ([e.flow_id] if e.flow_id else [])
    chain = _best_chain(e)
    steps = [{"kind": "view", "label": v.name, "status": CONFIRMED, "source_refs": [e.ep_id]}]
    for s in chain:
        step_label = _pretty(s["label"], names)
        if s["kind"] == "data_operation" and step_label.upper().startswith("DAO-"):
            d = bc.dao.get(step_label.upper()) or bc.dao.get(step_label)
            if d and (d.get("class") or d.get("method")):
                step_label = f'{d.get("class") or ""}.{d.get("method") or ""} ({step_label})'.strip(".")
        steps.append({"kind": s["kind"], "label": step_label, "status": CONFIRMED, "source_refs": s["source_refs"] or refs})
    path = BehaviorPath(action=label, steps=steps, flow_id=e.flow_id,
                        status=CONFIRMED if chain else UNRESOLVED, unresolved_calls=_group_unresolved(e))
    data: list[DataInteractionExplanation] = []
    seen = set()
    for o in ops:
        key = (o["procedure"], o["class"], o["method"])
        if key in seen:
            continue
        seen.add(key)
        via = f'{o["class"]}.{o["method"]}'.strip(".")
        effect = o["effect"]
        what = o["procedure"] or via
        plain = {"read": f"Consulta datos mediante «{what}»", "create": f"Registra datos mediante «{what}»", "update": f"Modifica datos mediante «{what}»",
                 "delete": f"Elimina datos mediante «{what}»", "mixed": f"Ejecuta una operación mixta «{what}»"}.get(effect, f"Ejecuta «{what}» (tipo de operación no determinado)")
        data.append(DataInteractionExplanation(object_name=what, kind="stored_procedure" if o["procedure"] else "data_operation", effect=effect,
                                               effect_status=INFERRED if effect != "unknown" else UNRESOLVED, plain=plain, via=via,
                                               source_refs=[r for r in (o["dao_id"], e.flow_id) if r] or refs, status=CONFIRMED))
    non_infra = [u for u in path.unresolved_calls if not u["infrastructure"]]
    if data:
        eff = _effects_phrase([d.effect for d in data if d.effect != "unknown"])
        targets = ", ".join(f"«{d.object_name}»" for d in data[:3]) + (" y otros" if len(data) > 3 else "")
        text = f"{label} se ejecuta {e.handler} y llega a {targets}{' (' + eff + ', tipo deducido del nombre)' if eff else ''}."
        status = INFERRED if eff else CONFIRMED
        basis = "ruta confirmada en el flujo persistido; el tipo de operación se deduce solo del nombre técnico" if eff else "ruta confirmada en el flujo persistido"
    else:
        text = f"{label} se ejecuta {e.handler}; el destino de datos posterior es indeterminado."
        status, basis = CONFIRMED, "manejador confirmado en la evidencia; sin destino de datos confirmado"
        biz = list(dict.fromkeys(u["business_call"] for u in non_infra if u["business_call"]))
        if biz:
            text += f" Llama a {', '.join('«' + b + '»' for b in biz[:3])}{' y otras' if len(biz) > 3 else ''}."
        elif non_infra:
            text += f" Llama a {', '.join('«' + u['label'] + '»' for u in non_infra[:3])}."
    result: list[Claim] = []
    rng = _sub_range(v, e.handler)
    if rng:
        for h in v.outgoing:
            if rng[0] <= h.line <= rng[1] and h.file.lower().endswith(".vb"):
                result.append(Claim(f"Desde este manejador se prepara la apertura de «{h.folder}/{h.view}» "
                                    f"({'ventana emergente' if h.mechanism == 'window_open' else 'enlace'}; línea {h.line}).", CONFIRMED,
                                    [src_ref(h.file, h.line)], "literal url=… en el manejador"))
        if v.code:
            for m in v.code.messages:
                if rng[0] <= m["line"] <= rng[1]:
                    shown = f"Puede mostrar el mensaje «{m['text']}»" if m["text"] else "Puede mostrar un mensaje o error al usuario (el texto no es un literal)"
                    result.append(Claim(f"{shown} (línea {m['line']}).", CONFIRMED, [src_ref(v.code_file, m["line"])], "llamada en el manejador"))
    return ActionExplanation(action=label, trigger=e.control or "MyBase", event=e.event, handler=e.handler,
                             simple=Claim(text, status, refs, basis, entities=[{"type": "event", "name": f"{e.control}.{e.event}"},
                                                                              {"type": "method", "name": e.handler}]),
                             technical_path=path, data=data, result=result,
                             status=CONFIRMED if chain else UNRESOLVED, source_refs=refs)


def explain_view(bc: BehaviorContext, path: str, *, detailed: bool = True) -> ViewExplanation:
    v = bc.view(path)
    names = _case_map(v, bc)
    folder, name = bc.view_folder_and_name(path)
    expl = ViewExplanation(view=path, name=v.name, kind="page" if path.lower().endswith(".aspx") else "user_control", family=family_of(v.name))
    title, title_ref = _title(v)
    expl.title = title
    actions = [a for a in (explain_event(bc, v, e, names) for e in v.events) if a is not None]
    expl.actions = actions
    data_all = [d for a in actions for d in a.data]
    effects = [d.effect for d in data_all]
    incoming = _dedupe_invocations(v.incoming, bc, v)
    expl.reached_by = incoming
    expl.reaches = _dedupe_invocations(v.outgoing, bc, v, outgoing=True)
    claims: list[Claim] = []
    if title:
        claims.append(Claim(f"El título visible de la pantalla es «{title}».", CONFIRMED, [title_ref], "literal en el marcado",
                            entities=[{"type": "view", "name": path}]))
    dialog = any("window_open" == i.mechanism and "selrow" in i.parameters for i in incoming) and (
        v.markup is not None and any(c.kind == "grid" for c in v.markup.controls))
    ops_kinds = set(effects)
    if dialog:
        claims.append(Claim("Parece un diálogo de búsqueda y selección: otras vistas lo abren en una ventana emergente con un parámetro de "
                            "selección y esta vista muestra una grilla de resultados para elegir un registro.", INFERRED,
                            [src_ref(i.file, i.line) for i in incoming[:2]] if incoming else [], "patrón: apertura emergente con «selrow» + grilla",
                            entities=[{"type": "view", "name": path}]))
    if ops_kinds & {"create", "update", "delete"}:
        what = _effects_phrase([e for e in ("create", "update", "delete") if e in ops_kinds])
        claims.append(Claim(f"Parece una pantalla de mantenimiento: sus acciones llegan a operaciones de {what} de datos.", INFERRED,
                            [r for a in actions for r in a.source_refs][:3], "tipo de operación deducido del nombre del procedimiento"))
    elif "read" in ops_kinds and not dialog:
        claims.append(Claim("Parece una pantalla de consulta: las operaciones de datos que alcanza son de lectura.", INFERRED,
                            [r for a in actions for r in a.source_refs][:3], "tipo de operación deducido del nombre del procedimiento"))
    claims.append(Claim("El propósito de negocio de esta pantalla no se puede determinar con la evidencia estática; lo anterior describe lo que "
                        "la pantalla observablemente hace.", UNRESOLVED, [], "ninguna evidencia declara el propósito de negocio"))
    expl.what_it_does = claims
    if v.code:
        seen = set()
        for r in v.code.receives:
            if r["name"] in seen:
                continue
            seen.add(r["name"])
            origin = "parámetro de la URL" if r["via"] == "QueryString" else "parámetro recibido de la vista que la abre (parametrosURL)"
            expl.receives.append(Claim(f"Recibe el {origin} «{r['name']}».", CONFIRMED, [src_ref(v.code_file, r["line"])], "lectura literal en el código"))
        if v.code.session_keys:
            expl.receives.append(Claim("Usa datos de sesión: " + ", ".join(f"«{k}»" for k in v.code.session_keys) + ".", CONFIRMED,
                                       [src_ref(v.code_file, 1)], "literales Session(\"…\") en el código"))
    fe = [e for e in v.events if e.kind == "web_event"]
    event_ids = {e.control for e in fe}
    expl.ui = wireframe.build(path, v.markup, v.markup_file, event_ids, styles=bc.styles, code=v.code)
    # classes by observed role
    roles: list[ClassRole] = []
    if v.inherits:
        roles.append(ClassRole(v.inherits.rsplit(".", 1)[-1], "ui_code_behind", CONFIRMED, "la directiva del marcado declara Inherits", [v.code_file or v.markup_file]))
    for cls in sorted({d["class"] for a in actions for d in [{"class": x.via.split(".")[0]} for x in a.data] if d["class"]}):
        imports_bl = any(".bl." in i.lower() for i in (v.code.imports if v.code else []))
        roles.append(ClassRole(cls, "business_or_data_access", INFERRED,
                               "la clase registra operaciones de datos" + ("; el código importa un espacio de nombres BL" if imports_bl else ""),
                               [r for a in actions for x in a.data if x.via.split(".")[0] == cls for r in x.source_refs][:2]))
    expl.classes = roles
    if v.code:
        expl.messages = [ViewMessage(m["kind"], m["text"], m["event"], m["line"], v.code_file) for m in v.code.messages
                         if m["kind"] != "error_display" or True]
    # unresolved / known / inferred
    unres = UnresolvedExplanation()
    n_chains = sum(1 for a in actions if a.technical_path and a.technical_path.status == CONFIRMED)
    unres.known = [Claim(f"{n_chains} de {len(actions)} acciones tienen una ruta confirmada desde el evento hasta el código del proyecto.", CONFIRMED,
                         [r for a in actions for r in a.source_refs][:4], "flujos persistidos")] if actions else []
    unres.inferred = [c for c in claims if c.status == INFERRED]
    shown = Counter()
    for a in actions:
        for u in (a.technical_path.unresolved_calls if a.technical_path else []):
            if not u["infrastructure"]:
                shown[u["label"]] += u["count"]
    for label, n in sorted(shown.items(), key=lambda kv: (-kv[1], kv[0]))[:8]:
        unres.unresolved.append(Claim(f"La llamada «{label}» no se resolvió hasta código del repositorio.", UNRESOLVED,
                                      [r for a in actions for r in a.source_refs][:1], "límite no resuelto del análisis estático"))
    unres.unresolved.append(Claim("El propósito de negocio, los actores y los textos visibles en ejecución no son determinables estáticamente.", UNRESOLVED, [],
                                  "análisis estático"))
    expl.unresolved = unres
    # measures (not narrative)
    expl.metrics = {
        "has_code_behind": bool(v.code_file), "has_markup": bool(v.markup_file), "events": len(v.events), "actions": len(actions),
        "reaches_business_or_dao": bool(roles[1:]), "reaches_dao": any(a.data for a in actions),
        "reaches_procedure": any(d.kind == "stored_procedure" for d in data_all), "incoming": len(incoming), "outgoing": len(expl.reaches),
        "wireframe": expl.ui.status == "DOCUMENTARY_RECONSTRUCTION",
        "unresolved_paths": sum(1 for a in actions if not a.data and a.technical_path and any(not u["infrastructure"] for u in a.technical_path.unresolved_calls)),
        "effects": sorted(set(effects)), "dialog": dialog,
        "unresolved_calls_non_infra": sum(shown.values()),
        "business_calls": len({u["business_call"] for a in actions if a.technical_path for u in a.technical_path.unresolved_calls if u["business_call"]}), "distinct_procedures": len({d.object_name for d in data_all}),
    }
    return expl


def _dedupe_invocations(hits, bc: BehaviorContext, v: ViewEvidence, *, outgoing: bool = False) -> list[ViewInvocation]:
    out: list[ViewInvocation] = []
    seen: set = set()
    rel_lower = {f.replace("/", "\\").lower() for f in bc.rel_files}
    for h in hits:
        key = (h.file, h.line, h.folder, h.view)
        if key in seen:
            continue
        seen.add(key)
        src_view = h.file[:-3] if h.file.lower().endswith(".vb") else h.file
        target = f"{h.folder}\\{h.view}"
        exists = any(f"{target}{ext}".lower() in rel_lower for ext in (".ascx", ".aspx"))
        if outgoing and h.view.lower() == v.name.lower():
            continue
        out.append(ViewInvocation(source_view=src_view, target_view=target + (".ascx" if f"{target}.ascx".lower() in rel_lower else ".aspx" if exists else ""),
                                  mechanism=h.mechanism, parameters=list(h.params), file=h.file, line=h.line, status=CONFIRMED,
                                  target_exists=exists, note="" if exists else "el destino del literal no existe como vista en el repositorio",
                                  source_refs=[src_ref(h.file, h.line)]))
    out.sort(key=lambda i: (i.source_view.lower(), i.line))
    return out


# ---------------------------------------------------------------- module / project / solution
def explain_modules(bc: BehaviorContext, family_counts: Counter) -> ModuleExplanation:
    """Module structure is claimed only from explicit structure: >= 2 folders, each holding >= 3 views that belong to THIS project's own
    root namespace. Shared/framework controls included from other namespaces are structural areas, not modules; name prefixes are a
    naming convention (listed, never promoted to modules)."""
    root_ns = str(bc.project.get("root_namespace") or "")
    folders: Counter = Counter()
    own_folders: Counter = Counter()
    namespaces: Counter = Counter()
    for p in bc.view_paths:
        folder = posixpath.dirname(p.replace("\\", "/")) or "(raíz del proyecto)"
        folders[folder] += 1
        inh = str(bc.webforms.get(p.replace("/", "\\").lower(), {}).get("inherits") or "")
        ns = inh.rsplit(".", 1)[0] if inh else "(sin Inherits)"
        namespaces[ns] += 1
        if root_ns and ns.lower().startswith(root_ns.lower()):
            own_folders[folder] += 1
    masters = {str(w.get("master_page")) for w in bc.webforms.values() if w.get("master_page")}
    own_big = [f for f, n in own_folders.items() if n >= 3]
    evidence = [
        {"signal": "carpetas con vistas (todas)", "values": dict(folders), "supports_modules": False},
        {"signal": f"carpetas con vistas del espacio de nombres propio «{root_ns}»", "values": dict(own_folders), "supports_modules": len(own_big) >= 2},
        {"signal": "espacios de nombres de las vistas", "values": dict(namespaces), "supports_modules": False},
        {"signal": "subproyectos", "values": {"proyectos_de_referencia_con_vistas": 0}, "supports_modules": False},
        {"signal": "páginas maestras / menús", "values": sorted(masters), "supports_modules": False},
    ]
    families = [{"family": f, "views": n, "status": INFERRED, "note": "convención de nombres, no un módulo"}
                for f, n in sorted(family_counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    if len(own_big) >= 2:
        cls = MODULE_CONFIRMED
        claim = Claim("Las vistas propias del proyecto se reparten en carpetas distintas: la estructura de módulos está respaldada por evidencia explícita.",
                      CONFIRMED, [f"project:{bc.project_path}"], "carpetas con vistas del espacio de nombres propio")
    else:
        cls = MODULE_NONE
        shared = sum(n for f, n in folders.items() if f not in own_folders)
        claim = Claim("No hay una estructura de módulos segura: las vistas propias del proyecto están en una sola carpeta y un solo espacio de nombres; "
                      f"las {shared} vistas restantes son controles compartidos de otros espacios de nombres, no módulos. Los prefijos de nombre se listan "
                      "como convención observada, no como módulos.", UNRESOLVED, [f"project:{bc.project_path}"],
                      "una carpeta propia, sin subproyectos, menús ni metadatos de módulo; prefijos de nombre no son una frontera estructural")
    return ModuleExplanation(classification=cls, claim=claim, evidence_considered=evidence, families=families)


def _project_behavior_sentence(catalog: list[dict]) -> str:
    n = max(1, len(catalog))
    with_data = sum(1 for r in catalog if r["effects"])
    writes = sum(1 for r in catalog if r["writes"] == "sí")
    dialogs = sum(1 for r in catalog if r["purpose"].startswith("Diálogo"))
    ratio = with_data / n
    amount = "la mayoría" if ratio > 0.6 else "una buena parte" if ratio > 0.25 else "una parte"
    parts = [f"La evidencia observable indica que {amount} de sus pantallas llega con certeza a operaciones de datos de clases de otros proyectos"]
    if writes:
        parts.append("algunas de ellas registran o modifican datos")
    if dialogs:
        parts.append("y varias funcionan como ventanas de búsqueda y selección")
    rest = max(0, n - with_data)
    tail = (f"; en el resto el análisis no confirma el destino de los datos ({'una parte' if rest / n < 0.6 else 'la mayoría'} de las pantallas)."
            if rest else ".")
    return ", ".join(parts) + tail


def explain_solution_and_project(bc: BehaviorContext, ctx, solution_slug: str | None, view_expls: list[ViewExplanation], catalog: list[dict],
                                 module: ModuleExplanation) -> tuple[SolutionExplanation, ProjectExplanation]:
    modules = ctx.area_modules(solution_slug) if solution_slug in ctx.solutions else []
    sol_name = bc.solutions[0]["name"] if bc.solutions else (solution_slug or "")
    projects = [{"name": m.values["name"], "path": m.values["path"], "layer": m.values["layer"], "layer_status": m.values["layer_status"]} for m in modules]
    layer_es = {"presentation": "presentación (pantallas)", "logic": "lógica / servicios", "data_access": "acceso a datos", "unclassified": "sin clasificar"}
    sol = SolutionExplanation(name=sol_name, projects=projects)
    names = ", ".join(f"«{p['name']}»" for p in projects)
    sol.summary = [
        Claim(f"La solución «{sol_name}» agrupa {len(projects)} proyectos: {names}." if projects else f"La solución «{sol_name}» agrupa los proyectos identificados por el análisis.",
              CONFIRMED, [f"solution:{sol_name}"], "contención en el archivo .sln"),
        Claim("Estructuralmente, el proyecto web contiene las pantallas y referencia a los proyectos de apoyo; ese reparto es una inferencia por reglas "
              "estructurales, no una descripción de negocio.", INFERRED, [], "reglas estructurales de capa (pantallas propias, referencias)"),
    ]
    sol.not_inferable = [Claim("El propósito de negocio de la solución no puede deducirse del código; los nombres de la solución y de sus proyectos no son evidencia de ese propósito.",
                               UNRESOLVED, [], "ninguna evidencia declara el propósito")]
    sol.facts = {"proyectos": len(projects), "capas": {p["name"]: layer_es.get(p["layer"], p["layer"]) for p in projects}}
    mod = next((m for m in modules if m.values["name"] == bc.project["name"]), None)
    refs = [r.get("name") for r in bc.project.get("project_references", [])]
    n_views = len(catalog)
    proj = ProjectExplanation(name=bc.project["name"], path=bc.project_path)
    proj.summary = [
        Claim(f"«{bc.project['name']}» es el proyecto web de la solución: contiene las pantallas (controles de usuario) con las que "
              "se trabaja y las acciones que cada una dispara.", INFERRED, [f"project:{bc.project_path}"],
              "el proyecto declara pantallas .ascx/.aspx; el rol de capa es inferido por regla estructural"),
        Claim(_project_behavior_sentence(catalog), INFERRED, [], "patrones de acciones y de invocaciones entre vistas (proporciones calculadas)"),
    ]
    proj.role_in_solution = [Claim(f"Dentro de «{sol_name}» ocupa la capa de {layer_es.get(mod.values['layer'], '—') if mod else 'presentación'} "
                                   "(capa inferida) y depende de " + (", ".join(f"«{r}»" for r in refs) or "otros proyectos") + ".", INFERRED,
                                   [f"project:{bc.project_path}"], "referencias de proyecto declaradas + regla de capa")]
    proj.structural_areas = [Claim(f"Las vistas están en {len(module.evidence_considered[0]['values'])} carpeta(s): "
                                   + ", ".join(f"{k} ({v})" for k, v in module.evidence_considered[0]["values"].items()) + ".", CONFIRMED,
                                   [f"project:{bc.project_path}"], "elementos de contenido del archivo de proyecto")]
    proj.dependencies = [Claim("Referencias de proyecto declaradas: " + (", ".join(f"«{r}»" for r in refs) or "ninguna") + ".", CONFIRMED,
                               [f"project:{bc.project_path}"], "ProjectReference en el archivo de proyecto")]
    by_eff_views: dict[str, list[str]] = {}
    for e in catalog:
        for eff in e["effects"]:
            by_eff_views.setdefault(eff, []).append(e["name"])

    def _names(names: list[str]) -> str:
        return ", ".join(sorted(names)[:6]) + (" y otras" if len(names) > 6 else "")
    proj.data_patterns = [Claim("Pantallas con acceso a datos observable, según el tipo de operación (deducido del nombre): " +
                                "; ".join(f"{EFFECT_ES[k]}: {_names(v)}" for k, v in sorted(by_eff_views.items())) + ".", INFERRED, [],
                                "tipo inferido del nombre técnico de la operación")] if by_eff_views else []
    unres_total = mod.values["unresolved_total"] if mod else 0
    proj.unresolved = UnresolvedExplanation(
        known=[Claim("Las acciones se detienen con frecuencia ante llamadas a clases de otros proyectos o de la plataforma que el análisis no sigue.", CONFIRMED,
                     [], "límites no resueltos persistidos")],
        unresolved=[Claim("El propósito de negocio de cada pantalla y los textos visibles en ejecución no son determinables estáticamente.", UNRESOLVED, [], "análisis estático")])
    proj.facts = {"vistas": n_views, "pantallas_con_eventos": sum(1 for e in catalog if e["actions"]), "elementos_no_resueltos": unres_total,
                  "referencias_de_proyecto": refs}
    return sol, proj
