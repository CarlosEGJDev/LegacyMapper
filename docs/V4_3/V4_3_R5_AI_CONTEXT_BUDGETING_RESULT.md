# V4.3 — R5 — Presupuesto de contexto de IA y anclaje estricto — Resultado

## Estado de esta ronda

`V4_3_R5_RESULT_IMPLEMENTED_PENDING_HUMAN_REVIEW`. Como R2/R3/R4, esta ronda implementa código de producción.
El `Gate` de R4 ("Pendiente de aprobación por el Líder Técnico antes de iniciar R5", secciones 12.6 y 13.9 de
`docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md`) queda satisfecho por la misma vía que
R0→R1→R2→R3→R4: la instrucción directa del Líder Técnico de ejecutar R5
(`ejecuta V4_3_R5_AI_CONTEXT_BUDGETING.md`). Esta ronda no cierra ni versiona V4.3 (sigue correspondiendo
exclusivamente a R9), no modifica `PROJECT_STATE.json` y no inicia R6.

`REAL_AI_RUNTIME_CALL_ALLOWED=false` sigue vigente: ningún test de esta ronda alcanza un proveedor real; todos
inyectan `FakeLLMProvider` (o una subclase que falla ruidosamente si se la llama) explícitamente. No se ejecutó
ninguna verificación manual del camino `--allow-ai-interpretation` (`AGENTS.md` §"Manual AI-Path Verification").

## 1. Objetivo

Corregir el fallo donde **presupuesto interno ≠ prompt real** y **contexto referencial ≠ contexto útil**
(`prompts/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING.md`).

Concretamente, cerrar los dos defectos que R0 dejó asignados a esta ronda:

- **D-01 / EEE-02**: un paquete `SYSTEM` sin techo obligatorio produjo un prompt real de ~13.8 MB / ~3.6 M
  tokens aunque la estimación interna fuese mucho menor. La causa verificada es doble: (a) nada obligaba a un
  presupuesto en el paquete, y (b) **nada medía el payload final serializado** — el único chequeo de tamaño
  existente (`FakeLLMProvider._status`) compara `context["statistics"]["estimated_tokens"]`, es decir el
  paquete solo, y además en producción nunca se activa porque
  `ai_interpretation._resolve_provider` construye un `ProviderConfig` sin `context_window`.
- **D-04 / EEE-05**: la instrucción de sistema no prohibía explícitamente el uso de herramientas ni exigía
  devolver únicamente la estructura pedida.

Y hacerlo implementando el contrato ya aprobado en R1 §5.2 (`ai_projection` /
`AI_HYDRATED_PROJECTION 1.0`), no rediseñándolo.

## 2. Qué se implementó

### 2.1 `legacy_documenter/context/ai_projection.py` (nuevo, 304 líneas)

Ubicación elegida: el mismo paquete `legacy_documenter/context/` donde ya viven `hydration.py` (R2, la fuente
de los registros), `composer.py` (los perfiles que se reutilizan) y `resolver.py`. Es la capa a la que
pertenece por responsabilidad (construcción de paquetes de contexto) y evita una dependencia nueva desde
`llm/` o `documentation/` hacia el modelo de evidencia.

Contrato expuesto:

| Símbolo | Responsabilidad |
|---|---|
| `AiProjectionBuilder.build(flow_ids, ix, source_snapshot=None, profile="SMALL", budget=None)` | Hidrata `flow_ids` llamando a `EvidenceHydrator.hydrate_flow` (nunca reimplementa la hidratación) y los empaqueta bajo presupuesto |
| `AiProjectionBuilder.package(records, ...)` | La misma aplicación de presupuesto sobre registros ya hidratados |
| `build_ai_projection(...)` | Envoltorio a nivel de módulo sobre `build` |
| `select_flow_ids(ix, max_flows)` | Selección determinista y **acotada** de flujos (confirmed → inferred → unresolved, luego `flow_id` ascendente). `max_flows` es obligatorio y positivo |
| `record_reference_ids(record)` / `package_reference_ids(package)` | Conjunto cerrado de ids citables por la IA |
| `ALLOWED_PROFILES`, `PROFILE_REDUCTION`, `PACKAGE_ID_PREFIX`, `InterpretedContentError` | Constantes/errores del contrato |

Reglas implementadas:

- **Perfiles**: `TINY`/`SMALL`/`MEDIUM`/`LARGE` **importados de `composer.PROFILES`**, no redefinidos
  (`ALLOWED_PROFILES == set(PROFILES) - {"FULL"}`, verificado por test).
- **`FULL` rechazado**: `ValueError` explícito. Motivo: `FULL` es `(10**9, 10**9)`, es decir efectivamente
  ilimitado — exactamente el defecto D-01. R1 §5.2 es literal: "un paquete `ai_projection` sin techo de
  presupuesto no es conforme a este contrato". Se rechaza en vez de recortarse en silencio para que un
  llamador nunca pueda creer que obtuvo un paquete ilimitado.
- **`flow_ids` obligatorio**: `build(None, ...)` es `ValueError`. No existe un barrido `SYSTEM` implícito.
- **Sobre aditivo, no nuevo**: mismos campos de envoltura que `ContextComposer.compose`
  (`package_type`/`schema_version`/`package_id`/`source_snapshot`/`statistics`/`truncation`/`selection_policy`/
  `provenance`), con `records` cuyo elemento es ahora un `HydratedRecord` en lugar de una `Reference`.
- **`package_id`**: `AIP-` + SHA-256 canónico (`json.dumps(sort_keys=True, separators=(",",":"))`) sobre el
  cuerpo serializado — **mismo método de cálculo** que `CTX-`, solo cambia el prefijo (R1 §4).
- **`statistics`/`truncation`/`completeness`**: mismo patrón que `composer.py`, incluyendo
  `BUDGET_INSUFFICIENT` cuando ni el contenido mínimo (envoltura + un registro) cabe.
- **Sin invención ni alteración de `confidence`**: los registros se copian tal cual salen del hidratador
  (test: `test_records_are_exactly_what_the_hydrator_produces`).
- **Sin `INTERPRETED` de entrada**: `_reject_interpreted_content` levanta `InterpretedContentError` si un
  registro contiene `"interpreted"`, `"ai_interpretation"` o `"interpretations"` como clave o valor. R1 §5.2
  queda impuesta **estructuralmente**, no solo documentada.
- **Independencia de runtime**: no importa `legacy_documenter.llm` (verificado por AST, no por texto), no lee
  ni escribe archivos, no llama a ningún proveedor.

Detalle de implementación del presupuesto por caracteres: en lugar de reserializar el cuerpo entero una vez
por registro candidato, se mide el coste exacto de la envoltura (`records: []`) y el coste canónico de cada
registro, usando la identidad exacta de JSON `len("[a,b,c]") == 2 + Σlen(itemᵢ) + (n-1)`. Es lineal y
exacto, no una aproximación (test: `test_statistics_character_count_matches_the_serialized_body`).

### 2.2 `legacy_documenter/llm/core.py` (modificado, 84 → 114 líneas)

Dos funciones nuevas, provider-neutrales, en el módulo donde ya viven `LLMRequest`/`STATUSES`:

- `render_request_payload(request, schema=None) -> str`: la representación final serializada que de verdad
  viaja al proveedor. **Es el cuerpo de `CopilotProvider._prompt` movido verbatim**, no una reimplementación:
  mismo envoltorio `<system_instruction>`/`<task_instruction>`/`<evidence_policy>`/`<claim_policy>`/
  `<missing_information_policy>`/`<context>`/`<output_contract>`+schema.
- `measure_request_payload(request, schema=None, chars_per_token=4) -> dict`: sus métricas
  (`payload_bytes`, `payload_characters`, `payload_estimated_tokens`, `chars_per_token`, `estimation_method`,
  `schema_included`), con el mismo método de estimación `ceil(chars/chars_per_token)` que ya usan
  `composer.py` y `ai_projection.py`, para que comparar estimación interna contra payload final sea comparar
  lo mismo.

Esto es **deduplicación de lógica que ya existía en un solo sitio**, no un framework nuevo: no se tocó
`LLMProvider`, `ProviderRegistry`, `ProviderConfig` ni la interfaz abstracta, y no se añadió soporte para
ningún proveedor nuevo.

### 2.3 `legacy_documenter/llm/providers/copilot.py` (modificado, 68 → 73 líneas)

`CopilotProvider._prompt` ahora **delega** en `render_request_payload` (misma firma, misma salida; test
`test_copilot_prompt_delegates_to_the_shared_renderer` compara byte a byte, y
`test_copilot_module_no_longer_holds_its_own_copy_of_the_wrapper` verifica que no queda una segunda copia que
pueda divergir). Ningún cambio en el transporte, la sesión, los permisos denegados ni el manejo de errores.

### 2.4 `legacy_documenter/orchestration/ai_interpretation.py` (modificado, 190 → 348 líneas)

**Decisión: se migró `run_ai_interpretation` in-place**, no se creó una función paralela.

Justificación: el prompt pide evaluar seriamente la migración directa antes de tomar la salida de la función
nueva, porque dejar el único camino de producción real sin corregir contradice el objetivo central de la
ronda. La migración resultó de bajo riesgo porque **la firma pública no se rompe**: los parámetros nuevos
(`flow_ids=None`, `profile="SMALL"`) son opcionales y con valor por defecto, de modo que el único llamador real
(`legacy_documenter/cli/full_pipeline.py::_run_ai_interpretation_stage`, que invoca
`run_ai_interpretation(output, provider=provider)`) **no requirió ningún cambio**, ni él ni ningún test
existente. Se verificó por búsqueda exhaustiva de `run_ai_interpretation(` en todo el repositorio: un único
llamador de producción y los tests de `tests/test_v4_2_r4_ai_interpretation_and_proposal_integration.py`,
todos en verde sin modificación.

Cambios:

1. **Fuente del paquete**: ya no `ContextComposer(resolver).compose("SYSTEM", profile="SMALL")`. Ahora
   `AiProjectionBuilder().build(flow_ids_acotados, ix, source_snapshot, profile)`, donde `ix` son los índices
   de **esta misma ejecución** (`<output_dir>/index/*.json`) y `source_snapshot` sale de
   `<output_dir>/ai_context/SYSTEM_CONTEXT.json`. La frontera de contexto de V4.2-R4 (evidencia de la
   ejecución actual, nunca un snapshot histórico) se preserva intacta, y el fallo cerrado
   (`CONTEXT_UNAVAILABLE`) sigue ocurriendo cuando falta cualquiera de las dos fuentes.
2. **Alcance por flujo**: sin `flow_ids` explícitos se usa `select_flow_ids(ix, PROFILES[profile][0])` — un
   conjunto acotado y determinista, nunca "todos los flujos".
3. **Gate de payload final** antes de `provider.structured_generate` (sección 3).
4. **`SYSTEM_INSTRUCTION` extendida** con la prohibición de herramientas (sección 4).
5. **`_validate_findings`** valida contra `package_reference_ids(package)` en vez de
   `{record["ref"] ...}` (sección 5).
6. **`INVALID_STRUCTURED_OUTPUT` intacto** como fallo seguro posterior a la llamada (sección 6).

### 2.5 `legacy_documenter/orchestration/_run_evidence_io.py` (nuevo, 44 líneas)

Carga de `index/*.json` y del `source_snapshot`, extraída de `ai_interpretation.py` siguiendo el patrón de
módulo interno `_*` detrás de una fachada sin cambios que el repositorio ya usa
(`knowledge/_readiness_io.py`, `extractors/_database_*.py`). Motivo explícito: sin esta extracción,
`ai_interpretation.py` acumulaba cinco responsabilidades según el inventario de mantenibilidad
(`domain_modeling`, `filesystem`, `provider_or_network`, `serialization`, `validation`) y cruzaba de `MEDIUM`
a **`VERY_HIGH`**; con ella se queda en `HIGH` (ver sección 9). `ai_interpretation` reexporta ambas funciones
como `_load_indexes`/`_load_source_snapshot`, por lo que su superficie interna no cambia.

### 2.6 `legacy_documenter/context/__init__.py` (modificado)

Añadido el párrafo de la etapa `ai_projection` al docstring del paquete, junto a las etapas de escritura,
lectura e hidratación ya documentadas (mismo criterio que V4.1-R8 y V4.3-R2).

## 3. Medición y límite del payload final real

### 3.1 Qué se mide

`measure_request_payload(request, FINDING_SCHEMA)` sobre el `LLMRequest` ya construido, es decir sobre el
string exacto que `render_request_payload` produce y que el adaptador de proveedor envía: `system_instruction`,
`user_instruction`, las tres políticas, el `context` completo serializado (sobre + `records` hidratados +
`statistics` + `truncation`) y el `<output_contract>` con el `schema`. Nada de esto lo cuenta
`package["statistics"]["estimated_tokens"]`.

Medición real sobre el fixture `tests/fixtures/v4_2_r3_sample` (1 flujo hidratado, perfil `SMALL`):

| Métrica | Valor |
|---|---|
| `package.statistics.estimated_tokens` (presupuesto interno) | 1.006 |
| `payload_estimated_tokens` (payload final medido) | ~1.642 |

Es decir, el payload real es ~1,63× el presupuesto interno incluso en el caso más pequeño posible. El test
`test_measured_payload_exceeds_the_packages_own_estimate` lo fija como garantía permanente: es la
demostración ejecutable de D-01 dentro de la propia suite.

### 3.2 Qué límite se aplica

**Corrección posterior a la implementación inicial de R5** (esta misma ronda, antes de que se iniciara R6):
la versión original de `_payload_token_limit(provider)` usaba `context_window` completo, sin reservar, como
techo del payload de *entrada*. Eso podía autorizar en teoría `input_tokens + max_output_tokens >
context_window` una vez el proveedor generase realmente su respuesta, porque nada reservaba capacidad de
salida dentro de la misma ventana. Corregido de forma determinista y fail-closed:

`_payload_token_limit(provider, request_max_output_tokens=None)`:

1. Si `provider.capabilities().context_window` **no** es un entero positivo válido: se aplica, sin cambios
   respecto a la versión original, el límite propio de LegacyMapper —
   **`DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS = 16000`** — sin ampliarlo por ningún `max_output_tokens` que el
   proveedor pudiera declarar por separado. Este es el caso normal en producción hoy, porque
   `_resolve_provider` no fija `context_window` en el `ProviderConfig` que construye.
2. Si `context_window` **sí** es válido, la ventana se comparte con la salida en vez de entregarse entera al
   payload de entrada:

   ```
   effective_input_limit = context_window - reserved_output_tokens
   ```

   `reserved_output_tokens` se obtiene de forma explícita y determinista, en este orden:

   - se prefiere `provider.capabilities().max_output_tokens` cuando es un entero positivo válido;
   - si además se conoce el `max_output_tokens` de la request concreta y es un entero positivo **menor** que
     el anterior, se usa ese valor menor en su lugar — es la reserva que esa request en particular podría
     realmente llegar a producir, nunca más que lo que el proveedor ya declaró como su propio techo;
   - si el proveedor no declara `max_output_tokens` en absoluto, `reserved_output_tokens = 0`: no hay ninguna
     otra cifra explícita y determinista que reservar, y LegacyMapper no la inventa.
3. `effective_input_limit` nunca puede quedar en cero o negativo sin que el llamador falle cerrado. Cuando la
   reserva consume toda la ventana o más, `run_ai_interpretation` devuelve `CONTEXT_TOO_LARGE` con
   `provider_called=False` **antes** de construir el paquete o la request — no solo antes de llamar al
   proveedor —, porque no hay ningún tamaño de entrada, por pequeño que sea, que pudiera convivir con esa
   reserva.

`_payload_token_limit` en sí misma nunca lanza excepción por esto: solo devuelve el número (que puede ser
`<= 0`), y es el llamador quien decide fallar cerrado sobre él.

Nunca se queda sin límite en ninguno de los dos casos.

**Justificación del 16.000** (sin cambios respecto a la versión original, explícita, no implícita): `EEE-04`
registró que una proyección `FLOW` hidratada de ~5.600 tokens fue suficiente para una interpretación útil y
trazable. 16.000 es ~2,9× ese tamaño, lo que deja margen real para las instrucciones, las políticas y el
schema que envuelven al paquete (todo lo que `measure_request_payload` cuenta y el presupuesto interno no), y
sigue estando ~225× por debajo del payload de ~3,6 M tokens de `EEE-02`. Con la estimación compartida de 4
caracteres por token son ~64.000 caracteres.

Tests: `test_default_limit_is_bounded_and_above_the_empirically_useful_size`,
`test_default_limit_applies_when_the_provider_declares_no_window`,
`test_provider_context_window_is_preferred_over_the_default_limit`,
`test_provider_without_context_window_keeps_the_default_input_payload_ceiling` (`OutputReservationGateTests`).

**Tests de la reserva de capacidad de salida** (`OutputReservationGateTests`, todos en verde):

| Caso | Test |
|---|---|
| `context_window=16000`, `max_output_tokens=2000` → límite efectivo `14000`, nunca `16000` | `test_effective_limit_reserves_the_declared_max_output_tokens` |
| `max_output_tokens` de la request, cuando es menor, estrecha la reserva aún más; nunca la ensancha por encima de lo que el proveedor ya declaró | `test_a_smaller_request_max_output_tokens_narrows_the_reservation_further` |
| Payload que cabe bajo `16000` pero no bajo el límite efectivo `14000`: `CONTEXT_TOO_LARGE`, `provider_called=False` | `test_payload_fitting_under_the_window_but_not_under_the_reserved_limit_is_rejected` |
| Payload que sí cabe bajo el límite efectivo `14000`: `SUCCESS` | `test_payload_fitting_under_the_reserved_limit_is_accepted` |
| Reserva igual a `context_window` (`2000`/`2000`): falla cerrado sin llamar al proveedor | `test_reservation_consuming_the_whole_window_fails_closed_without_calling_the_provider` |
| Reserva mayor que `context_window` (`2000`/`5000`, límite efectivo `-3000`): falla cerrado igual | `test_reservation_larger_than_the_window_also_fails_closed` |
| Proveedor sin `context_window` (aunque declare `max_output_tokens`): sigue aplicando `DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS=16000` sin ampliarlo | `test_provider_without_context_window_keeps_the_default_input_payload_ceiling` |
| La medición sigue siendo sobre el payload final serializado real; la reserva solo cambia el umbral de comparación | `test_gate_still_measures_the_real_final_serialized_payload` |

### 3.3 Política exacta cuando se excede: **reducir una vez, luego fallar cerrado**

Implementada en `_build_within_budget`:

1. Intento 1 con el perfil solicitado (por defecto `SMALL`).
2. Si el paquete vuelve `BUDGET_INSUFFICIENT`, **o** el payload medido supera el límite aplicable, se hace
   exactamente **un** reintento con el siguiente perfil menor (`PROFILE_REDUCTION`: `LARGE`→`MEDIUM`,
   `MEDIUM`→`SMALL`, `SMALL`→`TINY`).
3. Si el segundo intento tampoco cabe — o el perfil solicitado ya era el más pequeño — **no se llama al
   proveedor** y se devuelve `AiInterpretationResult(status="CONTEXT_TOO_LARGE", provider_called=False)`,
   reutilizando el estado ya existente en `legacy_documenter/llm/core.py::STATUSES`.

Por qué un solo reintento y no un bucle de reducción abierto: cada reducción descarta evidencia real; moler el
paquete en silencio hasta que "algo quepa" sería exactamente el comportamiento de "continuar ciegamente" que
esta ronda existe para eliminar. La razón de cada intento rechazado se acumula en `error_message`
(`payload_estimated_tokens=N>limit=M:profile=SMALL; budget_insufficient:profile=TINY`), de modo que un rechazo
es diagnosticable sin reejecutar. Tests: `test_reduce_then_retry_is_attempted_exactly_once`,
`test_oversized_payload_returns_context_too_large_without_calling_the_provider`,
`test_budget_insufficient_never_continues_to_the_provider`,
`test_gate_reports_the_measured_payload_size_it_rejected`.

Que el proveedor **no** se llama se prueba conductualmente, no por inspección: los tests del gate inyectan un
`_ExplodingProvider` cuyo `structured_generate` lanza `AssertionError`; si el gate fallase, el test fallaría.

Desde la corrección de la sección 3.2, `run_ai_interpretation` comprueba `limit <= 0` inmediatamente después de
`_payload_token_limit(provider)` y, si se cumple, devuelve `CONTEXT_TOO_LARGE`/`provider_called=False` **antes**
de construir ningún paquete o request (no solo antes de llamar al proveedor): cuando la reserva de salida ya
consume toda la ventana, no hay ningún tamaño de paquete que pudiera cambiar el resultado, así que no se gasta
trabajo en construirlo. Tests: `test_reservation_consuming_the_whole_window_fails_closed_without_calling_the_provider`,
`test_reservation_larger_than_the_window_also_fails_closed`.

## 4. Texto exacto de la prohibición de herramientas

Añadido a `SYSTEM_INSTRUCTION` (en `ai_interpretation.py`), conservando íntegro el texto de anclaje a
evidencia ya existente:

> `Tool use is prohibited: do not call, request, or simulate any tool, function, plugin, agent, or command. Do not inspect, open, read, list, or search any file, directory, repository, or URL. Do not execute shell commands or code. The attached evidence package is your only permitted source of information. Return only the requested structure: one strict JSON object, with no Markdown fences, comments, explanation, prefix, suffix, or chain-of-thought.`

Decisiones de redacción:

- Vive en el propio `SYSTEM_INSTRUCTION`, no en el `<output_contract>` de un proveedor concreto, para que
  viaje en el payload **independientemente del proveedor** (test:
  `test_prohibition_travels_in_the_payload_independently_of_the_provider`, que comprueba que aparece dentro
  del bloque `<system_instruction>`).
- El tono/precisión de la parte de formato reutiliza el del `<output_contract>` ya existente en
  `copilot.py` ("No Markdown fences, comments, explanation, prefix, suffix, or chain-of-thought"), que no se
  modifica ni se elimina — ambos coexisten.
- `USER_INSTRUCTION` se actualizó para describir los ids citables de un registro **hidratado**
  (`flow_id`, id del punto de entrada, `path_ids`, ids de nodo/terminal, `evidence_refs`) en vez de "los
  valores `ref` de los records".

Tests: clase `StrictGroundingInstructionTests` (6 tests), incluyendo
`test_evidence_grounding_rules_are_preserved` (las reglas anteriores no se debilitaron).

## 5. Metadata excluida del payload, y por qué

| Excluido | Motivo |
|---|---|
| `truncation.continuation_refs` (la lista completa de refs excluidas que sí emite `ContextComposer`) | A escala real es una lista no acotada y no aporta nada a la tarea de interpretación. En su lugar el paquete lleva **solo contadores**: `truncated`, `excluded_record_count`, `continuation_refs_included: false` y `continuation_policy: "EXCLUDED_FLOWS_ARE_REQUESTED_AS_SEPARATE_BOUNDED_PACKAGES"` — el modelo sabe que falta contenido y cuánto, sin recibir el bulto |
| `LLMRequest.metadata` (`evidence_policy`, `claim_policy`, `missing_information_policy`) | Se deja vacío deliberadamente, con lo que los tres bloques del envoltorio quedan en `{}` en vez de transportar estructuras de auditoría que la tarea no necesita |
| `entities`/`relationships`/`priority_records`/`warnings`/`counts_by_priority`/`coverage_by_priority` del paquete de referencias | No forman parte del contrato `AI_HYDRATED_PROJECTION 1.0`; el contenido semántico equivalente ya viaja hidratado dentro de cada registro |

**No excluido a propósito**: `source_index_pointer`/`path_provenance` de cada registro (R1 §2.1 los exige como
trazabilidad de vuelta al índice exhaustivo) y `statistics`/`truncation` del sobre (R1 §5.2 los enumera
explícitamente como parte del payload que debe medirse, no como algo a suprimir).

El contrato preexistente de `ContextComposer` **no se debilita**: sigue emitiendo `continuation_refs` igual
que antes (test `test_existing_composer_still_carries_continuation_refs_unchanged`). La omisión es una
propiedad de la superficie nueva, no un cambio del paquete de referencias.

Tests: `test_truncation_never_carries_a_continuation_refs_list`, `test_request_carries_no_bulk_metadata`.

## 6. Cobertura de requisitos (uno a uno contra el prompt literal de R5)

| Requisito literal | Dónde | Test(s) |
|---|---|---|
| presupuesto sobre representación final enviada al provider | `llm/core.py::measure_request_payload` + gate en `ai_interpretation.py` (3.1–3.2) | `test_measured_payload_exceeds_the_packages_own_estimate`, `test_copilot_prompt_delegates_to_the_shared_renderer` |
| medir bytes/chars/tokens estimados del payload final | `measure_request_payload` → `payload_bytes`/`payload_characters`/`payload_estimated_tokens` | `test_measurement_counts_instructions_envelope_and_schema`, `test_measurement_is_deterministic` |
| `BUDGET_INSUFFICIENT` no continúa ciegamente | `_build_within_budget` corta antes de la llamada (3.3) | `test_budget_insufficient_never_continues_to_the_provider`, `test_budget_insufficient_when_even_one_record_does_not_fit` |
| reducir, particionar o devolver `CONTEXT_TOO_LARGE` | Reducir-una-vez + `CONTEXT_TOO_LARGE` (3.3); el particionado por presupuesto de registros ya lo hace `package()` | `test_reduce_then_retry_is_attempted_exactly_once`, `test_oversized_payload_returns_context_too_large_without_calling_the_provider`, `test_context_too_large_is_an_already_existing_status` |
| usar proyección hidratada | `ai_projection` sobre `EvidenceHydrator.hydrate_flow` (2.1, 2.4) | `test_records_are_hydrated_records_not_bare_references`, `test_records_are_exactly_what_the_hydrator_produces`, `test_sent_request_context_is_the_hydrated_projection` |
| preferir FLOW y agregaciones controladas | `flow_ids` obligatorio + `select_flow_ids` acotado y priorizado | `test_flow_ids_are_mandatory`, `test_selection_is_bounded`, `test_confirmed_flows_are_selected_before_unresolved_ones`, `test_flow_ids_parameter_scopes_the_projection` |
| no enviar metadata/continuations masivas innecesarias | Sección 5 | `test_truncation_never_carries_a_continuation_refs_list`, `test_request_carries_no_bulk_metadata` |
| prompt estricto: no tools, no file inspection, no shell, output contract exacto | `SYSTEM_INSTRUCTION` (sección 4) | `StrictGroundingInstructionTests` (6) |
| validar `evidence_refs` | `_validate_findings` contra `package_reference_ids` | `test_evidence_refs_validate_against_hydrated_record_ids`, `test_unknown_evidence_ref_is_still_rejected` |
| conservar `INVALID_STRUCTURED_OUTPUT` como fallo seguro | Rama post-llamada intacta | `test_invalid_structured_output_remains_a_distinct_post_call_failure` |
| **No hacer**: framework genérico de providers/modelos ni anticipar V5 | No se tocó `LLMProvider`/`ProviderRegistry`/`ProviderConfig`/la interfaz abstracta; no se añadió ningún proveedor. Lo único hecho en `llm/` es mover una construcción que ya existía en un solo sitio a un lugar provider-neutral y hacer que su dueño original delegue | `test_copilot_module_no_longer_holds_its_own_copy_of_the_wrapper` |

Requisitos del contrato R1 §5.2 (además del prompt):

| Exigencia de R1 §5.2 | Test |
|---|---|
| Registros hidratados, nunca referencias sueltas | `test_records_are_hydrated_records_not_bare_references` |
| Presupuesto propio declarado y respetado | `BudgetTests` (8) |
| Perfiles reutilizados, `FULL` inadmisible | `test_allowed_profiles_are_reused_from_composer_not_redefined`, `test_full_profile_is_rejected` |
| Prefijo `AIP-<sha256>` | `test_package_id_uses_the_aip_prefix` |
| El presupuesto propio no autoriza la llamada | Sección 3 completa |
| Solo evidencia determinista; nunca `INTERPRETED` de entrada | `test_interpreted_content_is_rejected`, `test_ai_interpretation_confidence_value_is_rejected` |
| Sobre existente, cambio aditivo en `records` | `test_envelope_carries_the_same_fields_as_the_existing_package_envelope` |
| `confidence` nunca inventada ni alterada | `test_confidence_is_never_altered_or_invented` |

## 7. Tests

`tests/test_v4_3_r5_ai_context_budgeting.py` (**66 tests**, todos en verde — 58 de la implementación inicial
más 8 de la corrección posterior de la reserva de capacidad de salida, sección 3.2):

| Clase de test | Tests |
|---|---|
| `AiProjectionContractTests` | 14 |
| `BudgetTests` | 8 |
| `PayloadGateTests` | 8 |
| `OutputReservationGateTests` | 8 |
| `ProductionPathProjectionTests` | 8 |
| `PayloadMeasurementTests` | 6 |
| `StrictGroundingInstructionTests` | 6 |
| `RuntimeIndependenceTests` | 4 |
| `SelectFlowIdsTests` | 4 |
| **Total** | **66** |

Incluye, siguiendo el patrón de R2–R4: determinismo (`test_package_is_deterministic_for_the_same_input`,
`test_selection_is_deterministic`, `test_measurement_is_deterministic`), independencia de runtime
(`RuntimeIndependenceTests`: sin import de `llm`, sin I/O de archivos, sin reimplementar la hidratación) y no
invención de evidencia (`test_confidence_is_never_altered_or_invented`,
`test_records_are_exactly_what_the_hydrator_produces`, los dos tests de `InterpretedContentError`).

Ningún test existente fue debilitado ni modificado. En particular,
`tests/test_v4_2_r4_ai_interpretation_and_proposal_integration.py` (34 tests) sigue en verde **sin cambios**,
incluidas sus garantías de que sin opt-in no se resuelve proveedor, de que se usa el `ai_context` de la
ejecución actual, de sanitización de errores y de que `ai_interpretation.py` no nombra ninguna clase de
proveedor real.

## 8. Conteos de tests

- **Antes** de esta ronda: **1918 tests, 0 fallos, 132 skips** (`python -m unittest discover -s tests`,
  verificado al inicio de la sesión).
- **Tras la implementación inicial de R5**: **1976 tests, 0 fallos, 132 skips** (1918 + 58 nuevos).
- **Tras la corrección de la reserva de capacidad de salida** (sección 3.2, esta misma ronda, sin iniciar R6):
  **+8 tests** en `OutputReservationGateTests` → `tests/test_v4_3_r5_ai_context_budgeting.py` pasa de 58 a
  **66 tests**, todos en verde. El único fallo presente en `python -m unittest discover -s tests` es
  `test_v4_1_r0_maintainability_inventory.GeneratedArtifactOnDiskTests
  .test_on_disk_inventory_matches_fresh_build_if_present`, preexistente a esta corrección (reproducido también
  con `git stash`, sin ninguno de los cambios de esta corrección aplicado) y ajeno al gate de payload; no se
  toca aquí porque el prompt de esta corrección lo acota estrictamente al gate de `_payload_token_limit`.
- `python -m unittest tests.test_v4_3_r5_ai_context_budgeting` → **66/66 `OK`**.
- `python -m unittest tests.test_v4_2_r4_ai_interpretation_and_proposal_integration` → **34/34 `OK`**
  (sin cambios: la corrección no toca la firma pública de `run_ai_interpretation`).

### 8.1 Cierre del fallo de `GeneratedArtifactOnDiskTests.test_on_disk_inventory_matches_fresh_build_if_present`

Tras la corrección de la sección 3.2, `python -m unittest discover -s tests` quedó con **1 fallo**: el test
del inventario de mantenibilidad congelado (V4.1-R0) comparado contra un rebuild en caliente del árbol
`legacy_documenter/`. Se investigó exclusivamente ese test, según lo pedido, sin tocar de nuevo el gate de
payload salvo que el diagnóstico demostrara un defecto real en él — no lo demostró.

**Diagnóstico.**

1. **Diferencia exacta capturada** (`sorted(fresh_risk["high_risk_files"])` vs. el valor esperado que el test
   ya calculaba a partir del inventario congelado): el `fresh` build **no** contenía
   `legacy_documenter/orchestration/ai_interpretation.py` en `high_risk_files`, mientras que el valor esperado
   por el test sí lo incluía. Inspeccionando `risk_summary` directamente:
   `ai_interpretation.py` había pasado a `very_high_risk_files`, no a `high_risk_files` — su
   `risk_category` real era `VERY_HIGH`, no `HIGH`.
2. **Causa descartada explícitamente: el traslado del workspace.** Se buscó en todo el árbol (excluyendo
   `.git/`) por `C:\dev\LegacyMapper` y `C:\dev` en código, configuración y JSON: las únicas coincidencias
   están en documentación histórica de cierre/versionado (`docs/V4/V4_R*_CLOSURE_AND_VERSIONING_RESULT.md`,
   `docs/V4_1/...`, `docs/V4_2/...`, `docs/PROJECT_RECOVERY.md`), que registran literalmente la ruta desde la
   que se ejecutaron esos comandos históricos — no hay ninguna referencia en `.py`, en configuración de
   ejecución, ni en ningún artefacto que el código lea en tiempo de ejecución. Ningún camino de producción ni
   de test depende de una ruta absoluta persistida; el escaneo AST de `tools/v4_1_r0/inventory.py` opera sobre
   rutas relativas al `REPO_ROOT` que recibe como argumento. El traslado de `C:\dev\LegacyMapper` a
   `E:\IAProyectos\LegacyMapper` **no** es la causa.
3. **Causa real: cambio legítimo de esta misma ronda no reflejado en el test.** La corrección de la sección
   3.2 (reserva de capacidad de salida) hizo crecer `ai_interpretation.py` de 348 a 402 líneas: el chequeo
   `limit <= 0` añadido, su docstring extendida en `_payload_token_limit`, y el nuevo mensaje de error de
   `run_ai_interpretation`. Ese crecimiento cruza el umbral de línea/`except_exception` que el escaneo AST usa
   para `VERY_HIGH`. El test ya sabía que el cambio inicial de R5 (190 → 348 líneas) movía el archivo de
   `MEDIUM` a `HIGH` (comentario preexistente en la sección 9.1); lo que faltaba era reflejar que la propia
   corrección posterior de R5, dentro de la misma ronda y antes de iniciar R6, lo hace cruzar una segunda
   vez, de `HIGH` a `VERY_HIGH`. No es un artefacto obsoleto, ni una ruta persistida, ni un problema del
   traslado: es el propio inventario del test sin actualizar frente a un cambio de código real y ya aprobado
   funcionalmente (sección 3.2).

**Corrección aplicada** (en `tests/test_v4_1_r0_maintainability_inventory.py`, `GeneratedArtifactOnDiskTests`,
únicamente las expectativas que dependían del `risk_category` final de `ai_interpretation.py`; no se tocó el
gate de payload en `ai_interpretation.py` ni `_payload_token_limit`, porque el diagnóstico no encontró ningún
defecto en ellos):

- `r5_ai_interpretation_path` se retiró de la lista que se suma a `expected_high_risk_files` y se añadió a
  `expected_very_high_risk_files` (antes acompañaba solo a `r3_full_pipeline_path`).
- `expected_categories["HIGH"]` perdió el término `+ 1` que representaba la entrada (ya superada) de
  `ai_interpretation.py` en `HIGH`.
- `expected_categories["VERY_HIGH"]` ganó un término `+ 1` adicional para la entrada real de
  `ai_interpretation.py` en `VERY_HIGH`.
- Los comentarios que documentaban el razonamiento de esas dos secciones, y el comentario del bloque
  `largest_modules` que citaba "348 lines", se actualizaron para explicar el cruce en dos pasos
  (MEDIUM → HIGH en la implementación inicial de R5, HIGH → VERY_HIGH en su corrección posterior) en vez de
  fijar solo el primer paso.
- Ninguna aserción se debilitó, eliminó, ni se marcó `skip`/`expectedFailure`: se corrigieron los valores
  esperados para que coincidan con el estado real y correcto del código, que es el objetivo declarado de este
  test (detectar artefactos desactualizados, no tolerarlos).

**Verificación tras la corrección**:

- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → **22/22 `OK`**.
- `python -m unittest tests.test_v4_3_r5_ai_context_budgeting` → **66/66 `OK`**.
- `python -m unittest discover -s tests` → **1984 tests, 0 failures, 0 errors, 132 skipped**. (El texto
  `ERROR:`/`FAILED` que la propia suite imprime a stdout durante esta corrida proviene de tres tests que
  ejercitan deliberadamente el camino de fallo del pipeline (`AI_INTERPRETATION: FAILED
  (PROVIDER_ERROR: PROVIDER_ERROR)`, etc.) y verifican que el `RUN_SUMMARY`/la salida por consola lo reportan
  correctamente; no son fallos de test — el resumen final de `unittest` es `OK`.)

**Objetivo 5 (referencias a `C:\dev\LegacyMapper` / `C:\dev`)**: existen, exclusivamente en documentación
histórica de cierre/versionado y en `docs/PROJECT_RECOVERY.md`, registrando la ruta real desde la que se
ejecutaron verificaciones/comandos ya completados en su momento (p. ej.
`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_VERIFICATION.md`, que cita literalmente
`C:\dev\LegacyMapper\output\v3_r8_1\ARCHITECTURE_EVIDENCE.json` como argumento de un comando ya ejecutado). No
se reemplazaron: son registros históricos legítimos de una ejecución real en su momento y su ruta literal no
afecta el comportamiento ni la reproducibilidad de ningún test o herramienta actual — todo el código de
producción y de test opera sobre rutas relativas al repositorio, nunca sobre esa ruta absoluta.

## 9. Archivos runtime modificados/creados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/context/ai_projection.py` | **Nuevo** (304 líneas). Paquete `AI_HYDRATED_PROJECTION 1.0` con presupuesto obligatorio |
| `legacy_documenter/orchestration/_run_evidence_io.py` | **Nuevo** (44 líneas). Carga de `index/*.json` y `source_snapshot` extraída de `ai_interpretation.py` |
| `legacy_documenter/orchestration/ai_interpretation.py` | Migrado a `ai_projection` + gate de payload + prohibición de herramientas + validación contra ids hidratados (190 → 348 líneas) |
| `legacy_documenter/llm/core.py` | `render_request_payload`/`measure_request_payload` (84 → 114 líneas). Sin cambios en `LLMProvider`/`ProviderRegistry`/`STATUSES` |
| `legacy_documenter/llm/providers/copilot.py` | `_prompt` delega en `render_request_payload` (68 → 73 líneas). Sin cambios de transporte ni de comportamiento |
| `legacy_documenter/context/__init__.py` | Docstring del paquete: añadida la etapa `ai_projection` |
| `tests/test_v4_3_r5_ai_context_budgeting.py` | **Nuevo** (58 tests) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado (9.1) |

No se tocó `legacy_documenter/cli/full_pipeline.py` (la firma pública migrada es compatible), ni
`PROJECT_STATE.json`, ni el repositorio legacy fuente.

### 9.1 Actualización mecánica del inventario de mantenibilidad (V4.1-R0)

Mismo patrón exacto que cada ronda previa (cf. `V4_3_R4_..._RESULT.md` §13.6). Ninguna aserción existente se
debilitó; solo se ajustaron los valores esperados a los dos módulos nuevos y a los cruces de categoría reales:

| Sección del inventario | Ajuste |
|---|---|
| `production_python_module_count` | 172 → **174** (dos módulos nuevos) |
| Conjunto de rutas nuevas | + `context/ai_projection.py`, + `orchestration/_run_evidence_io.py` |
| `touched_paths` | + `llm/core.py`, + `llm/providers/copilot.py` (deduplicación del envoltorio de payload) |
| `risk_summary.high_risk_files` | + `context/ai_projection.py` (nuevo, `HIGH`), + `orchestration/ai_interpretation.py` (**`MEDIUM` → `HIGH`**) |
| `risk_summary.files_by_risk_category` | `HIGH` +2; `MEDIUM` neto 0 (`ai_interpretation.py` sale, `_run_evidence_io.py` entra); `LOW` y `VERY_HIGH` sin cambio |
| `dependency_findings.module_count` | +29 → **+31** |
| `largest_modules` | Entran `ai_projection.py` (304) y `ai_interpretation.py` (348); salen por corte `analysis/web_entry_resolver.py` y `knowledge/approval/service.py` |
| `largest_functions` | Entran `AiProjectionBuilder.package` y `run_ai_interpretation`; salen por corte `DatabaseResolver.resolve` y `CanonicalCompositionService.compose` |
| `largest_classes` | `CopilotProvider` +5 líneas, mismo `method_count` y misma `classification` |
| `side_effect_candidates.filesystem_access` | + `orchestration/_run_evidence_io.py` (+9 → +10) |

**Cruce de categoría explícito**: `orchestration/ai_interpretation.py` pasa de `MEDIUM` a `HIGH` (190 → 348
líneas). **No** llega a `VERY_HIGH` precisamente porque la responsabilidad de I/O se extrajo a
`_run_evidence_io.py` (sección 2.5): con ella incluida el módulo tenía cinco señales de responsabilidad y
puntuaba `VERY_HIGH`; sin ella son cuatro y queda en `HIGH`. Se documenta aquí como decisión consciente de
mantenibilidad, no como efecto colateral.

## 10. Fuera de alcance de esta ronda

- No se implementa `consumer_projection` / `LegacyMapperConsumerProjection 1.0` (es R6, R1 §9).
- No se crea un framework genérico de providers/modelos ni se anticipa V5; no se añade ningún proveedor nuevo
  ni se modifica estructuralmente `LLMProvider`/`ProviderRegistry`.
- No se modifica `PROJECT_STATE.json`.
- No se inicia V4.3-R6.
- No se modifica `legacy_documenter/documentation/interpretation.py` (`DocumentationProfile`/
  `DocumentationPrompt`): R1 §5.2 menciona "R5/R6" para la redacción de la instrucción, y esta ronda la
  implementó en el camino que **realmente llega hoy a un proveedor** (`ai_interpretation.py`, el único según
  R0 §3.3 y la lectura de esta ronda). Adaptar además la instrucción de `interpretation.py`, que hoy ningún
  camino de producción ejecuta contra un proveedor, queda disponible para R6 si el Líder Técnico lo considera
  necesario; se registra aquí explícitamente para que no se pierda.
- No se generan muestras (`docs/V4_3/samples/R5/`): esta ronda no produce documentación humana, solo un
  paquete machine-readable y un gate.
- No se ejecutó ninguna llamada real a proveedor ni verificación manual del camino AI
  (`REAL_AI_RUNTIME_CALL_ALLOWED=false`).

## 11. Revisión humana obligatoria (pendiente) — Gate para R6

Pendiente de aprobación por el Líder Técnico antes de iniciar R6:

- [ ] este resultado R5 (`docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md`);
- [ ] el módulo nuevo `legacy_documenter/context/ai_projection.py` y su contrato: perfiles admitidos
      (`TINY`/`SMALL`/`MEDIUM`/`LARGE`), rechazo explícito de `FULL`, `flow_ids` obligatorio, prefijo
      `AIP-<sha256>` (secciones 2.1 y 6);
- [ ] la deduplicación del envoltorio de payload a `llm/core.py` y la delegación de `CopilotProvider._prompt`,
      confirmando que no constituye un framework de providers (secciones 2.2, 2.3);
- [ ] el límite propio `DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS = 16000` y su justificación frente a `EEE-04`/
      `EEE-02` (sección 3.2);
- [ ] la política **reducir-una-vez-y-luego-fallar-cerrado** con `CONTEXT_TOO_LARGE` antes de llamar al
      proveedor (sección 3.3);
- [ ] la decisión de **migrar `run_ai_interpretation` in-place** en vez de crear una función paralela, y la
      compatibilidad de firma que hizo innecesario tocar `full_pipeline.py` (sección 2.4);
- [ ] el texto exacto de la prohibición de herramientas en `SYSTEM_INSTRUCTION` (sección 4);
- [ ] la metadata excluida del payload y la confirmación de que `ContextComposer` no se debilitó (sección 5);
- [ ] la extracción de `_run_evidence_io.py` y el cruce `MEDIUM → HIGH` de `ai_interpretation.py` en el
      inventario de mantenibilidad (secciones 2.5, 9.1);
- [ ] los conteos de tests: **1984 tests, 0 fallos, 0 errores, 132 skips** tras cerrar
      `GeneratedArtifactOnDiskTests.test_on_disk_inventory_matches_fresh_build_if_present` (secciones 8, 8.1);
- [ ] el punto abierto registrado sobre `documentation/interpretation.py` (sección 10).
