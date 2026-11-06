# Prompt — V4.3 R0 — Baseline empírico y contrato de alcance

## Modelo recomendado
Claude Opus 4.6.

## Objetivo
Formalizar el alcance de V4.3 usando los hallazgos empíricos suministrados como requisitos, sin depender de scripts o archivos externos del piloto.

## Instrucciones
1. Leer estado V4.2, arquitectura, contratos de contexto/documentación/IA y `docs/V4_3/V4_3_EXECUTION_PLAN.md`.
2. No asumir que existe ningún `test_flow_ai*.py`, `list_copilot_models.py` ni carpeta `C:\PruebasLegacyMapper` dentro del repo.
3. Registrar los hallazgos del plan como `EXTERNAL_EMPIRICAL_EVIDENCE`.
4. Inventariar componentes actuales de contexto, documentación, AI interpretation, propuestas y proyecciones.
5. Clasificar cada deuda como `V4_3_REQUIRED`, `V5_DEFERRED` o `NO_CHANGE_REQUIRED`.
6. No implementar código.
7. Mantener fuera de V4.3: agnosticismo tecnológico, framework genérico de providers/modelos, Plugin Runtime, adapters multi-tecnología y rediseño general del core.

## Resultado obligatorio
`docs/V4_3/V4_3_R0_SCOPE_AND_EMPIRICAL_BASELINE_RESULT.md`

## Revisión humana obligatoria
- resultado R0;
- documentos de decisión creados/modificados;
- mapa de componentes afectados;
- criterios de aceptación.

## Prohibido
- modificar runtime;
- copiar scripts del piloto;
- cerrar V4.3.
