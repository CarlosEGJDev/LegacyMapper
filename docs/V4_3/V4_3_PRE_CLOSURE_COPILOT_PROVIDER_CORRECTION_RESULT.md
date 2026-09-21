# V4.3 — Pre-Closure Copilot Provider Correction — Resultado

## 1. Objetivo

Corregir, sin ampliar alcance funcional ni iniciar V5, los tres problemas descubiertos durante el
piloto real de IA con GitHub Copilot SDK ejecutado antes del cierre formal de V4.3:

1. dependencia Python del SDK no declarada en el repositorio;
2. diagnóstico demasiado genérico de `CopilotProvider` (`PROVIDER_ERROR` / "Copilot provider
   request failed" para causas muy distintas);
3. pérdida del modelo realmente intentado (`attempted_model`) cuando `config.model_id` estaba vacío
   y el modelo se descubría dinámicamente (`auto`).

R9 no se ejecuta. V4.3 no se declara cerrada. `consumer_projection`, selección, hidratación,
documentación humana, confianza de flows, resolución de terminales y el contrato funcional de
structured output no se modificaron.

## 2. Causas raíz observadas (evidencia empírica del piloto)

| Situación | Causa raíz | Evidencia |
|---|---|---|
| `ModuleNotFoundError: No module named 'copilot'` | El repositorio no declara `github-copilot-sdk` en ningún archivo de dependencias (LegacyMapper tiene cero dependencias de terceros por diseño; ver `docs/PROJECT_RECOVERY.md`) | Import directo `from copilot import CopilotClient` sin declaración de paquete instalable |
| `JsonRpcError: Not authenticated` | Entorno externo sin `gh auth login`; comportamiento correcto y fuera de alcance de LegacyMapper | El provider no implementaba autenticación propia (correcto) pero tampoco preservaba de qué fase provenía el fallo |
| `PermissionError` en el runtime local del SDK | Caché/runtime local descargado por el SDK, fuera del control de LegacyMapper | No requiere cambio en LegacyMapper; confirma que el diagnóstico por fase es la mitigación correcta |
| Error genérico `PROVIDER_ERROR` / "Copilot provider request failed" | `CopilotProvider._generate` tenía un único `except Exception` que descartaba fase, tipo de excepción y modelo intentado | `legacy_documenter/llm/providers/copilot.py` (versión previa) |
| `model_id=""` en errores posteriores a la selección dinámica de `auto` | `_error()` solo usaba `self.config.model_id`, nunca el modelo resuelto en tiempo de ejecución | Mismo archivo |

## 3. Archivos modificados

* `legacy_documenter/llm/providers/copilot.py` — diagnóstico por fase, `attempted_model`, sanitización.
* `requirements-copilot.txt` (nuevo) — dependencia opcional del SDK.
* `tests/test_v4_3_pre_closure_copilot_provider_correction.py` (nuevo) — T1–T9.
* `docs/V4_3/V4_3_PRE_CLOSURE_COPILOT_PROVIDER_CORRECTION_RESULT.md` (este documento).
* `docs/V4_3/V4_3_FINAL_AI_PILOT_INSTRUCTIONS.md` (nuevo).

No se modificó `consumer_projection`, `hydration`, `selection`, documentación humana, confianza de
flows, resolución de terminales, la lógica de presentación de R8, `PROJECT_STATE.json`, V5 ni el
Plugin Runtime.

## 4. Dependencia agregada

El repositorio no tenía ningún mecanismo de dependencias (ni `requirements.txt` ni
`pyproject.toml`): `docs/PROJECT_RECOVERY.md` y `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
documentan explícitamente "cero dependencias de terceros" y anticipan que, si una ronda futura
introduce una dependencia, un `requirements.txt` (o equivalente) se vuelve parte del contrato en
ese momento. Esta tarea es ese momento, pero solo para el provider opcional COPILOT.

Se agregó `requirements-copilot.txt` (raíz del repositorio), separado del runtime obligatorio,
declarando:

```text
github-copilot-sdk>=1.0.14
```

No se fija la versión exacta `1.0.14` (el prompt lo pide explícitamente); se usa un piso mínimo
sobre la versión validada empíricamente en el piloto. No se creó ningún sistema de packaging nuevo
(no `pyproject.toml`, no `setup.py`); el runtime determinista y el FAKE provider siguen sin
requerir ninguna instalación. `ProviderRegistry` no cambió: sigue conectando únicamente
`FAKE`/`COPILOT`, y `COPILOT` sigue siendo opcional (solo se activa con
`--allow-ai-interpretation` y configuración explícita del provider).

## 5. Cambios diagnósticos en `CopilotProvider`

`_generate` ahora rastrea una variable `phase` que se actualiza inmediatamente antes de cada paso
real del SDK, y una variable `attempted_model` que se actualiza en cuanto el modelo real a usar es
conocido (ya sea el configurado o el descubierto dinámicamente). El único bloque `except Exception`
(y el `except TimeoutError` existente) capturan ahora `phase`, `type(exc).__name__` y
`attempted_model` junto con la excepción, y los pasan a `_error(...)`.

No se creó una jerarquía de excepciones nueva: se sigue usando `ProviderError` existente. No se
amplió el `except TimeoutError` existente (no hay evidencia concreta en el SDK de un tipo de
excepción de timeout distinto); si el SDK use otro tipo específico, debe demostrarse en una ronda
futura antes de tocarlo.

## 6. Fases diagnósticas soportadas

```text
client_init
client_start
list_models
create_session
send_and_wait
structured_parse
```

`structured_parse` se marca inmediatamente después de recibir el evento del SDK y antes de acceder
a `event.data`/`data.content`; la validación de JSON contra el schema sigue siendo no-excepcional
(sigue devolviendo `INVALID_STRUCTURED_OUTPUT`, no un `PROVIDER_ERROR`), sin cambio de
comportamiento.

## 7. Sanitización

Se agregó `_sanitize(message: str) -> str` en `legacy_documenter/llm/providers/copilot.py`, aplicada
únicamente al mensaje crudo de la excepción antes de guardarlo como `details.sanitized_message`
(nunca al `message` fijo y genérico de `ProviderError`, que ya era seguro por construcción). Los
patrones cubren, sin distinguir mayúsculas/minúsculas:

* `Bearer <token>`;
* `*token[:=]<valor>` (incluye `GH_TOKEN`, `GITHUB_TOKEN`, `COPILOT_GITHUB_TOKEN`);
* `api_key`, `session_token`, `oauth_secret`, y cualquier clave que contenga `secret`, seguida de
  `[:=]<valor>`;
* `cookie[:=]<valor>`;
* tokens con forma de GitHub PAT (`ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_...`).

No se copia `repr(exc)` completo a ningún artefacto persistente; solo se conserva el resultado ya
sanitizado, y solo cuando no queda vacío tras la sanitización.

## 8. Manejo de `attempted_model`

* Si `config.model_id` no está vacío, `attempted_model` arranca con ese valor.
* Si está vacío y `list_models()` resuelve un modelo (por ejemplo `auto`), `attempted_model` se
  actualiza a ese valor inmediatamente, antes de `create_session`/`send_and_wait`.
* Cualquier error en una fase posterior a la resolución del modelo conserva ese `attempted_model` en
  `details["attempted_model"]` y en `ProviderError.model_id`/`LLMResponse.model_id`, en vez de volver
  a caer en `model_id=""`.
* El comportamiento de éxito no cambió: `response.model_id` sigue siendo el modelo real devuelto por
  el SDK (por ejemplo `gpt-5.6-luna`), tomado de `data.model`.

## 9. Tests agregados

`tests/test_v4_3_pre_closure_copilot_provider_correction.py`, con mocks únicamente (ningún test
llama a GitHub/Copilot real ni requiere el paquete `copilot` instalado):

* T1 — el provider funciona con un cliente inyectado aunque `copilot` no esté en `sys.modules`.
* T2 — fallo en `client_init` (constructor del cliente) reporta `phase=client_init` y
  `exception_type`.
* T3 — fallo en `client.start()` reporta `phase=client_start`.
* T4 — fallo tipo "Not authenticated" en `list_models()` reporta `phase=list_models` y conserva un
  `sanitized_message` diagnosticable.
* T5 — modelo dinámico (`auto`) se conserva como `attempted_model` cuando falla una fase posterior
  (`create_session`).
* T6 — fallo en `create_session` reporta `phase=create_session`.
* T7 — fallo en `send_and_wait` reporta `phase=send_and_wait`.
* T8 — el camino de éxito existente (structured output válido, modelo real preservado) sigue
  funcionando sin cambios de comportamiento.
* T9 — una excepción sintética con `Authorization: Bearer SECRET_TOKEN` y `GH_TOKEN=SECRET` nunca
  aparece, en ninguna forma, en `ProviderError.details` ni en el resultado serializado.

Además se re-ejecutaron, sin modificarlos, los tests preexistentes de `CopilotProvider`
(`tests/test_v3_r6_1.py`) y el guard de proveedor real (`tests/test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py`), confirmando compatibilidad completa.

## 10. Resultados de tests

```text
Comando: python -m unittest discover -s tests

total:    2096
passed:   1964
failed:   0
errors:   0
skipped:  132
```

`0 failures`, `0 errors` (criterio obligatorio cumplido). El total creció respecto al baseline
previo (2087) porque se agregaron 9 tests nuevos (`test_v4_3_pre_closure_copilot_provider_correction.py`).

## 11. Runtime Independence / Distribution Boundary

`legacy_documenter/llm/providers/copilot.py` importa únicamente biblioteca estándar (`asyncio`,
`inspect`, `json`, `re`, `time`) y módulos internos de `legacy_documenter.llm`; el import del SDK
real (`from copilot import CopilotClient`) sigue siendo perezoso, dentro del método, y solo se
ejecuta si no se inyectó un `client_factory`. Ningún archivo runtime importa ni referencia `docs/`,
`prompts/`, `governance/`, `results/`, `PROJECT_STATE`, `tests/` ni artefactos de desarrollo.
`requirements-copilot.txt` es un archivo de declaración de dependencias para `pip`, no código
importado por el runtime. Verificado: PASS.

## 12. Restricciones verificadas

* No se amplió alcance funcional. PASS.
* No se inició trabajo de V5. PASS.
* No se introdujo Plugin Runtime. PASS.
* No se modificó `consumer_projection`. PASS.
* No se modificó semántica de selección, hidratación, documentación humana, confianza de flows ni
  resolución de terminales. PASS.
* No se declaró V4.3 cerrada. PASS.
* No se ejecutó R9. PASS.
* No se usó Copilot real en tests; no se incorporaron outputs del piloto real como fixtures (todos
  los fixtures son sintéticos). PASS.
* Se preservó: provider id actual, registry actual, FAKE provider, COPILOT provider, API pública,
  contratos actuales, status actuales, structured output actual, CLI actual, funcionamiento
  determinista sin IA, funcionamiento cuando COPILOT no se solicita. PASS.

## 13. Deuda residual

* `docs/PROJECT_RECOVERY.md` y `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md` siguen afirmando
  "cero dependencias de terceros" de forma absoluta; ahora es cierto para el runtime obligatorio
  pero no para el provider opcional COPILOT. Actualizarlos queda fuera del alcance mínimo de esta
  tarea (no fue solicitado explícitamente) y se deja como ítem abierto para R9/cierre formal.
* El timeout de `CopilotProvider` sigue capturando únicamente `TimeoutError`; si una ronda futura
  demuestra empíricamente que el SDK lanza otro tipo específico, debe tratarse entonces, no aquí.
* El tamaño del payload real medido en el piloto (~28K tokens estimados) no se optimiza en esta
  tarea, conforme a la instrucción explícita de no hacerlo todavía.

## 14. Estado final

```text
V4_3_READY_FOR_FINAL_AI_PILOT
```
