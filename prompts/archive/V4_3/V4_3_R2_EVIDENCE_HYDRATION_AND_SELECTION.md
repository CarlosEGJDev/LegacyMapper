# Prompt — V4.3 R2 — Evidence Hydration & Selection

## Modelo recomendado
Claude Opus 4.6.

## Objetivo
Implementar selección e hidratación determinista para que FLOW/PATH/DAO/SP no lleguen como IDs desnudos.

## Requisitos
- usar exclusivamente evidencia ya generada;
- hidratar FLOW con entry point, evento, handler, proyectos/capas, paths relevantes, terminales, SP/SQL/DAO, parámetros disponibles, confianza, unresolved y provenance;
- priorizar caminos confirmados hacia terminales;
- conservar unresolved significativos;
- deduplicar cadenas equivalentes;
- no usar LLM para seleccionar/hidratar;
- no borrar evidencia upstream;
- clasificar conservadoramente ruido técnico/infraestructura sin convertirlo en negocio.

## Tests obligatorios
selección, hidratación, deduplicación, trazabilidad, flujo con DB/SP, flujo sin terminal, unresolved e independencia runtime.

## Resultado obligatorio
`docs/V4_3/V4_3_R2_EVIDENCE_HYDRATION_AND_SELECTION_RESULT.md`

## Revisión humana
resultado, schemas modificados, archivos runtime modificados y conteos de tests.
