# LegacyMapper V5.0 R1 — Architecture Contract (PROMPT PROPUESTO — NO EJECUTAR HASTA APROBACIÓN)

## Modelo recomendado

Claude Sonnet 5, medium (Opus solo ante bloqueo arquitectónico real).

## Objetivo

Fijar los contratos de arquitectura de V5 a partir de `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md`. Ronda de DISEÑO/DOCUMENTAL: no modificar código productivo ni tests.

## Lee primero

`AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md` (secciones OPEN DECISIONS y RECOMMENDED R1 CONTRACT BOUNDARIES), `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`.

## Tareas

1. Resolver (o escalar con recomendación) cada decisión abierta 1–9 de R0.
2. Definir el contrato Normalized Evidence: entidades, campos, reglas de ID (idénticas a V4.3), provenance, estados confirmed/inferred/unresolved.
3. Definir la interfaz de Adapter (entrada: archivos; salida: entidades normalizadas) y mapear el adapter WebForms/VB/Oracle como caso de referencia, sin implementarlo.
4. Definir persistence/cache boundary: evidencia persistida vs proyección regenerable, versionado de schema/stage, reglas de invalidación (solo diseño).
5. Definir el modelo de proyecciones (`index`, `ai_context`, `consumer_projection`) y su garantía de no alterar evidencia.
6. Definir contratos Template / Profile / Renderer con los perfiles `human-functional`, `human-technical`, `ai-context`.
7. Definir el contrato de Provider (ABC completo, capacidades, estados, registro extensible, ciclo de vida, sanitización).
8. Definir política de compatibilidad y migración V4.3 → V5 con los invariantes de R0 como suite de aceptación.
9. Definir campos aditivos de observabilidad (timings/memoria por stage).
10. Decidir el destino de `readiness`, `closure`, `human_review`, `second_review` y módulos V3 acoplados a Copilot.

## Output obligatorio

`docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md` con: STATUS, DECISIONS, CONTRACTS, COMPATIBILITY & MIGRATION, ACCEPTANCE CRITERIA FOR R2, RISKS, FILES READ, FILES MODIFIED.

Estados permitidos: `V5_0_R1_CONTRACT_READY` | `V5_0_R1_BLOCKED`.

## Restricciones

No implementar normalized core, adapters, cache, templates ni providers. No cambiar CLI, prompts, budgets ni baselines cerrados. No ejecutar IA real. No iniciar R2.

## Principio

medir → comprender → fijar contrato → implementar una vez
