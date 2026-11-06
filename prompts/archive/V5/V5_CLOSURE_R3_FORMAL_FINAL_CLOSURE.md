# LegacyMapper V5 Closure — R3 Formal Final Closure
## Final Verification, Documentation Refresh, Commit & Push

## 1. Objetivo

Cerrar formalmente V5 después de:

```text
V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW
V5_CLOSURE_NEXT_R3_FINAL_CLOSURE
```

Closure R1 quedó aprobada. NO existe Closure R2.

Secuencia:

```text
freeze production
→ verify R1 evidence still valid
→ refresh user-facing orientation docs
→ finalize PROJECT_STATE + roadmaps
→ create final closure receipts
→ explicit staging
→ one commit
→ push origin/main
→ verify remote
→ mark V5_CLOSED
```

NO iniciar V6.

## 2. Estado de partida

Base publicada:

`957ef09538a7afea649d1f2ac195a3d3819a660f`

Esperado:

```text
branch = main
HEAD = origin/main = 957ef09538a7afea649d1f2ac195a3d3819a660f
ahead = 0
behind = 0

current_version = V5 Closure
status = V5_CLOSURE_IN_PROGRESS
latest_completed_round = V5-Closure-R1
latest_approved_round = V5.9-R3
round_status = V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_closed = false
v5_closure_started = true
```

Preservar recibo post-push V5.9 y artifacts Closure R1.

## 3. Autoridad Git

Esta R3 autoriza:

- staging explícito;
- UN commit;
- `git push origin main`;
- verificación remota.

NO:
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- segundo commit.

### Tag

NO crear tag automáticamente.

Inspeccionar:

```text
git tag --list
git log --decorate --oneline --all
```

Reportar una recomendación, pero dejar:

```text
TAG_NOT_CREATED_PENDING_HUMAN_DECISION
```

La creación del tag requiere autorización humana separada.

# FREEZE

## 4. Production freeze

R3 NO es desarrollo.

NO modificar comportamiento de:
- `legacy_documenter/`;
- adapters;
- evidence;
- cache;
- provider;
- segmentation;
- review/canonical;
- consumers/plugins;
- analyzer version/fingerprint;
- schemas.

Si aparece defecto bloqueante real:

```text
V5_CLOSURE_R3_BLOCKED
```

Detenerse; no corregir silenciosamente.

# PREFLIGHT

## 5. Git preflight

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

Debe cumplirse:

```text
main
HEAD == origin/main == 957ef09538a7afea649d1f2ac195a3d3819a660f
ahead = 0
behind = 0
```

Si no, detenerse antes de staging.

# REVALIDACIÓN R1

## 6. Baseline artifacts

Leer/verificar:

```text
docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md
docs/V5/V5_FINAL_BASELINE.json
docs/V5/V5_CLOSURE_R1_RESULT.json
docs/V5/V5_FINAL_CONTRACT_MATRIX.json
docs/V5/V5_FINAL_INVARIANT_MATRIX.json
docs/V5/V5_FINAL_DEBT_LEDGER.json
docs/V5/V5_FINAL_MAINTAINABILITY_INVENTORY.json
docs/V5/V5_OPERATIONS_GUIDE.md
```

Confirmar consistencia interna.

## 7. Analyzer freeze

Esperado:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT =
f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b
```

Si cambia por producción:

```text
V5_CLOSURE_R3_BLOCKED
```

## 8. Production tree proof

Comparar producción contra `957ef095...`.

Esperado:

```text
no production behavior changes after Closure R1
```

Docs/state/prompts pueden cambiar.

# TESTS

## 9. Directed closure verification

Ejecutar suite dirigida de:
- architecture guards;
- Evidence invariants;
- both adapters;
- provider guard;
- segmentation;
- review/canonical;
- consumer/plugin;
- V5.9 identity collision;
- runtime independence;
- security guards.

Criterio:

```text
0 failures
0 errors
```

## 10. Full suite

```text
python -X utf8 -m unittest discover -s tests
```

Baseline R1:

```text
3100 tests
0 failures
0 errors
132 skips
```

Criterio: 0 failures, 0 errors.

# IST / PYTHON BASELINES

## 11. IST closure proof

Esperado:

```text
source files = 15138
source SHA256 =
77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5

output files = 47523
output bytes = 2828066791

added = 0
removed = 0
changed = 0
```

Reutilizar R1/V5.9 solo si:
- producción frozen;
- fingerprint igual;
- source hash igual;
- outputs verificables.

Si alguna condición falla: `RUN FULL IST AGAIN`.

## 12. Python pilot proof

Esperado:

```text
SECOND_TECH_SOURCE_ID =
SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60

tree_hash =
a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e

adapter = python-generic 1.0
cross-tech total_shared_ids = 0
```

Mantener:

```text
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
independent_external_product = false
```

# DOCUMENTATION REFRESH

## 13. Resolver OB-14

Closure R1 detectó desactualización en:

```text
README.md
docs/PROJECT_RECOVERY.md
CLAUDE.md read-list
```

Actualizar SOLO orientación/documentación.

Objetivo:
- V5 baseline vigente;
- V4.3 historia/compatibilidad;
- `PROJECT_STATE.json` autoridad operativa;
- no borrar historia V4;
- no inventar V6.

## 14. README.md

Actualizar mínimo necesario:

- `LegacyMapper V5 CLOSED`;
- stacks:
  - VB.NET WebForms/Oracle
  - Python generic pilot;
- Evidence/docs/cache/AI proposal/review/canonical/consumers;
- disclaimer de piloto circular;
- enlace a `docs/V5/V5_OPERATIONS_GUIDE.md`;
- enlace a final baseline;
- Plugin Contract ≠ Plugin Runtime;
- no auto approval/canonicalization;
- dónde leer estado actual.

No convertirlo en manual exhaustivo.

## 15. docs/PROJECT_RECOVERY.md

Actualizar recuperación para empezar desde:

```text
PROJECT_STATE.json
docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md
docs/V5/V5_FINAL_BASELINE.json
docs/V5/V5_OPERATIONS_GUIDE.md
```

Preservar V4/V3 como histórico.

Debe permitir reconstruir:
- estado V5;
- commit final;
- invariantes;
- baselines;
- deuda;
- próximos trabajos post-V5.

## 16. CLAUDE.md

Actualizar solo lista/orden de lectura si está desactualizada.

Orden recomendado:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md
docs/V5/V5_OPERATIONS_GUIDE.md
roadmap/historia V5
```

No cambiar reglas salvo contradicción real.

# FINAL STATE

## 17. PROJECT_STATE

Si todo pasa:

```text
current_version = V5
status = V5_CLOSED
latest_completed_round = V5-Closure-R3
latest_approved_round = V5-Closure-R1
round_status = CLOSED
human_review = APPROVED

v5_closed = true
v5_closure_started = true

v5_final_production_commit = <closure commit hash>
v5_final_analyzer_version = 3
v5_final_analyzer_fingerprint =
f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b

next = POST_V5_PLANNING
v6_started = false
```

No poner `V6_READY_TO_START` salvo contrato previo explícito.

## 18. Roadmaps

Actualizar:

```text
V5.0 CLOSED
...
V5.9 CLOSED
V5 Closure R1 completed
V5 Closure R3 completed
V5 CLOSED
```

Registrar analyzer baseline, IST baseline, piloto Python circular, blocking debt=0 y deuda post-V5.

No crear roadmap V6.

# FINAL ARTIFACTS

## 19. Final closure report

Crear:

```text
docs/V5/V5_FINAL_CLOSURE.md
```

Cubrir:
1. objetivo;
2. estado inicial;
3. aprobación Closure R1;
4. production freeze;
5. analyzer fingerprint;
6. directed tests;
7. full suite;
8. IST baseline;
9. Python baseline;
10. contracts/invariants summary;
11. debt;
12. docs refresh;
13. PROJECT_STATE;
14. roadmap;
15. Git preflight;
16. staging;
17. commit;
18. push;
19. remote verification;
20. tag recommendation/status;
21. final state.

## 20. Machine-readable receipt

Crear:

```text
docs/V5/V5_FINAL_CLOSURE.json
```

Campos mínimos:

```text
status
closure_round
base_commit
final_commit
parent_commit
branch
remote
push_status
tag_status
tag_recommendation
analyzer_version
analyzer_fingerprint
tests
ist_baseline
python_pilot
blocking_debt
future_phase_debt_count
observation_debt_count
historical_compatibility_count
v5_closed
v6_started
```

## 21. Preserve R1 baseline

NO reemplazar:

```text
V5_FINAL_BASELINE.json
V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md
```

# DEBT

## 22. Debt final

Esperado:

```text
BLOCKING = 0
```

R1:

```text
FUTURE_PHASE = 14
OBSERVATION = 15
HISTORICAL_COMPATIBILITY = 5
```

Después del refresh:

```text
OB-14 = RESOLVED_IN_CLOSURE_R3
```

No borrar del ledger histórico; actualizar current_status/evidence.

No reclasificar otros items sin evidencia.

# SECURITY

## 23. Spot-check final

Confirmar:
- 0 real provider calls;
- no target execution;
- no network;
- no secrets agregados;
- no Plugin Runtime;
- no source mutation;
- docs refresh sin credenciales ni paths privados.

# GIT STAGING

## 24. Pre-staging

```text
git diff --check
git status --short
git diff --stat
```

NO `git add .` sin inspección.

## 25. Explicit staging

Incluir solo:
- Closure R1 artifacts;
- Closure R3 artifacts;
- prompts Closure si forman parte del repo;
- `README.md`;
- `docs/PROJECT_RECOVERY.md`;
- `CLAUDE.md` si cambia;
- `PROJECT_STATE.json`;
- roadmaps/historia;
- recibo post-push V5.9 si corresponde;
- debt ledger actualizado.

Excluir outputs locales, caches, IST outputs, temp/logs, test artifacts, `__pycache__`, secretos.

# COMMIT

## 26. One final closure commit

Crear UN commit.

Mensaje recomendado:

```text
chore(v5): close V5 release baseline
```

Registrar hash, parent, message, files, insertions/deletions.

No amend.
No segundo commit.

# PUSH

## 27. Push

```text
git push origin main
```

Sin force.

Si falla:

```text
V5_CLOSURE_R3_PUSH_BLOCKED
```

## 28. Remote verification

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

# TAG

## 29. Recommendation only

Inspeccionar tags existentes.

Reportar:

```text
existing_tags = [...]
recommended_final_v5_tag = <value or NONE>
tag_created = false
tag_status = TAG_NOT_CREATED_PENDING_HUMAN_DECISION
```

Si solo existe `v5.2` y no hay convención global suficiente, puede recomendarse `v5`, pero NO crearlo.

No usar `v5.0` automáticamente.

# POST-PUSH RECEIPT

## 30. Self-referential receipt

Después del push actualizar report/json con final commit, remote verification y tag recommendation/status.

Puede quedar como única modificación local post-push.

NO crear segundo commit solo por autorreferencia.

# FINAL STATES

## 31. Éxito

```text
V5_CLOSED
V5_FINAL_CLOSURE_R3_COMPLETED
V5_FINAL_CLOSURE_PUSHED_TO_ORIGIN_MAIN
POST_V5_PLANNING
```

Con:

```text
v5_closed = true
v6_started = false
TAG_NOT_CREATED_PENDING_HUMAN_DECISION
```

## 32. Bloqueo técnico

```text
V5_CLOSURE_R3_BLOCKED
```

## 33. Bloqueo push

```text
V5_CLOSURE_R3_PUSH_BLOCKED
```

## 34. Regla final

Cerrar V5 solo si:
- Closure R1 aprobada;
- no R2;
- production frozen;
- fingerprint estable;
- directed tests verdes;
- full suite verde;
- IST baseline válido;
- Python baseline válido;
- contracts/invariants sostenidos;
- BLOCKING=0;
- user-facing docs actualizados;
- PROJECT_STATE=V5_CLOSED;
- roadmaps actualizados;
- final closure artifacts creados;
- un commit;
- push exitoso;
- remote==HEAD;
- no V6 iniciada;
- tag no creado sin autorización humana.

Detenerse después del recibo final.
