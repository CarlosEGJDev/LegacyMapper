# LegacyMapper V5.9 — R1 Resume
## Authorized Circular Python Pilot

## 1. Decisión humana explícita

El bloqueo anterior fue:

```text
V5_9_R1_BLOCKED_SECOND_TECH_SOURCE
```

El usuario autoriza expresamente continuar usando una copia local de LegacyMapper en Python como segunda fuente tecnológica.

Esta decisión es consciente y excepcional:

```text
SECOND_TECHNOLOGY = Python
PILOT_KIND = SELF_HOSTED_CIRCULAR
INDEPENDENT_EXTERNAL_SYSTEM = false
```

No presentar este piloto como validación independiente contra un producto externo.

Sí puede demostrar:

```text
VB.NET WebForms/Oracle
vs
Python application
```

usando el mismo core V5.

---

## 2. Objetivo

Reanudar **la misma V5.9-R1** desde Gate A.

NO crear R1.1, R1B ni R2.

Secuencia:

```text
confirmar fuente Python autorizada
→ medirla
→ congelar copia
→ diseñar adapter Python mínimo
→ implementar
→ validar V5.1–V5.8
→ regresión IST
→ suite completa
→ actualizar entregables R1
→ revisión humana
```

---

## 3. Fuente autorizada

Fuente candidata previamente descubierta:

```text
C:\PruebasLegacyMapper\LegacyMapper
```

Puede contener subárboles/copias como `dist`.

Antes de usarla:

1. inspeccionar estructura;
2. identificar el root fuente real;
3. EXCLUIR:
   - `.git`
   - `dist`
   - `build`
   - `__pycache__`
   - `.venv`
   - `venv`
   - caches
   - outputs generados
   - copias redundantes;
4. medir solo el source tree Python real.

No analizar el repo de desarrollo activo `C:\dev\LegacyMapper` si existe una copia separada utilizable.

Preferir siempre la copia congelada bajo `C:\PruebasLegacyMapper\LegacyMapper`.

---

## 4. Circularity disclosure

Registrar obligatoriamente en todos los resultados:

```text
pilot_kind = SELF_HOSTED_CIRCULAR
second_source_is_legacy_mapper_itself = true
external_independence_claim = false
```

Interpretación permitida:

> V5.9 demuestra que la arquitectura V5 puede procesar al menos dos stacks tecnológicos diferentes (VB.NET WebForms/Oracle y Python) con contratos comunes.

Interpretación NO permitida:

> V5.9 prueba generalización independiente a sistemas externos arbitrarios.

Esa segunda afirmación requeriría un corpus externo futuro.

---

## 5. Baseline de la fuente Python

Antes de implementar:

registrar:

```text
SECOND_TECH_SOURCE_ID
root
pilot_kind
file_count
source_bytes
tree_hash
pyproject.toml?
setup.cfg?
setup.py?
requirements?
package structure
entrypoints
CLI entrypoints
module count
imports
calls
filesystem boundaries
network/provider boundaries
data access if present
```

No ejecutar LegacyMapper como target durante discovery.

Solo parsing estático.

---

## 6. Fuente read-only

El source Python seleccionado debe ser tratado como read-only.

Para pruebas de incremental:

```text
source original
→ copy to controlled temp/test directory
→ mutate copy
→ run test
→ discard copy
```

Nunca modificar la fuente original.

---

## 7. Adapter objetivo

Crear adapter mínimo:

```text
python-generic
```

o nombre equivalente coherente con arquitectura existente.

No llamarlo `legacymapper-python`.

El adapter debe ser tecnológicamente Python, no específico al producto LegacyMapper.

---

## 8. Scope del adapter Python piloto

Cubrir únicamente construcciones necesarias observadas realmente en el corpus:

- `.py` source artifacts;
- packages/modules;
- classes;
- functions/methods;
- CLI/main entry points;
- imports/dependencies;
- direct calls resolubles;
- filesystem/data operations si pueden detectarse estáticamente;
- external/provider dependencies si pueden expresarse como `ExternalDependency`;
- functional paths/flows con resolución conservadora;
- unresolved cuando no sea seguro resolver.

No intentar interpretar todo Python.

No ejecutar AST-derived code.

Usar parser/AST estático.

---

## 9. Regla de neutralidad

El adapter Python produce contratos V5.1 existentes.

No agregar al Core:

```text
PythonFunction
PythonModule
PythonImport
```

como entidades core nuevas.

Mapear hacia contratos neutrales existentes:

```text
SourceArtifact
Project
Component
EntryPoint
Call
ExternalDependency
DataOperation
FunctionalPath
FunctionalFlow
EvidenceReference
```

Technology-specific metadata solo en provenance/adapter metadata cuando corresponda.

---

## 10. AST / parsing

Permitido:

```text
ast.parse
tokenize
static file parsing
```

No permitido:

```text
import target modules
exec
eval
compile target for execution
runpy
subprocess target
pip install
execute CLI
```

El target es data.

---

## 11. Self-analysis contamination guard

Como el target es una copia de LegacyMapper:

- el adapter nuevo NO debe estar presente dentro del source target si la copia es anterior a V5.9;
- si la copia contiene cambios recientes de V5.9, crear/fijar una copia congelada desde el commit V5.8;
- registrar el commit/source snapshot si es identificable;
- no permitir que la implementación del adapter cambie el corpus durante la misma medición.

Objetivo:

```text
adapter implementation
≠
target source snapshot
```

---

## 12. Entrada temporal recomendada

Si la copia autorizada no está claramente congelada:

crear una copia controlada desde el estado publicado V5.8:

```text
source snapshot = bcb8d57097ec769da75f5fc7207b9a6db295e374
```

Solo si puede hacerse sin alterar historia y sin red.

No usar un working tree con cambios V5.9 como corpus final.

---

# V5.1 — NORMALIZED EVIDENCE

## 13. Validación

Generar Evidence neutral Python.

Registrar counts por:

```text
SourceArtifact
Project
Component
EntryPoint
Call
ExternalDependency
DataOperation
FunctionalPath
FunctionalFlow
EvidenceReference
unresolved
```

No exigir DataOperation si el corpus no ofrece un caso estático seguro.

No inventarlo.

---

## 14. Provenance

Cada entidad debe conservar:

```text
source file
line/span if available
adapter_id
adapter_version
evidence refs
deterministic identity
```

---

## 15. Determinism

Dos runs equivalentes del corpus congelado deben producir:

```text
same normalized identities
same ordering
same bytes where applicable
```

---

# V5.2 — DOCUMENTATION

## 16. Human profiles

Generar:

```text
human-functional
human-technical
```

sin template/renderer Python-specific.

Verificar que headings y rendering neutros no asumen:

```text
ASPX
WebForms
Oracle
VB.NET
```

fuera de data/provenance.

---

## 17. AI context

Generar:

```text
ai-context
```

con los contratos V5.5 existentes.

No provider real.

---

# V5.3 — CACHE

## 18. Cold/warm

Sobre Python:

```text
cold run
warm unchanged run
```

Medir hits/misses y outputs.

---

## 19. Incremental single-file

Sobre COPIA controlada:

modificar un archivo Python representativo.

Preferir un cambio simple que altere una función/call sin romper parsing.

Demostrar:

```text
1 file changed
→ bounded recomputation
```

Documentar exactamente qué se recomputó.

---

# V5.4 — ADAPTERS

## 20. Coexistencia

Deben coexistir:

```text
vbnet-webforms-oracle
python-generic
```

Probar selección correcta.

Wrong adapter:

```text
IST + python adapter
→ NOT_APPLICABLE / reject

Python corpus + vbnet adapter
→ NOT_APPLICABLE / reject
```

---

## 21. Core leakage guard

Buscar fuera de:

```text
legacy_documenter/adapters/<python-adapter>/
```

nuevos imports/lógica específicos de:

```text
ast
Python syntax
.py semantics
python-specific resolution
```

No debe contaminar core.

Wrappers neutrales mínimos solo si el contrato existente los requiere.

---

# V5.5 — PROVIDER

## 22. Fake provider E2E

Ejecutar:

```text
Python Evidence
→ AI context
→ Fake provider
→ structured response
→ grounding
→ proposal
```

Esperado:

```text
provider calls real = 0
LLM calls real = 0
proposal pending human review
```

---

# V5.6 — SEGMENTATION

## 23. Flows Python

Medir flows reales.

Si alguno excede budget:

```text
REAL segmentation
```

Si ninguno:

```text
NOT_TRIGGERED_REAL
```

y usar fixture Python controlado grande para validar contrato:

```text
CONTROLLED_FIXTURE
```

No mezclar ambas etiquetas.

---

# V5.7 — REVIEW / CANONICAL

## 24. Proposal Python

Fake provider produce proposal.

Debe permanecer:

```text
READY_FOR_REVIEW
canonical = false
```

---

## 25. Controlled approval

Solo sobre copia/artifact controlado:

```text
review prepare
→ APPROVE
→ canonical
→ audit chain
```

No aprobar automáticamente una proposal “real” del piloto.

---

## 26. Stale test

Sobre copia:

```text
prepare
→ mutate referenced Evidence
→ approve
→ PROPOSAL_STALE
```

---

# V5.8 — CONSUMERS / PLUGINS

## 27. ConsumerFacade Python

Probar:

```text
READ_EVIDENCE
READ_FLOW
READ_PARTIAL_FLOW if available
READ_AI_CONTEXT
RENDER_HUMAN_DOC
EXPORT_JSON
READ_CANONICAL controlled
READ_REVIEW_HISTORY controlled
```

Mismo contract 1.0.

---

## 28. Plugin manifest

Usar mismo Fake manifest V5.8.

No cambios por ser Python.

No Plugin Runtime.

---

# PILOT MATRIX

## 29. Estados

La matriz debe usar:

```text
REAL
CONTROLLED_FIXTURE
NOT_TRIGGERED_REAL
NOT_APPLICABLE
FAIL
```

Añadir además metadata global:

```text
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
```

---

## 30. Interpretación de resultados

Una fila Python puede marcar `REAL` porque el corpus es una aplicación real Python.

Pero el informe final debe mantener:

```text
real_second_technology = true
independent_external_product = false
```

No ocultar circularidad.

---

# QUALITY

## 31. Human sample

Revisar manualmente una muestra de Python:

- entry points;
- calls;
- imports/external deps;
- data/filesystem operations si existen;
- unresolved.

Registrar:

```text
sample_size
correct
incorrect
uncertain
```

No extrapolar precisión global.

---

## 32. Identity collision

Probar IDs entre:

```text
IST
Python corpus
```

para entidades con nombres similares:

```text
main
run
service
config
```

No colisiones.

---

## 33. Runtime independence

Confirmar:

- core no importa Python adapter;
- docs no importan Python adapter;
- review no importa Python adapter;
- consumers/plugins no importan Python adapter;
- provider layer no importa Python adapter;
- Python adapter no importa CLI.

---

## 34. Security

No:

- ejecutar target;
- instalar dependencias;
- acceder a red;
- importar target como package;
- escribir source original.

---

# IST REGRESSION

## 35. Full IST

Después de introducir el segundo adapter, ejecutar una regresión completa IST con AI OFF.

Esperado:

```text
added=0
removed=0
changed=0
```

respecto de V5.8.

No ampliar exclusiones.

---

## 36. Fingerprint

Inspeccionar contrato real.

Si adapter code participa en:

```text
ANALYZER_CODE_FINGERPRINT
```

el cambio puede ser legítimo.

Documentar old/new y cache invalidation.

No incrementar `ANALYZER_VERSION=3` salvo incompatibilidad real.

---

# TESTS

## 37. Python adapter tests

Cubrir:

- applicability;
- packages/modules;
- components;
- entrypoints;
- calls;
- imports/deps;
- unresolved;
- normalized projection;
- determinism;
- wrong-adapter;
- cache;
- no leakage;
- security/no execution.

---

## 38. Cross-tech tests

Usar assertions comunes para:

```text
vbnet-webforms-oracle
python-generic
```

donde contractualmente aplique.

---

## 39. Directed + full suite

Ejecutar tests V5.1–V5.8 relevantes + nuevos V5.9.

Suite completa:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline:

```text
3053 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

---

# DEUDA

## 40. Blocking

No considerar circularidad como deuda bloqueante porque fue autorizada explícitamente.

Pero registrarla como:

```text
OBSERVATION:
SELF_HOSTED_CIRCULAR_PILOT
```

FUTURE_PHASE recomendado:

```text
external independent second-tech validation
```

BLOCKING solo ante defecto técnico real.

---

# PROJECT_STATE

## 41. Si R1 queda limpia

Actualizar:

```text
current_version = V5.9
status = V5_9_IN_PROGRESS
latest_completed_round = V5.9-R1
latest_approved_round = V5.8-R3
round_status = V5_9_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_9_closed = false
next = HUMAN_REVIEW
second_technology = Python
second_adapter_id = <actual>
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
```

Eliminar/reemplazar el bloqueo anterior de fuente como estado activo.

Preservarlo en historia.

---

# ENTREGABLES

## 42. Actualizar los mismos entregables R1

Actualizar/reemplazar:

`docs/V5/V5_9_R1_INTEGRATED_DELIVERY.md`

`docs/V5/V5_9_R1_INTEGRATED_DELIVERY.json`

`docs/V5/V5_9_R1_MULTI_TECH_PILOT_MATRIX.json`

`docs/V5/V5_9_R1_SECOND_TECH_INVENTORY.json`

No crear otra ronda documental.

El inventario debe dejar constancia de:

```text
initial Gate A blocked
human explicitly authorized circular alternative
R1 resumed
```

---

# GIT

## 43. Git R1

Solo consultas.

NO:

- commit
- push
- tag
- amend
- rebase
- destructive reset
- clean

---

# ESTADOS FINALES

## 44. Éxito

```text
V5_9_R1_READY_FOR_HUMAN_REVIEW
```

y:

```text
V5_9_NEXT_R3_FINAL_VERIFICATION
```

si no hay defecto real.

O:

```text
V5_9_NEXT_R2_TARGETED_CORRECTIONS
```

si aparece defecto real.

Bloqueo técnico:

```text
V5_9_R1_BLOCKED
```

---

## 45. Regla final

La autorización humana elimina solamente este bloqueo:

```text
SECOND_TECH_SOURCE
```

No relaja ningún criterio técnico.

Ejecutar:

```text
freeze Python source snapshot
→ measure
→ build generic Python adapter
→ validate normalized core
→ templates
→ cache
→ Fake provider
→ segmentation
→ controlled review/canonical
→ consumers/plugins
→ cross-tech guards
→ full IST regression
→ full suite
→ update same R1 artifacts
→ stop for human review
```

No presentar circularidad como independencia externa.

No usar red.

No ejecutar target.

No provider real.

No Plugin Runtime.

No iniciar V5 Closure.
