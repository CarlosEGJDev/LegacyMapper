# V5.1 R1 — Contrato y Diseño del Normalized Evidence Core

Ejecuta la ronda **V5.1 R1** de LegacyMapper.

## Contexto

R0 fue cerrada correctamente:

* Suite: 2169 tests, 0 failures, 0 errors, 132 skips.
* Target real:
  `C:\Users\cgalianj\source\IST_40\Operacional`
* Full determinista exitoso.
* 933 archivos de salida.
* ~1.70 GB de salida.
* 15.138 archivos escaneados.
* 12.662 entry points.
* 12.662 event bindings.
* 12.642 functional flows.
* 170.020 functional paths.
* 20.082 data access.
* 74.633 data parameters.
* 5.389 stored procedures.
* 230.356 calls.
* 335.698 functional dependencies.
* 162.914 unresolved boundaries.
* 0 errores estructurados.
* No hubo `CONTRACT_CONFLICT`.

Resultado R0:
`docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`

Output R0:
`C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline`

## Objetivo de R1

Diseñar y cerrar documentalmente el contrato técnico de **V5.1 — Normalized Evidence Core**, preparado para implementación posterior.

**NO implementar V5.1 en esta ronda.**

La ronda debe resolver qué debe existir, qué debe preservarse, qué debe normalizarse, qué relaciones son canónicas y qué queda como extensión/legacy/proyección.

---

## Lectura obligatoria

Antes de trabajar, leer:

```text
CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md
docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md
docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md
docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md
```

También revisar el código actual necesario para determinar dónde están actualmente representados los conceptos que V5.1 deberá normalizar.

No asumir que el diseño conceptual de V5.0 ya está implementado.

---

# 1. Principio central

V5.1 debe establecer un modelo de evidencia normalizada independiente de la representación específica de LegacyMapper V4.x.

Cadena objetivo:

```text
Legacy Source
    ↓
Technology Adapter
    ↓
Normalized Evidence Core
    ↓
Evidence Persistence
    ↓
Projections
```

V5.1 NO debe implementar todavía:

* generic AI provider;
* nuevos proveedores AI;
* templates;
* profiles;
* incremental cache;
* segmentation avanzada;
* approval/canonical knowledge;
* plugin runtime;
* multi-technology pilot completo.

Esos temas pertenecen a fases posteriores según el roadmap V5.

---

# 2. Entidades mínimas a resolver

Analiza y define formalmente estas entidades:

```text
SourceArtifact
Solution
Project
Component
Method
MethodReference
EntryPoint
EventBinding
Call
Instantiation
DataOperation
DataObject
DataParameter
ExternalDependency
FunctionalPath
FunctionalFlow
FlowGraph
UnresolvedBoundary
EvidenceReference
ScanSummary
```

Para cada una debes determinar:

1. Propósito.
2. Identidad.
3. Campos mínimos.
4. Campos opcionales.
5. Relaciones.
6. Cardinalidad.
7. Origen de los datos.
8. Si pertenece al core o es extensión.
9. Si debe preservar información legacy.
10. Qué parte es evidencia primaria y qué parte es dato derivado.

No inventes campos solamente porque parezcan útiles.

Cada campo debe justificarse mediante:

* V5.0;
* evidencia de R0;
* código actual;
* o una necesidad estructural indispensable para el contrato.

Si algo no está suficientemente respaldado, marcarlo explícitamente como decisión pendiente en lugar de inventarlo.

---

# 3. Clasificación obligatoria

Cada concepto/campo relevante debe clasificarse como una de estas categorías:

```text
CORE_ENTITY
CORE_RELATION
ADAPTER_EXTENSION
DERIVED_PROJECTION
LEGACY_ONLY
```

El objetivo es evitar que detalles específicos de V4.x contaminen el modelo normalizado.

---

# 4. Identidad

Aplicar estrictamente el contrato V5.0 ya validado en R0.

Identidades legacy preservables:

```text
EP-
EVB-
FLOW-
DAO-
SP-
SQL-
PATH-
```

No convertir estos IDs en simples textos arbitrarios: documentar qué entidad representan y bajo qué condición pueden preservarse.

Los siguientes NO son identity keys canónicas:

```text
PAR-
CALL-
UNRES-
```

Deben permanecer como:

```text
legacy_ref
```

cuando corresponda.

Definir además los nuevos identificadores V5:

```text
PRJ- → Project
CMP- → Component
XDP- → ExternalDependency
CAL- → Call
```

Y resolver formalmente la identidad de:

```text
UnresolvedBoundary
```

sin reutilizar `UNRES-` como identidad canónica.

---

# 5. Relaciones críticas

Definir formalmente, como mínimo:

```text
EntryPoint → FunctionalFlow
EntryPoint → EventBinding
FunctionalFlow → FunctionalPath
FunctionalPath → Call
FunctionalPath → DataOperation
FunctionalPath → UnresolvedBoundary
Project → Component
Component → Method
Method → MethodReference
Project → ExternalDependency
DataOperation → DataObject
DataOperation → DataParameter
```

Especial atención:

```text
EntryPoint → FunctionalFlow = 1 : 0..1
```

No asumir 1:1.

Determinar también qué relaciones son:

* directas;
* derivadas;
* opcionales;
* preservadas desde legacy;
* reconstruidas por el adapter.

---

# 6. EvidenceReference

Diseñar el contrato de `EvidenceReference`.

Debe permitir como mínimo:

```text
entity
source
source_span
textual
```

y opcionalmente:

```text
legacy_ref
```

Debe quedar claro:

* qué identifica;
* qué evidencia respalda;
* cómo se relaciona con una entidad;
* qué ocurre cuando no existe una referencia de fuente precisa;
* cómo evitar que una proyección pierda trazabilidad.

No permitir que `EvidenceReference` se convierta en un mecanismo para inventar relaciones.

---

# 7. FunctionalFlow / FunctionalPath

Usar los datos reales de R0 para definir el contrato.

Considerar explícitamente:

* flow;
* path;
* depth;
* terminal;
* unresolved boundary;
* data access;
* stored procedure;
* SQL;
* dependencies;
* calls;
* evidence refs.

No introducir todavía segmentación avanzada.

Sin embargo, el diseño debe ser compatible con el futuro contrato de V5.6:

```text
parent_flow_id
segment_id
partial
included_paths
omitted_paths
evidence_refs
segment_reason
```

No implementar esos mecanismos si no pertenecen a V5.1.

---

# 8. UnresolvedBoundary

Definirlo como concepto de primera clase del modelo.

Debe distinguir claramente:

```text
confirmed
unresolved
unknown
```

o los estados que realmente justifique el código existente.

No convertir un unresolved en confirmed solamente porque exista un texto o una referencia parcial.

El contrato debe preservar el hecho de que:

> ausencia de evidencia ≠ evidencia de ausencia.

---

# 9. Adapter boundary

V5.1 debe dejar claramente definido qué corresponde al futuro Technology Adapter.

El core normalizado no debe depender directamente de:

* VB.NET;
* WebForms;
* .vbproj;
* archivos específicos;
* reglas particulares de un parser;
* estructuras internas de V4.x.

Si existe información específica de una tecnología que no puede entrar al core:

```text
ADAPTER_EXTENSION
```

Debe definirse cómo se conserva sin contaminar el modelo canónico.

---

# 10. Legacy compatibility

Determinar cómo se conserva compatibilidad con V4.x sin convertir los índices legacy en el modelo canónico.

Conceptualmente:

```text
Normalized Evidence
        ↓
Legacy Compatibility Projection
        ↓
V4-compatible index representation
```

La dirección NO debe invertirse.

`index/` no debe convertirse en la fuente de verdad de V5.

---

# 11. Persistence contract

Definir el contrato lógico de persistencia de:

```text
evidence/
index/
```

sin necesidad de implementar todavía el almacenamiento físico definitivo.

Debe quedar claro:

* qué es canónico;
* qué es compatibilidad;
* qué puede regenerarse;
* qué no debe perderse;
* qué identificadores deben permanecer estables;
* qué relaciones deben ser reconstruibles.

---

# 12. Invariantes

Definir un conjunto concreto de invariantes verificables por tests en R2.

Como mínimo considerar:

### Identidad

```text
EP/EVB/FLOW/DAO/SP/SQL/PATH
→ identidad preservable
```

```text
PAR/CALL/UNRES
→ legacy_ref
```

### Trazabilidad

Toda entidad normalizada relevante debe poder conducir hasta evidencia verificable.

### No invención

Una proyección no puede crear una relación que no exista en evidence.

### Unresolved

Un unresolved no puede convertirse automáticamente en confirmado.

### Compatibilidad

La proyección legacy no puede convertirse en la fuente canónica.

### Determinismo

La misma evidencia de entrada debe producir la misma evidencia normalizada.

---

# 13. Mapping V4.3 → V5.1

Crear una tabla conceptual que indique para cada concepto importante:

```text
V4.3 source/index
→ V5.1 normalized entity
→ classification
→ identity
→ transformation
```

Usar únicamente conceptos realmente existentes.

No crear mappings especulativos.

---

# 14. Impact analysis

Identificar qué componentes actuales deberán tocarse durante R2.

Clasificar cada componente:

```text
MODIFY
REUSE
ADAPTER
DEPRECATE_LATER
OUT_OF_SCOPE
```

No modificar código en R1.

---

# 15. Test contract

Definir qué debe probar R2.

Separar:

```text
unit tests
contract tests
real IST regression
legacy compatibility regression
determinism checks
identity checks
traceability checks
```

Los tests deben poder demostrar que V5.1 funciona sobre los datos reales encontrados en R0.

No utilizar únicamente fixtures pequeños.

---

# 16. V5.2/V5.5 compatibility

El contrato de V5.1 debe ser compatible con la arquitectura V5 posterior.

En particular:

```text
Normalized Evidence
        ↓
AI factual interpretation
        ↓
Audience transformation
        ↓
Profile
        ↓
Template
        ↓
Renderer
```

y:

```text
Normalized Evidence
        ↓
Generic AI Provider
```

V5.1 no debe acoplarse al proveedor AI ni a templates.

---

# 17. Criterio de cierre

R1 solo puede cerrarse si queda definido:

* modelo de entidades;
* identidad;
* relaciones;
* EvidenceReference;
* unresolved;
* adapter boundary;
* legacy compatibility;
* persistence boundary;
* invariantes;
* mapping V4.3 → V5.1;
* impacto de implementación;
* contrato de tests R2;
* compatibilidad con V5.2 y V5.5.

Si existe una contradicción real con V5.0:

```text
V5_1_R1_CONTRACT_CONFLICT
```

y detenerse sin modificar arquitectura por cuenta propia.

Si faltan datos para decidir algo:

```text
V5_1_R1_OPEN_DECISION
```

y documentarlo explícitamente.

No resolver silenciosamente una decisión arquitectónica.

---

# Restricciones

NO:

* implementar V5.1;
* modificar producción;
* modificar tests;
* modificar `PROJECT_STATE.json`;
* ejecutar IA real;
* cambiar V5.0;
* modificar el roadmap;
* introducir templates;
* introducir providers;
* introducir cache;
* introducir segmentation implementation;
* crear código provisional;
* crear fixtures solamente para justificar una decisión;
* crear documentación no solicitada.

## Documentación

Crear únicamente:

```text
docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md
```

No crear:

```text
FIX_NOTES.md
PATCH_RESULT.md
DIAGNOSTICO_EXTRA.md
TODO_FIX.md
CORRECCION_R1.md
```

No crear ningún otro `.md`.

No crear prompt siguiente.

---

# Estado final permitido

Si todo queda definido:

```text
V5_1_R1_CONTRACT_READY
```

Si existe una contradicción:

```text
V5_1_R1_CONTRACT_CONFLICT
```

Si faltan decisiones esenciales:

```text
V5_1_R1_OPEN_DECISION
```

Si el repositorio impide realizar el análisis:

```text
V5_1_R1_BLOCKED
```

Al finalizar, detenerse y esperar revisión humana.

No comenzar R2.
