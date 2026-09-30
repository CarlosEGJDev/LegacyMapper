# V5.1 R3 — Revalidación posterior a R3.1

## 1. Estado final

V5_1_R3_READY_FOR_R4

Los tres bloqueos originales de R3 (D-1, D-2, D-3) se revalidaron de forma independiente contra el código actual, contra dos corridas productivas reales sobre IST (`v5_1_r3_1_run_a`/`v5_1_r3_1_run_b`, reutilizadas porque `git status` confirma que el código no cambió desde que se generaron) y contra la suite completa, ejecutada de nuevo en esta ronda. Los tres están cerrados. D-4 y D-5 siguen abiertas, sin cambios desde R3, y se documenta aquí por qué no bloquean R4. No se corrigió ningún defecto nuevo; el único acto de esta ronda fue verificación, más una ejecución real adicional de `analyze` sobre el fixture para confirmar integración productiva de ese comando (§16).

## 2. Evidencia revisada

- Documentos: R0, R1, R2, R2.1, R3, R3.1 de V5.1 (leídos íntegros, no solo su resumen).
- Código real (no solo lo que narra R3.1): `identity.py`, `entities.py`, `builder.py`, `invariants.py`, `persistence.py`, `reference.py`, `projection.py`, `pipeline_stages.py` — leídos línea a línea y contrastados contra las afirmaciones de R3.1.
- `git status`/`git diff --stat`: el árbol de trabajo coincide exactamente con lo que R3.1 dejó; no hay cambios de código posteriores que invaliden reutilizar sus corridas.
- Dos corridas productivas reales sobre `C:\Users\cgalianj\source\IST_40\Operacional`: `C:\PruebasLegacyMapper\Resultados\v5_1_r3_1_run_a` y `...\v5_1_r3_1_run_b`, ambas re-leídas con un script de verificación independiente (recuento directo de JSON, sin reutilizar código de producción para contar) que recalcula identidad, XDP, `sha256`, persistencia, determinismo y compatibilidad V4.3 desde cero.
- Una invocación real adicional de `python main.py analyze` (fixture) para confirmar `evidence/` en ese comando fuera de los tests unitarios.
- Suite completa ejecutada de nuevo en esta ronda (no se reutiliza el resultado de R3.1).
- AST propio (no el de los tests) sobre runtime independence / AI independence / adapter boundary.

## 3. Estado D-1 (XDP uniqueness)

Confirmado corregido, verificado de forma independiente:

- Fórmula real en `builder.py::_build_external_dependencies`: `XDP- = sha256_id("assembly", project_path, include, hint_path, duplicate_ordinal)`, con `duplicate_ordinal` asignado por `DuplicateOrdinalAssigner` sobre la tupla `("assembly", project_path, include, hint_path)`. Ningún UUID, timestamp ni orden global: el ordinal solo depende del orden relativo entre registros con la misma tupla (mismo mecanismo que `CAL-`, código leído directamente).
- Sobre `v5_1_r3_1_run_a` (recuento propio, sin reutilizar `detect_collisions`): 4 839 registros `ExternalDependency`, 4 839 ids únicos, 0 colisiones. 31 registros con `duplicate_ordinal > 0` (coincide exactamente con los 31 registros extra que R3 había detectado). `v5_1_r3_1_run_b`: idéntico.
- Duplicados byte-idénticos también se detectarían: verificado aplicando el detector actual (`detect_collisions`) sobre la evidencia **no corregida** de R3 (`v5_1_r3_run_a/evidence/external_dependencies.json`, XDP con la fórmula antigua): 4 839 registros, 4 808 ids distintos, 5 ids duplicados, 36 registros involucrados, 31 extra — exactamente los números que R3 había reportado manualmente. El detector actual los recupera correctamente cuando se le da la evidencia antigua.
- Estabilidad entre ejecuciones equivalentes: A y B son byte-idénticos en `external_dependencies.json` (parte del árbol `evidence/` completo, 25 archivos, 0 diferencias).

`ExternalDependency records == unique XDP IDs`: **4 839 == 4 839** en A y B. `XDP duplicate canonical IDs = 0`.

## 4. Estado D-2 (`SourceArtifact.sha256` obligatorio)

Confirmado corregido, verificado de forma independiente:

- `SourceArtifact.sha256: str` sin default (`entities.py`), validado en `__post_init__` contra `is_sha256_hex` (64 hex minúsculas). No es posible instanciar un `SourceArtifact` con `sha256=None` o vacío: se probó directamente (`SourceArtifact(..., sha256=None)` lanza `ValueError`, confirmado por los tests §17 y por lectura del código).
- `build_evidence_artifacts` (`pipeline_stages.py`) construye siempre con `repo_root=indexes["repository"]["root"]`, tanto para `full` como para `analyze` (ambos comparten `export_artifacts`, confirmado por lectura directa, no supuesto).
- Sobre `v5_1_r3_1_run_a`: 15 138 `SourceArtifact`, 15 138 con `sha256` válido (64 hex), 0 `None`, 0 vacíos. `v5_1_r3_1_run_b`: idéntico. Se recalculó el SHA-256 real de una muestra de 202 archivos (cada ~75) directamente contra el contenido en disco de IST: 0 discrepancias.
- No depende de mtime/metadata: `_hash_file` (función de módulo en `builder.py`) usa `hashlib.file_digest` sobre los bytes; no se leyó ningún campo de filesystem aparte del contenido.
- Fallo de lectura impide considerar válida la ejecución: `_build_source_artifacts` no captura `OSError` de un archivo ilegible; se propaga hasta `build_evidence_artifacts`, que no la atrapa tampoco → la ejecución completa queda FAILED (ver D-3). Confirmado con un test dedicado y por lectura de código (ya no hay ningún `except OSError: return None`).

`SourceArtifacts without SHA-256 = 0` en A y B.

## 5. Estado D-3 (Evidence Core obligatorio para SUCCESS)

Confirmado corregido, revalidado con una ejecución de sondeo independiente (nuevo proceso, no reutilizando la sesión que hizo la corrección) contra la CLI real (`legacy_documenter.main.main`), inyectando el fallo por separado en cada una de las tres fases:

| Fase fallada | `full`: exit code | `full`: status | `EXPORT.error` | `index/` conservado | Manifest tras el fallo | `analyze` |
|---|---|---|---|---|---|---|
| `NormalizedEvidenceBuilder.build` | 4 | FAILED | `RuntimeError: injected build failure` | sí | ausente | propaga `RuntimeError` |
| `validate_evidence` | 4 | FAILED | `AssertionError: I-1: injected collision` | sí | ausente | propaga `AssertionError` |
| `write_evidence` | 4 | FAILED | `OSError: injected disk failure` | sí | ausente | propaga `OSError` |
| (sin inyección, restaurado) | 0 | SUCCESS | — | sí | presente | — |

- Exit code ≠ 0 en los tres casos (4, el código FAILED del contrato existente `legacy_documenter/cli/router.py`, sin código nuevo).
- Estado FAILED confirmado en `RunResult.status` y en `RUN_SUMMARY.json["status"]`.
- Error observable: queda en `EXPORT.error.category`/`.message` dentro de `RUN_SUMMARY.json`, además de un `LOG.error` visible por la consola (confirmado con `assertLogs`).
- No existe SUCCESS silencioso: en los tres casos el run es FAILED, nunca SUCCESS/PARTIAL.
- Manifest válido ausente: `evidence/EVIDENCE_MANIFEST.json` no existe tras el fallo en ninguno de los tres casos.
- Artefactos legacy previos se mantienen: `index/entry_points.json` existe tras el fallo en los tres casos (se escribe antes que `build_evidence_artifacts`).
- Un manifest de una corrida anterior no puede hacer pasar la corrida fallida como válida: `build_evidence_artifacts` borra `evidence/EVIDENCE_MANIFEST.json` (`stale_manifest.unlink(missing_ok=True)`) **antes** de intentar construir, y el manifest solo se vuelve a escribir al final de `write_evidence`, después de las 24 particiones. Verificado con un test de rerun (`test_rerun_failure_never_leaves_a_stale_manifest`, ejecutado en esta ronda dentro de la suite): una corrida SUCCESS con manifest presente, seguida de una corrida FAILED sobre el mismo `--output`, termina sin manifest.
- `git status` de `legacy_documenter/` antes y después del sondeo es idéntico: no quedaron hooks ni sabotajes en el producto.

## 6. Resultado del detector I-1

Verificado sin limitarse a XDP, sobre casos sintéticos directos (no solo tests preexistentes):

| Caso | Resultado |
|---|---|
| Mismo id, contenido distinto | `check_i1_id_unique_per_kind` lanza `InvariantViolation` |
| Mismo id, contenido byte-idéntico | `check_i1_id_unique_per_kind` lanza `InvariantViolation` (la corrección real de R3.1: R2/R2.1 lo exceptuaban) |
| Ids distintos | `check_i1_id_unique_per_kind` no lanza |

`detect_collisions`/`detect_duplicate_ids` (la infraestructura genérica en `identity.py`, no una función ad hoc de XDP) es lo que usan tanto `check_i1_id_unique_per_kind` como `identity_report`/`validate_evidence` (el gate de producción) — confirmado por lectura: un solo detector, reutilizado en los tres puntos, corregido una sola vez.

`validate_evidence` aplica I-1 a los 13 tipos de `CANONICAL_ID_KINDS` (no solo XDP) antes de persistir en producción — confirmado ejecutándose realmente en las dos corridas de IST (si hubiera fallado, las corridas habrían sido FAILED; fueron SUCCESS con 0 colisiones en los 13 tipos, ver §10).

## 7. Revisión I-1..I-11

| Invariante | Estado | Evidencia |
|---|---|---|
| I-1 (unicidad de id) | **PASS**, verificado a escala real | §6, §10: 13 tipos canónicos, 0 colisiones en A y B; gate de producción ejecutado realmente |
| I-2 (`PAR`/`CALL`/`UNRES` nunca como id) | **PASS** | Tests existentes (`check_i2_no_legacy_ref_as_identity`) siguen verdes; `CallIdentity.id` siempre `CAL-`, `legacy_ref` siempre `CALL-` (por diseño del builder, sin cambios de R3.1) |
| I-3 (EntryPoint → FunctionalFlow 0..1) | **PASS**, verificado a escala real | Sobre `v5_1_r3_1_run_a`: 12 642 `FunctionalFlow`, 12 642 `entry_point_id` distintos (máx. 1 flow por EP), 0 referencias a `entry_point_id` inexistente |
| I-4 (trazabilidad vía `provenance`/`EvidenceReference`) | **NO VALIDADA en su forma literal** | Ver §8: ningún `to_dict()` emite el campo `provenance` que R1/V5.0-R3 exigen como común obligatorio; `check_i4_traceability` no se invoca en ningún test ni en producción (grep: 0 llamadas). La trazabilidad *real* se verificó por un mecanismo distinto (claves foráneas): 0 `Component.source_ref`, `CallIdentity.source_artifact`, `Instantiation.source_artifact` colgantes sobre 9 859 + 230 356 + 40 278 registros reales |
| I-5 (referencia rota nunca pasa en silencio) | **NO VALIDADA en su forma literal** | Mismo motivo que I-4: `check_i5_evidence_reference_resolves_or_fails_explicitly` no se invoca fuera de sus propios tests unitarios sobre datos sintéticos; no hay `EvidenceReference` real que resolver en producción |
| I-6 (proyección no inventa relaciones) | **PASS** (sobre fixture; no repetido a escala IST en esta ronda) | Test existente verde: ids citados por la proyección ⊆ ids en evidencia |
| I-7 (no promoción sin `promotion_basis`) | **Vacuously PASS — precondición nunca ocurre** | `check_i7_no_promotion_without_basis` no se invoca en ningún test/producción; se verificó directamente sobre `v5_1_r3_1_run_a` que **0** registros de `components`/`data_objects`/`call_identities` tienen `_promoted_from_unresolved` — V5.1 no implementa ningún mecanismo de promoción todavía, así que la invariante no tiene caso real que ejercitar |
| I-8 (state estable entre proyecciones) | **PASS, implicado por I-9** | `check_i8_state_immutable_across_projections` tampoco se invoca directamente, pero la proyección legacy (`index/`) es byte-idéntica al original (I-9), lo que implica que ningún `state` cambia en esa proyección; no se verificó para `ai_context`/`documentation` en esta ronda |
| I-9 (equivalencia byte a byte con proyección legacy) | **PASS, verificado a escala real** | `index/` de `v5_1_r3_1_run_b` vs. baseline `v5_1_r3_run_a`: 21/22 archivos byte-idénticos, el único distinto (`repository.json`) solo en `duration_seconds`; `documentation/`: 876/876 sin diferencias |
| I-10 (determinismo) | **PASS, verificado a escala real** | A vs. B: `evidence/` 25 archivos, 0 diferencias byte a byte (incluido el manifest) |
| I-11 (`included_paths` ∩ `omitted_paths` = ∅) | **PASS** | Tests existentes verdes (fixture); no depende de datos reales de IST (es una regla estructural sobre `FunctionalFlow`, campos que R1 deja en su valor neutral) |

**Conclusión de esta sección:** ninguna invariante se declara PASS sin evidencia real detrás. I-4/I-5, tal como las define R1 §12 (literalmente sobre `provenance`/`EvidenceReference`), no están validadas porque su precondición no se cumple en el código actual — no es que fallen, es que no hay nada que verificar contra ellas todavía. Esto es una discrepancia real de contrato, tratada en D-4 (§8), no un defecto oculto.

## 8. Decisión técnica sobre D-4

**Hallazgo (más preciso que R3):** `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md` (línea 40) fija `provenance` (lista de `EvidenceReference`, ≥1, salvo `SourceArtifact` raíz) como **campo común obligatorio** de toda entidad. R1 hereda esa obligación textualmente (§6, línea 309). Ninguna entidad de `legacy_documenter/evidence/entities.py` serializa un campo `provenance` — confirmado leyendo los 9 `to_dict()` uno por uno. `builder.py`/`persistence.py` no construyen ningún `EvidenceReference` real (grep: 0 usos fuera de `reference.py` y de sus propios tests unitarios).

**Decisión: A) cumple suficientemente V5.1, no bloquea R4** — con la salvedad honesta de que es una desviación real de contrato, no una interpretación alternativa válida del mismo.

Justificación:

1. La trazabilidad que R1 pide *funcionalmente* (poder ir de cualquier entidad a su origen) está garantizada por un mecanismo alternativo, real y verificado a escala completa de IST: claves foráneas tipadas (`source_ref`, `source_artifact`, `legacy_ref`) más el passthrough íntegro (`extensions`) del registro legacy original. 0 referencias colgantes en 280 493 registros comprobados (`Component`, `CallIdentity`, `Instantiation` sobre A).
2. `check_i4_traceability`/`check_i5_evidence_reference_resolves_or_fails_explicitly` existen, están probados unitariamente con datos sintéticos, y `EvidenceReference` es un contrato ya implementado (`reference.py`, con validación propia en `__post_init__`) — no hay que inventar nada nuevo si una ronda futura decide emitirlo; el trabajo pendiente es de "conectar", no de "diseñar".
3. Ninguna de las tres decisiones que motivaron R3.1 (D-1/D-2/D-3) depende de `provenance`; añadirlo ahora sería exactamente el tipo de corrección nueva que esta ronda de revalidación tiene prohibido introducir.
4. R2, R2.1 y R3 ya llegaron a la misma conclusión de forma independiente en tres rondas sucesivas; no hay indicio nuevo que la contradiga.

Esto **no** es cerrar D-4: sigue siendo una contradicción real y documentada del contrato (`provenance` no se emite), que una ronda de integración posterior a V5.1 (o una R3.2 si el Technical Lead decide que debe cerrarse antes de eso) debe resolver explícitamente — implementando la emisión o enmendando el contrato para quitar la obligatoriedad de `provenance` en favor del mecanismo de claves foráneas ya en uso.

## 9. Decisión técnica sobre D-5

Sin cambios desde R3: no existe ningún lector `evidence/ → entidades` (`from_dict`/`read_evidence`) en `legacy_documenter/evidence/` — confirmado por grep, 0 coincidencias. `LegacyIndexProjector.project()` solo opera sobre un `NormalizedEvidence` ya en memoria, nunca sobre `evidence/*.json` releído desde disco.

**Decisión: deuda aceptable, no bloquea R4.** V5.0 D-01/D-04 exige que `index/` sea una proyección *posible* de `evidence/`, lo cual ya está demostrado (round-trip exacto vía I-9, con `evidence/` construido y `index/` proyectado en el mismo proceso). No exige que la implementación física invierta la fuente en V5.1. Construir el lector es trabajo de integración (V5.3 o una ronda dedicada), no una corrección bloqueante de R3.1's alcance.

## 10. Identidades canónicas

Sobre `v5_1_r3_1_run_a` (recuento independiente, `v5_1_r3_1_run_b` idéntico salvo donde se indica):

| Entidad | Registros | IDs distintos | Duplicados |
|---|---|---|---|
| SourceArtifact | 15 138 | 15 138 | 0 |
| Solution | 113 | 113 | 0 |
| Project | 259 | 259 | 0 |
| Component | 9 859 | 9 859 | 0 |
| EntryPoint | 12 662 | 12 662 | 0 |
| EventBinding | 12 662 | 12 662 | 0 |
| Call / CAL | 230 356 | 230 356 | 0 |
| DataOperation | 20 082 | 20 082 | 0 |
| DataObject | 5 392 | 5 392 | 0 |
| FunctionalPath | 170 020 | 170 020 | 0 |
| FunctionalFlow | 12 642 | 12 642 | 0 |
| ExternalDependency / XDP | 4 839 | 4 839 | 0 |
| UnresolvedBoundary | 162 914 | 162 914 | 0 |

`records == unique canonical IDs` se cumple en los 13 tipos, en A y en B. Este recuento se hizo con un script propio de esta ronda que lee los JSON de `evidence/` directamente y cuenta con `collections.Counter`, sin invocar `detect_collisions`/`validate_evidence` — es decir, no se confía en que el mismo código que se está revalidando también audite su propio resultado.

## 11. Cardinalidades

Verificadas directamente sobre `v5_1_r3_1_run_a`:

| Relación | Resultado |
|---|---|
| EntryPoint → FunctionalFlow (0..1) | 12 642 flujos, 12 642 `entry_point_id` distintos, máx. 1 flujo por EP, 0 referencias a EP inexistente |
| FunctionalPath → DataOperation | 4 612 paths con `terminal_type=data_operation`, 1 157 DAO distintos, máx. 254 paths por DAO, 0 colgantes |
| FunctionalPath → DataObject (SP) | 1 121 paths con `terminal_type=stored_procedure` (el id real del SP está en `nodes[-1]`, no en `terminal_target`, que es el nombre legible del SP — mismo patrón ya usado en R0/R3), 338 SP distintos, máx. 63 paths por SP, 0 colgantes |
| DataOperation → DataObject | 9 790 aristas (`functional_dependencies`: 9 784 `DataAccessOperation -> StoredProcedure` + 6 `-> SQL`), 5 392 objetos distintos, máx. 17 operaciones por objeto, 0 fuente/destino colgante |
| DataOperation → DataParameter | 74 633 aristas (`DataAccessOperation -> Parameter`), 9 774 DAO con parámetros, máx. 128 parámetros por operación, 0 fuente/destino colgante |
| SourceArtifact → Component (`source_ref`) | 9 859 componentes, 0 `source_ref` colgante |
| SourceArtifact → CallIdentity (`source_artifact`) | 230 356 calls, 0 `source_artifact` colgante |
| SourceArtifact → Instantiation (`source_artifact`) | 40 278 instanciaciones, 0 `source_artifact` colgante |

Todas las cifras coinciden exactamente con las que R3 había reportado manualmente, ahora recalculadas de forma independiente sobre la corrida corregida.

## 12. Persistencia

Sobre `v5_1_r3_1_run_a`/`v5_1_r3_1_run_b`, recuento propio (no reutilizando `EVIDENCE_MANIFEST.json` como única fuente de verdad):

- **Número real de particiones físicas: 24** (`NEW_ENTITY_PARTITIONS`: 9 + `scan_summary` + `PASSTHROUGH_PARTITIONS`: 14 = 24), más `EVIDENCE_MANIFEST.json` = 25 archivos en `evidence/`. Confirmado contando archivos `.json` en el directorio, no leyendo la constante del código: `ls evidence/*.json | wc -l` da 25 (24 + manifest).
- `manifest["entity_counts"]` tiene exactamente 24 claves; los nombres de archivo en disco coinciden 1:1 con esas claves.
- El conteo de cada partición (`len(json.load(...))`) coincide con `entity_counts[nombre]` en las 24.
- `partition_sha256[nombre]` del manifest coincide con el SHA-256 recalculado del archivo físico en las 24.
- `evidence_schema_version = "1.0"`, `physical_format = "json_compact"`.
- Aclaración de la discrepancia documental heredada de R2.1 ("23 particiones"): el producto real siempre generó 24 desde R2.1 (9 nuevas + `scan_summary` + 14 passthrough); R2.1 solo contó mal en su propio documento. No es un defecto de R3.1 ni de esta revalidación.

## 13. Instantiation

- Partición independiente: `evidence/instantiations.json` existe en A y B.
- Cantidad: 40 278 registros, igual a la suma de `instantiations[]` embebidos en `calls.json` (verificado sumando directamente sobre los 4 328 archivos de `calls.json`).
- Sin id canónico: 0 de 40 278 registros tiene campo `id` (`kind`/`schema_version` sí, `id` no — por diseño).
- Relación con `calls`: `source_artifact` + `position` (0-based, secuencial dentro de cada `source_artifact`) — verificado sobre la corrida real.
- 0 `source_artifact` colgante frente a los 15 138 `SourceArtifact` reales.
- Determinismo: partición byte-idéntica entre A y B.
- Sin regresión: mismas 40 278 (coincide con R0/R2.1/R3).

## 14. Determinismo

- `evidence/`: A vs. B, 25 archivos, **0 diferencias** (comparación de SHA-256 archivo por archivo, incluido el manifest).
- Árbol completo: A vs. B, 958 archivos, **1 diferencia**: `index/repository.json`, exclusivamente en `duration_seconds` (metadata operacional, excluida desde V5.0 D-01).
- Manifest: mismos `entity_counts` y mismos `partition_sha256` en A y B.
- Reproducibilidad del hash de contenido: 202 archivos muestreados de `source_artifacts.json` recalculados contra el contenido real en disco de IST — 0 discrepancias.

## 15. Compatibilidad V4.3

`v5_1_r3_1_run_b` frente al baseline `v5_1_r3_run_a` (la última corrida de R3, previa a las correcciones):

- `index/`: 22/22 archivos comparados, 21 byte-idénticos, 1 distinto (`repository.json`), y ese único distinto difiere **solo** en la clave `duration_seconds`.
- `documentation/`: 876/876 archivos, 0 diferencias.
- `RUN_SUMMARY.json`: igual estructuralmente (`==` en Python tras cargar ambos JSON): mismas 11 claves, mismos 13 stages, mismo `output_locations` (sin `evidence`).
- Particiones de `evidence/` que cambian frente al baseline de R3 (esperado, por las correcciones): solo `external_dependencies` (nuevos ids XDP + `duplicate_ordinal`) y `source_artifacts` (`sha256` deja de ser `null`). Las otras 22 particiones son byte-idénticas frente a R3.

No se declara "equivalente" sin haber comparado: las cifras anteriores son de una comparación real archivo por archivo, no una suposición.

## 16. Production integration

- `python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output ...`: dos corridas reales completas (A y B), SUCCESS, exit 0, generando `evidence/` automáticamente dentro de `EXPORT` — confirmado leyendo `pipeline_stages.export_artifacts` (llama a `build_evidence_artifacts` incondicionalmente) y confirmado por los archivos físicos en disco.
- `python main.py analyze`: se ejecutó en esta ronda una invocación real de CLI (`python main.py analyze tests/fixtures/v4_2_r7_full_sample --output ...`, no un test unitario) — exit 0, `evidence/` con 24 particiones + manifest, log `Evidence Core: build 0.0s, validate 0.0s, persist 0.1s (8 source artifacts)`. No se repitió a escala IST completa porque `analyze_repository` invoca literalmente la misma función `export_artifacts`/`build_evidence_artifacts` que `full` (confirmado por lectura directa de `legacy_documenter/main.py::analyze_repository`, línea que llama a `stages.export_artifacts(output, indexes)`) — a igual código y misma función, repetir el escaneo completo de IST solo para `analyze` no aporta una ruta de código distinta a la ya verificada por `full`.
- La conclusión no se basa únicamente en `tools/`, tests o fixtures: las cifras de identidad/XDP/sha256/persistencia/cardinalidades de este documento provienen de leer directamente los JSON físicos que dejó el producto real (`main.py full`) sobre el target real, con un script de conteo propio de esta ronda.

## 17. Runtime independence

AST propio (no reutilizando el de los tests) sobre los 184 archivos de `legacy_documenter/`: 0 imports de `tools`, `tests`, `docs` o `prompts`. Los únicos imports de `evidence/` hacia el resto de `legacy_documenter` son `legacy_documenter.utils.atomic_write` (desde `persistence.py`). Dirección `tools → runtime` intacta (sin verificar necesario de nuevo: no se tocó `tools/` en R3.1).

## 18. AI independence

Búsqueda de texto propia sobre `legacy_documenter/evidence/*.py`: 0 ocurrencias de `openai`, `anthropic`, `ollama`, `copilot`, `gemini`, `legacy_documenter.llm`. Las dos corridas reales de IST informan `AI requested: False` / `AI invoked: False`. El gate `validate_evidence` que ahora se ejecuta obligatoriamente en producción es puramente determinista (sin ninguna rama que consulte un provider) — confirmado leyendo `invariants.py` completo.

## 19. Technology Adapter boundary

Confirmado sin cambios de frontera: la lógica específica de VB.NET (`assembly_references`, `include`, `hint_path`) que motivó la nueva fórmula de XDP vive exclusivamente en `builder.py` (el adapter de referencia), no en los módulos "core" (`entities.py`, `reference.py`, `identity.py`, `invariants.py`, `projection.py`, `persistence.py`) — verificado con AST propio: 0 imports de `legacy_documenter.extractors`/`legacy_documenter.analysis` en esos 6 módulos. Lo añadido al núcleo por R3.1 (`duplicate_ordinal` en `ExternalDependency`, `is_sha256_hex`, `CANONICAL_ID_KINDS`, `validate_evidence`) es genérico, no específico de VB/WebForms/Oracle. No se implementó ningún adapter nuevo.

## 20. Resultados IST real

- Target: `C:\Users\cgalianj\source\IST_40\Operacional` (solo lectura; no se usó `C:\inetpub\wwwroot\2010\IST\Operacional`).
- Corridas reutilizadas de R3.1 (confirmado que el código no cambió desde entonces): `v5_1_r3_1_run_a` (SUCCESS, exit 0, 1 991 s) y `v5_1_r3_1_run_b` (SUCCESS, exit 0, 1 788 s).
- Cifras de identidad, XDP, sha256, cardinalidades, persistencia y determinismo: ver §10–§14, todas recalculadas en esta ronda con un script de conteo independiente.

## 21. Suite completa

`python -m unittest discover -s tests`, ejecutada de nuevo en esta ronda (no reutilizado el resultado de R3.1):

| Total | Passed | Failures | Errors | Skipped |
|---|---|---|---|---|
| 2 247 | 2 115 | 0 | 0 | 132 |

0 failures, 0 errors. Los 132 skips son los `expected_fresh_clone_skips` de `PROJECT_STATE.json` (mismo conjunto que en R3/R3.1).

## 22. Deuda restante dentro de V5.1

1. **D-4 (abierta, no bloqueante):** `provenance`/`EvidenceReference` no se emite en producción, pese a que V5.0-R3/R1 lo listan como campo común obligatorio. I-4/I-5 no están validadas en su forma literal (§7–§8). Trazabilidad real garantizada por claves foráneas, verificada a escala completa de IST.
2. **D-5 (abierta, no bloqueante):** no existe lector `evidence/ → entidades`; `index/` no se reconstruye desde `evidence/` persistido, solo desde un `NormalizedEvidence` en memoria (round-trip ya demostrado).
3. **Causa aguas arriba de D-1 (no corregida, no bloqueante):** `VBProjExtractor` sigue emitiendo referencias `<Reference>` con `Include` vacío en 5 proyectos de IST; se preservan correctamente como ocurrencias distintas vía `duplicate_ordinal`, pero la causa en el extractor no se tocó (fuera del alcance de R3.1 y de esta revalidación).
4. **I-6/I-8 no revalidadas a escala IST en esta ronda:** se verificaron sobre el fixture (tests existentes, verdes) pero no se repitió el round-trip completo de proyección sobre los 12 642 flujos reales de IST en esta revalidación — recomendado, no bloqueante, para una ronda de integración posterior.
5. **Discrepancia documental de R2.1 ("23 particiones") aclarada (§12):** el producto siempre generó 24; era un error de conteo en el documento de R2.1, no un defecto de código.

Ninguno de estos puntos depende de D-1/D-2/D-3 ni fue objeto del mandato de R3.1.

## 23. Evidencia para decidir R4

| Bloqueo original de R3 | Estado tras revalidación independiente |
|---|---|
| D-1 (XDP no único) | Cerrado: 4 839/4 839 ids únicos en dos corridas reales; detector genérico corregido y probado con casos sintéticos; ordinal estable ante inserciones |
| D-2 (`sha256` ausente) | Cerrado: 15 138/15 138 con hash válido en dos corridas reales; 0 `None`/vacíos; reproducible; `full` y `analyze` verificados con invocaciones reales |
| D-3 (fallo silencioso) | Cerrado: sondeo independiente confirma exit 4/FAILED en las tres fases de fallo, error observable, sin manifest obsoleto, artefactos legacy conservados |
| Detector I-1 genérico | Cerrado: verificado con casos sintéticos (distinto/idéntico/único) y con el gate de producción sobre 13 tipos en IST real |
| No regresión V4.3 | Confirmado: `index/` 21/22 (+ solo `duration_seconds`), `documentation/` 0 diffs, `RUN_SUMMARY.json` estructuralmente igual |
| Determinismo | Confirmado: `evidence/` byte-idéntica entre dos corridas independientes |
| Suite completa | 2 247/2 247, 0 failures, 0 errors, 132 skips |

D-4 y D-5 quedan documentadas como deuda técnica abierta y explícitamente no bloqueante para V5.1, con la justificación de §8–§9. R4 sigue siendo obligatorio y no se declara cierre de V5.1 en este documento.

V5_1_R3_READY_FOR_R4
