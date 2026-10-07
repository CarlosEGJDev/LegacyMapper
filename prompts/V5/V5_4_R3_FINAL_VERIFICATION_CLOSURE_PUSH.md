# LegacyMapper V5.4 — R3 Final Verification + Closure + Commit + Push

## 1. Objetivo

Cerrar V5.4 — Technology / DB Adapters en una única ronda final.

R1 ya fue aprobada humanamente y no requiere R2.

Esta ronda debe:

```text
verificación final
→ regresión real mínima
→ cierre documental/contractual
→ actualización de estado
→ commit único
→ push a origin/main
→ verificación remota
```

NO iniciar V5.5.

## 2. Estado de partida

V5.3 está cerrada y publicada.

Baseline Git antes de V5.4:

`9425319cb2edbae896b96f7abfbdcd3764beb538`

R1 V5.4 aprobada:

```text
V5_4_R1_READY_FOR_HUMAN_REVIEW
V5_4_NEXT_R3_FINAL_VERIFICATION
```

No ejecutar R2.

Adapter aprobado:

```text
id = vbnet-webforms-oracle
version = 1.0
architecture = composed adapter
```

Analyzer:

```text
ANALYZER_VERSION = 3
```

Defaults V5.3 preservados:

```text
cache-mode = auto
verify-cache = fast
trust-mtime = false
incremental-max-changed-ratio = None
```

## 3. Autorización

El usuario autoriza explícitamente en esta ronda:

- verificación final;
- actualización documental/estado;
- staging explícito;
- UN commit local;
- `git push origin main`;
- consultas Git para verificar remoto.

NO autoriza:

- tag;
- release;
- force push;
- amend;
- rebase;
- reset destructivo;
- clean;
- eliminación de ramas;
- iniciar V5.5.

Si push falla por divergencia/autenticación:

- NO usar force;
- NO rebase automático;
- NO merge improvisado;
- detenerse y documentar.

## 4. Fuentes obligatorias

Leer antes de actuar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos finales V5.0
- `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
- cierre V5.1
- cierre V5.2
- cierre V5.3
- `docs/V5/V5_4_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_4_R1_INTEGRATED_DELIVERY.json`
- `docs/V5/V5_4_R1_MAINTAINABILITY_INVENTORY.json`
- continuidad/roadmap V5

Regla:

```text
R3 verifica y cierra.
No rediseña V5.4.
```

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

- rama `main`;
- R1 todavía sin commit;
- no hay cambios inesperados;
- no hay outputs/cache/IST/temp;
- no hay secretos;
- no hay V5.5.

Clasificar también los administrativos pendientes de V5.3:

- `docs/V5/V5_3_R4_1_GIT_PUSH_RESULT.md`
- `prompts/V5/V5_3_R4_1_FINAL_GIT_PUSH.md`

Si siguen sin versionar y son correctos, incluirlos en este cierre para limpiar continuidad histórica.

## 6. Freeze de producción

Antes de verificación final:

- congelar cambios de producción;
- no refactorizar más;
- no mover módulos;
- no renombrar APIs;
- no cambiar fingerprints;
- no tocar analyzer version salvo defecto real.

R3 debe validar el resultado de R1.

## 7. Verificación arquitectónica final

Revalidar:

### Core neutral

El core no debe importar implementación concreta de:

- WebForms;
- VB.NET;
- Oracle;
- `.vbproj`;
- parser/resolver específico.

Debe mantenerse:

```text
core ← contratos neutrales ← adapter
```

Composition root/pipeline puede importar adapter concreto.

### Fronteras

Confirmar:

- `legacy_documenter/adapters/contracts.py` neutral;
- adapter concreto bajo `legacy_documenter/adapters/vbnet_webforms_oracle/`;
- Evidence Core neutral;
- flow neutral bajo `analysis/normalized_flow.py` + helpers neutrales;
- shims legacy sin lógica;
- 0 MIXED material restante según criterio R1.

Ejecutar nuevamente el guard arquitectónico R1.

## 8. Verificación de compatibilidad pública

Confirmar que imports históricos siguen funcionando:

- extractors legacy;
- resolvers legacy;
- evidence builder/projector legacy;
- flow resolver legacy.

Los shims deben:

- re-exportar;
- no contener algoritmos;
- preservar identidad/comportamiento.

Si un shim contiene lógica nueva, bloquear cierre.

## 9. Adapter contract final

Revalidar:

- `TechnologyAdapter` / contrato equivalente;
- capabilities;
- selección determinista;
- unsupported;
- ambigüedad;
- fake/synthetic adapter;
- extensions namespaced;
- provenance;
- schema target;
- adapter identity/version.

No agregar nuevo framework.

## 10. DB boundary final

Revalidar explícitamente:

- Oracle;
- ADO.NET;
- stored procedures;
- SQL;
- parámetros;
- transacciones;
- conexiones;
- unresolved target;
- ExternalDependency;
- DataOperation;
- DataObject;
- DataParameter.

Criterio:

```text
vocabulario DB específico
→ adapter internals/extensions

conceptos persistidos/core
→ neutrales
```

No perder evidencia específica.

## 11. Cache/fingerprint final

Confirmar:

- analyzer = 3;
- adapter implementation incluida en code fingerprint;
- adapter identity/version afecta contexto de cache cuando corresponde;
- cache analyzer 2 no reutilizable;
- cache analyzer 3 compatible consigo misma;
- no cache cruzada entre adapter identities;
- docs/prompts no invalidan analyzer cache.

Ejecutar tests dirigidos correspondientes.

## 12. Tests dirigidos R3

Ejecutar como mínimo:

- tests V5.4 R1;
- tests de architecture boundary;
- tests DB;
- tests normalization/evidence;
- tests fingerprint/cache;
- tests de legacy import compatibility;
- tests fake adapter.

Registrar:

- total;
- failures;
- errors;
- skips;
- duración.

No añadir tests nuevos salvo hueco real detectado.

## 13. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Criterio:

```text
failures = 0
errors = 0
```

Baseline R1:

```text
2850 tests
0 failures
0 errors
132 skips
```

Si cambia el conteo, explicar exactamente por qué.

## 14. IST real — una sola verificación final

R1 ya demostró equivalencia sobre copia controlada V5.3.

Para R3 hacer UNA corrida final preferentemente sobre IST oficial prístino:

```text
C:\Users\cgalianj\source\IST_40\Operacional
```

Antes:

- inventario;
- SHA;
- readonly/no mutación.

Después:

- inventario;
- SHA;
- confirmar fuente intacta.

No modificar IST.

## 15. Baseline para IST oficial

Si existe output canónico reciente generado desde IST oficial con:

- mismo source;
- mismo config;
- mismo schema;
- V5.3 cerrado;
- analyzer previo válido como referencia;

reutilizarlo.

Si no existe una referencia verificable, generar UNA referencia `off/full` antes de la corrida V5.4.

No ejecutar matrices.

Presupuesto máximo ideal:

```text
1 baseline full/off solo si hace falta
+
1 V5.4 final
```

## 16. Corrida V5.4 final

Ejecutar con configuración equivalente a baseline.

Preferencia:

```text
cache-mode auto
verify-cache fast
trust-mtime false
ratio None
AI off
```

Registrar:

- wall;
- stages;
- adapter seleccionado;
- analyzer version;
- cache session;
- fallback reason si existe;
- hits/misses;
- provider/AI calls = 0.

## 17. Comparación canónica

Usar:

`tools/v5_3_compare_full_incremental.py`

Comparar baseline oficial vs V5.4 final.

Debe resultar:

```text
added = 0
removed = 0
changed = 0
```

Fuera solo de exclusiones contractuales ya aprobadas:

- `_cache_v53/`
- root `RUN_SUMMARY.json`
- root `RUN_SUMMARY.md`
- `index/repository.json`

NO ampliar exclusiones.

## 18. Determinismo

No hace falta repetir otra corrida IST completa si:

- suite cubre determinismo;
- R1 ya demostró igualdad completa;
- R3 oficial coincide canónicamente.

Usar evidencia acumulada.

Solo repetir una corrida si aparece divergencia real.

## 19. Performance sanity check

Comparar con R1 y V5.3.

No recalibrar.

No exigir igualdad exacta.

Solo alertar si:

- extraction se multiplica inexplicablemente;
- resolvers empeoran materialmente;
- documentation/export empeoran materialmente;
- total presenta regresión grave.

No atribuir variaciones sin evidencia.

## 20. Seguridad final

Confirmar:

- IST oficial intacto;
- 0 IA/provider real;
- no secretos en reportes/cache;
- sanitización intacta;
- no source crudo persistido en docs R3;
- outputs locales fuera de Git.

## 21. Deuda final V5.4

Clasificar:

```text
BLOCKING
FUTURE_PHASE
OBSERVATION
```

Esperado no bloqueante:

- shims legacy;
- `full_pipeline.py` / `pipeline_stages.py` complejos;
- grandes algoritmos legacy;
- adapter registry CLI con un único adapter real;
- segunda tecnología real diferida a V5.9;
- partial resolver recomputation fuera de V5.4.

No convertir esto en R2 retrospectiva.

## 22. PROJECT_STATE

Si todo pasa:

```text
current_version = V5.4
status = V5_4_CLOSED
latest_completed_round = V5.4-R3
latest_approved_round = V5.4-R1
round_status = CLOSED
human_review = APPROVED
v5_4_closed = true
next_version = V5.5
next_round = V5.5-R1
V5_5_READY_TO_START = true
```

Registrar además:

- R2 = NOT_REQUIRED;
- R3 verification = COMPLETED;
- adapter = vbnet-webforms-oracle 1.0;
- analyzer = 3.

No marcar V5.5 iniciada.

## 23. Continuidad

Actualizar solo:

- estado vigente;
- ledger;
- cierre V5.4;
- R2 skipped/not required;
- R3 closure;
- próximo V5.5.

Preservar historia.

Mantener modelo:

```text
R1 Integrated Delivery
R2 Targeted Corrections only if needed
R3 Final Verification & Closure
```

## 24. Documento final

Crear:

`docs/V5/V5_4_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

Debe incluir:

1. Objetivo.
2. Estado inicial.
3. Aprobación R1.
4. R2 no requerido.
5. Freeze de producción.
6. Arquitectura final.
7. Compatibilidad legacy.
8. Adapter contract.
9. DB boundary.
10. Cache/fingerprint.
11. Tests dirigidos.
12. Suite completa.
13. IST oficial.
14. Baseline usada.
15. Corrida final.
16. Comparación canónica.
17. Determinismo.
18. Performance sanity.
19. Seguridad.
20. Deuda.
21. PROJECT_STATE.
22. Continuidad.
23. Git pre-commit.
24. Commit.
25. Push.
26. Estado remoto.
27. Próximo V5.5.
28. Estado final.

Opcional:

`docs/V5/V5_4_R3_FINAL_VERIFICATION_AND_CLOSURE.json`

## 25. Staging

Antes:

```text
git status --short
git diff --stat
git diff --check
```

Revisar todos los archivos.

Staging explícito por rutas.

NO usar `git add .` sin revisión.

Incluir:

- producción V5.4 R1;
- tests V5.4;
- docs R1;
- JSON/inventario R1;
- PROJECT_STATE;
- continuidad;
- prompt R1;
- prompt R3;
- documento R3;
- administrativos finales V5.3 pendientes si siguen correctos.

Excluir:

- output;
- IST;
- cache;
- logs;
- temp;
- `__pycache__`;
- secretos.

## 26. Commit

Crear UN commit local.

Mensaje recomendado:

```text
feat(v5.4): separate technology and database adapters
```

Alternativa aceptable si el repo prefiere cierre explícito:

```text
feat(v5.4): complete technology adapter separation
```

Elegir uno y documentar.

No amend.

## 27. Push autorizado

Después del commit:

```text
git push origin main
```

Sin force.

Si falla:

```text
V5_4_R3_PUSH_BLOCKED
```

No alterar historia para “hacerlo pasar”.

## 28. Verificación remota

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
HEAD == origin/main == remote refs/heads/main
ahead = 0
behind = 0
```

## 29. Tag

NO crear tag.

Registrar:

```text
TAG_NOT_CREATED_BY_INSTRUCTION
```

## 30. Working tree final

Ideal:

```text
clean
```

Si queda únicamente un reporte post-push auto-referencial:

- documentarlo;
- no crear segundo commit solo por ese reporte.

## 31. Estados finales permitidos

Éxito:

```text
V5_4_CLOSED
V5_4_R3_PUSHED_TO_ORIGIN_MAIN
V5_5_READY_TO_START
```

Bloqueo técnico:

```text
V5_4_R3_BLOCKED
```

Bloqueo solo push:

```text
V5_4_R3_PUSH_BLOCKED
```

## 32. Criterio de cierre

V5.4 se considera cerrada si:

- R1 aprobada;
- R2 no requerida;
- frontera adapter final verificada;
- core neutral;
- DB boundary correcto;
- cache/fingerprint correcto;
- suite completa verde;
- IST oficial equivalente;
- 0 divergencias canónicas;
- no deuda BLOCKING;
- PROJECT_STATE cerrado;
- continuidad actualizada;
- commit creado;
- push exitoso;
- remoto == HEAD;
- sin tag nuevo;
- V5.5 marcada READY_TO_START pero no iniciada.

Detenerse para revisión humana final.
