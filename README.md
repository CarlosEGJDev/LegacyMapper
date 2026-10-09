# LegacyMapper — V5 CLOSED (tag `v5`)

Principio: **Python descubre y resuelve hechos; la IA interpreta después.** El análisis es determinista; la IA es opcional, propone y nunca decide.

## Qué es V5

LegacyMapper V5 está **cerrada** (baseline de release en `docs/V5/V5_FINAL_BASELINE.json`). Contiene:

* Pila principal: **VB.NET WebForms / Oracle** (adapter `vbnet-webforms-oracle` 1.0), validada contra el repositorio IST sin diferencias.
* Segunda tecnología: **Python generic** (adapter `python-generic` 1.0), como **piloto**.
* Evidence normalizada neutral a la tecnología, documentación humana, cache de extracción incremental, contrato de proveedor de IA (propuestas), segmentación determinista de flujos, revisión humana auditada, conocimiento canónico y contratos de consumers/plugins.

**Aviso — piloto circular:** el piloto Python se ejecutó sobre el propio código de LegacyMapper (`SELF_HOSTED_CIRCULAR`). No es un producto externo independiente; `external_independence_claim=false`. La validación externa independiente queda como trabajo futuro.

## Límites que se mantienen

* **Plugin Contract ≠ Plugin Runtime.** Existe el contrato declarativo de solo lectura; el runtime de plugins **no está implementado** y los manifiestos nunca se ejecutan.
* **Sin aprobación ni canonicalización automáticas.** Una propuesta de IA solo pasa a conocimiento canónico por decisión humana explícita.
* La IA real nunca se invoca por defecto; la fuente legada es de solo lectura.

## Dónde leer

* Estado operativo actual (autoridad): `PROJECT_STATE.json`
* Auditoría y baseline final: `docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md`, `docs/V5/V5_FINAL_BASELINE.json`
* Uso: `docs/V5/V5_OPERATIONS_GUIDE.md`
* Cierre formal: `docs/V5/V5_FINAL_CLOSURE.md`
* Historia y continuidad: `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`; lecciones: `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md`
* Siguiente iniciativa (post-V5, planificada): `docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`
* Roadmap e historia: `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
* Recuperación desde un checkout nuevo: `docs/PROJECT_RECOVERY.md`
* Reglas para agentes: `AGENTS.md`, `CLAUDE.md`

## Verificación rápida

```text
python -X utf8 -m unittest discover -s tests
```

## Historia

V4.3 (plan de ejecución en `docs/V4_3/V4_3_EXECUTION_PLAN.md`, prompts R0–R9) y V1–V4 se conservan como historia y compatibilidad. No hay V6 iniciada; el siguiente paso es `POST_V5_PLANNING`.
