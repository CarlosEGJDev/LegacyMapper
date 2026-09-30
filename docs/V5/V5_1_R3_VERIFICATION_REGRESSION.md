# V5.1 R3 — Verification & Regression

## 1. Estado final

`V5_1_R3_BLOCKED`

Motivo: un defecto real de unicidad de identidad (D-1, `XDP-`) contradice el contrato R1 (I-1 / "unicidad"). Los demás puntos pasan; las decisiones D-2…D-5 requieren resolución del Technical Lead. No se recomienda R4 hasta resolver D-1.

## 2. Alcance ejecutado

Solo verificación. Sin cambios de código, tests, tools, roadmap ni `PROJECT_STATE.json`; sin commits/push. `git status` idéntico antes y después de la ronda. Salidas generadas fuera del repo, en `C:\PruebasLegacyMapper\Resultados\` (`v5_1_r3_run_a`, `v5_1_r3_run_b`). Target: `C:\Users\cgalianj\source\IST_40\Operacional` (solo lectura). Verificaciones ad hoc (scripts de solo lectura) se ejecutaron desde el scratchpad de sesión, no desde el repo. Documentos leídos: R0, R1, R2, R2.1 de V5.1.

## 3. Comandos utilizados

```text
python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output C:\PruebasLegacyMapper\Resultados\v5_1_r3_run_a --verbose   (exit 0, 1485 s)
python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output C:\PruebasLegacyMapper\Resultados\v5_1_r3_run_b --verbose   (exit 0, 1788 s)
python -m unittest discover -s tests   (x2)
```

`analyze` no se ejecutó: comparte `export_artifacts` con `full` (R2.1 §5, verificado por lectura de `pipeline_stages.py`) y el prompt lo pide solo "cuando corresponda". Las duraciones de las corridas incluyen contención con la suite ejecutándose en paralelo. Además: análisis AST del grafo de imports, lectura de `evidence/*.json` de la corrida A, comparación SHA-256 archivo a archivo A vs B / R0 / R2.1, y un sondeo del modo de fallo por monkeypatch en proceso (sin tocar código).

## 4. Resultados y métricas

Ambas corridas: `LegacyMapper full run: SUCCESS`, 13 stages (AI_INTERPRETATION/PROPOSAL_GENERATION `NOT_RUN`), sin proveedor de IA.

| Entidad | Esperado | Medido (A = B) |
|---|---|---|
| source_artifacts | 15 138 | 15 138 |
| solutions | 113 | 113 |
| projects | 259 | 259 |
| components | 9 859 | 9 859 |
| external_dependencies | 4 839 | 4 839 (**4 808 ids distintos**, ver D-1) |
| data_objects | 5 392 | 5 392 (5 389 SP + 3 SQL) |
| call_identities | 230 356 | 230 356 |
| unresolved_boundaries | 162 914 | 162 914 |
| instantiations | 40 278 | 40 278 |
| entry_points / event_bindings / flows / paths | — | 12 662 / 12 662 / 12 642 / 170 020 |
| data_access / data_parameters / functional_dependencies | — | 20 082 / 74 633 / 335 698 |

Ninguna cifra cambió respecto a R0/R2.1. Tamaño de `evidence/` (suma de las 24 particiones): 976 914 924 B (931.6 MB), idéntico en A y B. R2.1 informó 977 848 590 B (932.5 MB); la diferencia (0.1 %) no se investigó — el contenido de `evidence/` de R2.1 y de R3 es byte-idéntico (§10), por lo que se debe a cómo se sumó (p. ej. archivos incluidos), no a los datos.

## 5. Matriz de verificación

| Área | Verificación | Resultado | Evidencia |
|---|---|---|---|
| Contract | Entidades/particiones R1 presentes; `schema_version` 1.0 | PASS | Manifest `evidence_schema_version=1.0`, 24 particiones. |
| IDs | Unicidad, prefijos, sin `PAR/CALL/UNRES` como `id` | **BLOCKED** | SRC/SOL/PRJ/CMP/SP/SQL/CAL/UNB/EP/EVB/FLOW/DAO/PATH: 0 duplicados. `XDP-`: 31 registros con id repetido (D-1). 0 ids con prefijo `PAR/CALL/UNRES`. |
| CAL | Ordinal por tupla base, 230 356, sin colisiones | PASS | 230 356 ids únicos; 880 grupos duplicados / 2 263 registros / 1 383 extra (coincide con R0/R1); ordinales secuenciales por grupo en el 100 %; `legacy_ref` (`CALL-`) presente en todos. Fórmula en `builder.py:336-364` usa `DuplicateOrdinalAssigner` sobre la tupla, no la posición global. |
| UnresolvedBoundary | Identidad estable, siempre `unresolved` | PASS | 162 914 ids `UNB-` únicos; `state=unresolved` en el 100 %; `reason_code=unresolved_boundary`; mismo orden que `flow_unresolved.json`; `path_id` único; `candidates=[]` (nunca promovido). Identidad derivada de `(path_id, terminal_type, terminal_target)`, no de orden de procesamiento. |
| References | Trazabilidad hacia el origen | PASS con nota (D-4) | 0 referencias colgantes `source_artifact`/`source_ref` en CAL, Instantiation y Component. La unión `EvidenceReference` existe y está testeada, pero el builder no la emite ni persiste (D-4). |
| Cardinalities | Coherencia R1/R2 | PASS | Path→DAO: 4 612 paths / 1 157 DAO distintas / máx. 254 paths por DAO, 0 targets desconocidos. Path→SP: 1 121 paths / 338 SP / máx. 63. DAO→SP/SQL: 9 790 aristas / 5 389 objetos distintos / máx. 17 ops por objeto, 0 colgantes. DAO→Parameter: 9 774 ops con parámetros, máx. 128 por op, 74 633 aristas. |
| Instantiation | Partición propia, sin pérdida, sin id | PASS | `instantiations.json` 40 278 = suma de `calls.json[].instantiations`; sin campo `id`; `position` 0-based secuencial en cada uno de 2 776 archivos; `extensions` idéntico a los registros de `calls.json` (comparación exacta); 0 `source_artifact` colgantes. |
| Persistence | Manifest ↔ particiones ↔ registros | PASS | 24 particiones + manifest; nombres de archivo == claves del manifest; conteos del manifest == registros físicos en las 24; SHA-256 del manifest == SHA-256 del archivo en las 24; JSON compacto. Ver nota de 23 vs 24 particiones (§8). |
| Determinism | Dos corridas independientes | PASS | `evidence/`: 25 archivos, 0 diferencias (byte-idéntico). Árbol completo: 958 archivos, 1 diferencia (`index/repository.json`, `duration_seconds`). |
| Product integration | `main.py full` genera `evidence/` | PASS | Ver §6. |
| tools boundary | Dirección `tools → runtime`, sin duplicación | PASS | Ver §7. |
| Runtime independence | Sin imports a tools/tests/docs/prompts | PASS | AST sobre 184 archivos de `legacy_documenter/`: 0 imports. `evidence/` importa solo stdlib + `legacy_documenter.utils.atomic_write`. |
| AI independence | Sin proveedor/SDK/prompt | PASS | grep de `ollama/openai/anthropic/copilot/llm/prompt` en `evidence/`: solo la palabra "prompts" en un docstring de `__init__.py` que declara lo que NO lee. Corridas con `AI requested/invoked: False`. |
| Adapter boundary | Core sin tecnología | PASS | `ADAPTER_ID` no es constante de módulo; `adapter_id` es parámetro (`entities.py`). Tecnología solo en `builder.py` (adapter de referencia) y en claves `extensions[<adapter_id>]`. `projection.py` importa `REFERENCE_ADAPTER_ID` desde `builder.py` (default del constructor, no lógica de tecnología). |
| Compatibility | `index/`, `documentation/`, `RUN_SUMMARY` | PASS | Ver §8. |
| Real IST | Cifras a escala | PASS | Ver §4. |
| Full regression | 0 failures / 0 errors | PASS | 2 corridas: 2 228 tests, 0 F, 0 E, 132 skips. |

## 6. Evidencia de ejecución productiva

Cadena verificada por lectura de `legacy_documenter/cli/pipeline_stages.py` (`export_artifacts` → `build_evidence_artifacts` → `NormalizedEvidenceBuilder().build(indexes)` → `write_evidence(evidence, output)`) y por ejecución: las dos corridas de `python main.py full` sobre IST real produjeron `evidence/` con 24 particiones + `EVIDENCE_MANIFEST.json` sin ningún paso manual ni script de `tools/`. `repo_root` se omite en producción (ver D-2). `RUN_SUMMARY.json` no lista `evidence/` en `output_locations` ni tiene stage propio (decisión deliberada de R2.1 para preservar D-01; es relevante para D-3).

## 7. Evidencia de separación `tools → runtime`

- `tools/` contiene scripts de build/inventario/regresión (`v4_*`, `v5_1_r2_real_ist_regression.py`, `manual_verify_full_pipeline.py`, `v4_1_r0/`). El único que toca el Evidence Core (`v5_1_r2_real_ist_regression.py`) hace `from legacy_documenter.evidence... import` → dirección válida.
- Búsqueda de `class NormalizedEvidenceBuilder|SourceArtifact|UnresolvedBoundary|CallIdentity`, `def write_evidence`, `def build_call*` en `tools/`: 0 coincidencias. Sin extractores/resolvers/persistencia duplicados. Una única implementación de Evidence Core, en `legacy_documenter/evidence/`.
- Ningún módulo de `legacy_documenter/` importa `tools`/`tests`; ninguno referencia `PROJECT_STATE.json`, rutas `C:\...` de desarrollo ni `prompts/`. Las menciones a `docs/` en `legacy_documenter/` son solo comentarios/docstrings (no lecturas).
- `tools/` no fue modificado.

## 8. Regresión V4.3 y observaciones de contrato

- `index/`: 22 archivos por corrida; 21/22 byte-idénticos frente al baseline R0 (`v5_1_new_target_rebaseline`) y frente a la corrida R2.1; el único distinto es `repository.json`, solo en `duration_seconds` (112.73 s vs 370.07 s frente a R0). Sigue siendo exclusivamente metadata operacional (las demás claves son iguales; A vs B también difieren solo en `duration_seconds`).
- `documentation/`: 876 archivos, 0 diferencias frente a R0.
- `RUN_SUMMARY.json`: mismas 11 claves y 13 stages que V4.3; sin diferencias entre A y B.
- Round-trip: `LegacyIndexProjector().project(NormalizedEvidenceBuilder().build(index_A))` reproduce los 22 índices exactamente (I-9); una segunda construcción en proceso es idéntica (I-10).
- Nota de conteo: R2.1 y el prompt hablan de "23 particiones"; el producto genera **24** (9 entidades nuevas + `scan_summary` + 14 passthrough) más el manifest. Discrepancia documental, no funcional.

## 9. Regresión completa

| Corrida | Tests | Failures | Errors | Skips | Duración |
|---|---|---|---|---|---|
| 1 | 2 228 | 0 | 0 | 132 | 223.1 s |
| 2 | 2 228 | 0 | 0 | 132 | 212.5 s |

Estable entre corridas (132 skips = `expected_fresh_clone_skips` de `PROJECT_STATE.json`). El módulo de evidencia tiene 59 tests. El riesgo conocido `test_deterministic_run_then_ai_enabled_rerun_same_output` no reapareció en las 2 corridas (2 de 2 sin fallos). No se modificó ningún test.

## 10. Determinismo

Corridas A y B (scan completo desde cero, procesos independientes): 25 archivos de `evidence/` con SHA-256 idénticos, incluido `EVIDENCE_MANIFEST.json` (mismos conteos y hashes de partición); idénticos también a la corrida productiva de R2.1 (`v5_1_r2_1_full_pipeline_check`), es decir estable entre rondas. Único diferencial de todo el árbol: `index/repository.json.duration_seconds` (metadata operacional, no determinista por naturaleza, ya excluida por V5.0 D-01).

## 11. Deuda R2.1 revisada

| # | Punto | Contradice V5.1 | Deuda aceptable | Bloquea R4 | Recomendación |
|---|---|---|---|---|---|
| 14 | `index/` no se reconstruye desde `evidence/` | No: V5.0 D-01/D-04 lo exige como proyección *posible*; se demostró (round-trip exacto). | Sí, para V5.1. | No. | Nota factual (D-5): hoy no existe lector `evidence/ → entidades` (no hay `from_dict`/`read_evidence`); `LegacyIndexProjector` solo opera sobre el `NormalizedEvidence` en memoria. Convertirlo en requisito explícito de una versión posterior (integración/V5.3). |
| 15 | `SourceArtifact.sha256 = None` en producción | **Posible: ver D-2.** | Requiere decisión. | Depende de D-2. | Ver D-2. |
| 16 | Evidence Core best-effort | Ver D-3. | Requiere decisión. | Depende de D-3. | Ver D-3. |

## 12. Defectos y decisiones abiertas

**D-1 (defecto, BLOCKED) — `XDP-` no es único.** `external_dependencies.json` tiene 4 839 registros pero 4 808 ids distintos: 5 ids repetidos con 31 registros extra, todos `dependency_kind=assembly`, `name=""`, `extensions.include=""`, en 5 proyectos (repeticiones de 5, 5, 7, 14 y 5). Causa: `XDP-` se deriva de `("assembly", name, project_path)` sin ordinal, y esos proyectos tienen varias referencias con `Include` vacío. R2/R2.1 informaron "0/4 839 colisiones" porque `detect_collisions` no cuenta como colisión el mismo id con contenido idéntico; es una brecha del detector, no un resultado de unicidad. Contradice "unicidad" (R1 §identidad, I-1: "0 colisiones para … XDP"). Reproducción: cargar `evidence/external_dependencies.json` de cualquiera de las corridas y contar `Counter(r["id"])`. Además, la causa raíz aguas arriba (referencias con `Include` vacío en `projects.json`) merece revisión, pero no es objeto de R3. No corregido.

**D-2 (OPEN_DECISION) — `sha256` nulo en el 100 % de los `SourceArtifact` (0 de 15 138).** R1 §SourceArtifact lista `sha256` entre los *campos mínimos* y como "primario nuevo (medido, no derivado)". R2.1 justifica `None` como "fiel al contrato R1 (None cuando no se solicitó)", pero esa frase no aparece en R1: R1 solo señala el I/O adicional como riesgo. La ausencia no rompe ninguna invariante I-1…I-11 ni el round-trip, y la alternativa ya soportada existe (`NormalizedEvidenceBuilder(repo_root=...)`, usada por la tool; costo medido 81–153 s sobre 15 138 archivos, frente a ~25 min por corrida completa medidos aquí, ~5–10 % adicional). Decisión pendiente: ¿es opcional en V5.1 (enmendar R1) o debe calcularse en producción (p. ej. opt-in por flag)?

**D-3 (OPEN_DECISION) — Fallo del Evidence Core invisible para el contrato de ejecución.** Verificado con un fallo simulado (monkeypatch en proceso de `NormalizedEvidenceBuilder.build`): `build_evidence_artifacts` retorna normalmente, no se crea `evidence/`, y solo queda una línea `LOG.warning` a stderr (visible por defecto porque `main.py` fija nivel WARNING). No hay registro en `RUN_SUMMARY.json`, ni stage, ni cambio de exit code (0/SUCCESS), y `output_locations` nunca lista `evidence/` ni siquiera en éxito. Un run automatizado puede terminar en `SUCCESS` habiendo perdido toda la evidencia V5, y un consumidor V5 no puede distinguirlo de "no se pidió". Esto no contradice V4.3 (es su objetivo), pero sí es débil frente al objetivo V5 de evidencia canónica. Decisión pendiente: mantener best-effort con señal explícita (p. ej. sidecar de observabilidad ya previsto en V5.0 D-12/DR-R2-03) o elevar a fallo parcial.

**D-4 (OPEN_DECISION, menor) — `EvidenceReference` no se emite en la evidencia real.** La unión de 4 tipos (`reference.py`) y `resolve_against` existen y están cubiertos por tests unitarios, pero `builder.py`/`persistence.py` no las usan: la trazabilidad real es por claves foráneas string (`source_artifact`, `source_ref`, 0 colgantes a escala) y por los registros legacy `evidence` preservados en `extensions`/passthrough. Trazabilidad suficiente hoy; falta decidir si V5.1 exige la emisión de `EvidenceReference` en producción o queda para una ronda posterior.

**D-5 (observación) — Sin lector de evidencia.** `evidence/` es solo-escritura desde el runtime (ver §11, punto 14). Documentar como requisito de la versión que haga a `evidence/` fuente canónica de `index/`.

Sin otros defectos. `PAR-` con 5 ids duplicados en `data_parameters.json` es la condición legacy ya aceptada por R0/R1 (solo `legacy_ref`), no defecto nuevo.

## 13. Conclusión R3

La implementación R2.1 funciona desde el producto real, es determinista byte a byte, preserva la compatibilidad V4.3 (salvo la metadata operacional ya excluida), respeta la dirección de dependencias y mantiene una única fuente de verdad, con 2 228 tests estables. El bloqueo es exclusivamente D-1 (unicidad de `XDP-`), encubierto por la semántica del detector I-1. D-2 y D-3 requieren decisión explícita del Technical Lead antes de R4; D-4 y D-5 son de bajo riesgo. Esta ronda no autoriza correcciones: se espera autorización explícita para una ronda de corrección.

V5_1_R3_BLOCKED
