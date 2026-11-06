# LegacyMapper V5.0 R2 — Contract Validation (PROMPT PROPUESTO — NO EJECUTAR HASTA APROBACIÓN)

## Modelo recomendado

Claude Sonnet 5, medium.

## Objetivo

Validar, sin implementar V5.1, los contratos de `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md` contra IST, outputs V4.3, tests y distribución limpia. Ronda de VALIDACIÓN: solo lectura sobre producción; scripts de inspección permitidos fuera del paquete (scratchpad).

## Lee primero

`AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md`, `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md` (secciones ACCEPTANCE CRITERIA FOR R2 y TEST BASELINE RESOLUTION).

## Tareas

Cubrir los 11 criterios de "ACCEPTANCE CRITERIA FOR R2" de R1, en particular:
1. Detector de colisiones de IDs `EP/FLOW/DAO/PATH` sobre `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1\index` (solo lectura).
2. Tabla campo→entidad/extensión para cada campo de `index/*.json`; lista de campos WebForms/VB/Oracle en el núcleo (debe ser vacía).
3. Prototipo/análisis de round-trip sobre fixtures, sin tocar `legacy_documenter/`.
4. Brecha ABC de provider vs contrato; análisis AST de rutas de desarrollo bajo el paquete runtime.
5. Reproducir y clasificar los 4 tests rojos; proponer (sin aplicar) la corrección y pedir aprobación del Líder Técnico.
6. Verificar que `RUN_SUMMARY.json` acepta `observability` sin romper lectores V4.3.
7. Estimar tamaño/tiempo de `evidence/` sobre IST desde los índices existentes.

## Output obligatorio

`docs/V5/V5_0_R2_CONTRACT_VALIDATION.md` con: STATUS, RESULTADOS POR CRITERIO, DESVIACIONES DE CONTRATO (con propuesta de Decision Record), TESTS/COMANDOS, FILES READ, FILES MODIFIED.

Estados permitidos: `V5_0_R2_CONTRACTS_VALIDATED` | `V5_0_R2_CONTRACT_CHANGES_REQUIRED` | `V5_0_R2_BLOCKED`.

## Restricciones

No implementar V5.1, no modificar producción, tests, CLI, prompts ni `PROJECT_STATE.json`, no ejecutar IA real ni full IST. No aplicar la corrección de los 4 tests sin aprobación explícita.

## Principio

medir → comprender → decidir → fijar contrato → validar → implementar una vez
