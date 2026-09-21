# V4.3 — Instrucciones del Piloto Final de IA (GitHub Copilot)

## Estado que precede a este documento

`docs/V4_3/V4_3_PRE_CLOSURE_COPILOT_PROVIDER_CORRECTION_RESULT.md` y
`docs/V4_3/V4_3_PRE_CLOSURE_DISTRIBUTION_DEPENDENCY_FOLLOWUP_RESULT.md` — estado
`V4_3_READY_FOR_FINAL_AI_PILOT`. Este documento contiene únicamente instrucciones; el piloto
externo final **no se ejecuta dentro de esta tarea**.

## Paso 0 — Construir la distribución limpia del piloto (obligatorio)

El piloto NO debe ejecutarse directamente sobre el repositorio de desarrollo (`E:\IAProyectos\LegacyMapper`).
Debe ejecutarse desde una distribución limpia, runtime-only, construida por el builder actualizado
(`tools/v4_3_r7_build_pilot_distribution.py`), que ahora transporta también
`requirements-copilot.txt` junto a `main.py` y `legacy_documenter/`:

```bat
cd E:\IAProyectos\LegacyMapper
python -m tools.v4_3_r7_build_pilot_distribution "E:\IAProyectos\LegacyMapper_Pilot_Output\dist_v4_3_ai_final"
```

El destino debe estar vacío o no existir (el builder rechaza un destino no vacío para evitar mezclar
una copia previa). La distribución resultante contiene, en su raíz:

```text
main.py
requirements-copilot.txt
legacy_documenter/
```

## Paso 1 — Entrar a la distribución e instalar la dependencia opcional desde ESA distribución

No asumir que el SDK ya está instalado en el entorno global. Instalar siempre desde dentro de la
distribución recién construida, no desde el repositorio de desarrollo:

```bat
cd "E:\IAProyectos\LegacyMapper_Pilot_Output\dist_v4_3_ai_final"
python -m pip install -r requirements-copilot.txt
```

## Paso 2 — Autenticación (responsabilidad externa, no de LegacyMapper)

LegacyMapper no implementa autenticación propia. Verificar, no asumir:

```bat
gh auth status
```

Si no está autenticado:

```bat
gh auth login
```

Confirmar además que el runtime local del SDK (caché bajo
`%LOCALAPPDATA%\github-copilot-sdk\cli\...\prebuilds`) está operativo. Si aparece un
`PermissionError` durante su preparación, es un problema del entorno/caché local del SDK, no de
LegacyMapper; repararlo externamente antes de continuar.

## Paso 3 — Ejecutar el piloto (solo después de los pasos 0–2), desde dentro de la distribución

```bat
cd "E:\IAProyectos\LegacyMapper_Pilot_Output\dist_v4_3_ai_final"
python main.py full "E:\IAProyectos\revision\revision-main" --output "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final" --allow-ai-interpretation --verbose
```

Después:

```bat
python main.py output-manifest "E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final"
```

## Verificaciones mínimas obligatorias tras la ejecución

Revisar, como mínimo, en el directorio de salida:

* `RUN_SUMMARY.json` y `RUN_SUMMARY.md` — estado global, estado de cada stage, en particular
  `AI_INTERPRETATION`.
* `OUTPUT_MANIFEST` (generado por `output-manifest`).
* Estado de `AI_INTERPRETATION`: `SUCCESS` o `FAILED`, y si es `FAILED`, el `error_code` reportado.
* `provider_id` y `model_id` efectivamente usados (el `model_id` debe reflejar el modelo real
  devuelto por el SDK, por ejemplo algo equivalente a `gpt-5.6-luna`, no una cadena vacía, incluso
  si el modelo se resolvió dinámicamente como `auto`).
* `proposal_count` (o el conteo equivalente de propuestas generadas).
* Artefactos de propuesta de IA (`proposals/` o equivalente).
* Documentación humana generada.
* `consumer_projection` generado.

## Si ocurre un error durante el piloto

Con esta corrección aplicada, cualquier `PROVIDER_ERROR`/`TIMEOUT` de `CopilotProvider` debe traer,
dentro de `ProviderError.details` (visible en `RUN_SUMMARY.json`), como mínimo:

* `phase` — en cuál de `client_init`, `client_start`, `list_models`, `create_session`,
  `send_and_wait`, `structured_parse` ocurrió el fallo;
* `exception_type` — el tipo de la excepción real;
* `attempted_model` — el modelo que se intentó usar, incluso si se descubrió dinámicamente (por
  ejemplo `auto`) y el `model_id` original estaba vacío.

Verificar explícitamente que ningún artefacto persistido (`RUN_SUMMARY.json`, `RUN_SUMMARY.md`,
logs, `details`) contenga tokens, `Authorization` headers, cookies u otro material de credencial. Si
apareciera algo así, es un defecto y debe reportarse antes de continuar con el cierre de V4.3 — no
debe tratarse como aceptable "porque el piloto funcionó".

## Qué NO hacer en este piloto

* No ejecutar R9 a partir de este piloto sin aprobación explícita separada.
* No declarar V4.3 cerrada como consecuencia directa de este piloto.
* No modificar `consumer_projection`, hidratación, selección, documentación humana, confianza de
  flows o resolución de terminales para "hacer pasar" el piloto; cualquier hallazgo real debe
  documentarse como una ronda de corrección separada, igual que esta.
