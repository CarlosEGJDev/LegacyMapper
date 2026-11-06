# Prompt — V4.3 R5 — AI Context Budgeting & Strict Grounding

## Modelo recomendado
Claude Opus 4.6.

## Objetivo
Corregir el fallo donde presupuesto interno ≠ prompt real y contexto referencial ≠ contexto útil.

## Requisitos
- presupuesto sobre representación final enviada al provider;
- medir bytes/chars/tokens estimados del payload final;
- `BUDGET_INSUFFICIENT` no continúa ciegamente;
- reducir, particionar o devolver `CONTEXT_TOO_LARGE`;
- usar proyección hidratada;
- preferir FLOW y agregaciones controladas;
- no enviar metadata/continuations masivas innecesarias;
- prompt estricto: no tools, no file inspection, no shell, output contract exacto;
- validar evidence_refs;
- conservar INVALID_STRUCTURED_OUTPUT como fallo seguro.

## No hacer
No crear framework genérico de providers/modelos ni anticipar V5.

## Resultado obligatorio
`docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md`
