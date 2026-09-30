# V5.1 R3.1 — Correcciones bloqueantes posteriores a R3

## Rol

Trabaja sobre el repositorio LegacyMapper:

C:\dev\LegacyMapper

Esta ronda existe exclusivamente para corregir los bloqueos encontrados durante V5.1 R3.

NO es una nueva fase arquitectónica.
NO es V5.1 R4.
NO debe ampliar el alcance hacia V5.2–V5.9.

Debes implementar únicamente las correcciones necesarias para resolver los defectos confirmados por R3 y volver a ejecutar las verificaciones relevantes.

---

# 1. Documentos obligatorios a revisar

Antes de modificar código, leer como mínimo:

- docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md
- docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md
- docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md
- docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md
- docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md

El contrato de R1 continúa siendo autoridad para V5.1 salvo las decisiones explícitas tomadas posteriormente por el usuario.

No reinterpretar silenciosamente el contrato para acomodar la implementación actual.

---

# 2. Decisiones ya tomadas por el usuario

Estas decisiones están CERRADAS y no deben volver a solicitarse.

## D-2 — SourceArtifact.sha256

`SourceArtifact.sha256` es obligatorio.

Debe:

- calcularse siempre en producción;
- contener el SHA-256 real del SourceArtifact;
- no ser `None`;
- no quedar condicionado a flags de herramientas de validación;
- seguir siendo un dato primario medido conforme al contrato de R1.

Debe aplicarse también al flujo real de:

- `main.py full`
- `main.py analyze`

No convertirlo en un dato derivado posteriormente.

---

## D-3 — Fallo de Evidence Core

Evidence Core es obligatorio para que una ejecución V5 pueda considerarse exitosa.

Si falla la construcción, validación o persistencia del Evidence Core:

- la ejecución debe quedar en estado FAILURE;
- no debe reportarse SUCCESS;
- el error debe quedar observable;
- no debe ocultarse como warning best-effort;
- no debe presentarse una ejecución sin `evidence/` válido como una ejecución V5 correcta.

Esto NO significa eliminar los artefactos legacy que hayan podido generarse antes del fallo.

Significa únicamente que la ejecución completa no es válida como ejecución V5.

---

# 3. Defecto D-1 — XDP identity / collision detection

R3 encontró:

- ExternalDependency records: 4,839
- IDs distintos: 4,808
- 31 registros adicionales
- 5 IDs duplicados

R2/R2.1 habían informado 0 colisiones porque el detector aceptaba múltiples registros con el mismo ID cuando sus contenidos eran byte-identical.

Eso viola la invariante de identidad.

## Regla obligatoria

Para una entidad canónica V5:

> mismo tipo de entidad + mismo canonical ID en más de un registro = colisión

Esto aplica aunque los registros sean idénticos byte a byte.

El detector no debe considerar que duplicados idénticos dejan de ser colisiones.

---

# 4. Corregir ExternalDependency / XDP

Revisar la implementación real de `ExternalDependency` y su generación de identidad.

El contrato R1 define conceptualmente:

XDP- + SHA-256(
    dependency_kind
    + source
    + target
    + metadata mínima estable
)

La identidad debe:

- ser determinista;
- ser reproducible;
- distinguir entidades que son registros distintos dentro del modelo;
- no depender del orden global incidental;
- no utilizar valores volátiles;
- no generar IDs duplicados dentro de una misma ejecución;
- permanecer estable entre ejecuciones equivalentes.

No resolver el problema añadiendo UUIDs, timestamps o aleatoriedad.

Si existen varias dependencias semánticamente equivalentes pero representan ocurrencias distintas, utilizar un discriminador determinista basado en evidencia estable.

La solución debe ser consistente con la filosofía usada para CAL y otros IDs canónicos.

---

# 5. Corregir el detector de colisiones

Revisar todas las validaciones relacionadas con I-1.

Debe detectar:

- mismo canonical ID repetido dentro del mismo tipo de entidad;
- incluso si los objetos serializados son idénticos.

El detector debe reportar el número real de IDs duplicados y registros afectados.

Agregar pruebas específicas que demuestren que:

1. dos entidades diferentes con el mismo ID fallan;
2. dos entidades byte-identical con el mismo ID también fallan;
3. IDs distintos pasan;
4. el dataset real de IST termina con cero colisiones canónicas.

No limitar la corrección únicamente a XDP si el bug pertenece a una infraestructura genérica de validación de IDs.

---

# 6. SourceArtifact.sha256 obligatorio

Eliminar del camino productivo cualquier comportamiento que deje:

`sha256 = None`

para un SourceArtifact válido.

Revisar:

- builder;
- adapters;
- pipeline;
- persistence;
- manifest;
- tests;
- herramientas de regresión que consuman el modelo.

El SHA-256 debe calcularse sobre el archivo fuente correspondiente.

Mantener determinismo.

No utilizar timestamps, mtime o metadata del filesystem como sustituto del contenido.

---

# 7. Medición obligatoria del coste de SHA-256

R2.1 informó que calcular SHA-256 para aproximadamente 15,138 archivos tenía un coste relevante.

La decisión funcional ya está tomada: el hash continúa siendo obligatorio.

Sin embargo, esta ronda debe medir nuevamente el impacto real.

Registrar al menos:

- cantidad de SourceArtifacts;
- tiempo empleado en hashing;
- tiempo de construcción de Evidence Core;
- tiempo total relevante;
- tamaño de evidence resultante.

No optimizar de forma especulativa.

Si existe una optimización sencilla que preserve exactamente el contrato y el determinismo puede aplicarse.

No implementar todavía el cache incremental de V5.3.

---

# 8. Evidence Core obligatorio en producción

Revisar la integración realizada en:

`pipeline_stages.export_artifacts`

o su ubicación actual equivalente.

Eliminar el comportamiento por el cual:

Evidence Core FAIL
→ warning
→ V4.3 continúa
→ proceso termina SUCCESS

Debe pasar a:

Evidence Core FAIL
→ error observable
→ ejecución FAILURE

La implementación debe preservar en lo posible la información necesaria para diagnóstico.

No introducir una arquitectura paralela.

No agregar un nuevo sistema de estados innecesario.

---

# 9. Compatibilidad V4.3

La corrección de D-3 no autoriza modificar los artefactos históricos arbitrariamente.

Verificar que cuando Evidence Core funciona correctamente:

- `index/` mantiene compatibilidad V4.3;
- `documentation/` mantiene compatibilidad;
- los stages legacy permanecen funcionalmente equivalentes;
- los formatos legacy no son reescritos innecesariamente.

Las diferencias inevitables deben identificarse y justificarse.

No convertir `index/` en canonical evidence en esta ronda.

La reconstrucción completa de `index/` desde Evidence puede permanecer fuera de alcance si no es necesaria para resolver R3.

---

# 10. Instantiation

No rediseñar Instantiation.

R2.1 ya lo materializó como partición propia sin identidad canónica independiente.

Verificar únicamente que las modificaciones de esta ronda no rompan:

- persistencia;
- referencias;
- determinismo;
- cardinalidades existentes.

---

# 11. Technology Adapter boundary

No implementar V5.4.

Debe conservarse la frontera:

Legacy Source
    ↓
Technology Adapter
    ↓
Normalized Evidence Core

No introducir lógica VB/WebForms/Oracle específica dentro de las entidades genéricas del Evidence Core salvo metadata ya contemplada por el contrato.

---

# 12. AI independence

Evidence Core debe continuar sin dependencia de:

- Claude;
- OpenAI;
- Ollama;
- proveedores LLM;
- SDKs de IA;
- prompts;
- ai_context.

No implementar V5.5.

---

# 13. Runtime independence

El runtime productivo no debe depender de:

- tools/
- tests/
- docs/
- prompts/
- PROJECT_STATE
- archivos de desarrollo
- rutas personales de desarrollo

Está permitido:

tools → importar runtime

No está permitido:

runtime → importar tools

Verificar esta regla nuevamente después de las modificaciones.

---

# 14. Target real obligatorio

La regresión real debe ejecutarse contra:

C:\Users\cgalianj\source\IST_40\Operacional

NO utilizar como target principal:

C:\inetpub\wwwroot\2010\IST\Operacional

Ese path corresponde a la baseline histórica/deployment anterior.

Para esta ronda utilizar una carpeta nueva de resultados bajo:

C:\PruebasLegacyMapper\Resultados\

No reutilizar una carpeta anterior de forma que pueda contaminar las mediciones.

---

# 15. Validaciones obligatorias

## 15.1 Identidad

Comprobar como mínimo:

- SourceArtifact
- Solution
- Project
- Component
- EntryPoint
- EventBinding
- Call / CAL
- DataOperation
- DataObject
- FunctionalPath
- FunctionalFlow
- ExternalDependency / XDP
- UnresolvedBoundary

Reportar:

- registros;
- IDs distintos;
- colisiones.

Para entidades con identidad canónica:

records == unique canonical IDs

debe cumplirse.

---

## 15.2 XDP

Reportar explícitamente:

- total ExternalDependency;
- total unique XDP IDs;
- número de duplicate IDs;
- número de registros involucrados;
- resultado final del invariant check.

Resultado requerido:

XDP duplicate canonical IDs = 0

---

## 15.3 SourceArtifact SHA-256

Sobre el target real:

- todos los SourceArtifact deben tener SHA-256;
- cero valores `None`;
- cero valores vacíos;
- formato válido;
- hash reproducible.

Reportar:

SourceArtifacts total
SourceArtifacts with SHA-256
SourceArtifacts without SHA-256

Resultado requerido:

without SHA-256 = 0

---

## 15.4 Failure semantics

Crear una prueba controlada que provoque fallo en Evidence Core sin modificar permanentemente el producto.

Verificar que:

- el fallo se propaga;
- la ejecución no termina SUCCESS;
- el exit/status sea de fallo según la arquitectura existente;
- el error sea observable.

Después restaurar el comportamiento normal.

No dejar hooks artificiales ni sabotajes en producción.

---

## 15.5 Persistence

Verificar:

- `evidence/`;
- manifest;
- particiones;
- counts;
- SHA-256 de particiones;
- lectura posterior;
- consistencia entre manifest y archivos físicos.

Mantener el formato físico decidido en R2.1 salvo que exista un defecto directamente relacionado con esta ronda.

No reabrir JSON vs JSONL.

---

## 15.6 Determinismo

Realizar al menos dos ejecuciones independientes equivalentes sobre IST.

Comparar Evidence Core de ambas.

Los artefactos deterministas deben ser equivalentes byte a byte cuando corresponda.

No considerar tiempos de ejecución u observabilidad volátil como evidencia canónica.

---

## 15.7 V4.3 regression

Comparar los outputs legacy relevantes.

Reportar diferencias reales.

No declarar equivalencia sin medirla.

---

## 15.8 Suite completa

Ejecutar la suite completa.

Reportar:

- total tests;
- passed;
- failures;
- errors;
- skipped.

No ocultar skips.

---

# 16. Tests nuevos obligatorios

Agregar o ajustar tests únicamente cuando sean necesarios para estas correcciones.

Debe existir cobertura para:

- duplicate canonical IDs con contenido diferente;
- duplicate canonical IDs con contenido idéntico;
- XDP deterministic identity;
- XDP no collisions;
- mandatory SourceArtifact.sha256;
- Evidence Core failure propagates to execution FAILURE;
- successful Evidence Core preserves normal successful execution;
- determinism de las nuevas reglas.

No sustituir la regresión real por fixtures sintéticos.

Los fixtures complementan, no reemplazan, IST real.

---

# 17. No hacer

NO:

- implementar V5.2;
- implementar Template Engine;
- implementar Output Profiles completos;
- implementar cache incremental V5.3;
- implementar nuevos Technology Adapters V5.4;
- implementar Generic AI Provider V5.5;
- implementar Rich Flow Segmentation V5.6;
- implementar Approval/Canonical Knowledge V5.7;
- implementar Consumer Plugin Contract V5.8;
- implementar Multi-Technology Pilot V5.9;
- hacer refactorizaciones generales;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentación auxiliar;
- crear archivos FIX_NOTES.md;
- crear PATCH_RESULT.md;
- crear DIAGNOSTICO_EXTRA.md;
- crear TODO_FIX.md;
- crear prompts adicionales.

---

# 18. Resultado documental

Crear EXACTAMENTE un documento de resultado:

docs/V5/V5_1_R3_1_CORRECCIONES_BLOQUEANTES.md

No crear documentos adicionales para esta ronda.

El documento debe incluir como mínimo:

1. Estado final.
2. Archivos de producción modificados.
3. Archivos de tests modificados/agregados.
4. Corrección de XDP.
5. Corrección del detector de colisiones.
6. Implementación de SourceArtifact.sha256 obligatorio.
7. Medición real del coste SHA-256.
8. Nueva semántica de fallo de Evidence Core.
9. Resultado del test controlado de FAILURE.
10. Persistencia Evidence.
11. Determinismo.
12. Compatibilidad V4.3.
13. Runtime independence.
14. AI independence.
15. Technology Adapter boundary.
16. Resultados reales sobre IST.
17. Resultado de suite completa.
18. Deuda técnica restante dentro del alcance V5.1.
19. Evidencia suficiente para decidir si R3 puede pasar a READY_FOR_R4.

Toda afirmación cuantitativa debe estar respaldada por ejecución reproducible.

---

# 19. Estados finales permitidos

El documento debe terminar con exactamente uno de estos estados:

V5_1_R3_1_READY_FOR_R3_REVALIDATION

V5_1_R3_1_BLOCKED

V5_1_R3_1_CONFLICT

V5_1_R3_1_OPEN_DECISION

No declarar:

V5_1_R3_READY_FOR_R4

en esta ronda.

Esta ronda corrige los bloqueos.

La autorización para pasar a R4 ocurrirá únicamente después de revisar externamente este resultado y, si corresponde, realizar/revalidar R3.

---

# 20. Regla de cierre

Al terminar:

- generar únicamente el documento solicitado;
- no crear el siguiente prompt;
- no avanzar automáticamente a otra ronda;
- esperar revisión externa.