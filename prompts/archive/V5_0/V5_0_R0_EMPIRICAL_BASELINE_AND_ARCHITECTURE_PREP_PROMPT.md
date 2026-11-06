# LegacyMapper V5.0 R0 — Empirical Baseline & Architecture Preparation

## Modelo recomendado

Claude Sonnet 5, medium.

No usar Opus salvo bloqueo arquitectónico real.

---

# Objetivo

Preparar el baseline empírico y arquitectónico de LegacyMapper V5 antes de modificar producción.

Esta ronda es:

```text
DIAGNOSTIC / DOCUMENTAL
```

NO modificar código productivo.

---

# Root

```text
C:\dev\LegacyMapper
```

Target real conocido:

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

---

# Estado de partida

```text
V4_3_CLOSED
V5_0_READY_TO_START
```

V4.3 ya demostró sobre IST real análisis determinista, documentación, ai_context, consumer_projection, AI interpretation real, proposals grounded, Runtime Independence, clean distribution, no auto-approval y no canonical knowledge automático.

Último run real conocido:

```text
Deterministic analysis: SUCCESS
Documentation: SUCCESS
AI requested: True
AI invoked: True
AI_INTERPRETATION: SUCCESS
PROPOSAL_GENERATION: SUCCESS
FINAL_SUMMARY: SUCCESS
3 proposals pending
provider: copilot-local
model: mai-code-1.1-flash
```

Existe además una observación: un run determinista escribió `FINAL_SUMMARY=SUCCESS` y `RUN_SUMMARY`, pero el proceso Python quedó vivo. Un run posterior con IA terminó normalmente. No declarar causa raíz sin reproducirla.

---

# Principios obligatorios

```text
Python descubre; IA interpreta.
```

Preservar determinism, provenance, unresolved, evidence_refs, no auto-approval, no auto-canonicalization, Runtime Independence, IST como baseline y compatibilidad V4.3 salvo decisión explícita.

---

# Roadmap V5 vigente

```text
V5.0 — Architecture & Contracts
V5.1 — Normalized Evidence Core
V5.2 — Template-Driven Documentation & Output Profiles
V5.3 — Incremental Engine & Cache
V5.4 — Technology / DB Adapters
V5.5 — Generic AI Provider + Context
V5.6 — Rich Flow Segmentation
V5.7 — Approval + Canonical Knowledge
V5.8 — Consumer / Plugin Contract
V5.9 — Real Multi-Technology Pilot
```

V5.2 fue adelantada porque la prueba real confirmó que la documentación determinista es correcta pero difícil de seguir y las AI proposals son grounded pero demasiado técnicas.

---

# Tarea R0

## 1. Inventario arquitectónico

Identificar módulos principales, dependencias internas, entrypoint CLI, etapas del pipeline, models/contracts, exporters, projections, documentation renderers, providers, selection/hydration/packing y runtime packaging.

No leer indiscriminadamente todo el repositorio si existen índices/tests/result docs suficientes.

## 2. Mapa de acoplamientos tecnológicos

Identificar exactamente qué partes están acopladas a:

```text
VB.NET
ASP.NET WebForms
.NET Framework
Oracle
Copilot
```

Clasificar cada acoplamiento como core, adapter candidate, provider candidate, presentation o legacy compatibility.

No corregirlos.

## 3. Contratos V4.3 que deben preservarse

Identificar IDs, evidence refs, unresolved semantics, deterministic ordering, proposal status, runtime independence, clean distribution, CLI behavior, output directories, consumer projection, human documentation y provider optionality.

## 4. Baseline de rendimiento

Usar evidencia existente y solo comandos no destructivos si son necesarios.

Medir/documentar suite size, flows/paths del baseline real, tamaño aproximado de outputs, archivos más grandes, etapas costosas, duplicación aparente, lazy generation y cache candidates.

No ejecutar un full IST adicional si no aporta evidencia nueva.

## 5. Baseline de documentación

Comparar conceptualmente:

```text
documentation/
proposals/
ai_context/
consumer_projection/
```

Determinar qué es evidence, presentation, AI-facing, qué puede regenerarse sin reanalizar y qué debería persistirse como normalized knowledge.

## 6. Requisitos de templates V5.2

Diseñar requisitos, NO implementación.

Perfiles mínimos:

```text
human-functional
human-technical
ai-context
```

Separar:

```text
Template = presentación
Profile = selección
Renderer = formato
```

Templates no alteran evidence/confidence/relationships/unresolved.

## 7. Baseline incremental V5.3

Identificar qué stages podrían reutilizar resultados si cambian pocos archivos. Documentar hipótesis sobre fingerprints, cache keys, invalidation, dependency propagation y persisted index.

NO implementar.

## 8. Provider abstraction baseline

Mapear qué partes dependen hoy de Copilot/FAKE e identificar el contrato mínimo para providers futuros: Copilot, Claude, OpenAI, Ollama, Gemini y Fake.

NO implementar.

## 9. Runtime Independence

Verificar que runtime productivo no dependa de:

```text
docs/
prompts/
tests/
PROJECT_STATE
governance/
resultados de desarrollo
```

No modificar packaging.

## 10. Observación de process exit

Buscar evidencia en código/tests de provider lifecycle, threads, executors, atexit, subprocess o Copilot CLI, pero NO cambiar nada.

Conclusión permitida:

```text
reproducible
not reproduced
insufficient evidence
```

---

# Output obligatorio

Crear:

```text
docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md
```

Debe contener:

```text
STATUS
SCOPE
CURRENT ARCHITECTURE
V4.3 CONTRACTS TO PRESERVE
TECHNOLOGY COUPLINGS
PROVIDER COUPLINGS
DOCUMENTATION/PROJECTION BASELINE
PERFORMANCE/SCALE BASELINE
INCREMENTAL/CACHE CANDIDATES
TEMPLATE/PROFILE REQUIREMENTS
RUNTIME INDEPENDENCE
PROCESS EXIT OBSERVATION
RISKS
OPEN DECISIONS FOR R1
RECOMMENDED R1 CONTRACT BOUNDARIES
TESTS / COMMANDS EXECUTED
FILES READ
FILES MODIFIED
```

---

# Estados permitidos

```text
V5_0_R0_READY_FOR_ARCHITECTURE
V5_0_R0_BLOCKED
```

---

# Restricciones

NO modificar producción, implementar normalized core, crear adapters, implementar cache/templates, cambiar providers/budgets/prompts/CLI, actualizar baselines cerrados ni arreglar deudas.

---

# Tests

Ejecutar solo tests/comandos necesarios para establecer baseline. Si la suite completa tiene evidencia reciente y repetirla no aporta valor, documentarlo y evitar gasto innecesario.

---

# Next step

Si queda `V5_0_R0_READY_FOR_ARCHITECTURE`, crear un prompt propuesto para:

```text
V5.0 R1 — Architecture Contract
```

pero NO ejecutarlo.

Si queda BLOCKED, explicar exactamente qué evidencia falta.

---

# Principio final

```text
medir → comprender → fijar contrato → implementar una vez
```
