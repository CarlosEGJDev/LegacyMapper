# Prompt — V4.3 R7 — Aceptación interna y paquete para piloto real

## Modelo recomendado
Claude Sonnet 4.6.

## Objetivo
Validar internamente y preparar distribución limpia para piloto externo.

## Obligatorio
1. suite completa;
2. separar readiness DEV/GOVERNANCE de PRODUCT/RUNTIME;
3. distribución limpia sin docs/prompts/tests/histórico;
4. `full` funcional;
5. documentación humana y consumer projection en fixtures;
6. manifest de outputs;
7. instrucciones de piloto externo sin incorporar datos reales al repo.

## Importante
Los scripts de `C:\PruebasLegacyMapper` no existen en el repo de desarrollo y no son dependencia.

## Entregables
- `docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md`
- `docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md`

## Estado esperado
`V4_3_READY_FOR_EXTERNAL_REAL_PILOT`
