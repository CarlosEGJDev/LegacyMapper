# LegacyMapper — Historia del proyecto, estado actual y roadmap V5

> **Actualización de continuidad — 29-09-2026:** V5.0 y V5.1 están cerradas; V5.2 tiene implementación y revisión de R3.4.1 realizadas, pero **NO está cerrada formalmente**. Falta la aprobación explícita del Technical Lead y ejecutar/documentar R4 de cierre. Los estados antiguos `V5_0_READY_TO_START` que figuran más abajo son una fotografía histórica, no el estado vigente. El siguiente paso no es V5.3 ni activar IA en V5.2.


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

---

# 36. Actualización de continuidad V5.0–V5.2 (29-09-2026)

Esta sección actualiza el punto de partida histórico de §34 sin borrar el registro V1–V4.3.

## Estado confirmado y autoridad

```text
V4_3_CLOSED
V5.0 — cerrada (Architecture & Contracts)
V5.1 — CERRADA; cierre formal: docs/V5/V5_1_R4_CIERRE_FINAL.md
V5.2 — R3.4.1 READY_FOR_HUMAN_REVIEW; R4 NO ejecutada ni aprobada
V5.3 — NO iniciada
```

**No declarar `V5_2_CLOSED`, `READY_FOR_R4` ni iniciar V5.3 por inferencia.** La revisión conversacional consideró satisfactorias las correcciones R3.4.1, pero el usuario seleccionó revisar un aspecto adicional antes del cierre y después consultó por la distinción entre documentación determinista e interpretación IA. No consta todavía una autorización explícita de R4. Al reanudar: confirmar con el usuario si aprueba humanamente R3.4.1 y autoriza preparar el prompt R4; no generarlo antes de esa autorización.

## Entregables y secuencia V5.2

| Ronda | Resultado | Estado práctico |
| --- | --- | --- |
| R0 | `docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md` | Baseline documental realizado. |
| R1 | `docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md` | Contrato de perfiles/templates. |
| R2 | `docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md` | Motor inicial implementado. |
| R3 | `docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md` | Validación técnica; aprobación humana retenida por errores semánticos. |
| R3.1 | `docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md` | Propiedad de pantallas, flujos y acceso real a datos corregidos. |
| R3.2 | `docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md` | Identidad real de proyectos y dirección de dependencias. |
| R3.3 | `docs/V5/V5_2_R3_3_COMPONENT_NAVIGATION.md` | Navegación Solution→Project→Archivo→Componente→métodos. |
| R3.4 | `docs/V5/V5_2_R3_4_METHOD_TRACEABILITY.md` | Relaciones técnicas individuales por método, con límites de atribución declarados. |
| R3.4.1 | `docs/V5/V5_2_R3_4_1_METHOD_DETAIL_QUALITY.md` | Calidad del detalle y filtro de documentos de bajo valor; `READY_FOR_HUMAN_REVIEW`. |
| R4 | No existe cierre aportado en este handover | Pendiente de aprobación y ejecución; NO se ha generado prompt R4. |

Los prompts nuevos deben guardarse bajo `prompts/V5/`; un único resultado de ronda bajo `docs/V5/`. Claude puede tener referencias antiguas a `prompts/V5_0/`: comprobar la ruta real antes de ejecutar, no asumir que son idénticas.

## Decisiones funcionales de V5.2

- Modelo: `Evidence Core → Audience Transformation → Output Profile → Template → Markdown Renderer`. El template define cómo presentar; el perfil qué incluir; el renderer escribe Markdown. No trasladar clasificación de evidencia al renderer ni alterar Evidence Core por una mejora visual.
- Dos perfiles humanos implementados: **General Overview** (breve) y **Developer Technical** (navegación progresiva). La documentación `documentation_v52/` se genera **completa**; los ZIP `human_review_sample` enviados al asistente son solo selecciones de revisión, no el producto íntegro. `documentation/` legacy se conserva durante la transición.
- Jerarquía real: `.sln` es Solution; `.vbproj`/`.csproj` es Project; clase/formulario es Component; archivo físico es SourceArtifact. `BLInterfazSAP.vbproj` sí existe como Project dentro de `SlnInterfazSAP`; `BLInterfazSAP.vb` es su archivo de código homónimo. No inferir entidades por prefijos `BL`/`Web`/`sys` ni nombres de carpeta.
- Vistas de método: nombre/tipo/visibilidad y enlaces individuales solo donde hay relaciones verificables; llamadas salientes/entrantes, expresiones originales no resueltas y acceso real a datos separado de control transaccional. Cuando solo hay ruido técnico, un método puede permanecer en el índice sin página propia. El enlace de detalle es **documentación ya generada**, no un llamado a IA en tiempo de consulta.
- No atribuir a un método dependencias que solo se conocen a nivel de Project, ni límites de flujos no resueltos que carecen de pertenencia inequívoca al método. Sin identidad canónica por firma/sobrecarga no asignar relaciones individuales a homónimos ambiguos.
- Pertenencia ambigua: `img\aceptar.gif` aparece declarado por 5 proyectos; se muestra como compartido/ambiguo, sin atribuir propiedad exclusiva ni crear proyecto ficticio.
- Mantener métricas semánticas correctas de IST: 12.642 recorridos observados; 672 (5,3 %) alcanzan operación **real** de datos; otros 1.698 llegan exclusivamente a control transaccional. No confundir ambos grupos.

## Última evidencia de validación R3.4.1 (informe de Claude, pendiente aprobación formal humana)

- Corrida IST completa `SUCCESS`, IA opcional `NOT_RUN`, `MANIFEST.json` sin advertencias, documentación legacy preservada (876 archivos).
- `python -m unittest discover -s tests`: **2.441 pruebas, 0 fallas, 0 errores, 132 omisiones esperadas**.
- 33.610 filas de métodos identificados; documentos individuales R3.4 **22.215** → R3.4.1 **21.407** (−808). Documentos Markdown totales R3.4 **47.375** → R3.4.1 **46.567**. El criterio conserva llamadas no resueltas con expresión útil; no forzar reducción numérica perdiendo trazabilidad.
- Se verificaron **5.514 enlaces** dentro de una muestra de 3.000 documentos de la salida completa, 0 rotos **en esa muestra**; no equivale a revisión exhaustiva de todos los enlaces.
- La muestra humana R3.4.1 contiene 21 archivos y marca 103 enlaces que apuntan a contenido externo a esa selección. Esto no implica enlaces rotos del producto completo.
- Resultado completo: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\ist_full_run\documentation_v52\`.
- Muestra: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\human_review_sample\README.md`.

## Qué NO está terminado: interpretación IA en documentación V5.2

V5.2 genera documentación humana **determinista** y evidencia técnica bajo demanda (enlaces a información recopilada previamente). No genera explicaciones funcionales de IA integradas en esos documentos y abrir un enlace no ejecuta una IA. La corrida R3.4.1 confirma `AI_INTERPRETATION` y `PROPOSAL_GENERATION` en `NOT_RUN`. La capacidad IA de V4.3 (contexto y propuestas grounded) es precedente, **no** prueba de una capa interpretativa ya integrada en `documentation_v52/`. La evolución prevista pasa por V5.5 (provider genérico/contexto), V5.6 (segmentación) y V5.7 (aprobación humana/conocimiento canónico). Separar explícitamente hecho verificado, propuesta IA y conocimiento aprobado; nunca canonizar automáticamente.

## Pendientes/deudas relevantes

- `gap.method_dependencies_not_available`: dependencias declaradas solo a nivel de proyecto.
- `gap.method_unresolved_not_attributable`: límites de flujo no resueltos no atribuibles inequívocamente a método con el consumo actual.
- `gap.method_identity_no_signatures` y ambigüedad de sobrecargas/homónimos.
- Relación directa `.aspx/.ascx`→clase code-behind pendiente cuando haya evidencia; otros GAP anteriores siguen documentados en informes de ronda y no se reabren automáticamente.
- **Punto de continuación**: confirmar aprobación humana de R3.4.1 → solamente entonces preparar R4 de cierre documental, con revisión de compatibilidad y registros finales → tras cierre explícito, iniciar V5.3 (incremental/cache). No introducir interpretación IA anticipadamente en R4.

## Forma de trabajo al retomar

El usuario maneja git personalmente. No ordenar a Claude `commit`/`push` ni editar roadmap/`PROJECT_STATE.json` sin autorización. Una responsabilidad por ronda; un prompt con nombre/ruta precisos; un único documento de resultado en `docs/V5/`; revisar resultado y muestra antes de redactar prompt posterior. Al emitir prompt, especificar ruta del prompt y ruta exacta de resultado esperado. Antes de nuevas suites largas, comprobar procesos/logs existentes, evitar espera pasiva infinita en monitores y no ejecutar suites concurrentes repetitivas. Para un nuevo chat, estos tres documentos y los últimos informes R3.4/R3.4.1 permiten recuperar el estado sin reconstruir la conversación.

---

# 37. Cierre formal de V5.2 (R4.3)

**Estado:** V5.2 cerrada formalmente (`V5_2_CLOSED_PENDING_GIT_APPROVAL`; pendiente solo el versionado Git). Informe: `docs/V5/V5_2_R4_3_CIERRE_FORMAL.md`. `PROJECT_STATE.json` actualizado (V5.0, V5.1 y V5.2 cerradas; `next = V5.3`).

**Secuencia de cierre:** R4 (revisión documental) → R4.1 (diagnóstico de pendientes, solo lectura) → R4.2 (correcciones pre-cierre) → R4.3 (cierre formal).

**Decisiones principales:**

- Baseline oficial de V5.2: `C:\Users\cgalianj\source\IST_40\Operacional`. La otra ruta IST no es equivalente (repositorios Git en ramas y commits distintos; 281 archivos comunes con contenido distinto).
- Política: evitar deuda técnica corregible dentro de la fase; lo que requiere nueva arquitectura o extracción se documenta como fase futura, no como defecto de V5.2.
- Prompts nuevos desde V5.3 en `prompts/V5/`; los históricos permanecen en `prompts/V5_0/`.
- Git por versión: commit de cierre + tag + push, semi-automático (el agente prepara y valida; el push exige aprobación humana explícita).

**Correcciones registradas (R4 contenía dos afirmaciones inexactas):** el origen de `atomic_write.py` **sí** estaba documentado (`docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`) y el cambio de `run_summary_presenter.py` **sí** estaba documentado (R3/R3.1) y probado. R4 no se modificó retroactivamente.

**Deuda corregida en R4.2:** pruebas directas de `_replace_with_retry` y aclaración del texto «archivos de código» frente a la tabla de archivos (solo i18n).

**Limitaciones futuras por contrato (no son defectos de V5.2):** dependencias a nivel de método; identidad de sobrecargas y firmas; atribución de ciertos `unresolved`; enlace `.aspx/.ascx` → code-behind; flujo → `archivo:línea`; clasificación más rica de tipos de proyecto; validación en otro repositorio; agrupación funcional; refactor de módulos grandes en ronda propia.

**Siguiente paso:** V5.3 — Incremental Engine & Cache (`READY_TO_START`, no iniciada), tras el versionado Git.
