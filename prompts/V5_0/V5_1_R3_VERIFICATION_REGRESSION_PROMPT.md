# V5.1 R3 — Verification & Regression

## Objetivo

Verificar de forma estricta que la implementación realizada en V5.1 R2.1 cumple el contrato de V5.1, funciona desde el producto real y no introduce dependencia arquitectónica incorrecta.

Esta ronda es exclusivamente de:

* verificación;
* regresión;
* medición;
* inspección arquitectónica;
* validación contra el contrato R1;
* validación de integración R2.1.

**NO realizar implementación, refactorización ni correcciones durante R3.**

Si se detecta un defecto, documentarlo con evidencia reproducible y clasificarlo como `BLOCKED`, `CONFLICT` u `OPEN_DECISION` según corresponda.

---

# 1. Documentos de referencia obligatorios

Leer antes de ejecutar cualquier prueba:

* `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`
* `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
* `docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md`
* `docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md`

Respetar además el roadmap V5 existente.

No modificar:

* roadmap;
* PROJECT_STATE;
* documentos históricos;
* contratos anteriores.

El resultado de esta ronda debe quedar exclusivamente en:

`docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md`

No crear documentos adicionales de diagnóstico, corrección, workaround, notas técnicas o similares.

---

# 2. Regla fundamental de R3

R3 debe comprobar el sistema **realmente ejecutable**.

No aceptar como evidencia suficiente:

* solamente tests unitarios;
* solamente fixtures;
* solamente scripts de `tools/`;
* solamente inspección estática;
* resultados históricos.

Debe existir evidencia del producto real ejecutando sobre:

`C:\Users\cgalianj\source\IST_40\Operacional`

---

# 3. Integración productiva

Verificar desde el producto real:

```text
python main.py full "<IST>" ...
```

y, cuando corresponda:

```text
python main.py analyze "<IST>" ...
```

Confirmar que el flujo productivo genera `evidence/` mediante el runtime real.

Debe demostrarse:

```text
main.py
  ↓
pipeline_stages
  ↓
NormalizedEvidenceBuilder
  ↓
write_evidence()
  ↓
evidence/
```

La ejecución productiva NO debe depender de:

* `tools/`;
* tests;
* documentación;
* prompts;
* PROJECT_STATE;
* resultados previamente generados;
* rutas de desarrollo;
* scripts auxiliares.

---

# 4. Inspección estricta de tools/

Aclaración importante:

La existencia de `tools/` dentro del mismo repositorio NO constituye por sí misma un defecto.

Debe verificarse la dirección de dependencias.

Arquitectura válida:

```text
tools/
   ↓
legacy_documenter/
```

Arquitectura inválida:

```text
legacy_documenter/
   ↓
tools/
```

o:

```text
tools/
   └── copia/implementación alternativa de legacy_documenter
```

Inspeccionar físicamente el contenido de `tools/` y determinar si contiene:

1. scripts de validación que importan el runtime real; o
2. una copia/duplicación del sistema productivo.

Verificar especialmente:

* imports;
* módulos duplicados;
* clases duplicadas;
* `NormalizedEvidenceBuilder` duplicado;
* lógica de persistencia duplicada;
* extractores/resolvers duplicados;
* otra implementación de Evidence Core;
* rutas que hagan que el producto utilice `tools/`.

El objetivo es comprobar que existe **una única fuente de verdad productiva**.

No modificar `tools/` durante R3.

---

# 5. Contrato de Normalized Evidence

Verificar contra R1:

## Identidades

Comprobar:

* `SRC-`
* `SOL-`
* `PRJ-`
* `CMP-`
* `EP-`
* `EVB-`
* `CAL-`
* `DAO-`
* `SP-`
* `SQL-`
* `PATH-`
* `FLOW-`
* `XDP-`
* `UNRES-`

y distinguir correctamente:

* identidad canónica V5;
* `legacy_ref`;
* identificadores que permanecen legacy.

Verificar especialmente:

* unicidad;
* determinismo;
* ausencia de colisiones no explicadas;
* estabilidad entre ejecuciones.

---

# 6. Call Identity

Verificar específicamente el problema detectado en R1.

La identidad de `CAL-` debe utilizar un ordinal estable dentro del tuple base:

```text
source_artifact
containing_symbol
line
expression
resolved_target
```

o una definición equivalente documentada en R1/R2.

No aceptar un ordinal dependiente de la posición global de `calls[]`.

Verificar:

* 230356 llamadas esperadas según baseline;
* grupos duplicados;
* ausencia de colisiones;
* determinismo entre ejecuciones independientes.

---

# 7. UnresolvedBoundary

Verificar que:

* mantiene identidad V5 estable;
* siempre representa un límite no resuelto;
* no se convierte silenciosamente en una resolución;
* su identidad es determinista;
* no depende de orden accidental de procesamiento.

Comparar contra las reglas de R1 y los resultados de R2.1.

---

# 8. EvidenceReference

Verificar el contrato:

```text
entity
source
source_span
textual
```

y el uso opcional de:

```text
legacy_ref
```

Comprobar que las referencias permiten trazabilidad suficiente desde evidencia normalizada hacia el origen.

---

# 9. Cardinalidades

Verificar explícitamente las cardinalidades establecidas en R1/R2:

```text
FunctionalPath → DataOperation
N paths : 1 operation
```

```text
FunctionalPath → SP
N paths : 1 object
```

```text
DataOperation → DataObject
N operations : 1 object
```

```text
DataOperation → DataParameter
1 operation : N parameters
```

Verificar que no exista una interpretación distinta entre:

* entidades;
* persistencia;
* builder;
* invariants;
* projection.

---

# 10. Instantiation

R2.1 introdujo una partición propia para `Instantiation`.

Verificar:

* que existe la partición;
* que contiene los registros esperados;
* que la información no se perdió respecto a R2;
* que no existe identidad canónica artificial;
* que no existe duplicación semántica innecesaria;
* que la representación es determinista.

Comparar cantidad y estructura con la evidencia producida anteriormente.

---

# 11. Persistencia

Verificar la persistencia R2.1:

* 23 particiones;
* JSON compacto;
* `EVIDENCE_MANIFEST.json`;
* schema version;
* counts;
* SHA-256 de particiones;
* lectura/deserialización;
* determinismo.

No aceptar únicamente que los archivos "existen".

Comprobar que:

```text
manifest
    ↓
partitions
    ↓
records
```

es coherente.

Verificar que los counts del manifest corresponden a los registros físicos.

---

# 12. Determinismo

Ejecutar dos generaciones independientes sobre el mismo target real.

Comparar:

* estructura;
* counts;
* IDs;
* orden;
* contenido;
* hashes;
* manifest;
* particiones.

El resultado debe ser byte-identical cuando el contrato así lo exige.

Documentar explícitamente cualquier diferencia.

No considerar automáticamente una diferencia como error: determinar si está justificada por datos no deterministas o metadata operacional.

---

# 13. Compatibility Projection

Verificar que `index/` continúa siendo una proyección de compatibilidad V4.3 y no la fuente canónica.

Comprobar:

* byte-equivalence donde corresponde;
* contenido equivalente donde el contrato permite metadata variable;
* ausencia de regresión funcional;
* documentación equivalente;
* `RUN_SUMMARY.json`.

Prestar especial atención a la diferencia conocida de:

```text
repository.json
duration_seconds
```

Determinar si continúa siendo exclusivamente metadata operacional.

---

# 14. Evidencia vs index

R2.1 dejó pendiente verificar completamente si `index/` puede reconstruirse desde `evidence/`.

En R3 NO implementar esta capacidad.

Determinar únicamente:

1. si el estado actual contradice el contrato V5.1;
2. si constituye una deuda aceptable para V5.1;
3. si bloquea R4;
4. si debe convertirse en requisito explícito de una versión posterior.

No convertir automáticamente esta verificación en implementación.

---

# 15. SourceArtifact SHA-256

R2.1 dejó:

```text
SourceArtifact.sha256 = None
```

en la ejecución productiva por el coste medido sobre 15138 archivos.

R3 debe verificar:

* comportamiento actual;
* impacto real;
* contrato R1;
* si la ausencia en producción contradice alguna invariante;
* si existe alternativa ya soportada por el diseño;
* si la situación es aceptable para V5.1.

No implementar hashing durante R3.

Si existe contradicción real entre contrato y producción, documentarla como defecto.

---

# 16. Best-effort Evidence Core

R2.1 estableció que un fallo del Evidence Core no debe hacer fallar la exportación V4.3.

Verificar cuidadosamente esta decisión.

Determinar:

* qué ocurre si Evidence Core falla;
* cómo se registra el fallo;
* si existe observabilidad suficiente;
* si el producto puede terminar aparentemente correcto mientras pierde evidencia V5;
* si esto contradice el objetivo arquitectónico de V5.

Este punto es crítico.

No asumir que "no romper V4.3" implica automáticamente que el comportamiento sea correcto para V5.

No modificar el comportamiento durante R3.

---

# 17. Runtime Independence

Inspeccionar el grafo de imports del runtime productivo.

Confirmar que `legacy_documenter` no importa ni depende de:

* `tools`;
* tests;
* docs;
* prompts;
* PROJECT_STATE;
* resultados;
* artefactos de desarrollo.

La dirección válida es:

```text
tools → runtime
tests → runtime
```

y no:

```text
runtime → tools
runtime → tests
runtime → docs
runtime → prompts
runtime → PROJECT_STATE
```

Verificar tanto:

* imports directos;
* imports indirectos relevantes;
* rutas de ejecución.

---

# 18. AI Independence

Verificar que Evidence Core no depende de:

* Ollama;
* OpenAI;
* Anthropic;
* SDKs de proveedores;
* clientes LLM;
* prompts;
* modelos específicos.

La interpretación AI pertenece a una capa posterior.

No implementar V5.5 durante esta ronda.

---

# 19. Technology Adapter Boundary

Verificar que Evidence Core recibe datos normalizados desde el límite de tecnología existente.

Confirmar que:

* VB/WebForms/Oracle no contaminan innecesariamente las entidades core;
* `ADAPTER_ID` no reapareció como propiedad estructural incorrecta del core;
* no existe lógica específica de una tecnología escondida en las entidades normalizadas.

No implementar nuevos adapters.

---

# 20. Escala real

Repetir validación sobre:

```text
C:\Users\cgalianj\source\IST_40\Operacional
```

Verificar al menos:

* 15138 source artifacts;
* 113 solutions;
* 259 projects;
* 9859 components;
* 4839 external dependencies;
* 5392 data objects;
* 230356 call identities;
* 162914 unresolved boundaries;
* 40278 instantiations;
* counts restantes según baseline R2.1.

Si alguna cifra cambia, explicar exactamente por qué.

No aceptar simplemente "los tests pasan".

---

# 21. Full regression suite

Ejecutar la suite completa.

Objetivo mínimo:

```text
0 failures
0 errors
```

Registrar:

* total de tests;
* skips;
* duración;
* cantidad de ejecuciones;
* estabilidad entre ejecuciones.

Repetir la suite cuando sea necesario para verificar determinismo/regresión.

---

# 22. Prohibiciones de R3

NO:

* modificar producción;
* modificar Evidence Core;
* modificar tests para hacerlos pasar;
* modificar tools;
* crear nuevos adapters;
* implementar templates;
* implementar profiles;
* implementar cache;
* implementar AI provider;
* implementar segmentation;
* implementar approval;
* implementar consumer/plugin contract;
* modificar roadmap;
* modificar PROJECT_STATE;
* crear documentación adicional fuera del resultado R3.

R3 es una fase de verificación.

---

# 23. Criterio de cierre

El resultado debe contener una matriz:

| Área                 | Verificación | Resultado    | Evidencia |
| -------------------- | ------------ | ------------ | --------- |
| Contract             | ...          | PASS/BLOCKED | ...       |
| IDs                  | ...          | PASS/BLOCKED | ...       |
| CAL                  | ...          | PASS/BLOCKED | ...       |
| UnresolvedBoundary   | ...          | PASS/BLOCKED | ...       |
| References           | ...          | PASS/BLOCKED | ...       |
| Cardinalities        | ...          | PASS/BLOCKED | ...       |
| Instantiation        | ...          | PASS/BLOCKED | ...       |
| Persistence          | ...          | PASS/BLOCKED | ...       |
| Determinism          | ...          | PASS/BLOCKED | ...       |
| Product integration  | ...          | PASS/BLOCKED | ...       |
| tools boundary       | ...          | PASS/BLOCKED | ...       |
| Runtime independence | ...          | PASS/BLOCKED | ...       |
| AI independence      | ...          | PASS/BLOCKED | ...       |
| Adapter boundary     | ...          | PASS/BLOCKED | ...       |
| Compatibility        | ...          | PASS/BLOCKED | ...       |
| Real IST             | ...          | PASS/BLOCKED | ...       |
| Full regression      | ...          | PASS/BLOCKED | ...       |

---

# 24. Estado final obligatorio

El documento debe terminar con exactamente uno de:

```text
V5_1_R3_READY_FOR_R4
```

```text
V5_1_R3_BLOCKED
```

```text
V5_1_R3_CONFLICT
```

```text
V5_1_R3_OPEN_DECISION
```

Si todo cumple, utilizar:

```text
V5_1_R3_READY_FOR_R4
```

No recomendar R4 si existe un defecto de V5.1 que contradiga el contrato o la arquitectura.

---

# 25. Resultado único

Crear únicamente:

`docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md`

Ese documento debe contener:

1. estado final;
2. alcance ejecutado;
3. comandos utilizados;
4. resultados;
5. métricas;
6. matriz de verificación;
7. evidencia de ejecución productiva;
8. evidencia de separación `tools → runtime`;
9. regresión V4.3;
10. regresión completa;
11. determinismo;
12. deuda R2.1 revisada;
13. defectos encontrados, si existen;
14. conclusión R3.

No crear ningún otro `.md`.

No realizar cambios de código.

No realizar commits ni push.

No modificar roadmap ni PROJECT_STATE.
