# LegacyMapper V5.0 R2 — Contract Validation

## MODELO RECOMENDADO

Claude Sonnet 5, medium.

Usar Opus solo si existe un bloqueo arquitectónico real que Sonnet no resuelve tras aproximadamente tres intentos bien acotados.

---

# OBJETIVO

Validar empíricamente el contrato arquitectónico definido en:

```text
docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md
```

Esta ronda es:

```text
VALIDACIÓN / DOCUMENTAL
```

NO es una ronda de implementación de V5.1.

R2 debe demostrar que los contratos de R1 son viables sobre la evidencia real de V4.3, detectar contradicciones antes de modificar producción y cerrar específicamente la ambigüedad del baseline de tests.

---

# ROOT

```text
C:\dev\LegacyMapper
```

Target real conocido:

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

Output real V4.3 preferido, si sigue presente:

```text
C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1
```

Si no existe, usar un output real equivalente ya existente y documentar la ruta exacta.

NO ejecutar un nuevo `full` IST salvo necesidad demostrada.

---

# LEE PRIMERO

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md
docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md
docs/continuity/LEGACYMAPPER_V5_ROADMAP.md
docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md
```

Usar lectura dirigida. No releer indiscriminadamente todo el repositorio.

---

# ESTADO DE PARTIDA

```text
V5_0_R1_CONTRACT_READY
```

Las decisiones D-01…D-16 de R1 son la fuente de verdad actual.

R2 NO puede cambiarlas silenciosamente.

Si una validación contradice una decisión, registrar:

```text
CONTRACT_CONFLICT
```

y proponer el Decision Record necesario para aprobación posterior.

No corregirlo por cuenta propia.

---

# PRINCIPIOS OBLIGATORIOS

```text
Python descubre; IA interpreta.
```

Preservar:

- determinismo;
- provenance;
- evidence_refs;
- unresolved;
- no auto-approval;
- no auto-canonicalization;
- Runtime Independence;
- compatibilidad V4.3;
- templates no alteran verdad;
- provider opcional;
- IST como baseline real.

---

# REGLA DE DOCUMENTACIÓN

No crear archivos `.md` adicionales por iniciativa propia.

Esta ronda solo puede crear:

```text
docs/V5/V5_0_R2_CONTRACT_VALIDATION.md
docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE_PROPOSED_PROMPT.md
```

El segundo solo si R2 queda VALIDATED.

Todo hallazgo adicional debe integrarse en `V5_0_R2_CONTRACT_VALIDATION.md`.

No crear:

```text
FIX_NOTES.md
PATCH_RESULT.md
CORRECCION.md
DIAGNOSTICO_EXTRA.md
TODO_FIX.md
WORKAROUND.md
R2A / R2B / R2C
```

sin autorización explícita.

---

# TAREA R2

## 1. Validar round-trip conceptual del modelo normalizado

Construir una tabla exhaustiva de mapeo:

```text
V4.3 field
→ normalized entity.field
→ extension field, si aplica
→ legacy projection field
```

Cubrir como mínimo:

```text
files
projects
solutions
symbols
entry_points
calls
data_access
data_parameters
stored_procedures
sql_operations
functional_paths
functional_flows
flow_unresolved
dependencies
functional_dependencies
webforms
configuration
event_bindings
logical_symbols
repository
flow_summary
```

Objetivo:

demostrar que ninguna información necesaria para reconstruir `index/*.json` queda sin destino.

No crear modelos Python productivos.

---

## 2. Validar D-01 — compatibilidad en capas

Verificar que el contrato es técnicamente viable:

```text
evidence/
→ legacy projection index/
```

Evaluar específicamente:

- ordering;
- serialización JSON;
- defaults;
- campos temporales;
- paths;
- normalización de strings;
- campos omitidos vs null;
- listas vacías;
- estabilidad byte a byte.

Resultado permitido:

```text
VIABLE
VIABLE_WITH_CONSTRAINTS
CONTRACT_CONFLICT
```

Si la byte-equivalencia completa de `index/` es demasiado fuerte o imposible por diseño, NO cambiar D-01: documentar el conflicto con evidencia y proponer Decision Record.

---

## 3. Detector real de colisiones de IDs

Ejecutar sobre índices IST existentes.

Validar por kind al menos:

```text
EP-
FLOW-
DAO-
PATH-
```

Reportar:

```text
entity_count
unique_id_count
collision_count
collision_examples
```

No cambiar IDs.

Si existen colisiones:

- R2 queda `CONTRACT_CHANGES_REQUIRED`;
- no inventar aliases;
- documentar evidencia exacta.

---

## 4. Validar identidades asumidas en R1

R1 contiene algunas identidades que deben comprobarse contra V4.3 real.

Validar explícitamente:

```text
Project
Component
ExternalDependency
Call
UnresolvedBoundary
```

Comprobar:

- si existe realmente un ID V4.3 reutilizable;
- si el ID es estable;
- si el tipo existe como entidad propia o solo como estructura embebida;
- si el contrato está asumiendo una identidad que V4.3 nunca tuvo.

Especialmente revisar afirmaciones como:

```text
Project → ID V4.3 (PROJECT-…)
Component → ID V4.3 de símbolo/webform
ExternalDependency → ID V4.3
Call → ID V4.3
UnresolvedBoundary → ID V4.3
```

No asumir que son correctas solo porque aparecen en R1.

Si alguna no existe realmente:

```text
CONTRACT_CONFLICT
```

y proponer el ajuste mínimo.

---

## 5. Validar neutralidad tecnológica

Revisar el contrato R1 y listar cualquier campo core con semántica específica de:

```text
VB.NET
WebForms
.NET Framework
Oracle
ADO.NET
.vbproj
```

Resultado objetivo:

```text
0 campos tecnológicos obligatorios en el core
```

Los datos específicos deben poder vivir en:

```text
extensions[adapter_id]
```

o adapters/proyecciones.

---

## 6. Validar EvidenceReference

Comprobar que el modelo propuesto puede representar toda referencia actual:

```text
FLOW-
PATH-
EP-
DAO-
CALL-
source location
source span
texto técnico no-ID cuando hoy exista
```

Debe soportar:

```text
proposals
hydration
traceability
template evidence appendix
consumer projection
```

Determinar si hacen falta subtipos explícitos:

```text
entity reference
source reference
source-span reference
external/unresolved textual reference
```

Si la estructura `{source_id, kind, locator}` + `entity_id/entity_kind` resulta ambigua o contradictoria, marcar conflicto.

---

## 7. Validar SourceArtifact

Confirmar que:

```text
SRC- + SHA-256(path relativo posix)
```

es suficiente como identidad.

Evaluar si renombrar un archivo debe:

```text
crear nuevo SourceArtifact
```

o preservar identidad por contenido.

No cambiar la decisión; solo validar consecuencias para V5.3 incremental/cache.

---

## 8. Validar templates V5.2

Sin implementar template engine, tomar al menos:

1. un flow trivial;
2. un flow rico con DB/transacción;
3. un flow unresolved.

Para cada uno construir conceptualmente:

```text
human-functional
human-technical
ai-context
```

Demostrar:

- mismos IDs;
- refs resuelven;
- mismo `state`;
- mismas relaciones;
- diferencia solo de selección/presentación.

Validar especialmente la invariante:

```text
template_truth_invariance
```

No ejecutar IA real.

---

## 9. Validar Profile vs AI projection

Comprobar que:

```text
Profile ai-context
```

puede limitar contenido declarativamente sin reemplazar:

```text
select_flow_ids
AiProjectionBuilder.package
measure_request_payload
```

Confirmar que V5.2 no necesita mover budgeting al template engine.

---

## 10. Validar Provider Contract

Crear tabla:

```text
contract item
→ LLMProvider ABC actual
→ FakeLLMProvider
→ CopilotProvider
→ orchestration actual
→ gap
```

Cubrir al menos:

```text
generate
structured_generate
capabilities
model_info
close
timeout
rate limit
retryability
structured output
json mode
context window
max output
sanitization
credential_source
lazy import
registry
```

Confirmar que `orchestration/ai_interpretation.py` usa solo capacidades que podrán quedar en el contrato.

No modificar providers.

---

## 11. Validar Runtime Independence formal

Realizar análisis dirigido/AST/grep para identificar referencias de runtime hacia:

```text
docs/
prompts/
tests/
PROJECT_STATE.json
governance/
codex/
output/
```

Separar:

```text
runtime productivo
tooling de desarrollo
legacy congelado
```

Confirmar la viabilidad de sacar `readiness/closure/human_review/second_review` de la distribución limpia sin romper:

```text
analyze
full
output-manifest
```

No mover archivos todavía.

---

## 12. Validar observabilidad aditiva

Tomar un `RUN_SUMMARY.json` V4.3 existente.

Demostrar que agregar:

```json
"observability": {}
```

no rompe lectores V4.3 actuales.

Revisar lectores reales, no asumir tolerancia a claves desconocidas.

Confirmar si:

```text
duration_ms
stage_started_at
stage_finished_at
input_count
output_count
```

pueden agregarse de forma aditiva.

No implementar instrumentación.

---

## 13. Validar incremental/cache future-proofing

Confirmar que el schema definido en R1 puede soportar posteriormente:

```text
file fingerprint
adapter version
extractor/stage version
schema version
reverse dependency index
flow invalidation
projection cache key
template/profile version
```

sin breaking change de evidence.

No diseñar todavía el algoritmo completo de invalidación.

---

## 14. Validar segmentation future-proofing

Confirmar que los campos:

```text
parent_flow_id
segment_id
partial
included_paths
omitted_paths
evidence_refs
segment_reason
```

son suficientes para V5.6 y no contaminan los flows completos.

Revisar especialmente la invariante:

```text
included_paths ∪ omitted_paths = path_ids del padre
```

y si requiere:

```text
intersection = empty
```

como invariante explícita.

No implementar segmentación.

---

## 15. Validar Approval / Canonical boundary

Confirmar que V5.1 puede mantener stores separados:

```text
evidence/
proposals/
decisions/
canonical/
```

sin introducir decision/canonical fields en evidence.

No implementar V5.7.

---

## 16. Reproducir y cerrar clasificación de los 4 tests rojos

Ejecutar solo los tests necesarios para reproducir exactamente los 4 fallos conocidos.

Verificar que se deban exclusivamente a:

```text
provider_calls
real_llm_calls
baseline snapshot vs PROJECT_STATE vivo
```

Comparar con el artefacto congelado de V4-R14.

R2 debe recomendar UNA opción:

```text
A) mover las aserciones de "0 llamadas" al baseline congelado
B) cambiar la aserción sobre PROJECT_STATE a propiedad monotónica/no-decreciente
```

No aplicar el cambio.

El documento debe incluir:

```text
RECOMMENDED_TEST_BASELINE_FIX
```

y dejar explícito que requiere aprobación humana antes de tocar tests.

No declarar suite verde todavía.

---

## 17. Estimar tamaño de evidence/

Usando los índices reales existentes, estimar:

- tamaño bruto aproximado;
- duplicación evitada posible;
- impacto temporal de coexistencia `evidence/ + index/`;
- tamaño de partición razonable;
- JSON vs JSONL particionado, sin decidir por intuición.

No generar un `evidence/` real de 1 GB en esta ronda.

Resultado:

```text
recommended physical format for V5.1 prototype
```

con justificación empírica.

---

## 18. Process Exit

Mantener:

```text
NOT_REPRODUCED
```

salvo nueva evidencia directa.

No investigar más ni crear fix en esta ronda.

---

# VALIDACIÓN DE LAS 16 DECISIONES

El resultado debe contener una tabla:

```text
D-01 ... VALIDATED / VALIDATED_WITH_CONSTRAINTS / CONTRACT_CONFLICT
...
D-16 ... VALIDATED / VALIDATED_WITH_CONSTRAINTS / CONTRACT_CONFLICT
```

Ninguna D-xx puede quedar sin estado.

---

# OUTPUT OBLIGATORIO

Crear únicamente:

```text
docs/V5/V5_0_R2_CONTRACT_VALIDATION.md
```

Debe contener:

```text
STATUS
EXECUTIVE SUMMARY
D-01..D-16 VALIDATION MATRIX
ROUND-TRIP FIELD MAPPING
ID COLLISION RESULTS
IDENTITY ASSUMPTION VALIDATION
TECHNOLOGY NEUTRALITY
EVIDENCE REFERENCE VALIDATION
TEMPLATE/PROFILE VALIDATION
PROVIDER CONTRACT GAP MATRIX
RUNTIME INDEPENDENCE VALIDATION
OBSERVABILITY VALIDATION
INCREMENTAL/CACHE FUTURE-PROOFING
SEGMENTATION VALIDATION
APPROVAL/CANONICAL VALIDATION
TEST BASELINE RESOLUTION
EVIDENCE STORE SIZE/FORMAT ESTIMATE
CONTRACT CONFLICTS
RISKS
TESTS / COMMANDS EXECUTED
FILES READ
FILES MODIFIED
```

---

# ESTADOS PERMITIDOS

Solo:

```text
V5_0_R2_CONTRACTS_VALIDATED
V5_0_R2_CONTRACT_CHANGES_REQUIRED
V5_0_R2_BLOCKED
```

---

# CRITERIO PARA CONTRACTS_VALIDATED

Solo usar:

```text
V5_0_R2_CONTRACTS_VALIDATED
```

si:

1. D-01…D-16 están validadas o validadas con restricciones no-breaking;
2. no hay identidad inventada en el modelo;
3. no hay colisiones de IDs reales sin resolver;
4. todo campo V4.3 tiene destino en core/extensions/projection;
5. core neutral no contiene campos específicos de WebForms/VB/Oracle;
6. EvidenceReference cubre la evidencia real;
7. template truth invariance es comprobable;
8. provider contract es implementable sin tocar evidence/selection;
9. Runtime Independence tiene separación viable;
10. observability es realmente aditiva;
11. cache/segmentation/approval no exigen breaking changes;
12. los 4 tests rojos quedan reproducidos y su corrección recomendada queda claramente definida.

Si alguno requiere cambiar D-01…D-16:

```text
V5_0_R2_CONTRACT_CHANGES_REQUIRED
```

---

# NEXT STEP

Si R2 queda:

```text
V5_0_R2_CONTRACTS_VALIDATED
```

crear:

```text
docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE_PROPOSED_PROMPT.md
```

pero NO ejecutarlo.

Si queda `CONTRACT_CHANGES_REQUIRED`:

- NO crear una ronda correctiva por cuenta propia;
- incluir en el mismo resultado los Decision Records propuestos;
- esperar aprobación.

---

# RESTRICCIONES

NO:

- modificar producción;
- modificar tests;
- modificar PROJECT_STATE.json;
- implementar V5.1;
- crear adapters;
- crear evidence store productivo;
- implementar templates;
- implementar cache;
- cambiar providers;
- ejecutar IA real;
- ejecutar full IST;
- crear documentos auxiliares no solicitados.

---

# PRINCIPIO FINAL

```text
medir
→ comprender
→ decidir
→ fijar contrato
→ validar
→ implementar una vez
```
