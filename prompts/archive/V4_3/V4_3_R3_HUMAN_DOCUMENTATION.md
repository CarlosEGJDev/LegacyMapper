# Prompt — V4.3 R3 — Documentación humana prioritaria

## Modelo recomendado
Claude Sonnet 4.6 si R1/R2 están cerrados; escalar a Opus si surge decisión de contrato.

## Objetivo
Generar documentación humana útil, en español por defecto, basada en la proyección hidratada.

## Cada módulo/componente/flujo debe presentar
1. Qué es / dónde está.
2. Evento/entrada inicial.
3. Qué hace según evidencia.
4. Servicios/capas.
5. Datos/SP/SQL.
6. Qué queda no resuelto.
7. Evidencia/trazabilidad.

## Reglas
- no traducir JSON mecánicamente;
- IDs técnicos no son explicación principal;
- nombres técnicos intactos;
- IA solo aporta `INTERPRETED`;
- sin IA debe existir documentación determinista útil;
- declarar límites.

## Resultado obligatorio
`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md`
