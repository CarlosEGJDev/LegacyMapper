# Prompt — V4.3 R1 — Contrato de proyección consumible

## Modelo recomendado
Claude Opus 4.6.

## Objetivo
Diseñar el contrato estable que separa evidencia interna exhaustiva de proyecciones consumibles por humanos, IA y futuro plugin.

## Superficies requeridas
1. `human_documentation`: prioridad máxima, español por defecto, resumen antes de detalle.
2. `ai_projection`: evidencia hidratada, compacta y autocontenida con presupuesto real.
3. `consumer_projection`: JSON estable para futuros consumidores sin implementar Plugin Runtime.

## Requisitos
- definir referencia vs registro hidratado;
- IDs estables y trazabilidad;
- `CONFIRMED` / `INTERPRETED` / `UNRESOLVED`;
- AI nunca sustituye evidencia determinista;
- índices exhaustivos siguen siendo fuente técnica;
- español solo para superficie humana; identificadores intactos;
- schema/version de proyecciones;
- compatibilidad V4.2.

## Criterio
Un consumidor no debe necesitar abrir `FUNCTIONAL_FLOWS.json` completo para comprender un flujo.

## Resultado obligatorio
`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`

## Gate
No avanzar a R2 sin revisión humana.
