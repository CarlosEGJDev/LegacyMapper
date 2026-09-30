# V5.1 R3.1 — Correcciones bloqueantes posteriores a R3

## 1. Estado final

Se corrigieron D-1 (unicidad `XDP-` + detector I-1), D-2 (`SourceArtifact.sha256` obligatorio) y D-3 (fallo del Evidence Core ⇒ ejecución FAILURE). Todo se verificó sobre IST real con dos corridas productivas independientes y con la suite completa. No se implementó nada de V5.2–V5.9. No se modificaron `PROJECT_STATE.json`, el roadmap ni `tools/`. No hubo commits ni push. El estado final figura al pie del documento.

## 2. Archivos de producción modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/evidence/identity.py` | `detect_collisions` cuenta como colisión cualquier id repetido, aunque los registros sean byte-idénticos. Nuevos `detect_duplicate_ids` (opera sobre ids sueltos) y `collision_summary` (ids duplicados / registros involucrados / registros extra). |
| `legacy_documenter/evidence/entities.py` | `SourceArtifact.sha256: str` pasa a ser obligatorio (sin default) y se valida en `__post_init__` (64 hex minúsculas); nuevo helper `is_sha256_hex`. `ExternalDependency` gana `duplicate_ordinal` (default 0), que se serializa en `to_dict`. |
| `legacy_documenter/evidence/builder.py` | Hashing incondicional: la raíz es `repo_root` o, si falta, `indexes["repository"]["root"]`. Si no hay raíz, lanza `ValueError`; si un archivo no se puede leer, propaga `OSError` (antes devolvía `None`). `_hash_file` pasa a ser una función de módulo sobre `hashlib.file_digest`. Nueva identidad `XDP-` de las dependencias `assembly` (§4). |
| `legacy_documenter/evidence/invariants.py` | `CANONICAL_ID_KINDS` (13 tipos), `identity_report` y `validate_evidence`, que es el gate de producción: I-1 sobre los 13 tipos más `sha256` obligatorio. |
| `legacy_documenter/evidence/persistence.py` | Constante `EVIDENCE_MANIFEST_FILENAME`. El formato no cambia. |
| `legacy_documenter/cli/pipeline_stages.py` | `build_evidence_artifacts` deja de ser best-effort: se eliminó el `try/except → LOG.warning`. Invalida el manifest previo, hace build → validate → persist y registra los tiempos en nivel INFO. |

## 3. Archivos de tests modificados/agregados

- `tests/test_v5_1_r2_normalized_evidence_core.py`: pasa de 59 a 78 tests (+19).
  - Invertidos:
    - `test_no_collision_for_exact_duplicates` → `test_byte_identical_duplicates_are_a_collision`.
    - `test_evidence_build_failure_does_not_fail_export_or_the_run` → `test_evidence_build_failure_fails_export_and_the_run`.
  - Nuevos:
    - `collision_summary`: ids duplicados, registros involucrados y registros extra.
    - `check_i1`: contenido distinto y contenido idéntico fallan; ids distintos pasan.
    - Fallo de validación ⇒ FAILED.
    - Exit ≠ 0 por la CLI.
    - `analyze` aborta.
    - Un rerun fallido no deja un manifest obsoleto.
    - `ExternalDependencyIdentityTests` (×5): ids distintos para referencias idénticas, determinismo, fórmula, estabilidad ante inserciones y proyecto distinto ⇒ id distinto.
    - `MandatorySourceArtifactSha256Tests` (×8): hash real contra `hashlib`, reproducibilidad, rechazo de `None`/`""`/formato inválido, sin raíz ⇒ error, archivo ilegible ⇒ error, partición productiva sin nulos, `identity_report` con 0 colisiones en los 13 tipos, duplicado byte-idéntico inyectado ⇒ `InvariantViolation`.
- `tests/test_v4_1_r0_maintainability_inventory.py`: `evidence/builder.py` pasa de MEDIUM a HIGH en el inventario heurístico. Tiene más de 400 líneas y una señal real nueva de `validation` (el `raise ValueError` fail-closed). Se actualizaron la lista `high_risk_files` y los conteos por categoría, con comentario justificativo, siguiendo el mismo patrón que usaron las rondas anteriores.

## 4. Corrección de XDP

- **Causa (confirmada en `index/projects.json` de R3):** 5 proyectos tienen varios `<Reference>` con `include=""` y `hint_path=null` (5, 5, 7, 14 y 5 ocurrencias). La fórmula anterior era `SHA-256("assembly", include, project_path)`, sin discriminador.
- **Nueva fórmula** (dependency_kind + source + target + metadata estable + ordinal):
  `XDP- = sha256_id("assembly", project_path, include, hint_path, duplicate_ordinal)`.
- **Cálculo del ordinal:** lo asigna `DuplicateOrdinalAssigner` sobre esa tupla base, que es el mismo mecanismo que usa `CAL-`. Depende solo del orden relativo de las referencias idénticas dentro del `.vbproj`. No hay posición global, timestamp, UUID ni aleatoriedad.
- **Conexiones:** las `database_connection` conservan su fórmula (`"database_connection", CONN-id`). Siguen deduplicadas por diseño: existe 1 por target.
- **Estabilidad ante inserciones:** insertar una referencia no relacionada no altera los ids existentes (test dedicado).
- **Impacto:** cambian los ids `XDP-` de todas las dependencias `assembly` respecto de R2/R3. Ningún consumidor productivo los referencia todavía; `index/` no los contiene.
- **Causa aguas arriba no tocada:** no se cambió que el extractor V4.3 emita referencias con `Include` vacío. Queda como observación (§18).

## 5. Corrección del detector de colisiones

La brecha estaba en la infraestructura genérica y no solo en XDP: `detect_collisions` descartaba los duplicados con contenido idéntico. Ahora se aplica la regla "mismo tipo + mismo id en más de un registro = colisión" para todos los tipos, porque `check_i1_id_unique_per_kind`, `identity_report` y la herramienta de regresión R2 usan el mismo detector.

Para probar que el detector ya capta el defecto, se aplicó el nuevo detector sobre la evidencia **pre-corrección** de R3 (`v5_1_r3_run_a/evidence/external_dependencies.json`):

| Registros | Ids distintos | Ids duplicados | Registros involucrados | Registros extra | Tamaños de grupo |
|---|---|---|---|---|---|
| 4 839 | 4 808 | 5 | 36 | 31 | 5, 14, 5, 7, 5 |

Coincide con R3 (5 ids, 31 registros extra). Con el detector de R2/R2.1 esto daba 0.

## 6. Implementación de `SourceArtifact.sha256` obligatorio

- **Producción:** `build_evidence_artifacts` construye con `repo_root = indexes["repository"]["root"]`, la raíz absoluta resuelta por SCAN (V4.3). Vale tanto para `full` como para `analyze`, porque ambos comparten `export_artifacts`.
- **Cómputo:** SHA-256 del contenido real (`hashlib.file_digest`). No usa mtime ni metadata del filesystem.
- **Garantías de no nulidad:** en ningún camino queda `None` o vacío:
  - La entidad rechaza cualquier valor que no sea hex de 64 caracteres.
  - El builder lanza un error si falta la raíz o si un archivo no se puede leer.
  - `validate_evidence` vuelve a comprobarlo antes de persistir.
- **Herramienta:** `tools/v5_1_r2_real_ist_regression.py` fue revisada y sigue siendo compatible sin cambios (pasa `repo_root` explícito y usa `detect_collisions`, que ya tiene la nueva semántica).

## 7. Medición real del coste SHA-256

Los tiempos del Evidence Core salen del log INFO de cada corrida. El hashing aislado se midió con `_hash_file` de producción sobre `files.json` de la corrida A.

| Medida | Valor |
|---|---|
| SourceArtifacts | 15 138 (332 247 881 B de contenido) |
| Hashing aislado, caché caliente (3 pasadas) | 16.75 s / 12.63 s / 12.64 s (≈25 MB/s); digest agregado idéntico en las 3 |
| Build del Evidence Core desde `index/` con hash / con hash stub | 19.9 s y 18.5 s / 6.2 s ⇒ el hashing ≈ 12–14 s en caliente |
| Corrida A (caché fría de los fuentes) | build 122.3 s (≈116 s de hashing), validate 0.8 s, persist 11.3 s ⇒ Evidence Core 134.4 s de 1 991 s totales (6.8 %) |
| Corrida B (caché caliente) | build 24.2 s, validate 0.9 s, persist 11.5 s ⇒ 36.6 s de 1 788 s (2.0 %) |
| Tamaño de `evidence/` (24 particiones) | 977 957 317 B (932.6 MB); con manifest, 977 959 942 B |
| Frente a R3 | 976 914 924 B ⇒ +1 042 393 B (+0.11 %): `sha256` pasa de `null` a un digest y se añade `duplicate_ordinal` en XDP |

El coste dominante es la I/O en frío, no el cómputo. No se aplicó ninguna optimización: el hashing en paralelo sería especulativo y el prompt prohíbe optimizar sin necesidad demostrada. Tampoco hay cache incremental (V5.3).

## 8. Nueva semántica de fallo de Evidence Core

```text
Evidence Core FAIL (build | validate | persist)
  → excepción propagada desde export_artifacts
  → full:    StageId.EXPORT = FAILED (category/message en RUN_SUMMARY.json)
             → _compute_status ⇒ RunStatus.FAILED → exit 4 → resumen por LOG.error
  → analyze: excepción no capturada (contrato existente de analyze) → exit ≠ 0
```

- No se añadió ningún stage ni estado nuevo: se reutiliza el contrato existente de EXPORT (`export_ok` es condición de éxito).
- `index/` y `documentation/`, escritos antes del fallo, se conservan para diagnóstico. La ejecución no es válida como ejecución V5.
- **Manifest obsoleto:** `EVIDENCE_MANIFEST.json` de una corrida previa se elimina antes de construir. El manifest se escribe al final, así que su presencia equivale a que esa corrida completó la evidencia. Un rerun fallido sobre el mismo `--output` no puede quedar respaldado por un manifest anterior.
- **Éxito:** `RUN_SUMMARY.json` es igual al de R3 (mismas 11 claves, 13 stages, sin `evidence` en `output_locations`), así que se preserva V5.0 D-01.

## 9. Resultado del test controlado de FAILURE

Parche en proceso (`unittest.mock.patch`) a través de `legacy_documenter.main.main`, la CLI real, sobre `tests/fixtures/v4_2_r7_full_sample`. Script en el scratchpad de la sesión; el producto no se modificó.

| Punto inyectado | `full`: exit / status | EXPORT.error | `index/` conservado | Manifest | `analyze` |
|---|---|---|---|---|---|
| `NormalizedEvidenceBuilder.build` | 4 / FAILED | `RuntimeError: injected build failure` | sí | ausente | lanza `RuntimeError` |
| `validate_evidence` | 4 / FAILED | `AssertionError: I-1: injected collision` | sí | ausente | lanza `AssertionError` |
| `write_evidence` | 4 / FAILED | `OSError: injected disk failure` | sí | ausente | lanza `OSError` |
| Sin parche (restaurado) | 0 / SUCCESS | — | sí | presente | — |

`git status` de `legacy_documenter/` quedó sin cambios respecto de antes de la prueba: no quedan hooks. Los mismos casos están cubiertos de forma permanente por los tests de §3.

## 10. Persistencia de Evidence

Corridas A y B:

- 24 particiones más el manifest; los nombres de archivo coinciden con las claves del manifest.
- Los conteos del manifest coinciden con los registros físicos en las 24 particiones (0 discrepancias).
- El `partition_sha256` del manifest coincide con el SHA-256 del archivo en las 24 (0 discrepancias).
- `physical_format=json_compact`, `evidence_schema_version=1.0`.
- La relectura completa de todas las particiones funciona. El formato R2.1 no cambió.

## 11. Determinismo

- `evidence/` A frente a B: 25 archivos, 0 diferencias byte a byte (incluido el manifest).
- Árbol completo A frente a B: 958 archivos, 1 diferencia: `index/repository.json`, solo en `duration_seconds` (metadata operacional ya excluida por D-01).
- El SHA-256 de 202 archivos muestreados se recalculó contra los fuentes reales: 0 discrepancias.
- Tests de determinismo de XDP y `sha256`: §3.

## 12. Compatibilidad V4.3

Corrida B frente a la corrida R3 `v5_1_r3_run_a`:

- `index/`: 22/22 archivos, 21 byte-idénticos; `repository.json` difiere solo en `duration_seconds`.
- `documentation/`: 876/876 archivos, 0 diferencias.
- `RUN_SUMMARY.json`: idéntico.
- Particiones de `evidence/` que cambian frente a R3: solo `external_dependencies` (nuevos ids y `duplicate_ordinal`) y `source_artifacts` (`sha256`). Las otras 22 son byte-idénticas.
- **Instantiation:**
  - 40 278 registros, igual a la suma de los `instantiations[]` embebidos en `calls`.
  - 0 registros con campo `id`.
  - Partición intacta.
- `index/` sigue siendo producido por `JSONExporter`; no se convirtió en canonical evidence.

## 13. Runtime independence

Análisis AST de los 184 archivos de `legacy_documenter/`: 0 imports de `tools`, `tests`, `docs` o `prompts`. `evidence/` importa, fuera de su propio paquete, solo stdlib y `legacy_documenter.utils.atomic_write`. `PROJECT_STATE` solo aparece en el docstring de `evidence/__init__.py`, que declara que no lo lee. Los imports nuevos de `pipeline_stages.py` son `legacy_documenter.evidence.invariants` y `.persistence`. La dirección `tools → runtime` se mantiene.

## 14. AI independence

En `evidence/*.py` no hay ocurrencias de `openai`, `anthropic`, `ollama`, `claude`, `copilot`, `gemini`, `legacy_documenter.llm` ni `ai_context` (búsqueda de texto y `AiIndependenceTests`). Las corridas A y B informan `AI requested/invoked: False`. El gate de validación es puramente determinista.

## 15. Technology Adapter boundary

- La lógica específica de VB.NET (`assembly_references`, `include`, `hint_path`) vive solo en `builder.py`, que es el adapter de referencia.
- Lo añadido al núcleo es genérico: `duplicate_ordinal`, `is_sha256_hex`, `detect_duplicate_ids` y el gate I-1.
- `TechnologyAdapterBoundaryTests` pasa: el núcleo no importa extractors ni analysis, y `adapter_id` sigue siendo un parámetro.

## 16. Resultados reales sobre IST

- **Target:** `C:\Users\cgalianj\source\IST_40\Operacional` (solo lectura).
- **Corrida A:** `python main.py full <target> --output C:\PruebasLegacyMapper\Resultados\v5_1_r3_1_run_a --verbose`. SUCCESS, exit 0, 1 991 s.
- **Corrida B:** mismo comando con salida `v5_1_r3_1_run_b`. SUCCESS, exit 0, 1 788 s.

Ambas se hicieron en carpetas nuevas, en secuencia y sin la suite corriendo en paralelo.

| Entidad | Registros | Ids distintos | Colisiones |
|---|---|---|---|
| SourceArtifact | 15 138 | 15 138 | 0 |
| Solution | 113 | 113 | 0 |
| Project | 259 | 259 | 0 |
| Component | 9 859 | 9 859 | 0 |
| EntryPoint | 12 662 | 12 662 | 0 |
| EventBinding | 12 662 | 12 662 | 0 |
| Call / CAL | 230 356 | 230 356 | 0 |
| DataOperation (DAO) | 20 082 | 20 082 | 0 |
| DataObject (SP+SQL) | 5 392 | 5 392 | 0 |
| FunctionalPath | 170 020 | 170 020 | 0 |
| FunctionalFlow | 12 642 | 12 642 | 0 |
| ExternalDependency / XDP | 4 839 | 4 839 | 0 |
| UnresolvedBoundary | 162 914 | 162 914 | 0 |

En los 13 tipos se cumple records == unique canonical IDs, en A y en B. El gate `validate_evidence` se ejecutó en producción en ambas corridas; si hubiera fallado, las corridas habrían sido FAILED.

**XDP (§15.2):**

- Total ExternalDependency: 4 839 (4 838 `assembly` y 1 `database_connection`).
- Ids XDP únicos: 4 839.
- Ids duplicados: 0; registros involucrados: 0.
- Registros con `duplicate_ordinal > 0`: 31, exactamente los 31 extra de R3.
- Invariant check: PASS.

`XDP duplicate canonical IDs = 0`.

**SHA-256 (§15.3):**

- SourceArtifacts total: 15 138.
- Con SHA-256 válido: 15 138.
- Sin SHA-256: **0** (0 `None`, 0 vacíos, 0 con formato inválido).
- Reproducibilidad: A = B (particiones byte-idénticas) y muestra de 202 recalculada sin discrepancias.

El resto de cifras (`instantiations` 40 278, `data_parameters` 74 633, `functional_dependencies` 335 698, etc.) no cambia frente a R0/R2.1/R3.

## 17. Resultado de suite completa

`python -m unittest discover -s tests`:

| Corrida | Tests | Passed | Failures | Errors | Skipped |
|---|---|---|---|---|---|
| 1 (antes del ajuste de inventario) | 2 247 | 2 114 | 1 | 0 | 132 |
| 2 (final) | 2 247 | 2 115 | 0 | 0 | 132 |
| 3 (estabilidad) | 2 247 | 2 115 | 0 | 0 | 132 |

- La única falla de la corrida 1 fue `test_on_disk_inventory_matches_fresh_build_if_present`: la reclasificación heurística de `builder.py` se corrigió en §3.
- 2 247 tests = 2 228 (R3) + 19 nuevos.
- Los 132 skips son los `expected_fresh_clone_skips` de `PROJECT_STATE.json`, igual que en R3.

## 18. Deuda técnica restante dentro del alcance V5.1

1. **D-4 (sin cambios):** `EvidenceReference` no se emite en la evidencia productiva. La trazabilidad es por claves foráneas, con 0 referencias colgantes.
2. **D-5 (sin cambios):** no hay lector `evidence/ → entidades`, y `index/` no se reconstruye desde `evidence/`.
3. **Causa aguas arriba de D-1:** `VBProjExtractor` emite referencias con `Include` vacío (5 proyectos de IST, en carpetas `Backup`/`_back`). Se preservan como ocurrencias distintas mediante el ordinal. No se investigó si deberían filtrarse, porque eso cambiaría `index/projects.json` (V4.3).
4. **Coste del hashing en frío:** ≈116 s por corrida sobre IST (6.8 % del total). Aceptado por D-2. Cualquier reducción corresponde a V5.3 o a una medición dedicada.
5. **Restos de un fallo:** si `write_evidence` falla a mitad de escritura, pueden quedar particiones parciales o de una corrida anterior sin manifest. La regla vigente es "sin manifest ⇒ evidencia inválida", y el run queda FAILED. No se añadió limpieza de particiones para no introducir borrados en el output.
6. **Nueva condición de fallo:** I-1 se aplica ahora también a los ids legacy preservados (EP/EVB/FLOW/DAO/SP/SQL/PATH). Si otro repositorio produjera ids legacy repetidos, aunque sean idénticos, la ejecución V5 fallaría en lugar de persistir. En IST hay 0.
7. **Discrepancia documental heredada:** el producto genera 24 particiones, no las 23 que menciona R2.1 (ya señalado en R3).

## 19. Evidencia para decidir si R3 puede pasar a READY_FOR_R4

| Bloqueo R3 | Estado | Evidencia |
|---|---|---|
| D-1 unicidad `XDP-` | Corregido | 4 839/4 839 en A y B; el detector ahora capta los 5/36/31 de R3 (§5); tests §3 |
| Detector I-1 | Corregido (genérico) | Duplicados idénticos y distintos fallan; gate productivo sobre 13 tipos |
| D-2 `sha256` | Implementado y obligatorio | 15 138/15 138, 0 `None`, 0 vacíos, reproducible; coste medido (§7) |
| D-3 semántica de fallo | Implementado | Exit 4 / FAILED / error en `RUN_SUMMARY.json`; `analyze` aborta; sin manifest obsoleto (§8–9) |
| No regresión | Verificado | `index/` 21/22 (+ `duration_seconds`), `documentation/` 0 diffs, `RUN_SUMMARY` idéntico, determinismo byte a byte, suite 0/0 |

Queda pendiente la revisión externa y, si corresponde, revalidar R3 sobre estas corridas (`v5_1_r3_1_run_a` / `v5_1_r3_1_run_b`). D-4 y D-5 siguen abiertas como decisiones menores, igual que en R3.

V5_1_R3_1_READY_FOR_R3_REVALIDATION
