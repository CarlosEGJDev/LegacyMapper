# LegacyMapper V5.0 R1 — Architecture Contract

## MODELO RECOMENDADO

Claude Sonnet 5, medium.

Usar Opus solo si existe un bloqueo arquitectónico real que Sonnet no resuelve tras aproximadamente tres intentos bien acotados.

---

# OBJETIVO

Fijar los contratos de arquitectura de LegacyMapper V5 a partir del baseline empírico aprobado en:

```text
docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md
```

Esta ronda es:

```text
DISEÑO / DOCUMENTAL
```

NO es una ronda de implementación.

El objetivo es reducir al mínimo las correcciones posteriores de V5.1–V5.9 dejando decisiones centrales explícitas antes de tocar producción.

---

# ROOT

```text
C:\dev\LegacyMapper
```

Baseline real:

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

---

# LEE PRIMERO

Obligatorio:

```text
AGENTS.md
PROJECT_STATE.json
docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md
docs/continuity/LEGACYMAPPER_V5_ROADMAP.md
docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md
docs/V4_3/V4_3_R9_FINAL_CLOSURE_RESULT.md
```

No releer indiscriminadamente todo el repositorio si R0 ya contiene evidencia suficiente.

---

# ESTADO DE PARTIDA

```text
V4_3_CLOSED
V5_0_R0_READY_FOR_ARCHITECTURE
```

R0 identificó, entre otros:

- core V4.3 aún contaminado por vocabulario WebForms/VB/Oracle;
- `index/` como evidence y resto mayormente regenerable;
- outputs reales de ~1.6 GB;
- índices JSON monolíticos de hasta ~227 MB;
- provider ABC incompleto respecto del contrato realmente usado;
- Runtime Independence válida para `analyze/full/output-manifest`, pero `readiness/closure/human_review/second_review` todavía referencian artefactos de desarrollo;
- falta de timings por stage;
- 4 fallos actuales en tests V4-R13/R14 por expectativas históricas de `provider_calls == 0`, pese a que el piloto real V4.3 dejó `provider_calls == 1`;
- process-exit issue no reproducido;
- necesidad comprobada de documentación por templates/perfiles.

---

# PRINCIPIOS OBLIGATORIOS

```text
Python descubre; IA interpreta.
```

Preservar:

1. determinismo;
2. provenance;
3. evidence_refs;
4. semántica confirmed / inferred / unresolved;
5. no auto-approval;
6. no auto-canonicalization;
7. provider opcional;
8. Runtime Independence del producto;
9. IST como baseline real;
10. no romper V4.3 sin decisión explícita;
11. templates cambian presentación, no verdad;
12. medir antes de implementar.

---

# TAREA R1

Resolver explícitamente las decisiones abiertas de R0 y producir contratos suficientemente concretos para que R2 pueda validarlos sin reinterpretar la intención.

## 1. Normalized Evidence Contract

Definir entidades mínimas y campos.

Como mínimo considerar:

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
UnresolvedBoundary
EvidenceReference
```

Para cada entidad definir:

- identidad;
- campos obligatorios;
- campos opcionales;
- provenance;
- relaciones;
- confidence/state;
- reglas de serialización;
- extensiones específicas de adapter;
- invariantes.

Decidir explícitamente:

- qué nombres son neutrales;
- qué datos WebForms/VB/Oracle pasan a extensiones/adapters;
- cómo se preservan IDs V4.3;
- cómo se evita promover unresolved.

NO implementar.

---

## 2. Política de IDs y compatibilidad

Resolver explícitamente si V5 exige:

```text
A) byte-identical outputs V4.3
B) semantic compatibility
C) ambos, pero en capas distintas
```

La recomendación debe distinguir:

```text
internal V5 normalized model
legacy V4.3 projections
```

Definir qué invariantes son obligatorios:

- IDs;
- evidence_refs;
- conteos;
- estados;
- ordering;
- CLI;
- output paths;
- consumer projection;
- proposal semantics.

No dejar esta decisión ambigua.

---

## 3. Persistence / Knowledge Boundary

Decidir si el conocimiento normalizado:

```text
a) se persiste como artefacto propio
b) se cachea solamente
c) se persiste y además alimenta proyecciones legacy
```

Definir:

- ubicación conceptual;
- schema version;
- stage version;
- source snapshot;
- invalidation contract;
- qué es evidence;
- qué es projection;
- qué puede regenerarse sin reanalizar.

No implementar cache todavía.

---

## 4. Adapter Contract

Definir qué produce un adapter y qué NO puede hacer.

Debe cubrir:

```text
source discovery
extraction
technology-specific normalization
database-specific normalization
```

Reglas:

- adapter no interpreta significado de negocio;
- adapter no promueve confidence;
- adapter no canonicaliza;
- adapter entrega entidades normalizadas con provenance.

Mapear el caso actual:

```text
VB.NET
ASP.NET WebForms
.NET Framework
Oracle / ADO.NET
```

como adapter de referencia.

---

## 5. Projection Contract

Definir cómo V5 producirá:

```text
index/ legacy
documentation/
ai_context/
consumer_projection/
proposals/
```

a partir del conocimiento normalizado.

Resolver si `index/*.json`:

```text
continúa siendo canonical evidence
```

o pasa a ser:

```text
legacy compatibility projection
```

La respuesta debe ser explícita.

---

## 6. Template / Profile / Renderer Contract

Definir formalmente:

```text
Template = presentación
Profile = selección
Renderer = formato
```

Perfiles mínimos:

```text
human-functional
human-technical
ai-context
```

Definir:

- entradas;
- outputs;
- idioma;
- audience;
- detail level;
- evidence appendix;
- custom templates;
- default templates;
- versioning;
- cache key;
- validation;
- fallback behavior;
- errores de template.

Invariante:

```text
dos templates distintos sobre la misma evidencia
NO pueden cambiar IDs, refs, confidence, relations o unresolved.
```

---

## 7. Provider Contract

Completar el contrato real.

Debe resolver:

- `generate`;
- `structured_generate`;
- `capabilities`;
- `model_info`;
- context window;
- max output;
- structured output;
- JSON mode;
- system instruction;
- temperature control;
- lifecycle;
- timeout;
- rate limit;
- sanitización;
- credenciales;
- lazy SDK import;
- registro extensible.

Estados mínimos recomendados:

```text
SUCCESS
CONTEXT_TOO_LARGE
INVALID_STRUCTURED_OUTPUT
PROVIDER_ERROR
TIMEOUT
RATE_LIMITED
UNSUPPORTED_CAPABILITY
```

Decidir destino de `GeminiProvider` actual:

```text
complete
isolate
deprecate
```

sin implementarlo todavía.

---

## 8. Runtime / Tooling Boundary

Resolver explícitamente el destino de:

```text
readiness
closure
human_review
second_review
módulos V3 históricos acoplados a Copilot
```

Elegir y justificar entre:

```text
runtime productivo
tooling de desarrollo
legacy congelado
retirar en fase posterior
```

La distribución limpia V5 debe tener una frontera formal.

---

## 9. Observability Contract

Definir campos aditivos para:

```text
RUN_SUMMARY.json
```

Como mínimo evaluar:

```text
stage_started_at
stage_finished_at
duration_ms
peak_memory_mb
input_count
output_count
cache_hit
cache_miss
```

No romper lectores V4.3.

Definir qué métricas son:

```text
obligatorias
opcionales
diagnósticas
```

---

## 10. Incremental / Cache Contract Boundary

Sin implementar V5.3, fijar desde ahora contratos suficientes para que V5.1/V5.2 no lo bloqueen después.

Definir:

- file fingerprint;
- extractor version;
- schema version;
- reverse dependency index;
- invalidation unit;
- cache key;
- projection cache key;
- template version;
- profile version.

No diseñar algoritmos completos todavía.

---

## 11. Rich Flow Segmentation Boundary

Aunque se implemente en V5.6, decidir ahora qué campos deberá poder representar V5.1.

Como mínimo:

```text
parent_flow_id
segment_id
partial
included_paths
omitted_paths
evidence_refs
```

Evitar que V5.1 necesite un breaking change posterior.

---

## 12. Approval / Canonical Boundary

Aunque se implemente en V5.7, decidir ahora qué separación debe preservar V5.1:

```text
Evidence
→ Proposal
→ Human Decision
→ Canonical Knowledge
```

No implementar Approval Surface.

---

## 13. Resolver la inconsistencia actual de tests como decisión arquitectónica

R0 ejecutó:

```text
2169 tests
4 failures
132 skips
```

Los cuatro fallos parecen provenir de tests V4-R13/R14 que aún esperan:

```text
provider_calls == 0
real_llm_calls == 0
```

mientras el piloto real V4.3 dejó llamadas reales registradas.

R1 NO debe modificar esos tests.

Debe decidir y documentar:

- cuál es la fuente de verdad;
- si esos tests están obsoletos;
- si `PROJECT_STATE.json` debe representar historia acumulada o baseline de una fase;
- qué debe verificar R2 antes de autorizar implementación.

No declarar la suite V5 baseline "verde" hasta resolver esta contradicción.

---

## 14. Process Exit

Mantener estado:

```text
NOT_REPRODUCED
```

salvo nueva evidencia.

No diseñar una corrección especulativa.

Definir únicamente cómo observarlo si reaparece.

---

# DECISION RECORDS OBLIGATORIOS

Cada decisión importante debe tener este formato:

```text
Decision ID:
Problem:
Decision:
Rationale:
Alternatives rejected:
Compatibility impact:
Migration impact:
Acceptance test:
Deferred work:
```

No dejar decisiones como recomendaciones vagas.

---

# OUTPUT OBLIGATORIO

Crear:

```text
docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md
```

Debe incluir como mínimo:

```text
STATUS
EXECUTIVE SUMMARY
DECISIONS
NORMALIZED EVIDENCE CONTRACT
ID / COMPATIBILITY CONTRACT
ADAPTER CONTRACT
PERSISTENCE / CACHE BOUNDARY
PROJECTION CONTRACT
TEMPLATE / PROFILE / RENDERER CONTRACT
PROVIDER CONTRACT
RUNTIME / TOOLING BOUNDARY
OBSERVABILITY CONTRACT
INCREMENTAL / CACHE CONTRACT BOUNDARY
SEGMENTATION FUTURE-PROOFING
APPROVAL / CANONICAL BOUNDARY
V4.3 → V5 MIGRATION STRATEGY
TEST BASELINE RESOLUTION
ACCEPTANCE CRITERIA FOR R2
RISKS
DEFERRED ITEMS
FILES READ
FILES MODIFIED
```

---

# ACCEPTANCE CRITERIA FOR R1

R1 solo puede quedar READY si:

1. las 9 decisiones abiertas de R0 tienen respuesta;
2. no quedan contradicciones entre normalized model, projections y compatibility;
3. V5.2 puede implementarse después de V5.1 sin redefinir evidence;
4. V5.3 puede agregar cache sin cambiar IDs/schema base;
5. V5.4 puede agregar adapters sin contaminar el core;
6. V5.5 puede cambiar providers sin tocar selection/evidence;
7. V5.6 segmentation ya tiene campos previstos;
8. V5.7 approval no exige rediseñar evidence;
9. Runtime Independence tiene frontera explícita;
10. la contradicción de los 4 tests queda clasificada con criterio de resolución para R2.

---

# ESTADOS PERMITIDOS

Solo:

```text
V5_0_R1_CONTRACT_READY
V5_0_R1_BLOCKED
```

---

# RESTRICCIONES

NO:

- modificar producción;
- modificar tests;
- implementar normalized core;
- implementar adapters;
- implementar cache;
- implementar templates;
- cambiar providers;
- cambiar budgets;
- cambiar prompts de IA;
- cambiar CLI;
- corregir `PROJECT_STATE.json`;
- actualizar baselines V4.3;
- ejecutar IA real;
- iniciar R2.

---

# TESTS / COMANDOS

Esta ronda es documental.

No repetir full IST.

No repetir suite completa salvo que aparezca evidencia nueva que lo justifique.

Se permiten:

```text
grep
find
lecturas dirigidas
pequeños scripts de inspección
```

si resuelven una decisión concreta.

---

# NEXT STEP

Si queda:

```text
V5_0_R1_CONTRACT_READY
```

crear:

```text
docs/V5/V5_0_R2_CONTRACT_VALIDATION_PROPOSED_PROMPT.md
```

pero NO ejecutarlo.

R2 debe validar contratos, no implementar V5.1.

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
