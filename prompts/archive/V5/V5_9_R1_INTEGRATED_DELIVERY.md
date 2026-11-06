# LegacyMapper V5.9 — R1 Integrated Delivery
## Real Multi-Technology Pilot

## Objetivo

Ejecutar el piloto real multi-tecnología de V5 con el patrón vigente:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo oficial:

```text
IST
+ segunda tecnología real
+ normalized core
+ templates
+ incremental/cache
+ provider
+ segmentation
+ trazabilidad
+ runtime independence
```

La meta es demostrar que el mismo core V5 analiza y proyecta dos tecnologías distintas sin introducir dependencias tecnológicas nuevas en el core.

## Estado de partida

V5.8 está cerrada y publicada.

Commit efectivo:

`bcb8d57097ec769da75f5fc7207b9a6db295e374`

Estado esperado:

```text
V5_8_CLOSED
V5_8_R3_PUSHED_TO_ORIGIN_MAIN
V5_9_READY_TO_START
v5_9_started = false
```

Puede existir como única modificación administrativa local post-push:

`docs/V5/V5_8_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Preservarla.

## Fuentes obligatorias

Leer antes de diseñar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierres V5.0–V5.8
- ambos roadmaps/continuidad
- V5.1 Evidence
- V5.2 templates/profiles/renderers
- V5.3 cache/fingerprints
- V5.4 adapters
- V5.5 AI provider/context
- V5.6 segmentation
- V5.7 review/canonical
- V5.8 consumer/plugin contract
- `legacy_documenter/adapters/`
- `legacy_documenter/evidence/`
- `legacy_documenter/cache/`
- `legacy_documenter/documentation_v52/`
- `legacy_documenter/context/`
- `legacy_documenter/consumers/`

Regla:

```text
medir antes de diseñar
```

# Gate A — segunda tecnología real

## Descubrir corpus disponibles

Antes de elegir stack, inventariar fuentes locales ya disponibles que NO sean IST/WebForms/VB.NET/Oracle.

Buscar sin red:

- fixtures;
- sample repos;
- demo repos;
- carpetas de pruebas;
- fuentes reales locales documentadas;
- corpus Java, Python, JavaScript/TypeScript, modern .NET u otra tecnología.

Para cada candidato medir:

```text
technology
repository/path
file_count
source_bytes
project/build files
entrypoint forms
call forms
data-access forms
external dependencies
representativeness
```

No seleccionar por conveniencia antes de medir.

## Selección

Elegir exactamente UNA segunda tecnología.

Prioridad:

1. corpus real/local;
2. pequeño para iterar;
3. suficientemente representativo para artifacts, components, entry points, calls, paths/flows y data/external deps si existen;
4. diferente de VB.NET WebForms/Oracle;
5. sin network.

Preferencias solo si los candidatos son equivalentes:

```text
Python
Java
JavaScript/TypeScript
modern .NET
```

## Bloqueo por falta de fuente

Si NO existe fuente real/local utilizable:

```text
V5_9_R1_BLOCKED_SECOND_TECH_SOURCE
```

No fabricar un piloto “real” con un fixture trivial nuevo.

Documentar candidatos inspeccionados y requisitos mínimos de la fuente que debe aportar el humano.

Fixtures sintéticos solo sirven para unit tests.

# Gate B — baseline

## IST

Revalidar:

```text
source files = 15138
source SHA256 = 77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
output files = 47523
output bytes = 2828066791
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT =
4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6
```

No modificar IST.

## Segundo corpus

Registrar:

```text
SECOND_TECH_SOURCE_ID
technology
root
file_count
source_bytes
source_sha256/tree_hash
project_count
candidate_entrypoints
candidate_calls
candidate_data_access
candidate_external_dependencies
```

Fuente read-only.

# Gate C — adapter

## Principio

```text
technology-specific source
→ adapter/extraction
→ normalized Evidence Core
→ V5 common pipeline
```

Nunca modificar Evidence Core solo para acomodar el nuevo stack.

## Contrato

Reutilizar V5.4.

No crear contract v2 salvo contradicción real.

Declarar:

```text
adapter_id
adapter_version
technology
capabilities
```

## Scope mínimo

Implementar solo lo necesario para el piloto:

- source artifacts;
- project/component structure;
- entry points;
- calls/dependencies;
- functional paths/flows;
- data/external operations si existen;
- unresolved cuando no pueda resolverse con seguridad.

No cubrir todo el ecosistema de la tecnología.

## Unresolved

```text
si no puede resolverse determinísticamente
→ preserve unresolved
```

No inventar relaciones para subir coverage.

## Leakage guard

Fuera del nuevo adapter no deben aparecer imports o lógica del nuevo stack en:

- Evidence Core;
- context;
- cache;
- consumers;
- review;
- canonical;
- templates;
- plugin contract.

# Validación V5.1 — Normalized Core

Comparar IST y segundo stack sobre las categorías relevantes:

```text
SourceArtifact
Project
Component
EntryPoint
Call
DataOperation
ExternalDependency
FunctionalPath
FunctionalFlow
EvidenceReference
```

No exigir todas las categorías si no aplican.

Registrar por stack:

```text
count by entity type
confirmed
inferred
unresolved
evidence refs
```

Usar el `EVIDENCE_SCHEMA_VERSION` vigente.

Provenance debe conservar source artifact, location, adapter/extractor, refs e identidad determinista.

# Validación V5.2 — Templates

Generar para ambos stacks:

```text
human-functional
human-technical
ai-context
```

Confirmar que usan los mismos contratos/profile/template/renderers.

No crear renderer especial por tecnología salvo evidencia estrictamente necesaria.

No hardcodear WebForms/ASPX/Oracle en capas neutrales.

# Validación V5.3 — Cache / Incremental

## Cold run

Registrar:

```text
wall time
files scanned
files analyzed
cache hits/misses
artifacts produced
```

## Warm unchanged run

Esperado:

```text
same outputs
high cache reuse
minimal recomputation
```

## Single-file change

Sobre COPIA controlada del segundo corpus:

- modificar exactamente un archivo representativo;
- ejecutar incremental;
- medir changed files, affected artifacts, recomputed stages, hits/misses y outputs intactos;
- no modificar fuente original.

Objetivo:

```text
small source change
→ bounded recomputation
```

Cache identity no debe asumir WebForms/Oracle.

# Validación V5.4 — Adapters

Deben coexistir:

```text
vbnet-webforms-oracle
<second-adapter>
```

Probar wrong-adapter:

```text
IST + second adapter → reject/not-applicable
second tech + vbnet-webforms-oracle → reject/not-applicable
```

# Validación V5.5 — Provider

No usar provider real.

Usar Fake/networkless:

```text
normalized evidence
→ AI context
→ Fake provider
→ structured response
→ grounding validation
→ proposal
```

Esperado:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
```

Adapter nuevo no importa providers.

# Validación V5.6 — Segmentation

Medir flows del segundo stack.

Si existe flow grande real:

- segmentarlo;
- validar partial, included/omitted, refs, union y no overlap.

Si no existe:

- documentar `NOT_TRIGGERED_REAL`;
- usar fixture del nuevo adapter para probar compatibilidad contractual;
- no afirmar que el corpus real necesitó segmentación.

Nunca truncar silenciosamente.

# Validación V5.7 — Review / Canonical

Con Fake:

```text
second-tech evidence
→ proposal
→ pending review
canonical = false
```

Sobre COPIA controlada:

- `review prepare`;
- APPROVE simulado;
- canonical readback;
- audit chain.

No aprobar artifacts reales automáticamente.

Probar stale:

```text
prepare baseline
→ evidence cambia
→ approve
→ PROPOSAL_STALE
```

# Validación V5.8 — Consumers / Plugins

Ejecutar sobre segundo stack:

- READ_EVIDENCE;
- READ_FLOW;
- READ_PARTIAL_FLOW si aplica;
- READ_AI_CONTEXT;
- RENDER_HUMAN_DOC;
- EXPORT_JSON;
- READ_CANONICAL sobre artifact controlado;
- READ_REVIEW_HISTORY.

Usar el mismo Fake manifest V5.8.

No Plugin Runtime.

# Pilot Matrix

Crear matriz comparativa:

| Capability | IST WebForms/Oracle | Second Technology | Result |
|---|---|---|---|
| Adapter detection | | | |
| Normalized Evidence | | | |
| Provenance | | | |
| Unresolved | | | |
| human-functional | | | |
| human-technical | | | |
| AI context | | | |
| Cold cache | | | |
| Warm cache | | | |
| Single-file incremental | | | |
| Fake provider proposal | | | |
| Segmentation contract | | | |
| Review baseline | | | |
| Canonical controlled | | | |
| ConsumerFacade | | | |
| Plugin Contract | | | |
| Runtime independence | | | |

Usar estados:

```text
REAL
CONTROLLED_FIXTURE
NOT_TRIGGERED_REAL
NOT_APPLICABLE
FAIL
```

No marcar PASS real con evidencia sintética.

# Quality / Cross-tech

## Coverage

Para ambos stacks:

```text
source files
projects
components
entry points
calls
data operations
external dependencies
paths
flows
unresolved
```

## Human sample review

Sobre segundo stack, revisar muestra pequeña de:

- entry points;
- calls;
- data access;
- unresolved.

Documentar:

```text
sample size
correct
incorrect
uncertain
```

No extrapolar precisión global.

## Determinism

```text
same source + same config + same adapter version
→ same normalized outputs
```

## Collision

Probar que entidades parecidas de ambos stacks no colisionen.

No cambiar contrato de IDs sin necesidad.

## Runtime independence

Demostrar:

- core no depende del segundo adapter;
- second adapter no depende de CLI;
- consumers/plugins no dependen del adapter;
- review/canonical no dependen del adapter;
- templates no importan adapter.

## Security

No network.
No ejecutar código analizado.
No shell/build/compiler automáticamente.
No secrets.
No escribir en source repo.

Si parsing exige ejecutar build/compiler:

```text
stop + justify
```

# IST regression

V5.9 toca adapters/selección: ejecutar preferentemente una regresión real completa IST, AI OFF.

Esperado respecto de V5.8:

```text
added = 0
removed = 0
changed = 0
```

No ampliar exclusiones.

Registrar wall time, cache state, output count/bytes y memoria si está disponible.

# Tests

Crear unit tests del nuevo adapter para:

- detection/applicability;
- project structure;
- artifacts;
- entrypoints;
- calls;
- data/external operations;
- unresolved;
- normalized projection;
- deterministic IDs;
- wrong-adapter;
- no core leakage;
- cache identity.

Agregar cross-tech contract tests usando los mismos assertions cuando corresponda.

Tests dirigidos deben cubrir V5.1–V5.8 relevantes.

Suite completa:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline V5.8:

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

# Performance / Maintainability

Medir:

- adapter detection;
- extraction;
- normalization;
- flow resolution;
- docs;
- cold cache;
- warm cache;
- incremental.

Auditar before/after:

- module count;
- adapter sizes;
- imports;
- technology-specific strings outside adapter;
- provider imports;
- cache coupling.

No crear adapter monolítico si la evidencia justifica separar adapter/extractors/analysis/normalization.

No sobrearquitectar.

# Analyzer fingerprint

Inspeccionar el contrato vigente para decidir si el nuevo adapter cambia:

```text
ANALYZER_CODE_FINGERPRINT
```

No hardcodear la respuesta.

Si cambia legítimamente:

- old/new;
- razón;
- invalidación esperada.

`ANALYZER_VERSION=3` no debe cambiar salvo incompatibilidad real.

# Deuda

Clasificar:

```text
BLOCKING
FUTURE_PHASE
OBSERVATION
```

BLOCKING si:

- core requiere cambios específicos del stack;
- adapter no produce Evidence válido;
- IST regresa;
- templates requieren forks tecnológicos;
- cache falla cross-tech;
- IDs colisionan;
- provider/context depende del stack;
- consumers se rompen;
- runtime independence falla;
- suite roja.

FUTURE_PHASE aceptable:

- coverage exhaustiva;
- frameworks extra;
- DB adapters adicionales;
- build-system enrichment;
- provider real;
- Plugin Runtime;
- tercera tecnología.

# Definition of Done R1

R1 lista si:

- existe fuente real de segunda tecnología;
- fuente medida/read-only;
- segundo adapter mínimo funcional;
- Evidence neutral válido;
- provenance/unresolved preservados;
- human docs funcionan;
- AI context funciona;
- cache cold/warm/incremental demostrado;
- Fake provider grounded E2E;
- segmentation compatible;
- review/canonical controlado funciona;
- consumers/plugins funcionan;
- no technology leakage;
- runtime independence;
- determinism;
- IST full regression verde;
- full suite verde;
- BLOCKING = [].

# R2 solo si hace falta

Abrir R2 solo por defecto real:

- leakage;
- normalized contract defect;
- cache invalidation defect;
- IST regression;
- collision;
- partial defect;
- stale/review defect;
- consumer/plugin incompatibility;
- suite roja;
- regresión material de performance.

No abrir R2 por coverage adicional, otro framework, tercera tecnología, provider real, Plugin Runtime o V5 Closure.

Si R1 queda limpia:

```text
R1 → R3
```

# PROJECT_STATE

Al finalizar con éxito:

```text
current_version = V5.9
status = V5_9_IN_PROGRESS
latest_completed_round = V5.9-R1
latest_approved_round = V5.8-R3
round_status = V5_9_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_9_closed = false
next = HUMAN_REVIEW
```

Registrar además:

```text
second_technology
second_adapter_id
second_source_id/hash
```

No cerrar V5.9.
No iniciar V5 Closure.

# Continuidad

Actualizar:

- V5.8 CLOSED;
- V5.9 R1;
- segunda tecnología elegida con evidencia;
- pilot matrix;
- R2 solo si defecto real;
- V5 Closure no iniciada.

# Git

R1:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO reset destructivo;
- NO clean.

Registrar branch, HEAD, origin/main, ahead/behind, cambios y recibo post-push V5.8.

# Entregables

Crear:

`docs/V5/V5_9_R1_INTEGRATED_DELIVERY.md`

Recomendado:

`docs/V5/V5_9_R1_INTEGRATED_DELIVERY.json`

Obligatorio:

`docs/V5/V5_9_R1_MULTI_TECH_PILOT_MATRIX.json`

Recomendado:

`docs/V5/V5_9_R1_SECOND_TECH_INVENTORY.json`

El Markdown debe cubrir: objetivo, estado, fuentes, descubrimiento de corpus, selección, baseline, adapter, Evidence, provenance, unresolved, templates, AI context, cache cold/warm/incremental, coexistencia/wrong-adapter, Fake provider, segmentation, review/canonical, stale guard, consumers/plugins, pilot matrix, coverage, human sample, determinism, collisions, runtime independence, security, IST regression, performance, tests, maintainability, fingerprint/cache, debt, PROJECT_STATE, continuidad, Git y recomendación R2/R3.

# Estados finales permitidos

Éxito:

```text
V5_9_R1_READY_FOR_HUMAN_REVIEW
```

y exactamente una:

```text
V5_9_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_9_NEXT_R3_FINAL_VERIFICATION
```

Sin fuente real:

```text
V5_9_R1_BLOCKED_SECOND_TECH_SOURCE
```

Otro bloqueo:

```text
V5_9_R1_BLOCKED
```

# Regla final

Ejecutar:

```text
descubrir y medir segunda fuente real
→ elegir stack
→ diseñar adapter mínimo
→ implementar
→ normalizar
→ docs
→ cache
→ Fake provider
→ segmentation
→ review/canonical controlado
→ consumer/plugin
→ cross-tech guards
→ IST regression real
→ full suite
→ documentar
```

No usar red.
No descargar repos.
No ejecutar código del proyecto analizado.
No usar provider real.
No implementar Plugin Runtime.
No iniciar V5 Closure.
Detenerse para revisión humana.
