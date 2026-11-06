# V5.1 R2 — Normalized Evidence Core — Implementation

## Objetivo

Implementar el **Normalized Evidence Core de V5.1** definido en:

`docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`

Esta ronda convierte el contrato aprobado en una implementación real, manteniendo compatibilidad con el comportamiento V4.3 y demostrando el resultado contra el sistema IST real.

La implementación debe seguir estrictamente:

> **Python descubre; IA interpreta.**

La lógica determinista de extracción, selección, identidad, validación, persistencia y compatibilidad debe permanecer en código Python. No introducir decisiones heurísticas de IA en el Evidence Core.

---

# 1. Documentación obligatoria antes de modificar código

Leer completamente:

* `CLAUDE.md`
* `AGENTS.md`
* `PROJECT_STATE.json`
* `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`
* `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`
* `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
* `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`
* `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`

Además, inspeccionar el código existente antes de decidir dónde implementar.

No asumir que la estructura actual del código coincide perfectamente con el contrato.

---

# 2. Regla principal de esta ronda

No comenzar implementando entidades directamente.

Primero realizar una fase breve de **medición y resolución de las decisiones abiertas de R1**.

Las decisiones deben quedar justificadas por evidencia del código real y/o mediciones reproducibles.

No resolverlas por intuición.

---

# 3. Resolver primero las decisiones abiertas de R1

Resolver explícitamente:

### 3.1 Solution identity

Determinar una identidad determinista y estable para `Solution`.

Debe ser compatible con el contrato V5 y reproducible.

---

### 3.2 Method / MethodReference

Determinar si:

* `Method` debe tener identidad canónica V5;
* `MethodReference` debe ser una entidad independiente;
* o alguna combinación de ambas.

Inspeccionar especialmente cómo el extractor actual representa métodos, overloads y referencias.

No introducir una identidad que el extractor actual no pueda producir de manera determinista.

---

### 3.3 Component discriminator

R1 detectó posibles duplicados en:

```text
(file, name, kind)
```

Determinar mediante medición real cómo diferenciar componentes duplicados.

El discriminador debe:

* ser determinista;
* ser reproducible;
* ser estable;
* no depender de orden global accidental;
* no generar colisiones.

---

### 3.4 CONN-

Determinar cómo representar `CONN-*`.

Debe quedar claro si:

* se preserva como referencia legacy;
* se convierte en entidad V5;
* o se representa mediante otra relación normalizada.

No inventar una entidad solamente para conservar una nomenclatura histórica.

---

### 3.5 unknown state

Determinar si V5.1 necesita físicamente un estado `unknown`.

No introducirlo si el comportamiento actual puede expresar correctamente la semántica sin él.

Si se decide reservarlo para una fase posterior, documentarlo como decisión de contrato/implementación.

---

# 4. Corregir dos puntos obligatorios antes de fijar el schema

## 4.1 CAL-* duplicate ordinal

La propuesta R1 de usar:

> posición dentro de `calls[]` del SourceArtifact

no es suficientemente estable ante inserciones no relacionadas.

Ejemplo:

```text
A
B
B
```

y posteriormente:

```text
X
A
B
B
```

Los B cambiarían de ordinal.

### Resolver obligatoriamente

El `duplicate_ordinal` debe calcularse **entre registros que compartan exactamente el mismo tuple base de identidad**.

El tuple base debe incluir todos los campos que formen parte de la identidad estructural de `Call`, incluyendo como mínimo los definidos por R1:

```text
source_artifact
containing_symbol
line
expression
resolved_target
```

Si el contrato final requiere otros campos, incluirlos.

El ordinal debe ser:

* determinista;
* estable ante inserciones de calls no relacionadas;
* reproducible;
* independiente del orden global de calls;
* validado con tests específicos.

No utilizar un contador global de `calls[]`.

---

# 5. Corregir cardinalidades

La representación de cardinalidades debe ser inequívoca.

En particular, revisar:

```text
FunctionalPath → DataOperation
DataOperation → DataObject
```

No utilizar expresiones ambiguas como:

```text
0..1 : 1
```

cuando la relación real sea de muchos paths hacia una operación.

Expresar claramente las cardinalidades y convertirlas en tests de contrato.

---

# 6. Implementar Normalized Evidence Core

Implementar las entidades definidas por R1:

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

Mantener la clasificación definida por R1:

```text
CORE_ENTITY
CORE_RELATION
ADAPTER_EXTENSION
DERIVED_PROJECTION
LEGACY_ONLY
```

No crear entidades adicionales sin justificar su necesidad arquitectónica.

---

# 7. Identidades

Preservar las identidades legacy cuando el contrato R1 lo permite:

```text
EP-
EVB-
FLOW-
DAO-
SP-
SQL-
PATH-
```

Crear nuevas identidades V5 para:

```text
PRJ-
CMP-
XDP-
CAL-
```

Mantener:

```text
PAR-
CALL-
UNRES-
```

como `legacy_ref`, no como identidad canónica V5.

`UnresolvedBoundary` debe tener identidad V5 determinista derivada de su evidencia estructural, manteniendo siempre su estado unresolved.

---

# 8. EvidenceReference

Implementar la unión definida en R1:

```text
entity
source
source_span
textual
```

con:

```text
legacy_ref
```

opcional.

Las referencias deben ser verificables.

Una referencia rota no debe convertirse silenciosamente en evidencia válida.

Debe producir un fallo explícito y detectable.

---

# 9. FunctionalFlow / FunctionalPath

Implementar las estructuras definidas en R1 utilizando las mediciones reales de R0.

Preservar:

* path IDs;
* terminales;
* estados;
* relation types;
* evidence references;
* unresolved semantics;
* traceability.

No implementar todavía segmentación avanzada de V5.6.

Los campos reservados para segmentación futura pueden existir solamente si R1 los definió y deben conservar sus valores neutrales.

---

# 10. Persistence

Implementar la separación:

```text
evidence/
index/
```

donde:

```text
evidence/
    = canonical V5 normalized evidence

index/
    = legacy compatibility projection
```

`index/` NO debe convertirse en la fuente canónica.

La persistencia debe ser:

* determinista;
* reproducible;
* validable;
* separable por entidad/proyección;
* independiente de proveedores de IA.

No introducir en esta ronda:

* cache V5.3;
* provider V5.5;
* templates V5.2;
* segmentation V5.6;
* approval V5.7;
* plugin runtime V5.8.

---

# 11. Compatibilidad V4.3

Una condición crítica de V5.1 es no romper la representación legacy existente.

Después de implementar el nuevo Evidence Core:

```text
Normalized Evidence
        ↓
Legacy Compatibility Projection
        ↓
index/
```

debe continuar generando la representación compatible esperada.

Siempre que sea técnicamente posible, comparar los índices generados contra:

`C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline`

La comparación debe distinguir:

* diferencias legítimas por la nueva capa de normalización;
* diferencias de proyección;
* diferencias reales de comportamiento.

No modificar V4.3 arbitrariamente para hacer coincidir resultados.

---

# 12. Tests obligatorios

Agregar tests para:

## Unit tests

Entidades, IDs, relaciones, serialización y validaciones.

## Contract tests

Validar todas las decisiones del contrato R1.

## Identity tests

Validar:

* unicidad;
* determinismo;
* reproducibilidad;
* estabilidad;
* ausencia de colisiones.

Especialmente:

```text
CAL- duplicate ordinal
CMP- discriminator
PRJ-
XDP-
UnresolvedBoundary
```

## Traceability tests

Toda evidencia normalizada debe poder rastrearse hasta su origen correspondiente.

## Unresolved tests

Verificar:

```text
unresolved ≠ confirmed
absence of evidence ≠ evidence of absence
```

No permitir promoción automática de unresolved a confirmed.

## Determinism tests

Mismo input:

```text
run A == run B
```

en las estructuras deterministas relevantes.

Incluir específicamente un test que demuestre que insertar una `Call` no relacionada antes de otras calls no cambia el ID de las calls existentes cuyo tuple base no cambió.

## Compatibility tests

Validar la proyección legacy.

## Real IST regression

Ejecutar contra:

`C:\Users\cgalianj\source\IST_40\Operacional`

utilizando como baseline:

`C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline`

---

# 13. Invariantes

Implementar y probar las 11 invariantes definidas por R1.

No sustituirlas por aproximaciones.

Si alguna no puede implementarse exactamente como fue definida, detenerse y reportar el conflicto en el documento de resultado.

No reinterpretar silenciosamente el contrato.

---

# 14. Runtime independence

Mantener la separación:

```text
runtime productivo
tooling de desarrollo
legacy congelado
```

El runtime productivo no debe depender de:

* docs;
* prompts;
* result files;
* governance;
* PROJECT_STATE;
* tests;
* archivos exclusivos de desarrollo.

---

# 15. No introducir V5.2/V5.5

No implementar todavía:

* generic AI provider;
* nuevos proveedores;
* template engine;
* profiles;
* AI context redesign;
* cache;
* incremental processing;
* segmentation;
* approval workflow;
* canonical knowledge;
* plugin runtime.

V5.1 debe terminar siendo un núcleo de evidencia, no una implementación anticipada del roadmap completo.

---

# 16. Validación final

Ejecutar como mínimo:

1. tests específicos de V5.1;
2. suite completa;
3. determinismo;
4. compatibility projection;
5. real IST regression.

La regresión real debe utilizar:

```text
TARGET:
C:\Users\cgalianj\source\IST_40\Operacional

BASELINE:
C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline
```

Registrar cantidades relevantes y diferencias.

No utilizar:

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

como target de nuevas mediciones.

Ese path es histórico/obsoleto para V5.

---

# 17. Manejo de fallos

Si una prueba falla:

1. analizar la causa;
2. corregir el problema;
3. volver a ejecutar la prueba correspondiente;
4. continuar únicamente cuando exista evidencia de la corrección.

Si aparece una contradicción del contrato R1:

* detener la implementación afectada;
* identificar exactamente la contradicción;
* no inventar una solución silenciosa.

Si el mismo problema falla tres veces de forma repetida:

> detener los intentos y realizar un diagnóstico de causa raíz.

No realizar retries ciegos.

---

# 18. Documentación de esta ronda

Crear solamente:

```text
docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md
```

Ese documento debe contener:

* estado final;
* decisiones abiertas resueltas;
* cambios realizados;
* arquitectura implementada;
* entidades implementadas;
* identidades;
* persistence;
* compatibility projection;
* tests agregados;
* resultados de tests;
* resultado de suite completa;
* resultado de regresión real IST;
* comparación contra R0;
* diferencias encontradas;
* riesgos o decisiones pendientes para R3.

No crear:

```text
FIX_NOTES.md
PATCH_RESULT.md
CORRECCION_R1.md
DIAGNOSTICO_EXTRA.md
TODO_FIX.md
```

ni ningún otro documento Markdown adicional.

No crear un prompt para R3 salvo que sea solicitado explícitamente.

---

# 19. Restricción de cambios

No modificar:

* roadmap;
* PROJECT_STATE;
* documentación histórica V4.3;
* contratos V5.2/V5.5;
* comportamiento no relacionado;
* archivos de documentación no requeridos.

Si un cambio adicional fuese imprescindible para V5.1, justificarlo en el resultado.

---

# 20. Git

No realizar:

* commit;
* push;
* branch management;
* merge.

El manejo de Git lo realizará manualmente el usuario.

---

# 21. Resultado esperado

Al finalizar, el resultado debe permitir responder claramente:

1. ¿El contrato V5.1 de R1 quedó implementado?
2. ¿Las 5 decisiones abiertas quedaron resueltas con evidencia?
3. ¿Las identidades son deterministas?
4. ¿`CAL-*` mantiene estabilidad frente a inserciones no relacionadas?
5. ¿Las cardinalidades quedaron inequívocamente implementadas?
6. ¿Las 11 invariantes están verificadas?
7. ¿La trazabilidad está preservada?
8. ¿`UnresolvedBoundary` mantiene correctamente la semántica unresolved?
9. ¿La proyección legacy continúa funcionando?
10. ¿La implementación funciona sobre el target real de IST?
11. ¿La suite completa continúa pasando?
12. ¿Existe alguna decisión que deba pasar a R3?

El documento final debe terminar con uno de estos estados:

```text
V5_1_R2_IMPLEMENTATION_READY
V5_1_R2_IMPLEMENTATION_CONFLICT
V5_1_R2_OPEN_DECISION
V5_1_R2_BLOCKED
```

La ronda debe considerarse `V5_1_R2_IMPLEMENTATION_READY` solamente si la implementación, tests y regresión real proporcionan evidencia suficiente de que el contrato V5.1 está implementado correctamente.
