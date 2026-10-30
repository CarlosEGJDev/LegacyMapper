"""Observable-usage classification (post-V5 H4-R5).

Existence in source is not use. This module classifies a view from POSITIVE evidence only, and never states that something is unused,
dead or obsolete as fact: absence of observable usage is not evidence of obsolescence.

    ACTIVE_OBSERVABLE  at least one confirmed incoming invocation from another existing, non-backup view
    POSSIBLY_ACTIVE    meaningful behavior and an indirect reference (its name appears in other code), but no confirmed invocation
    UNRESOLVED_USAGE   the project loads views by name through a shell (dynamic loading): no safe conclusion without a confirmed invocation
    LEGACY_CANDIDATE   cautious label only when several indicators align (no incoming, no behavior, no reference, copy/duplicate-looking name)
    ISOLATED           exists, no observable incoming relationship, no shell/dynamic-loading evidence (does NOT mean obsolete)
"""
from __future__ import annotations

import re

from .model import CONFIRMED, INFERRED, UNRESOLVED, Claim

ACTIVE, POSSIBLE, ISOLATED, LEGACY, UNRESOLVED_USAGE = "ACTIVE_OBSERVABLE", "POSSIBLY_ACTIVE", "ISOLATED", "LEGACY_CANDIDATE", "UNRESOLVED_USAGE"
USAGE_STATES = (ACTIVE, POSSIBLE, ISOLATED, LEGACY, UNRESOLVED_USAGE)
EXISTS_IN_SOURCE, REACHABLE, OBSERVABLY_USED = "EXISTS_IN_SOURCE", "REACHABLE_FROM_OBSERVED_FLOW", "OBSERVABLY_USED"
USAGE_ES = {
    ACTIVE: "Uso observable activo", POSSIBLE: "Posiblemente activa", ISOLATED: "Aislada (sin relación entrante observable)",
    LEGACY: "Candidata a heredada (indicadores alineados; no es una conclusión)", UNRESOLVED_USAGE: "Uso no resuelto",
}
FORBIDDEN_WORDS = re.compile(r"(?i)\b(obsolet[oa]s?|c[oó]digo muerto|dead code|no se usa|sin uso|en desuso|no utilizad[oa]|inutilizad[oa]|deprecad[oa])\b")
_COPY_NAME = re.compile(r"(?i)(_\d+$|\d+$|copia|backup|old$|nuevo$|v\d+$)")


def is_backup_path(path: str) -> bool:
    low = path.replace("/", "\\").lower()
    return "\\backup" in low or low.startswith("backup") or "\\copia" in low


def classify(view, *, shell_evidence: int, name_references: int, behavior: bool) -> dict:
    """`view` is a ViewExplanation. Returns {status, ladder, reasons[Claim], evidence_refs, wording}."""
    live = [i for i in view.reached_by if i.target_exists and not is_backup_path(i.file) and not i.source_view.lower().endswith(view.name.lower() + ".ascx")]
    backups = [i for i in view.reached_by if is_backup_path(i.file)]
    refs_live = [r for i in live for r in i.source_refs][:6]
    reasons: list[Claim] = []
    if live:
        status = ACTIVE
        distinct = sorted({i.source_view.rsplit("\\", 1)[-1] for i in live})
        reasons.append(Claim(f"Otras pantallas la abren de forma confirmada: {', '.join(distinct[:5])}{' y otras' if len(distinct) > 5 else ''}.", CONFIRMED,
                             refs_live, "literales url=… en el código de otras vistas (apertura emergente o enlace)"))
        wording = "Esta vista tiene invocaciones entrantes confirmadas desde otras pantallas."
        ladder = OBSERVABLY_USED
    elif behavior and name_references:
        status = POSSIBLE
        reasons.append(Claim("Tiene comportamiento propio y su nombre aparece en el código de otros componentes, pero no se confirmó una invocación que la abra.",
                             INFERRED, [], "referencia por nombre en otro código; sin literal de apertura"))
        wording = "Su uso es posible pero no está confirmado: otros componentes la nombran, sin una invocación de apertura observable."
        ladder = REACHABLE
    elif shell_evidence:
        indicators = [not behavior, not name_references, bool(_COPY_NAME.search(view.name)) or bool(backups)]
        if all(indicators):
            status = LEGACY
            reasons.append(Claim("Varios indicadores coinciden: no se encontró invocación entrante, no tiene comportamiento propio observable, ninguna otra "
                                 "pieza la nombra y su nombre parece una copia o variante. Es solo una señal cautelosa.", INFERRED, [],
                                 "indicadores alineados; sin prueba de desuso"))
            wording = ("No se encontró evidencia observable de uso en el alcance analizado y varios indicadores coinciden; es solo una candidata a "
                       "revisión, no una conclusión.")
        else:
            status = UNRESOLVED_USAGE
            reasons.append(Claim("No se encontró una invocación entrante, pero la aplicación abre vistas por nombre a través de un shell "
                                 "(default.aspx?url=…); por eso el análisis estático no puede concluir si esta vista se usa.", UNRESOLVED, [],
                                 "carga dinámica por nombre desde el shell, confirmada para otras vistas"))
            wording = "Su uso permanece no resuelto porque la aplicación puede cargarla dinámicamente desde el shell."
        ladder = EXISTS_IN_SOURCE
    elif behavior:
        status = POSSIBLE
        reasons.append(Claim("Tiene comportamiento propio observable, pero no se encontró ninguna relación entrante ni mecanismo de carga conocido.", INFERRED, [],
                             "comportamiento propio sin entrada observable"))
        wording = "Su uso es posible pero no está confirmado."
        ladder = EXISTS_IN_SOURCE
    else:
        status = ISOLATED
        reasons.append(Claim("No se encontró ninguna relación entrante observable ni participación en un flujo resuelto. Esto no significa que esté obsoleta.",
                             UNRESOLVED, [], "ausencia de evidencia de uso en el alcance analizado"))
        wording = "No se encontró evidencia observable de uso en el alcance analizado."
        ladder = EXISTS_IN_SOURCE
    if backups:
        reasons.append(Claim(f"{len(backups)} invocación(es) provienen de copias de respaldo del código (carpetas Backup) y no se cuentan como uso.", CONFIRMED,
                             [r for i in backups for r in i.source_refs][:3], "ruta de origen dentro de una carpeta Backup"))
    return {"status": status, "ladder": ladder, "label": USAGE_ES[status], "wording": wording, "reasons": reasons,
            "counts": {"incoming_confirmed": len(live), "incoming_from_backups": len(backups), "name_references": name_references, "shell_pattern": bool(shell_evidence)}}
