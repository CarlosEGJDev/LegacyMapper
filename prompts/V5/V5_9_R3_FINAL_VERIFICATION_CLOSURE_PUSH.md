# LegacyMapper V5.9 — R3 Final Verification + Closure + Commit + Push
## Real Multi-Technology Pilot

## 1. Objetivo

Cerrar V5.9 después de R1 y R2 aprobadas.

Secuencia:

```text
freeze
→ final verification
→ cross-tech regression
→ IST regression
→ full suite
→ state/docs closure
→ explicit staging
→ one commit
→ push origin/main
→ remote verification
```

NO iniciar V5 Closure.

## 2. Estado de partida

Base publicada:

`bcb8d57097ec769da75f5fc7207b9a6db295e374`

Piloto:

```text
second_technology = Python
second_adapter_id = python-generic
pilot_kind = SELF_HOSTED_CIRCULAR
real_second_technology = true
second_source_is_legacy_mapper_itself = true
external_independence_claim = false
independent_external_product = false
```

Fuente congelada:

```text
SECOND_TECH_SOURCE_ID =
SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60

tree_hash =
a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e
```

R2 dejó corregida la colisión cross-repository de `SourceArtifact`.

## 3. Autorización Git

Esta R3 autoriza:

- verificación final;
- actualización documental/estado;
- staging explícito;
- UN commit;
- `git push origin main`;
- verificaciones remotas.

NO autoriza:

- tag;
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- segundo commit;
- iniciar V5 Closure.

Si falla push:

```text
V5_9_R3_PUSH_BLOCKED
```

y detenerse.

# FREEZE

## 4. Production freeze

No ampliar `python-generic`.
No cambiar resolución Python.
No agregar frameworks.
No hacer obligatorio `repository_id`.
No rediseñar IDs.
No cambiar Consumer/Plugin Contract.
No Plugin Runtime.
No provider real.
No iniciar V5 Closure.

R3 verifica y cierra.

## 5. Preflight Git

Ejecutar:

```text
git status --short
git status -sb
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git diff --check
git diff --stat
```

Confirmar:

```text
branch = main
HEAD = origin/main = bcb8d57097ec769da75f5fc7207b9a6db295e374
ahead = 0
behind = 0
```

No hacer staging todavía.

# PILOT NATURE

## 6. Circularity disclosure

Los artifacts finales deben conservar:

```text
pilot_kind = SELF_HOSTED_CIRCULAR
second_source_is_legacy_mapper_itself = true
real_second_technology = true
external_independence_claim = false
independent_external_product = false
```

No afirmar generalización independiente a productos externos arbitrarios.

# SECOND SOURCE

## 7. Frozen Python source

Revalidar:

```text
origin_commit =
e9e3d6063243073e65a93cbece97d6050184a0c6
```

y el tree hash anterior.

Confirmar:

- source intacta;
- target no ejecutado;
- sin network;
- sin instalar dependencias;
- snapshot sin código V5.9.

# ADAPTER

## 8. python-generic 1.0

Revalidar adapter/version.

Scope congelado:

- modules;
- classes;
- functions/methods;
- `__main__` entry points;
- imports/dependencies;
- conservative calls;
- filesystem/data ops;
- flows/paths;
- unresolved.

No agregar argparse/type inference rica/DB/decorators.

## 9. Static parsing guard

Permitido:

```text
ast.parse
static parsing
```

Prohibido:

```text
import target
exec
eval
runpy
subprocess target
pip install
network execution
```

# NORMALIZED CORE

## 10. Evidence schema

Revalidar:

```text
EVIDENCE_SCHEMA_VERSION = 1.0
```

Sin entidades core Python-specific.

## 11. Python counts

Baseline esperado:

```text
SourceArtifact = 540
Project = 4
Component = 887
EntryPoint = 73
Call = 16145
ExternalDependency = 1
DataOperation = 692
DataObject = 0
FunctionalFlow = 19
FunctionalPath = 4600
UnresolvedBoundary = 4191
EvidenceReference = 22514
```

No aceptar cambios funcionales no explicados.

## 12. Provenance / unresolved

Confirmar refs resolubles, deterministic identity, adapter metadata, I-4/I-5, no dangling refs y unresolved preservado.

# R2 SOURCE IDENTITY

## 13. Repository identity contract

Congelar:

```text
repository_id declared
→ SRC = sha256_id("SRC", repository_id, relative_posix_path)

repository_id undeclared
→ legacy V5.1 SRC formula unchanged
```

No hacerlo obligatorio.

## 14. Collision proof

Revalidar:

```text
same relative path + different repo ids → different SRC
same logical repo id + different physical root → same SRC
```

## 15. Cross-tech collision inventory

Esperado:

```text
shared SourceArtifact IDs = 0
shared Project IDs = 0
shared Component IDs = 0
shared EntryPoint IDs = 0
shared EventBinding IDs = 0
shared Call IDs = 0
shared DataAccess IDs = 0
shared ExternalDependency IDs = 0
shared FunctionalFlow IDs = 0
shared FunctionalPath IDs = 0
shared UnresolvedBoundary IDs = 0
total_shared_ids = 0
```

Repos sin `repository_id` siguen en namespace legacy V5.1: OBSERVATION, no reabrir defecto.

## 16. Relocation

Mismo corpus + mismo logical repository id + root físico distinto:

- mismos SRC ids;
- mismas particiones de evidence salvo outputs que imprimen root físico por diseño.

Documentar diferencias, no tratarlas como identity failure.

# DOCS / CONTEXT / CACHE

## 17. Human docs

Revalidar `human-functional` y `human-technical` sobre Python.

Mismo renderer/profile contract.
Terminology overlay data-only.
No template fork Python-specific.
IST legacy intacto.

## 18. AI context

Revalidar `READ_AI_CONTEXT`.

Esperado:

```text
REAL_PROVIDER_CALLS = 0
REAL_LLM_CALLS = 0
PROVIDER_RESOLUTION_ATTEMPTS = 0
```

## 19. Cache

Revalidar cold/warm y test incremental.

Warm esperado:

```text
243 hits
0 misses
same outputs
```

Incremental:

```text
1 changed file
242 hits
1 miss
1 file re-extracted
```

No reabrir scope `mode=full`; es OBSERVATION conocida.

# PROVIDER / SEGMENTATION

## 20. Fake provider

```text
Python Evidence
→ AI context
→ Fake provider
→ grounded proposal
```

Esperado:

```text
READY_FOR_REVIEW
canonical=false
0 real provider resolution
```

## 21. Segmentation

Revalidar:

```text
FLOW-0042743202
108 segments
partial=true
included union=parent
no overlap
omitted present
refs present
```

# REVIEW / CANONICAL

## 22. Controlled review

Sobre copia:

```text
prepare
→ APPROVE simulated
→ canonical
→ readback equal
→ audit chain valid
```

Original sin `knowledge/`.

## 23. Stale guard

```text
prepare
→ mutate evidence
→ APPROVE
→ PROPOSAL_STALE
→ no canonical
```

# CONSUMERS / PLUGINS

## 24. Consumer Contract 1.0

Revalidar:

```text
READ_EVIDENCE
READ_FLOW
READ_PARTIAL_FLOW
READ_AI_CONTEXT
RENDER_HUMAN_DOC
EXPORT_JSON
READ_CANONICAL controlled
READ_REVIEW_HISTORY controlled
```

## 25. Plugin Contract 1.0

Mismo Fake manifest:

```text
READ_EVIDENCE → OK
READ_FLOW → OK
undeclared capability → UNSUPPORTED_CAPABILITY
write capability → READ_ONLY_VIOLATION
```

No Plugin Runtime.

# ARCHITECTURE

## 26. Runtime independence

Confirmar core/evidence/cache/docs/review/consumers/plugins/provider/context no importan `python-generic`.

El adapter no importa CLI/provider/review/consumers/context.

Solo composition root puede importarlo.

# TESTS

## 27. Directed

Ejecutar V5.1–V5.9 relevantes, arquitectura, provider guard y maintainability.

Criterio:

```text
0 failures
0 errors
```

## 28. Full suite

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R2:

```text
3100 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

# REAL PILOT / IST

## 29. Python final proof

Confirmar:

```text
source intact
tree hash same
repository_id declared
cross-tech collisions = 0
determinism = true
provider calls = 0
```

## 30. Pilot matrix

Actualizar solo si hace falta.

Asegurar:

```text
FAIL = 0
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
```

## 31. IST regression

R2 ya verificó:

```text
47523 files
2828066791 bytes
added=0
removed=0
changed=0
source files=15138
source SHA256 =
77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5
```

R3 puede reutilizar SOLO si:

- producción congelada;
- analyzer behavior intacto;
- fingerprint actual coincide;
- source sigue igual.

Si no:

```text
RUN FULL IST AGAIN
```

## 32. Analyzer fingerprint

Esperado:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT =
f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b
```

Si producción congelada, debe permanecer igual.

# SECURITY / DEBT

## 33. Security

Confirmar:
- no target execution;
- no network;
- no provider real;
- no secrets;
- no absolute path en IDs;
- repository_id no expone path;
- no Plugin Runtime.

## 34. Debt

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
undeclared repositories share legacy V5.1 SRC namespace
PRJ-/CMP-/CAL-/XDP- remain path-derived
physical-root names appear in some presentation outputs
```

FUTURE_PHASE:

```text
external independent second-tech validation
richer Python type inference
argparse/console entry points
Python DB adapters
Plugin Runtime
third technology
```

# CLOSURE STATE

## 35. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.9
status = V5_9_CLOSED
latest_completed_round = V5.9-R3
latest_approved_round = V5.9-R2
round_status = CLOSED
human_review = APPROVED
v5_9_closed = true

second_technology = Python
second_adapter_id = python-generic
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false

next_version = V5 Closure
V5_CLOSURE_READY_TO_START = true
v5_closure_started = false
```

No iniciar V5 Closure.

## 36. Continuidad

Actualizar ambos roadmaps:

- V5.9 R1 completed;
- V5.9 R2 completed;
- V5.9 R3 completed;
- V5.9 CLOSED;
- pilot circular explícito;
- external validation futura;
- next = V5 Closure;
- V5 Closure not started.

Preservar historia del bloqueo inicial, autorización circular y R2.

# DOCUMENTATION

## 37. Final report

Crear:

`docs/V5/V5_9_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Recomendado:

`docs/V5/V5_9_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

Debe cubrir:
1. objetivo;
2. estado inicial;
3. aprobación R1/R2;
4. pilot nature;
5. frozen source;
6. adapter;
7. security/static parsing;
8. normalized Evidence;
9. provenance/unresolved;
10. repository identity;
11. collision proof;
12. relocation;
13. templates;
14. AI context;
15. cache;
16. Fake provider;
17. segmentation;
18. review/canonical;
19. stale guard;
20. consumers;
21. Plugin Contract;
22. runtime independence;
23. directed tests;
24. full suite;
25. Python proof;
26. pilot matrix;
27. IST regression;
28. analyzer fingerprint;
29. security;
30. debt;
31. PROJECT_STATE;
32. continuity;
33. Git preflight;
34. staging;
35. commit;
36. push;
37. remote verification;
38. V5 Closure readiness;
39. final state.

# GIT CLOSURE

## 38. Staging review

Antes:

```text
git status --short
git diff --stat
git diff --check
```

No `git add .` sin revisión.

Incluir explícitamente:
- `python-generic`;
- cambios neutrales R1;
- source identity R2;
- tests R1/R2;
- docs R1/R2/R3;
- matrix/inventories;
- prompts V5.9;
- PROJECT_STATE;
- roadmaps;
- recibo V5.8 si corresponde.

Excluir:
- output;
- `_local_v59r1`;
- caches;
- IST outputs;
- temp/logs;
- `__pycache__`;
- secrets.

## 39. Commit

Crear UN commit.

Mensaje recomendado:

```text
feat(v5.9): add multi-technology pilot and python adapter
```

No amend.
No segundo commit.

Registrar hash, parent, message y stat.

## 40. Push

```text
git push origin main
```

Sin force.

## 41. Remote verification

Ejecutar:

```text
git status -sb
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
git log -1 --oneline
```

Confirmar:

```text
HEAD == origin/main == remote main
ahead = 0
behind = 0
```

## 42. Tag

NO crear tag.

Registrar:

```text
TAG_NOT_CREATED_BY_INSTRUCTION
```

## 43. Working tree final

Ideal:

```text
clean
```

Si queda solo el recibo R3 autorreferencial post-push:
- documentarlo;
- no crear segundo commit.

# FINAL STATES

## 44. Éxito

```text
V5_9_CLOSED
V5_9_R3_PUSHED_TO_ORIGIN_MAIN
V5_CLOSURE_READY_TO_START
```

## 45. Bloqueo técnico

```text
V5_9_R3_BLOCKED
```

## 46. Bloqueo push

```text
V5_9_R3_PUSH_BLOCKED
```

## 47. Regla final

Cerrar V5.9 solo si:
- R1/R2 approved;
- second adapter valid;
- Evidence neutral;
- source identity fix verified;
- cross-tech collisions = 0;
- relocation stable;
- docs/cache/provider/segmentation/review/consumers valid;
- runtime independence;
- provider calls = 0;
- full suite green;
- IST regression green;
- fingerprint stable after R2;
- BLOCKING = [];
- state/docs closed;
- one commit;
- push successful;
- remote == HEAD;
- no tag;
- V5 Closure ready but not started.

Detenerse para revisión humana final.
