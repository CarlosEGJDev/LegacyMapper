# LegacyMapper V5.9 — R2 Targeted Corrections
## Cross-Repository SourceArtifact Identity

## 1. Objetivo

Corregir exactamente un defecto detectado en V5.9-R1:

```text
SourceArtifact IDs pueden colisionar entre repositorios distintos
cuando comparten la misma ruta relativa.
```

Evidencia R1:

```text
IST SourceArtifact count = 15138
Python SourceArtifact count = 540
shared SourceArtifact IDs = 1
shared id = SRC-b1fb90c6...
relative path = .gitignore
```

Todas las demás familias de identidad cross-tech quedaron sin colisiones.

R2 NO debe rediseñar V5.9.
R2 NO debe ampliar el adapter Python.
R2 NO debe modificar otras familias de ID salvo dependencia directa estrictamente necesaria.

## 2. Estado de partida

```text
V5_9_R1_READY_FOR_HUMAN_REVIEW
V5_9_NEXT_R2_TARGETED_CORRECTIONS
```

Piloto:

```text
second_technology = Python
second_adapter_id = python-generic
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
```

Base publicada:

`bcb8d57097ec769da75f5fc7207b9a6db295e374`

Cambios V5.9-R1 siguen locales.

R2:
- NO commit
- NO push
- NO tag

## 3. Defecto

Hoy puede ocurrir:

```text
repo A/.gitignore
repo B/.gitignore
→ mismo SRC id
```

El objetivo es:

```text
SourceArtifact identity must be unique across repository identities
while remaining deterministic.
```

## 4. Medir antes de diseñar

Inspeccionar y documentar:
- implementación exacta de `SRC-*`;
- inputs del hash;
- dónde se calcula;
- qué entidades derivan directa/indirectamente de `SourceArtifact`;
- qué artifacts contienen `SRC-*`;
- qué tests pinnean hashes;
- qué contratos V5.1 fijan identidad;
- cómo existe hoy repository identity;
- si ya hay `repository_id` o equivalente estable.

No asumir solución antes de medir.

## 5. Diseño mínimo

Preferencia:

```text
SourceArtifact identity =
hash(repository identity + normalized relative path)
```

o equivalente ya soportado por los contratos existentes.

NO usar:
- absolute local path;
- machine name;
- timestamp;
- random UUID;
- user-specific path;
- technology name como único namespace.

Mover el mismo repo a otra carpeta no debe cambiar IDs.

## 6. Repository identity

Reutilizar una identidad estable existente si existe.

Si no existe una usable:
- diseñar la mínima necesaria;
- documentar por qué;
- no crear una segunda noción incompatible.

## 7. Determinismo

Debe cumplirse:

```text
same repository logical identity
+ same relative path
→ same SRC id
```

y:

```text
different repository logical identity
+ same relative path
→ different SRC id
```

Además:

```text
same repo copied/moved to another absolute root
→ same SRC ids
```

## 8. Compatibilidad

Clasificar antes del cambio:

```text
IDENTITY_BREAKING
IDENTITY_COMPATIBLE
MIGRATION_REQUIRED
```

Si el contrato V5.1 permite evolución:
- documentarla;
- actualizar pins legítimos.

Si rompe contrato cerrado:
- detener;
- proponer compatibilidad/migración;
- no cambiar silenciosamente.

## 9. IDs derivados

Revisar explícitamente:
- Project;
- Component;
- EntryPoint;
- Call;
- FunctionalPath;
- FunctionalFlow;
- EvidenceReference;
- cache keys;
- consumer result identity;
- proposal/review/canonical provenance.

Clasificar cada familia:

```text
UNCHANGED
CHANGED_BECAUSE_DEPENDS_ON_SRC
UNAFFECTED_BY_DESIGN
```

No modificar familias no dependientes.

## 10. Tests mínimos de colisión

Crear:

```text
repo A/.gitignore
repo B/.gitignore
```

Esperado:

```text
SRC_A != SRC_B
```

Y:

```text
same logical repository
same .gitignore
different absolute root
→ same SRC id
```

## 11. Cross-tech real

Repetir inventario IST vs Python.

Esperado:

```text
shared SourceArtifact IDs = 0
```

Mantener también:

```text
shared Project IDs = 0
shared Component IDs = 0
shared EntryPoint IDs = 0
shared Call IDs = 0
shared FunctionalFlow IDs = 0
shared FunctionalPath IDs = 0
shared ExternalDependency IDs = 0
shared UnresolvedBoundary IDs = 0
```

## 12. Root relocation stability

Analizar el mismo corpus Python congelado desde dos roots físicos distintos.

Esperado:

```text
same SourceArtifact IDs
same normalized identities
same ordering
same bytes where applicable
```

## 13. IST compatibility

Hay dos escenarios.

### A. IDs IST no cambian

Exigir:

```text
47523 files
2828066791 bytes
added=0
removed=0
changed=0
```

### B. IDs IST cambian legítimamente

NO fingir equivalencia byte-identical.

Debe:
- explicar por qué;
- cuantificar artifacts afectados;
- demostrar equivalencia semántica;
- demostrar no pérdida de Evidence;
- demostrar mismas relaciones funcionales;
- NO rebaselinar sin aprobación humana.

Preferencia fuerte: preservar IDs IST si el contrato lo permite limpiamente.

## 14. Cache

Si `SRC-*` participa en cache/manifests/index/fingerprints, documentar:

```text
old behavior
new behavior
expected invalidation
```

No reusar cache incompatible.

No cambiar `ANALYZER_VERSION=3` salvo incompatibilidad de formato real.

Recalcular `ANALYZER_CODE_FINGERPRINT` si corresponde.

## 15. Evidence invariants

Reejecutar:
- refs resolubles;
- provenance válida;
- unresolved preservado;
- deterministic IDs;
- no dangling refs;
- schema 1.0.

## 16. Review / Canonical

Sobre artifacts controlados:
- proposal refs resuelven;
- baseline fingerprint correcto;
- snapshot válido;
- canonical audit chain válido.

Si cambian IDs:
- no stale false-negative;
- no refs huérfanas silenciosas.

## 17. ConsumerFacade

Reprobar:

```text
READ_EVIDENCE
READ_FLOW
READ_PARTIAL_FLOW
READ_AI_CONTEXT
READ_CANONICAL controlled
READ_REVIEW_HISTORY controlled
```

Consumer Contract 1.0 no cambia.

## 18. Python pilot

No ampliar coverage.

Solo reejecutar lo necesario para demostrar:
- IDs correctos;
- determinismo;
- cache coherente;
- no regresión del adapter.

No agregar argparse, richer type inference, DB, decorators, etc.

## 19. Runtime independence

El fix debe ser neutral.

No introducir imports del Python adapter en:
- core;
- evidence;
- cache;
- consumers;
- review;
- docs;
- provider layer.

## 20. Security

No incluir en identidad:
- absolute path;
- username;
- machine-specific data;
- secrets.

## 21. Tests nuevos R2

Al menos:
1. same relative path + different repository identity → different SRC;
2. same repository identity + different root → same SRC;
3. Python corpus relocation → same identities;
4. IST/Python SourceArtifact shared IDs = 0;
5. derived refs resolve;
6. cache behavior correcto;
7. review/canonical controlled chain válido;
8. consumers siguen válidos;
9. no path leakage;
10. determinism.

## 22. Directed tests

Ejecutar:
- V5.1 identity/evidence;
- V5.3 cache;
- V5.4 adapters;
- V5.7 review/canonical;
- V5.8 consumers;
- V5.9 adapter/cross-tech;
- fingerprint tests;
- architecture guards.

Registrar total/duración.

## 23. Full suite

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
3083 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

## 24. Python real rerun

Fuente:

```text
SECOND_TECH_SOURCE_ID =
SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60

tree_hash =
a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e
```

Demostrar:
- colisión resuelta;
- determinismo;
- fuente intacta;
- 0 provider real.

## 25. IST real regression

Ejecutar regresión real IST si el cambio afecta IDs o artifacts.

AI OFF.

Fuente esperada:

```text
15138 files
SHA256 =
77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
```

No ampliar exclusiones.

## 26. Deuda

Esperado:

RESOLVED:

```text
CROSS_REPOSITORY_SOURCE_ARTIFACT_ID_COLLISION
```

BLOCKING:

```text
[]
```

OBSERVATION:

```text
SELF_HOSTED_CIRCULAR_PILOT
```

FUTURE_PHASE:

```text
external independent second-tech validation
```

## 27. PROJECT_STATE

Si R2 queda limpia:

```text
current_version = V5.9
status = V5_9_IN_PROGRESS
latest_completed_round = V5.9-R2
latest_approved_round = V5.8-R3
round_status = V5_9_R2_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_9_closed = false
next = HUMAN_REVIEW
```

Mantener:

```text
second_technology = Python
second_adapter_id = python-generic
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
```

## 28. Entregables

Crear:

`docs/V5/V5_9_R2_TARGETED_CORRECTIONS.md`

Recomendado:

`docs/V5/V5_9_R2_TARGETED_CORRECTIONS.json`

Opcional:

`docs/V5/V5_9_R2_IDENTITY_IMPACT.json`

El Markdown debe cubrir:
1. defecto;
2. medición pre-fix;
3. contrato actual;
4. diseño;
5. repository identity;
6. compatibilidad;
7. impacto derivado;
8. implementación;
9. collision tests;
10. relocation;
11. cross-tech inventory;
12. cache;
13. Evidence invariants;
14. review/canonical;
15. consumers;
16. Python rerun;
17. IST regression;
18. fingerprint/version;
19. directed tests;
20. full suite;
21. runtime independence;
22. security;
23. debt;
24. PROJECT_STATE;
25. Git;
26. recomendación R3;
27. estado final.

## 29. Git R2

Solo consultas.

NO:
- commit
- push
- tag
- amend
- rebase
- reset destructivo
- clean

No crear R2.1/R2.2.

## 30. Estados finales

Éxito:

```text
V5_9_R2_READY_FOR_HUMAN_REVIEW
V5_9_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_9_R2_BLOCKED
```

## 31. Regla final

Resolver exactamente:

```text
cross-repository SourceArtifact identity collision
```

Secuencia:

```text
measure current identity
→ identify repository namespace
→ minimal deterministic fix
→ same-path/different-repo test
→ relocation stability
→ verify derived identities
→ rerun Python collision inventory
→ rerun IST as required
→ full suite
→ document
→ stop for human review
```

No ampliar adapter Python.
No modificar Consumer Contract.
No implementar Plugin Runtime.
No iniciar V5 Closure.
No commit/push/tag.
