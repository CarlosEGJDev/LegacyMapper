# V5.1 R3 — Revalidación posterior a R3.1

## Rol

Trabaja sobre el repositorio:

C:\dev\LegacyMapper

Esta ronda revalida V5.1 R3 después de las correcciones implementadas en:

docs/V5/V5_1_R3_1_CORRECCIONES_BLOQUEANTES.md

NO es una nueva ronda de implementación.
NO es R4.
NO debe ampliar alcance hacia V5.2–V5.9.

El objetivo es verificar si los bloqueos originales de R3 están realmente cerrados y si V5.1 puede quedar habilitada para R4.

---

# 1. Documentos obligatorios a revisar

Leer como mínimo:

- docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md
- docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md
- docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md
- docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md
- docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md
- docs/V5/V5_1_R3_1_CORRECCIONES_BLOQUEANTES.md

No asumir que R3.1 es correcto solo porque su documento lo afirma.

Verificar nuevamente contra:

- código real;
- tests;
- outputs físicos;
- corridas reales;
- invariantes del contrato R1.

---

# 2. Alcance

Esta ronda debe REVALIDAR.

NO debe realizar nuevas correcciones salvo ajustes mínimos indispensables para ejecutar la verificación.

Si se descubre un defecto nuevo o una corrección incompleta:

- documentarlo;
- marcar BLOCKED;
- NO convertir esta ronda en otra ronda de implementación.

---

# 3. Bloqueos originales de R3 a revalidar

## D-1 — XDP uniqueness

Verificar que:

- ExternalDependency tiene identidad canónica única;
- no existen canonical IDs duplicados;
- duplicados byte-idénticos también serían detectados;
- el discriminador determinista no depende de UUID, timestamp ni orden global incidental;
- la identidad se mantiene estable entre ejecuciones equivalentes.

Resultado esperado sobre IST real:

ExternalDependency records == unique XDP IDs

y:

XDP duplicate canonical IDs = 0

---

## D-2 — SourceArtifact.sha256 obligatorio

La decisión del Technical Lead es:

SourceArtifact.sha256 es obligatorio siempre.

Verificar que:

- production `full` calcula SHA-256;
- production `analyze` calcula SHA-256;
- ningún SourceArtifact válido contiene `None`;
- ningún SourceArtifact contiene hash vacío;
- todos tienen formato SHA-256 válido;
- el hash corresponde al contenido real;
- no depende de mtime ni metadata filesystem;
- fallo de lectura impide considerar válida la ejecución.

Resultado esperado:

SourceArtifacts without SHA-256 = 0

---

## D-3 — Evidence Core obligatorio para SUCCESS

La decisión del Technical Lead es:

si Evidence Core falla, la ejecución V5 debe quedar FAILURE.

Verificar nuevamente:

build FAIL
→ run FAILURE

validation FAIL
→ run FAILURE

persistence FAIL
→ run FAILURE

Comprobar:

- exit code != 0;
- estado FAILED;
- error observable;
- manifest válido ausente;
- no existe SUCCESS silencioso;
- artefactos legacy previos pueden mantenerse para diagnóstico;
- un manifest de una corrida anterior no puede hacer pasar la corrida fallida como válida.

---

# 4. Detector genérico I-1

Verificar la infraestructura genérica de identidades.

Regla:

mismo tipo de entidad + mismo canonical ID en más de un registro = colisión

aunque ambos registros sean byte-idénticos.

Comprobar al menos:

- duplicate id + contenido distinto ⇒ FAIL;
- duplicate id + contenido idéntico ⇒ FAIL;
- ids diferentes ⇒ PASS.

No limitar la prueba a XDP.

---

# 5. Invariantes R1

Revalidar I-1 a I-11 en la medida en que estén implementadas y sean verificables en V5.1.

Especial atención a:

- I-1 canonical identity uniqueness;
- I-2 PAR/CALL/UNRES solo como legacy_ref;
- I-3 EntryPoint → FunctionalFlow 0..1;
- I-4 trazabilidad;
- I-5 referencias rotas;
- I-6 proyecciones no inventan entidades/relaciones;
- I-7 no promotion sin basis;
- I-8 state estable entre proyecciones;
- I-9 legacy projection equivalence;
- I-10 determinismo;
- I-11 included ∩ omitted = ∅.

No declarar PASS para una invariante que no haya sido realmente validada.

---

# 6. D-4 — EvidenceReference

R3 dejó abierta esta decisión menor:

`EvidenceReference` existe como contrato y tests, pero no se emite materialmente en producción.

Esta ronda debe determinar si eso:

A. cumple suficientemente V5.1 porque la trazabilidad real ya está garantizada por claves foráneas y referencias legacy;

o

B. contradice el contrato R1 de forma suficiente como para bloquear R4.

No implementar una solución nueva.

Solo revisar contrato + código + evidencia real y emitir una conclusión técnica clara.

Verificar especialmente:

- referencias `source_artifact`;
- `source_ref`;
- provenance;
- referencias colgantes;
- comportamiento explícito ante referencias inválidas.

Si se considera deuda aceptable, justificar por qué no bloquea V5.1.

Si contradice una invariante obligatoria de R1, marcar BLOCKED.

---

# 7. D-5 — evidence/ como fuente canónica

R3 dejó documentado que:

- actualmente no existe un lector completo `evidence/ → entidades`;
- `index/` no se reconstruye directamente desde evidence persistido;
- `LegacyIndexProjector` puede proyectar desde NormalizedEvidence en memoria.

Verificar si esta condición sigue siendo compatible con el alcance V5.1.

No implementar el lector.

No mover trabajo de V5.3 o integración futura a esta ronda.

La conclusión debe indicar explícitamente:

- bloquea R4;
- o es deuda aceptable posterior.

---

# 8. Persistencia

Verificar la evidencia física actual.

Comprobar:

- carpeta `evidence/`;
- manifest;
- número real de particiones;
- filenames;
- counts;
- `partition_sha256`;
- `evidence_schema_version`;
- `physical_format`;
- relectura física;
- consistencia manifest ↔ partitions.

Usar el número REAL de particiones.

No repetir automáticamente “23” o “24” sin verificar.

La discrepancia documental anterior debe quedar aclarada.

---

# 9. Instantiation

Verificar:

- partición independiente;
- cantidad;
- ausencia de canonical id si así lo define el contrato;
- relación con instantiations embebidos en calls;
- determinismo;
- ausencia de regresión.

No rediseñar la entidad.

---

# 10. Identidades canónicas

Sobre las corridas reales, reportar para cada entidad con canonical identity:

- records;
- unique IDs;
- duplicate IDs.

Como mínimo:

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

Debe cumplirse:

records == unique canonical IDs

para todos los tipos canónicos.

---

# 11. Cardinalidades

Revalidar las cardinalidades relevantes del contrato:

- EntryPoint → FunctionalFlow = 0..1;
- FunctionalPath → DataOperation;
- FunctionalPath → DataObject/SP;
- DataOperation → DataObject;
- DataOperation → DataParameter;
- las relaciones necesarias de SourceArtifact / Component / Call.

Reportar referencias colgantes y cardinalidades inválidas.

---

# 12. Determinismo

Usar al menos dos ejecuciones productivas independientes y equivalentes.

Preferentemente reutilizar:

C:\PruebasLegacyMapper\Resultados\v5_1_r3_1_run_a

C:\PruebasLegacyMapper\Resultados\v5_1_r3_1_run_b

solo si se confirma que corresponden exactamente al código actual que se está revalidando.

Si el código cambió desde esas corridas, ejecutar dos nuevas.

Comparar:

- Evidence Core;
- manifest;
- particiones;
- canonical IDs;
- counts.

Los artefactos deterministas deben ser equivalentes byte a byte cuando corresponda.

Excluir únicamente metadata operacional explícitamente no canónica.

---

# 13. Compatibilidad V4.3

Verificar nuevamente:

- `index/`;
- `documentation/`;
- `RUN_SUMMARY.json`;
- stages legacy.

Reportar diferencias exactas.

No declarar “equivalente” sin comparar.

Diferencias exclusivamente operacionales como `duration_seconds` deben identificarse claramente.

---

# 14. Production integration

Verificar desde el producto real:

`python main.py full`

y:

`python main.py analyze`

cuando corresponda.

No basar la conclusión únicamente en:

- tools/;
- scripts de regresión;
- tests unitarios;
- fixtures.

La evidencia normalizada debe existir como parte del flujo productivo.

---

# 15. Runtime independence

Verificar nuevamente que runtime productivo no dependa de:

- tools/
- tests/
- docs/
- prompts/
- PROJECT_STATE
- rutas personales
- archivos de desarrollo

Permitido:

tools → runtime

Prohibido:

runtime → tools

---

# 16. AI independence

Verificar que Evidence Core no dependa de:

- Claude;
- OpenAI;
- Ollama;
- Anthropic SDK;
- providers;
- prompts;
- ai_context;
- ejecución LLM.

No implementar V5.5.

---

# 17. Technology Adapter boundary

Verificar que continúe existiendo la separación conceptual:

Legacy Source
    ↓
Technology Adapter
    ↓
Normalized Evidence Core

No implementar nuevos adapters.

No mover lógica específica de VB/WebForms/Oracle al núcleo genérico salvo extensiones permitidas por contrato.

---

# 18. Target real

Target obligatorio:

C:\Users\cgalianj\source\IST_40\Operacional

NO usar como target principal:

C:\inetpub\wwwroot\2010\IST\Operacional

Ese path es histórico.

---

# 19. Suite completa

Ejecutar:

python -m unittest discover -s tests

Reportar:

- total;
- passed;
- failures;
- errors;
- skipped.

Si existe cualquier failure/error final:

no declarar READY_FOR_R4.

---

# 20. No hacer

NO:

- modificar arquitectura;
- corregir nuevos defectos grandes;
- implementar V5.2;
- implementar Template Engine;
- implementar Output Profiles;
- implementar V5.3 cache;
- implementar V5.4 adapters;
- implementar V5.5 AI provider;
- implementar V5.6 segmentation;
- implementar V5.7 approval;
- implementar V5.8 plugin contract;
- implementar V5.9 pilot;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentos auxiliares;
- crear FIX_NOTES.md;
- crear PATCH_RESULT.md;
- crear DIAGNOSTICO_EXTRA.md;
- crear TODO_FIX.md;
- crear prompts adicionales.

---

# 21. Resultado documental

Crear EXACTAMENTE:

docs/V5/V5_1_R3_REVALIDATION.md

No crear otro documento de resultado.

Debe incluir como mínimo:

1. Estado final.
2. Evidencia revisada.
3. Estado D-1.
4. Estado D-2.
5. Estado D-3.
6. Resultado del detector I-1.
7. Revisión I-1..I-11.
8. Decisión técnica sobre D-4.
9. Decisión técnica sobre D-5.
10. Identidades canónicas.
11. Cardinalidades.
12. Persistencia.
13. Instantiation.
14. Determinismo.
15. Compatibilidad V4.3.
16. Production integration.
17. Runtime independence.
18. AI independence.
19. Technology Adapter boundary.
20. Resultados IST real.
21. Suite completa.
22. Deuda restante dentro de V5.1.
23. Evidencia para decidir R4.

Todas las cifras deben ser reproducibles.

---

# 22. Estados finales permitidos

El documento debe terminar con exactamente uno:

V5_1_R3_READY_FOR_R4

V5_1_R3_BLOCKED

V5_1_R3_CONFLICT

V5_1_R3_OPEN_DECISION

No declarar cierre de V5.1.

R4 sigue siendo obligatorio aunque R3 quede READY_FOR_R4.

---

# 23. Regla final

Al terminar:

- crear únicamente `docs/V5/V5_1_R3_REVALIDATION.md`;
- no crear el prompt de R4;
- no modificar roadmap;
- no modificar PROJECT_STATE;
- no avanzar automáticamente;
- esperar revisión externa.