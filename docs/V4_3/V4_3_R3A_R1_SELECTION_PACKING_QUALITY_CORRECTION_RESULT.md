# V4.3 R3A (R1) — Selection/Packing Quality Correction — Resultado

## Estado de esta ronda

`V4_3_READY_FOR_R3_RERUN`. Corrección de código real (no diagnóstico) aplicada, medida y verificada contra
fixtures sintéticas y contra el output determinista real reconstruido en
`C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline`. No se ejecutó ningún piloto real. No se ejecutó R9. V4.3
no se declara cerrada (`V4_3_CLOSED` no se usa).

## 1. Causa raíz (heredada del diagnóstico R3 + rebaseline, dos capas — no re-diagnosticada aquí)

Fuente: `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` +
`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 12 (reproducida de nuevo en un equipo distinto,
misma estructura, mismos 12642 flows).

```text
candidatos seleccionados (select_flow_ids, SMALL, max_flows=80): 80
  de ellos, richness bucket 0/1 ("ricos"): 40
ANTES de esta corrección:
  records incluidos en el paquete final: 6 (todos bucket 2/3, triviales)
  records ricos en el request final: 0
  records ricos excluidos por budget: 40 (100%)
```

Dos capas, ninguna sustituye a la otra:

- **Capa 1 — outliers reales de tamaño (no corregible por reordenamiento)**: 35 de 40 candidatos ricos
  (87.5%) exceden, cada uno por sí solo, el presupuesto completo de `SMALL` (16000 caracteres): 84948-161040
  caracteres, 75-149 paths cada uno.
- **Capa 2 — orden de evaluación + first-fit greedy sin look-ahead (la causa que esta corrección ataca)**: 5
  de 40 candidatos ricos (12.5%) caben individualmente bajo el presupuesto completo (9680, 11778, 15352,
  15659, 15795 caracteres — `FLOW-0004993422`, `FLOW-0005929194`, `FLOW-0011096966`, `FLOW-0006182693`,
  `FLOW-0020041332`), y aun así ninguno entraba al paquete final antes de esta corrección.
  `_bucketed_order` itera round-robin entre buckets 0/1/2/3, y dentro de cada bucket ordena por `confidence`
  y luego `flow_id` ascendente — nunca por tamaño. Los primeros elementos de bucket 0 en ese orden son
  outliers enormes que se descartan sin consumir presupuesto, mientras los elementos pequeños de buckets 2/3
  que tocan en cada ronda del round-robin se aceptan de inmediato (first-fit greedy, sin mirar hacia
  adelante). El presupuesto de 16000 caracteres (≈15311-15373 utilizables tras descontar el envelope) queda
  consumido por records triviales aceptados en las primeras ~10 posiciones, antes de que el packer llegue
  siquiera al primer candidato rico de tamaño razonable (posición 24 de 80).

`payload_estimated_tokens` del request final estaba en 4648-4700 de un límite de 16000 — el gate final
`measure_request_payload` nunca fue el cuello de botella; el problema es enteramente el presupuesto interno de
`AiProjectionBuilder.package`.

## 2. Diseño evaluado

Se evaluaron las 4 direcciones de la sección 3 del prompt, con mediciones deterministas reales (código
ejecutado, no solo razonamiento):

1. **Empaquetado consciente de tamaño dentro de/entre buckets (prioridad sugerida por el prompt, ataca capa
   2).** Explorado en dos variantes:
   - *(a) Ordenar por tamaño dentro de cada bucket* — descartada: rompe el orden `confidence` → `flow_id` ya
     vigente y exigido por tests existentes (`test_confirmed_records_survive_a_tight_budget_before_unresolved_
     ones` en `tests/test_v4_3_r5_ai_context_budgeting.py`), y el prompt exige combinar, no reemplazar ese
     criterio.
   - *(b) Reserva de un candidato rico que quepa por bucket, antes del first-fit-greedy normal* —
     **elegida**. Ver sección 3.
2. **Partición de un record rico en sub-unidades citables (ataca capa 1).** Evaluada y **rechazada para esta
   ronda**: `AiProjectionBuilder`/`AI_HYDRATED_PROJECTION 1.0` no define ningún contrato de partición parcial
   de un record hidratado (el contrato fijado en `docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`
   sección 5.2 no contempla un record "truncado pero declarado como tal"); definir ese contrato desde cero
   invita exactamente el riesgo que el prompt prohíbe explícitamente (sección 2 ítem 2:
   "evidencia incompleta pero no marcada como tal") si no se hace con el cuidado suficiente, y el prompt marca
   esta dirección como "solo si ya existe o se puede definir sin inventar semántica nueva" — no existe, y
   definirla correctamente (con su propio schema, su propio `truncated: true` explícito, su propia
   validación contra `record_reference_ids`) es un cambio de contrato mayor que excede el alcance de una
   corrección de selección/empaquetado. Además, el prompt mismo aclara que capa 2 (12.5% de los ricos) no la
   necesita — basta reordenar — y es exactamente donde esta corrección concentra su efecto medible.
3. **Presupuesto diferenciado entre perfil de selección y perfil de empaquetado real.** Evaluada y
   **rechazada**: el prompt mismo señala que ampliar presupuesto sin corregir el orden solo pospone el mismo
   problema a otra escala (sección 3, nota final de esta viñeta) — confirmado por la causa raíz: el gate final
   ya tiene ~11300 tokens de margen y **eso no ayudó** porque el defecto está en el orden de evaluación
   interno, no en el tamaño del presupuesto. Ampliar el presupuesto interno de `package()` también violaría la
   restricción explícita de la sección 2 ítem 1 del prompt si se interpretara como tocar
   `composer.PROFILES`; no se tocó.
4. Ninguna otra dirección adicional demostró ser necesaria una vez que (1b) resolvió el caso demostrado.

## 3. Diseño elegido

**Empaquetado en dos pasadas dentro de `AiProjectionBuilder.package`: reserva + backfill.**

Pasada 1 (reserva, nueva): recorre `capped` (la misma lista, en el mismo orden `_bucketed_order` ya
establecía — round-robin por bucket, luego `confidence`, luego `flow_id` ascendente dentro de cada bucket) y
para el bucket 0 primero, luego el bucket 1, busca el **primer** candidato de ese bucket cuyo tamaño
individual quepa bajo el presupuesto restante, y lo acepta antes que cualquier otra cosa. Como máximo un
candidato por bucket (0 y 1) se reserva así — nunca más, para no revertir al problema opuesto (bucket rico
monopolizando la muestra). Si ningún candidato de un bucket cabe (el caso capa-1 puro), no se reserva nada
para ese bucket y la pasada 2 se comporta exactamente igual que antes de esta corrección.

Pasada 2 (backfill, idéntica a la lógica pre-existente): recorre `capped` en el mismo orden, aceptando
first-fit-greedy cualquier candidato no reservado aún que quepa en el presupuesto restante — nunca aborta al
encontrar el primer candidato que no cabe (la corrección V4.3 final AI pilot R2 ya establecida se preserva
sin cambios).

La lista final `records` se construye recorriendo `capped` en su orden natural e incluyendo los aceptados
(por cualquiera de las dos pasadas) — un candidato reservado aparece en su posición natural dentro del
orden bucket/confidence/flow_id, no se mueve al frente.

**Por qué es seguro matemáticamente**: el costo total exacto del cuerpo canónico serializado es
`envelope_chars + sum(costs elegidos) + (n-1 si n>0)` — una fórmula que **no depende del orden** en que los
elementos se agregan a la lista elegida, solo del conjunto y la cuenta. Por eso reservar un elemento fuera de
su posición natural de evaluación no cambia el total de caracteres que producirá el paquete final; solo
cambia **qué conjunto** de elementos queda elegido cuando el presupuesto es insuficiente para todos.

Algoritmo exacto (pseudo-código, ver `legacy_documenter/context/ai_projection.py`,
`AiProjectionBuilder.package`, líneas ~358-425):

```python
accepted = [False] * len(capped)
used = 0
count = 0

def _try_accept(index):
    extra = costs[index] + (1 if count else 0)
    if envelope_chars + used + extra > max_chars:
        return False
    accepted[index] = True
    used += extra; count += 1
    return True

# Pasada 1 -- reserva (nueva en esta corrección)
for bucket_wanted in (0, 1):
    for index, record in enumerate(capped):
        if accepted[index] or _record_richness_bucket(record) != bucket_wanted:
            continue
        if _try_accept(index):
            break  # como máximo un candidato reservado por bucket

# Pasada 2 -- backfill (idéntica a la lógica pre-existente, ahora corre después)
for index in range(len(capped)):
    if accepted[index]:
        continue
    _try_accept(index)

chosen = [record for index, record in enumerate(capped) if accepted[index]]
```

## 4. Por qué se descartaron las alternativas

Ver sección 2 para el razonamiento por dirección. En resumen: ordenar por tamaño puro rompe un invariante ya
exigido por tests existentes y por el prompt (`confirmed` antes que `inferred` antes que `unresolved`);
partición parcial requiere un contrato nuevo que el prompt marca como fuera de alcance sin una definición
previa; ampliar presupuesto no ataca la causa raíz real (confirmado con datos: 11300 tokens de margen ya
existían y no ayudaron).

## 5. Invariantes preservados

- **Evidencia atómica**: ningún record incluido pierde `evidence_refs`/`path_ids`/`terminal` — la reserva
  solo cambia el ORDEN de aceptación dentro de `package()`, nunca el contenido de un record ya hidratado por
  `EvidenceHydrator.hydrate_flow` (no tocado). Verificado en `T2AtomicEvidenceTests`
  (`tests/test_v4_3_r3a_r1_selection_packing_quality_correction.py`).
- **Diversidad**: la reserva nunca acepta más de un candidato por bucket rico (0 y 1), así que no puede
  revertir al problema opuesto (ricos monopolizando la muestra); la pasada 2 (backfill) sigue siendo la misma
  lógica round-robin/first-fit-greedy de siempre, así que records triviales (bucket 2/3) siguen entrando
  cuando el presupuesto lo permite. Verificado en `T3DiversityPreservedTests`.
- **Determinismo**: mismo input produce mismo output, mismo orden — la reserva recorre `capped` en un orden
  ya determinista (`_bucketed_order`), sin aleatoriedad ni llamada a IA. Verificado en `T6DeterminismTests`
  (incluye entrada en orden invertido).
- **Sin mutación de `confidence`/`terminal_type`/clasificación de riqueza**: `_richness_bucket`,
  `_record_richness_bucket`, `_flow_richness_bucket` no se modificaron — solo se leen, igual que antes.
  Verificado en `T5NoMutationTests`.
- **Presupuesto real respetado**: `measure_request_payload` del request final sigue dentro del límite del
  provider (verificado con la fixture sintética y con el output real reconstruido — sección 7 punto 9).

## 6. Archivos modificados (diff-relevantes, no los ya cargados sin cambios por el worktree)

```text
legacy_documenter/context/ai_projection.py
  -- AiProjectionBuilder.package: reemplazado el bucle único first-fit-greedy por la pasada de reserva +
     backfill descrita en la sección 3. Sin cambios en select_flow_ids, _bucketed_order,
     _richness_bucket, _record_richness_bucket, _flow_richness_bucket, record_reference_ids,
     package_reference_ids, _reject_interpreted_content, ni en el contrato AI_HYDRATED_PROJECTION 1.0.
     56 inserciones, 14 eliminaciones (git diff --stat).

tests/test_v4_3_r3a_r1_selection_packing_quality_correction.py  (nuevo)
  -- 21 tests cubriendo los 9 items de la sección 6 del prompt (T1 regresión de capa 2 con fixture
     sintética real, T2 evidencia atómica, T3 diversidad, T4 payload final dentro de límite, T5 sin
     mutación, T6 determinismo, T7 sin provider/red, T9 reproducción contra el output real
     reconstruido -- skip explícito, no failure, si esa ruta externa no existe en la máquina que corre
     la suite).

docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md  (este documento, nuevo)
```

**No modificados** (restricción de la sección 5 del prompt, verificado): `CopilotProvider`,
`SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`/`FINDING_SCHEMA`, `measure_request_payload`, `hydration.py`
(`EvidenceHydrator.hydrate_flow`), `consumer_projection.py`, `proposal_adapter.py`, `PROJECT_STATE.json`,
`composer.PROFILES` (la corrección define su presupuesto reordenando la aceptación DENTRO del presupuesto ya
existente de `ai_projection`, sin tocar los perfiles compartidos con otros consumidores — no fue necesario
evaluar una alternativa a esto porque el diseño elegido no requiere ningún cambio de presupuesto, solo de
orden de aceptación), `select_flow_ids`/`_bucketed_order`/`_richness_bucket` (clasificación de riqueza
intacta), distribution builder / `requirements-copilot.txt`, V5 / Plugin Runtime.

Nota sobre el resto de `git status`: el checkout de este worktree partió de un `robocopy` no destructivo
desde el checkout principal (instrucción de la tarea), que trae consigo el estado de trabajo V4.3 R0-R8 ya
presente en el checkout principal (idéntico al "18 archivos modified" ya documentado en
`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 2, ahora extendido a prácticamente todo el árbol
por diferencias de representación de fin de línea entre el checkout de origen y este worktree —
`core.autocrlf=true`). Esos archivos **no fueron tocados por esta tarea**; `git diff --stat` sobre
`legacy_documenter/context/ai_projection.py` confirma que el único cambio de contenido real introducido por
esta corrección es el descrito arriba (56+/14-), no ruido CRLF.

## 7. Tests (sección 6 del prompt, T1-T9)

Todos en `tests/test_v4_3_r3a_r1_selection_packing_quality_correction.py` salvo donde se indica:

1. **Regresión del escenario real demostrado, incluyendo explícitamente capa 2**: `T1RegressionReproduces
   LayerTwoTests` construye una fixture sintética con 6 candidatos ricos individualmente sobredimensionados
   (bucket 0, ~20000 caracteres cada uno, con ids que ordenan ANTES que los candidatos capa-2 bajo el mismo
   criterio `confidence`+`flow_id` que usa la producción — replicando por qué el algoritmo viejo los evalúa
   primero), 2 candidatos ricos que caben individualmente (~9000-9500 caracteres) pero que
   `test_old_order_alone_would_have_starved_every_rich_candidate` demuestra que el algoritmo PRE-corrección
   los excluye igualmente (reproduce el bug exacto, ejecutando la lógica vieja aislada, antes de verificar
   que la corregida es distinta), y 8 candidatos triviales (bucket 3, ~2200 caracteres) suficientes para
   agotar el presupuesto en el orden viejo. `test_corrected_package_includes_at_least_one_rich_record`
   verifica que la corrección SÍ incluye al menos un candidato capa-2 sin exceder el presupuesto
   (`test_corrected_package_never_exceeds_the_profile_character_budget`).
2. **Evidencia atómica**: `T2AtomicEvidenceTests` — ningún record incluido pierde `evidence_refs`/
   `path_ids`/`terminal`; un record incluido es byte-idéntico a una hidratación fresca.
3. **Diversidad preservada**: `T3DiversityPreservedTests` — no revierte a 100% trivial cuando hay candidatos
   ricos, y los candidatos triviales siguen entrando cuando el presupuesto lo permite (diversidad en ambos
   sentidos).
4. **`measure_request_payload` dentro del límite real**: `T4FinalPayloadWithinLimitTests` (fixture sintética)
   y `T9RealRepositoryReproductionTests.test_final_measured_payload_still_fits_the_real_provider_limit`
   (output real).
5. **Sin mutación**: `T5NoMutationTests` — `confidence`, `terminals`, y los valores de
   `_richness_bucket`/`_record_richness_bucket` permanecen sin cambio.
6. **Determinismo**: `T6DeterminismTests` — mismo input produce el mismo paquete byte a byte en 5
   repeticiones, y el orden de entrada de los records no cambia el resultado.
7. **Sin provider/red**: `T7NoProviderOrNetworkTests` — verificación AST de que `ai_projection` y este propio
   módulo de test nunca importan `legacy_documenter.llm`, `CopilotProvider`, `GeminiProvider`, ni una
   librería de red.
8. **Regresión completa V4.2/V4.3**: ver sección 8 de este documento (suite completa).
9. **Reproducción contra el output real reconstruido**: `T9RealRepositoryReproductionTests` (con
   `@unittest.skipUnless` sobre `C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline.exists()`, mismo patrón que
   `tests/test_v3_r8_2.py` usa para dumps externos regenerables — no falla si la ruta no existe en la máquina
   que corre la suite, la reporta como skip explicado). Ejecutado en esta tarea (la ruta SÍ existe en esta
   máquina): `test_at_least_one_named_under_budget_rich_candidate_survives_the_corrected_package` — PASS,
   `FLOW-0004993422` sobrevive al paquete final bajo la corrección (`rich_in_final_request_count` pasó de 0 a
   1 al re-ejecutar `python -m tools.v4_3_ai_selection_diagnostic` sin modificar esa herramienta, que reusa
   `AiProjectionBuilder.package` sin cambios de su parte). Ver sección 9 para el detalle completo.

Resultado del módulo nuevo, aislado: `Ran 21 tests in ~13-15s -- OK (0 failed, 0 errors, 0 skipped)` (los 3
tests de T9 corrieron y pasaron porque la ruta externa existe en esta máquina).

## 8. Resultados de suite completa

```text
python -m unittest discover -s tests
Ran 2169 tests in 132.541s
OK (skipped=132)
```

`0 failed`, `0 errors`. Los 132 skips son los mismos, exactamente, que documentó
`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 6 (80 requieren `output/v2_r5_1_full/`, 52
requieren `output/v3_r8_1/`, dumps del repositorio real no versionados — `PROJECT_STATE.json.all_skips_
explained=true`). El total (2169) es exactamente 21 más que el baseline de la ronda de rebaseline (2148),
correspondiendo uno a uno con los 21 tests nuevos de este módulo — ningún test pre-existente cambió de
estado. **No reaparecieron fallos de hash CRLF de baseline V4/V4.1** en esta ejecución (0 fallos de ese tipo,
igual que en el rebaseline); no fue necesario clasificar ningún FAIL como worktree/CRLF porque no hubo
ninguno.

Ejecución aislada previa de los módulos V4.3 relevantes (R5 budgeting, proposal quality correction, R3
diversity diagnostic, R2 context budget correction) confirmó `Ran 116 tests -- OK` antes de la corrida
completa, incluyendo específicamente `test_confirmed_records_survive_a_tight_budget_before_unresolved_ones`
(el invariante `confirmed` antes que `unresolved` sigue intacto bajo la corrección) y
`test_richer_flows_are_not_all_excluded_by_a_tight_character_budget`.

## 9. Reproducción contra el output real (sección 6 ítem 9 del prompt)

Ejecutado en esta tarea con `tools/v4_3_ai_selection_diagnostic.py` (sin modificar) contra
`C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline` (existente en esta máquina, reconstruido en la ronda de
rebaseline previa, `flow_count=12642`, idéntico al histórico):

```text
ANTES de esta corrección (V4_3_WORKSTATION_REBASELINE_RESULT.md sección 11, reproducido idéntico):
  candidate_count: 80, final_request_included_count: 6,
  rich_in_final_request_count: 0, rich_excluded_count: 40

DESPUÉS de esta corrección (misma ejecución, mismo repositorio, mismos índices, ai_projection.py corregido):
  candidate_count: 80, final_request_included_count: 3,
  rich_in_final_request_count: 1, rich_excluded_count: 39
  rich_flows_in_final_request: ["FLOW-0004993422"]   <- uno de los 5 candidatos capa-2 identificados
  package.statistics: {records_included: 3, records_excluded: 77, completeness: "TRUNCATED",
                        estimated_tokens: 3787, max_characters: 16000, confirmed_flow_count: 1,
                        unresolved_flow_count: 2}
```

`FLOW-0004993422` (el más pequeño de los 5 candidatos capa-2, 9680 caracteres) ahora sobrevive al paquete
final, cuando antes de esta corrección ninguno de los 5 lo hacía. `measure_request_payload` del request final
correspondiente reporta `estimated_tokens=3787`, muy por debajo del límite de 16000 tokens del provider
(`DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS`) — el gate final sigue sin ser el cuello de botella, exactamente como
predijo el diseño.

Nota: `final_request_included_count` bajó de 6 a 3 en este caso concreto — no es una regresión de diversidad,
es la consecuencia esperada y correcta de que el candidato rico reservado (9680 caracteres) consume mucho más
presupuesto que los 6 records triviales pequeños que ocupaba antes (1633-5100 caracteres cada uno); el
paquete sigue reportando `completeness: TRUNCATED` (no `BUDGET_INSUFFICIENT`) y sigue incluyendo records
triviales junto al rico (`unresolved_flow_count: 2` en el resultado), consistente con el invariante de
diversidad verificado por `T3DiversityPreservedTests`.

## 10. Runtime Independence

PASS. `legacy_documenter/context/ai_projection.py` sigue sin importar `legacy_documenter.llm` ni ningún
provider (verificado por `RuntimeIndependenceTests` en `tests/test_v4_3_r5_ai_context_budgeting.py`, sin
modificar, y por `T7NoProviderOrNetworkTests` en el módulo nuevo). El cambio de esta corrección es
exclusivamente aritmético/de orden dentro de una función pura ya existente — no añade ninguna dependencia
nueva, ninguna lectura/escritura de archivo, ninguna llamada de red. `tools/v4_3_ai_selection_diagnostic.py`
no se modificó. No se ejecutó ningún piloto real ni se invocó ningún provider en ningún momento de esta
tarea.

## 11. Restricciones

PASS. No se modificó `CopilotProvider`, `SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`/`FINDING_SCHEMA`,
`measure_request_payload`, `hydration.py`, `consumer_projection.py`, `proposal_adapter.py`,
`PROJECT_STATE.json`, `composer.PROFILES`, ni nada de V5/Plugin Runtime/distribution builder/
`requirements-copilot.txt`. No se ejecutó un piloto real. No se ejecutó R9. V4.3 no se declara cerrada.
`Python selecciona y presupuesta; IA interpreta` permanece 100% determinista — no se introdujo LLM, red,
random, ni ranking IA en `select_flow_ids` ni en `AiProjectionBuilder.package`.

## 12. Estado final

`V4_3_READY_FOR_R3_RERUN`. Esto habilita, en una tarea FUTURA separada, un nuevo piloto real con la
corrección aplicada. Ese piloto NO se ejecutó en esta tarea.
