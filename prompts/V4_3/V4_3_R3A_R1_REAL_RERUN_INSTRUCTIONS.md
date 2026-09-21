# V4.3 — Instrucciones para rerun real R3 después de R3A-R1

## Rutas vigentes

LegacyMapper:
`C:\dev\LegacyMapper`

Repositorio legacy real:
`C:\inetpub\wwwroot\2010\IST\Operacional`

Salida nueva recomendada:
`C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1`

Distribución limpia recomendada:
`C:\PruebasLegacyMapper\dist\v4_3_ai_r3a_r1`

## Precondición

`docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`
debe indicar:

`V4_3_READY_FOR_R3_RERUN`

No ejecutar R9 en este rerun.

## 1. Reconstruir distribución limpia

```bat
cd /d C:\dev\LegacyMapper
python -m tools.v4_3_r7_build_pilot_distribution "C:\PruebasLegacyMapper\dist\v4_3_ai_r3a_r1"
```

El destino debe no existir o estar vacío.

Verificar que contenga:

```text
main.py
requirements-copilot.txt
legacy_documenter\
```

## 2. Instalar dependencia opcional de Copilot

```bat
cd /d C:\PruebasLegacyMapper\dist\v4_3_ai_r3a_r1
python -m pip install -r requirements-copilot.txt
```

## 3. Verificar GitHub CLI

En el rebaseline de este notebook, `gh` no estaba disponible en PATH.

```bat
where gh
gh --version
gh auth status
```

Si `gh` no está instalado, instalar GitHub CLI antes de continuar.

Después:

```bat
gh auth login
gh auth status
```

## 4. Ejecutar piloto real

```bat
cd /d C:\PruebasLegacyMapper\dist\v4_3_ai_r3a_r1
python main.py full "C:\inetpub\wwwroot\2010\IST\Operacional" --output "C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1" --verbose --allow-ai-interpretation
```

## 5. Generar manifest

```bat
python main.py output-manifest "C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1"
```

## 6. Verificaciones obligatorias

Revisar:

```text
RUN_SUMMARY.json
RUN_SUMMARY.md
proposals\AI_PROPOSALS.json
proposals\AI_PROPOSALS_PENDING_REVIEW.md
OUTPUT_MANIFEST.json
```

Esperado:

```text
status: SUCCESS
AI_INTERPRETATION: SUCCESS
PROPOSAL_GENERATION: SUCCESS
ai_invoked: true
canonical knowledge produced: false
Technical Lead approval: false
```

Verificar también:

- provider/model reales;
- ausencia de secretos;
- cantidad de propuestas;
- diversidad de propuestas;
- ausencia de `CONTEXT_TOO_LARGE`.

## 7. Criterio importante

R3A-R1 ya demostró determinísticamente que el paquete final puede incluir un flow rico (`FLOW-0004993422`) contra el output real reconstruido.

Si en el rerun real el modelo sigue sin generar findings ricos pese a recibir evidencia rica, el siguiente problema ya no sería selection/packing sino la interpretación/finding del LLM.

No modificar otra vez el selector sin demostrarlo.

## 8. Después del rerun

No ejecutar R9 automáticamente.

Entregar para revisión:

```text
RUN_SUMMARY.json
RUN_SUMMARY.md
AI_PROPOSALS.json
AI_PROPOSALS_PENDING_REVIEW.md
OUTPUT_MANIFEST.json
```
