# Prompt — V4.3 R8 — Correcciones posteriores al piloto real

## Modelo recomendado
Claude Opus 4.6 para clasificación; Sonnet para correcciones mecánicas.

## Cuándo
Solo si el piloto externo encuentra problemas.

## Entrada
Resultados que el usuario suministre. No asumir acceso directo a `C:\PruebasLegacyMapper`.

## Matriz mínima
A CobLiquidacionDeudaPrev/Page_Load
B cobCargaArcIntRea/btnCargar_Click
C cobChqInsRen/HypGuardar_Click
D flujo unresolved/no-terminal

## Clasificación
BUG_V4_3 / DOCUMENTATION_USABILITY / PROJECTION_GAP / AI_CONTEXT_GAP / UPSTREAM_ANALYSIS_GAP / DEFER_V5 / EXPECTED_LIMITATION

## Regla
No expandir V4.3 hacia agnosticismo tecnológico/provider.

## Resultado obligatorio
`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md`

## Gate
`V4_3_READY_FOR_CLOSURE`
