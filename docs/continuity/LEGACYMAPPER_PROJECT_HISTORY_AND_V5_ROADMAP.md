# LegacyMapper — Historia del proyecto, estado actual y roadmap V5

## 1. Propósito de este documento

Este documento existe para poder retomar LegacyMapper en una conversación futura, incluso para una eventual V6, sin reconstruir nuevamente toda la historia del proyecto.

Debe leerse junto con:

- `LEGACYMAPPER_LESSONS_LEARNED.md`
- `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md`
- `CLAUDE_CODE_CLI_BEST_PRACTICES.md`

El objetivo es conservar:

- qué problema resuelve LegacyMapper;
- qué decisiones ya están cerradas;
- qué versiones se completaron;
- qué problemas reales aparecieron;
- qué arquitectura y reglas deben preservarse;
- qué debe hacerse en V5;
- qué debe quedar fuera de V5 salvo decisión explícita.

---

# 2. Visión de LegacyMapper

LegacyMapper es una herramienta de análisis y documentación de sistemas legacy.

Su principio central es:

> **Python descubre, estructura, selecciona y presupuesta; la IA interpreta.**

La herramienta debe:

1. analizar código fuente de manera determinista;
2. descubrir estructura, dependencias, entry points, accesos a datos y flujos;
3. producir evidencia trazable;
4. generar documentación humana;
5. producir contexto compacto para IA;
6. permitir que una IA proponga interpretaciones;
7. mantener esas propuestas separadas del conocimiento canónico hasta revisión humana.

LegacyMapper no debe convertir inferencias de IA en verdad automáticamente.

---

# 3. Rutas actuales

## Repositorio de desarrollo

```text
C:\dev\LegacyMapper
```

## Proyecto legacy real usado como baseline

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

## Distribución limpia recomendada

Ejemplo:

```text
C:\Tools\LegacyMapper
```

## Resultados externos recomendados

Ejemplo:

```text
C:\LegacyMapperResults
```

o:

```text
C:\PruebasLegacyMapper\Resultados
```

Los outputs grandes de análisis real no deben formar parte automáticamente del repositorio de desarrollo.

---

# 4. Fronteras de runtime

La independencia del runtime es un contrato permanente.

La distribución ejecutable no debe depender de:

```text
docs/
prompts/
tests/
PROJECT_STATE.json
governance/
resultados de rondas
documentación de desarrollo
```

La distribución limpia validada en V4.3 contiene conceptualmente:

```text
main.py
legacy_documenter\
requirements-copilot.txt   # opcional, solo para Copilot real
```

El provider de IA debe seguir siendo opcional.

El análisis determinista debe funcionar sin instalar el SDK de Copilot.

---

# 5. Versiones anteriores

## V1–V3

V1–V3 construyeron la base funcional inicial de LegacyMapper.

V3 quedó formalmente cerrada.

Principios heredados:

- preservar decisiones humanas;
- preservar estado unresolved;
- evitar inferir arquitectura no demostrada;
- trazabilidad de afirmaciones;
- separar evidencia de interpretación;
- mantener autoridad humana sobre decisiones.

---

# 6. V4

V4 consolidó el análisis técnico y el modelo de conocimiento.

Fue desarrollada en múltiples rondas y cerrada formalmente.

El trabajo incluyó, entre otros:

- scanning;
- extraction;
- resolución de llamadas;
- WebForms;
- database access;
- functional flows;
- dependency resolution;
- export;
- context;
- documentación;
- contratos plugin-facing;
- regresiones y seguridad.

V4 llegó hasta R14.

---

# 7. V4.1

V4.1 fue principalmente una fase de mantenibilidad y caracterización.

Objetivos principales:

- limpiar deuda interna;
- reforzar determinismo;
- caracterizar readiness;
- mantener comportamiento observable estable;
- evitar romper outputs ya aprobados.

V4.1 quedó cerrada.

---

# 8. V4.2

V4.2 consolidó CLI, documentación de producto y operación.

Capacidades relevantes:

```text
analyze
full
readiness
output-manifest
```

`full` es determinista salvo que el usuario habilite IA explícitamente:

```text
--allow-ai-interpretation
```

La documentación técnica de producto se llevó a español.

También se reforzó la distribución limpia.

---

# 9. Deudas heredadas anteriores a V4.3

Entre las deudas conocidas:

- F05: duración omitida por compatibilidad byte-identical previa;
- F06: ruido `InitializeComponent`;
- F07: gaps WebForms markup `outgoing_calls`;
- renderer técnico grande;
- Approval Surface no implementada;
- Plugin Runtime no implementado;
- provider abstraction aún no genérica;
- agnosticismo tecnológico aún no resuelto.

Estas deudas no deben reabrirse automáticamente en una fase futura: deben clasificarse según el scope activo.

---

# 10. V4.3 — Evidence Projection & Consumable Documentation

V4.3 fue la última consolidación funcional antes de V5.

Objetivo:

```text
legacy
  ↓
análisis determinista
  ↓
evidence
  ↓
selection
  ↓
hydration
  ↓
projection
  ↓
human docs / AI context / consumer projection
```

## Incluido

- hydration;
- selección determinista;
- documentación humana;
- scaling y partitioning;
- budgeting real;
- AI context;
- consumer projection;
- trazabilidad;
- provider real validado;
- distribución limpia;
- Runtime Independence.

## Fuera de scope

- core multi-tecnología;
- adapters genéricos;
- provider abstraction completa;
- Plugin Runtime;
- V5 redesign.

---

# 11. Rondas principales V4.3

## R0
Baseline empírico y scope.

## R1
Contrato de projection consumible.

## R2
Hydration y selección.

## R3
Documentación humana.

## R4
Scaling y partitioning.

## R5
AI context budgeting.

## R6
AI/consumer projection.

## R7
Aceptación interna.

## R8
Correcciones posteriores a piloto externo.

## R9
Cierre final y versionado.

---

# 12. Escala real del proyecto IST

El baseline real de IST utilizado durante V4.3 produjo aproximadamente:

```text
flow_count: 12642
path_count: 170020
```

El output completo puede superar ampliamente 1 GB.

Esto convirtió rendimiento, incrementalidad y almacenamiento en temas centrales para V5.

---

# 13. Problemas reales descubiertos en V4.3

## 13.1 Documentación humana demasiado grande

Una agrupación demasiado genérica produjo documentos enormes.

Corrección:

- ownership por `.vbproj`;
- subpartición cuando corresponde;
- límite adicional por cantidad de flows.

---

## 13.2 Verbosidad excesiva

Flows con muchos paths producían documentación difícil de consumir.

Corrección:

- formato summary-first;
- separar resumen de detalle exhaustivo.

---

## 13.3 Ruido técnico mezclado con incertidumbre funcional

Ejemplos como:

```text
InitializeComponent()
```

podían aparecer como findings de bajo valor.

Corrección:

- separar ruido técnico de unresolved funcional;
- conservar evidencia sin presentarla como hallazgo principal.

---

## 13.4 Budgeting incorrecto

La selección podía detenerse ante un flow gigante.

Corrección:

```text
skip, never break
```

Un candidato sobredimensionado se salta, pero no impide probar los siguientes.

---

## 13.5 Proposal diversity

El selector priorizaba de forma insuficiente diversidad de evidencia.

Se introdujeron richness buckets y orden determinista.

---

## 13.6 Selection/Packing

El problema final más importante de V4.3 fue descubierto con mediciones reales.

De 80 candidatos SMALL:

```text
40 ricos
40 restantes
```

Antes de R3A-R1:

```text
records finales: 6
ricos finales: 0
```

El rebaseline real mostró:

```text
35/40 ricos >= 16000 chars
5/40 ricos < 16000 chars
```

Los cinco ricos que sí cabían individualmente seguían quedando fuera por:

```text
orden fijo
+
first-fit greedy
+
consumo previo del budget por records triviales
```

Corrección R3A-R1:

- packing en dos pasadas;
- reserva determinista de un candidato rico por bucket 0/1 cuando cabe;
- backfill posterior con la lógica existente;
- sin aumentar budgets;
- sin truncar evidencia;
- sin modificar confidence;
- sin IA en selección.

Resultado real:

```text
rich_in_final_request_count: 0 → 1
```

El flow rescatado:

```text
FLOW-0004993422
```

---

# 14. Piloto real final V4.3

Provider:

```text
copilot-local
```

Modelo:

```text
gpt-5.6-luna
```

Resultado:

```text
SUCCESS
AI_INTERPRETATION: SUCCESS
PROPOSAL_GENERATION: SUCCESS
proposal_count: 4
```

La IA produjo propuestas grounded sobre:

```text
FLOW-0004993422
hypAnular_Click
PreAdhClasuc.txeliminar
BeginTrans
```

y también paths unresolved relacionados con:

```text
PreAdhClasuc.eliminar(...)
dbc.BeginTrans()
dbc.Close()
dbc.Rollback()
dbc.Commit()
DesplegarError(ex)
```

Esto validó de extremo a extremo:

```text
legacy real
→ análisis determinista
→ selección
→ hydration
→ packing
→ budget
→ IA real
→ findings grounded
→ proposals
```

---

# 15. Estado final V4.3

Estado oficial:

```text
V4_3_CLOSED
```

Suite final:

```text
2169 tests
0 failed
0 errors
132 skipped
```

Las propuestas permanecen:

```text
PENDING_TECHNICAL_LEAD_REVIEW
```

No se genera conocimiento canónico automáticamente.

No existe aprobación automática.

---

# 16. Uso práctico de V4.3

Para uso normal no es necesario ejecutar dos análisis separados.

Puede ejecutarse directamente:

```bat
python main.py full "<repo>" --output "<out>" --verbose --allow-ai-interpretation
```

El pipeline genera primero la evidencia determinista y después la capa IA.

La IA no reemplaza la documentación determinista.

Conceptualmente:

```text
determinista = evidencia
IA = interpretación adicional
```

---

# 17. V5 — objetivo general

V5 debe transformar LegacyMapper desde una herramienta principalmente orientada al stack legacy actual hacia un motor de conocimiento más genérico, incremental, cacheable y configurable.

Regla principal:

> **V5 no debe romper la capacidad de analizar IST demostrada por V4.3.**

IST seguirá siendo el baseline real de regresión.

---

# 18. Orden oficial de V5

Después de validar V4.3 sobre IST real y revisar la utilidad de la documentación humana y de las propuestas de IA, el orden de V5 se ajusta.

El cambio principal es adelantar documentación basada en templates desde V5.6 a V5.2.

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
V5 Closure
```

Dependencia mínima:

```text
V5.0
arquitectura y fronteras
        ↓
V5.1
modelo normalizado
        ↓
V5.2
templates + profiles + renderers
```

No conviene implementar templates directamente sobre estructuras específicas de V4.3 porque obligaría a rehacerlos después de normalizar el core.

---

# 19. V5.0 — Architecture & Contracts

Objetivo: definir la arquitectura V5 antes de modificar producción.

Debe fijar:

- fronteras;
- módulos;
- contratos;
- invariantes;
- compatibilidad con V4.3;
- runtime independence;
- estrategia de migración;
- estrategia de rollback;
- baseline de rendimiento;
- contratos de persistencia/caché;
- contracts para templates/profiles/renderers;
- frontera core/adapters/providers.

Rondas objetivo:

```text
R0 — Empirical baseline
R1 — Architecture contract
R2 — Contract validation / compatibility proof
R3 — Final architecture package
R4 — Closure
```

No todas las rondas son obligatorias si una subfase puede cerrarse antes sin perder calidad.

---

# 20. V5.1 — Normalized Evidence Core

Crear un modelo común independiente de tecnología.

Conceptos candidatos:

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

Reglas:

- el core no debe conocer WebForms;
- el core no debe conocer Oracle;
- el core no debe conocer VB.NET;
- adapters deben proyectar evidencia específica hacia contratos normalizados;
- provenance debe conservarse;
- unresolved debe conservarse;
- IDs y determinismo deben mantenerse.

---

# 21. V5.2 — Template-Driven Documentation & Output Profiles

Esta capacidad se adelanta porque V4.3 demostró una necesidad real:

- la documentación determinista es correcta pero difícil de seguir;
- la interpretación IA es grounded pero todavía demasiado técnica;
- distintos consumidores necesitan distintos outputs.

Arquitectura:

```text
Normalized Evidence
        ↓
Documentation Model
        ↓
Profile
        ↓
Template
        ↓
Renderer
        ↓
Output
```

Separación formal:

```text
Template = cómo presentar
Profile  = qué incluir
Renderer = formato final
```

Perfiles iniciales obligatorios:

```text
human-functional
human-technical
ai-context
```

Un template puede ordenar, agrupar, cambiar títulos, idioma, secciones visibles, nivel de detalle y ubicación de evidencia técnica.

Un template NO puede cambiar confidence, inventar relaciones, alterar evidence_refs ni convertir unresolved en confirmed.

Fallback:

```text
si no existe template del usuario
→ usar template interno por defecto
```

Objetivo:

> **Analizar una vez, proyectar muchas veces.**

---

# 22. V5.3 — Incremental Engine & Cache

Capacidad central de V5.

Objetivo:

```text
cambió 1 archivo
→ no analizar todo el repositorio otra vez
```

Debe cubrir fingerprints/hashes, cache por etapa, invalidación determinista, dependencias afectadas, recomputación parcial, persisted index y análisis por scope.

Scopes objetivo:

```text
repository
project
folder
component
changed
```

También debe investigar el caso observado en V4.3 donde un run determinista terminó `FINAL_SUMMARY=SUCCESS` pero el proceso Python permaneció vivo. Un run posterior con IA terminó normalmente, por lo que no debe asumirse como reproducible sin medición.

---

# 23. V5.4 — Technology / DB Adapters

Mover lógica específica fuera del core.

Arquitectura candidata:

```text
adapters/
    dotnet/
        webforms/
        modern_dotnet/
    java/
    python/
    javascript/
```

Persistencia/adapters posibles:

```text
Oracle
SQL Server
PostgreSQL
MySQL
Entity Framework
Dapper
JDBC
SQLAlchemy
```

---

# 24. V5.5 — Generic AI Provider + Context

Contrato genérico objetivo:

```text
AIProvider
    generate()
    capabilities()
    context_window
    structured_output
```

Providers posibles:

```text
Copilot
Claude
OpenAI
Ollama
Gemini
Fake
```

El core no debe depender de un provider concreto.

---

# 25. V5.6 — Rich Flow Segmentation

Resolver flows demasiado grandes con un contrato explícito:

```text
parent_flow_id
partial = true
included_paths
omitted_paths
evidence_refs
```

Nunca presentar un segmento como flow completo ni truncar evidencia silenciosamente.

---

# 26. V5.7 — Approval + Canonical Knowledge

Formalizar:

```text
Evidence
    ↓
AI Proposal
    ↓
Human Decision
    ↓
Canonical Knowledge
```

Estados humanos:

```text
APPROVE
REJECT
CORRECT
DEFER
```

Sin auto-approval ni auto-canonicalization.

---

# 27. V5.8 — Consumer / Plugin Contract

Formalizar contrato de consumidores y mantener separado `Plugin Contract` de `Plugin Runtime`.

Plugin Runtime puede quedar post-V5 si aumenta demasiado el alcance.

---

# 28. V5.9 — Real Multi-Technology Pilot

Validar con:

1. IST como baseline WebForms/Oracle;
2. al menos una segunda tecnología;
3. outputs normalizados;
4. templates humanos;
5. templates IA;
6. incremental/cache;
7. trazabilidad;
8. provider IA;
9. compatibilidad/runtime independence.

---

# 29. Persisted Knowledge / Query Layer

Evolución objetivo:

```text
repository
   ↓
normalized/persisted knowledge index
   ↓
projections
```

Desde el índice se podrán producir human docs, AI context, client docs, architect docs, queries, plugins, graphs y migration docs sin volver a escanear el repositorio completo.

Consultas objetivo:

```text
¿Dónde se usa PCOB_DEUDAS_ENCABEZADO?
¿Qué pantallas terminan en esta SP?
¿Qué flows escriben en esta tabla?
¿Quién llama a blCobMorosidad?
```

Primero respuesta determinista; IA solo para explicación opcional.

---

# 30. Baseline humano/IA de V4.3 para comparar V5

V4.3 real sobre IST produjo:

```text
deterministic documentation: SUCCESS
AI interpretation: SUCCESS
proposal generation: SUCCESS
```

Run reciente:

```text
provider: copilot-local
model: mai-code-1.1-flash
proposals: 3
```

Las propuestas fueron grounded y trazables, pero siguen usando lenguaje técnico del tipo `FLOW`, `DAO`, `PATH` y `CALL`.

Objetivo V5.2:

```text
Nivel 1 — humano/funcional
Nivel 2 — técnico
Nivel 3 — evidencia/auditoría
```

La misma evidencia debe poder proyectarse a los tres niveles.

---

# 31. Proceso por subfase V5.*

Patrón preferido:

```text
R0 — Empirical baseline
R1 — Contract & design
R2 — Implementation
R3 — Verification + real regression
R4 — Closure
```

Solo agregar R2A/R3A/etc. ante evidencia inesperada.

Si una subfase comienza a acumular muchas rondas correctivas, detener y rediagnosticar antes de seguir.

---

# 32. Regla de modelos Claude

Experiencia real:

Sonnet 5 medium produjo buenos resultados durante V3 y V4.

```text
Sonnet 5 medium
→ modelo principal

Opus
→ arquitectura crítica
→ contratos difíciles
→ rediseño complejo
→ diagnóstico persistente
```

Después de aproximadamente tres intentos fallidos atribuibles al modelo, cambiar de modelo.

---

# 33. Principios permanentes

1. Python descubre; IA interpreta.
2. No inventar cuando existe incertidumbre.
3. Evidencia primero.
4. Human approval antes de canonical knowledge.
5. Runtime independiente de gobernanza.
6. Medir antes de diseñar.
7. IST es baseline real.
8. Tests sintéticos no reemplazan pruebas reales.
9. No romper contratos cerrados sin evidencia.
10. Analizar una vez, proyectar muchas veces.
11. Templates controlan presentación, no verdad.
12. Incremental/cache es capacidad central.
13. Multi-tecnología se resuelve mediante adapters.
14. Provider IA debe ser sustituible.
15. IDs/evidence refs deben permanecer disponibles para auditoría aunque se oculten en la vista humana.
16. Rendimiento debe medirse desde R0, no al final.

---

# 34. Punto de partida oficial de V5

Estado:

```text
V4_3_CLOSED
V5_0_READY_TO_START
```

Primer trabajo:

```text
V5.0 R0 — Empirical Baseline & Architecture Preparation
```

R0 debe ser diagnóstico/documental y no debe modificar producción.

---

# 35. Punto de partida para una futura V6

Antes de iniciar V6:

1. leer este documento;
2. leer `LEGACYMAPPER_LESSONS_LEARNED.md`;
3. leer `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md`;
4. leer `CLAUDE_CODE_CLI_BEST_PRACTICES.md`;
5. revisar el cierre formal de V5;
6. confirmar rutas actuales;
7. ejecutar suite baseline;
8. medir el estado real antes de diseñar V6.
