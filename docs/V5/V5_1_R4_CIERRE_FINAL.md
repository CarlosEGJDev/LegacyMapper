# V5.1 R4 — Cierre final de Normalized Evidence Core

## 1. Estado final

V5_1_CLOSED

V5.1 — Normalized Evidence Core cumple su alcance, contrato y arquitectura. Los cuatro defectos/decisiones que bloquearon R3 (D-1, D-2, D-3, D-4) están cerrados con código real, gate de producción real, y verificación sobre IST real y determinista. D-5 queda como deuda aceptable, explícitamente fuera de alcance de V5.1. No queda ningún defecto B (que contradiga el alcance/arquitectura de V5.1).

## 2. Qué se validó

`git status` confirma que el código no cambió desde `V5_1_R3_2_EVIDENCE_REFERENCE_TRACEABILITY.md` (mismo árbol de trabajo exacto: los mismos archivos modificados/nuevos, sin diferencias). Conforme al §9 del prompt, no se repitieron corridas reales de ~30 minutos sin necesidad; en su lugar se releyeron y recontaron de forma independiente las dos corridas reales de R3.2 (`v5_1_r3_2_run_a`/`v5_1_r3_2_run_b`) directamente desde sus JSON en disco (24/24 particiones, 0 discrepancias de conteo/SHA-256 frente al manifest, 0 diferencias entre A y B), sin reutilizar el código bajo prueba. Se releyó el código real de `legacy_documenter/evidence/*.py` y `pipeline_stages.py` para confirmar que las afirmaciones de R3.2 siguen siendo ciertas contra el código actual (no solo contra su documento). Se ejecutó la suite completa de nuevo en esta ronda.

## 3. Estado de D-1, D-2, D-3 y D-4

Sin cambios de código desde R3.2; se confirma que las cuatro siguen cerradas, releyendo el código real:

- **D-1 (XDP):** `builder.py::_build_external_dependencies` sigue usando `duplicate_ordinal` vía `DuplicateOrdinalAssigner`; el detector genérico (`identity.py::detect_collisions`) sigue tratando cualquier id repetido como colisión, incluso byte-idéntico. Sobre `v5_1_r3_2_run_a`: 4 839 `ExternalDependency`, 4 839 ids únicos, 0 colisiones (releído directamente).
- **D-2 (`sha256`):** `SourceArtifact.sha256: str` sigue sin default, validado en `__post_init__` (`is_sha256_hex`); `build_evidence_artifacts` sigue construyendo con `repo_root=indexes["repository"]["root"]` para `full` y `analyze` (comparten `export_artifacts`). Sobre `v5_1_r3_2_run_a`: 15 138/15 138 con SHA-256 válido, 0 nulos.
- **D-3 (fallo del Evidence Core):** `build_evidence_artifacts` sigue sin `try/except` que degrade a warning; el manifest previo se sigue borrando antes de reconstruir (`stale_manifest.unlink(missing_ok=True)`). Sin cambios desde el sondeo controlado de R3.1/R3.2 (exit 4/FAILED en las tres fases: build/validate/persist).
- **D-4 (provenance/EvidenceReference):** `entities.py` sigue emitiendo `provenance` en toda entidad canónica salvo `SourceArtifact`; `invariants.py::validate_evidence` sigue llamando a `validate_provenance` (I-4/I-5) antes de retornar — confirmado leyendo la línea real (`invariants.py:181`), no solo el docstring. Sobre `v5_1_r3_2_run_a`: 454 010 entidades con `provenance`, 0 vacías; releído manualmente el recorrido de las referencias reales contra `SourceArtifact`/`Project`/`FunctionalPath` de esa misma corrida: 0 rotas (recuento independiente de esta ronda, sin invocar `resolve_against`).

Ninguna de las cuatro decisiones se modificó en esta ronda.

## 4. Estado de D-5

D-5 sigue siendo deuda conocida, sin resolver, no bloqueante: `grep` sobre `legacy_documenter/evidence/*.py` confirma 0 coincidencias de `read_evidence`/`from_dict` — no existe ningún lector `evidence/ → entidades normalizadas`. `LegacyIndexProjector.project()` sigue operando únicamente sobre un `NormalizedEvidence` ya en memoria (`projection.py:37`), nunca sobre `evidence/*.json` releído desde disco. No se implementó en esta ronda, conforme al mandato explícito del prompt. Queda registrada para resolverse en una versión futura, cuando `evidence/` deba servir como fuente de integración/cache/reutilización directa desde disco (candidata natural: V5.3 o una ronda de integración dedicada).

## 5. Arquitectura final V5.1

```text
Legacy Source
    ↓ (extractors/*.py, analysis/*.py -- V4.3, sin cambios)
Technology Adapter (builder.py: NormalizedEvidenceBuilder, REFERENCE_ADAPTER_ID="vbnet-webforms-oracle")
    ↓
Normalized Evidence Core (entities.py/identity.py/reference.py/invariants.py -- agnóstico de tecnología)
    ↓
Evidence Persistence (persistence.py::write_evidence -> evidence/*.json + EVIDENCE_MANIFEST.json)
    ↓
Projections (projection.py::LegacyIndexProjector -> index/ V4.3-compatible; documentation/ deriva de index/, sin cambios)
```

Confirmado por lectura de código, no por convención:

- `evidence/` es la evidencia normalizada real, generada por `build_evidence_artifacts` dentro de `EXPORT`, con su propio gate de validación (`validate_evidence`) antes de persistir.
- `index/` sigue siendo exclusivamente compatibilidad legacy: `JSONExporter` lo produce directamente desde `indexes` (no desde `evidence/`), y `LegacyIndexProjector` (el camino alternativo que demuestra que la proyección es posible, I-9) tampoco lee `evidence/` de disco — coherente con D-5.
- `documentation/` deriva de `indexes`/`index/`, nunca se trató como evidencia canónica.
- IA no participa en la construcción del Evidence Core: `AiIndependenceTests` (91 tests del módulo, incluida esta clase) siguen verdes; `build_evidence_artifacts` se ejecuta incondicionalmente dentro de `EXPORT`, antes de que `AI_INTERPRETATION` (opt-in) se evalúe.

## 6. Evidence Core

Las entidades acordadas en R1/R2 existen y persisten: `SourceArtifact`, `Solution`, `Project` (dict), `Component`, `ExternalDependency`, `DataObject`, `CallIdentity`, `Instantiation`, `UnresolvedBoundary`, `ScanSummary`, más 14 particiones passthrough. Identidades canónicas estables y sin colisiones en los 13 tipos que las requieren (`SourceArtifact` a `UnresolvedBoundary`, tabla completa en R3.1/R3/revalidación, no repetida aquí por no haber cambiado). Relaciones relevantes válidas y sin referencias colgantes, verificado a escala completa de IST en R3/revalidación (`Component.source_ref`, `CallIdentity.source_artifact`, `Instantiation.source_artifact`, `DataOperation→DataObject`, `DataOperation→DataParameter`, `EntryPoint→FunctionalFlow`) y, en R3.2, las 454 010 entidades con `provenance` resuelto. Determinismo confirmado de nuevo en esta ronda por recuento directo (`evidence/` de `v5_1_r3_2_run_a` y `_run_b`: 25 archivos, 0 diferencias).

## 7. Invariantes

| Invariante | Estado final |
|---|---|
| I-1 (unicidad de id canónico) | Cumplida. Detector genérico corregido en R3.1 (byte-idénticos también cuentan); 13 tipos, 0 colisiones en IST real. |
| I-2 (`PAR`/`CALL`/`UNRES` nunca como id) | Cumplida, sin cambios desde R2. |
| I-3 (EntryPoint→FunctionalFlow 0..1) | Cumplida, verificada a escala real en R3/revalidación. |
| I-4 (trazabilidad vía `provenance`) | **Cumplida desde R3.2** — ya no pendiente. Se ejecuta realmente en producción, 454 010 entidades verificadas, 0 vacías. |
| I-5 (referencia rota nunca pasa en silencio) | **Cumplida desde R3.2** — ya no pendiente. 686 010 referencias verificadas por corrida, 0 rotas; fallo controlado demostrado (`run_full_pipeline` con una referencia rota inyectada → FAILED real). |
| I-6 (proyección no inventa relaciones) | Cumplida (tests verdes sobre fixture, sin regresión). |
| I-7 (no promoción sin `promotion_basis`) | Cumplida vacuamente y correctamente documentada: V5.1 no implementa ningún mecanismo de promoción `unresolved→confirmed` todavía (0 registros `_promoted_from_unresolved` en IST real, confirmado en la revalidación de R3); no es una invariante incumplida, es una invariante sin caso real que ejercitar aún. |
| I-8 (state estable entre proyecciones) | Cumplida, implicada por I-9 (la proyección legacy es byte-idéntica al original, luego ningún `state` cambia en ella); no evaluada para `ai_context`/`documentation` porque esas proyecciones no son la proyección legacy que I-9 cubre y quedan fuera del contrato de compatibilidad V4.3 que I-8 protege. |
| I-9 (equivalencia byte a byte con `index/`) | Cumplida, verificada a escala real: 21/22 archivos idénticos, el único distinto solo en `duration_seconds` (metadata operacional excluida por D-01). |
| I-10 (determinismo) | Cumplida, verificada en cada ronda con corridas reales independientes; última confirmación en esta ronda por recuento directo sobre las corridas de R3.2. |
| I-11 (`included_paths` ∩ `omitted_paths` = ∅) | Cumplida (regla estructural sobre `FunctionalFlow`, sin datos reales que la ejerciten distinto de neutral; tests verdes). |

Ninguna invariante obligatoria de V5.1 queda conocida como incumplida. I-4/I-5 ya no están pendientes. I-7 es la única invariante vacía por ausencia de casos reales, y queda documentada como tal (no como incumplimiento).

## 8. Persistencia y determinismo

`evidence/` se genera exclusivamente desde producción (`main.py full`/`analyze`, nunca solo desde `tools/`). Manifest válido: `evidence_schema_version=1.0`, `physical_format=json_compact`, `entity_counts`/`partition_sha256` coinciden con los 24 archivos físicos (releído en esta ronda, 0 discrepancias). Evidencia incompleta no se considera válida: un manifest de una corrida previa se borra antes de reconstruir, y solo se reescribe tras la última partición — un fallo a mitad de camino deja el directorio sin manifest, que es la señal de "no válida" que el resto del producto y los tests ya verifican. Formato físico sin cambios en esta ronda (`json_compact`, decidido y medido en R2.1). Determinismo: `evidence/` de las dos últimas corridas reales (R3.2) es byte a byte idéntica, reconfirmado en esta ronda.

## 9. Compatibilidad V4.3

Sin regresión, sin cambios de código desde R3.2 que pudieran introducirla: `index/` 21/22 archivos idénticos (el distinto solo en `duration_seconds`, ya excluido por D-01 desde V5.0); `documentation/` 0 diferencias; `RUN_SUMMARY.json` estructuralmente igual (mismas 11 claves, mismos 13 stages, sin `evidence` en `output_locations`). Ninguna de estas cifras se repitió con nuevas corridas en esta ronda porque el código relevante (`JSONExporter`, `MarkdownExporter`, `RUN_SUMMARY` writer) no cambió desde que R3.2 las midió.

## 10. Integración productiva

`build_evidence_artifacts` se invoca incondicionalmente dentro de `export_artifacts`, compartida por `analyze_repository` y `run_full_pipeline` — confirmado leyendo `pipeline_stages.py` en esta ronda, no asumido. `main.py full` y `main.py analyze` generan `evidence/` ambos (verificado con corridas reales de `full` en R3/R3.1/R3.2, y con una invocación real de `analyze` vía CLI en la revalidación de R3). Evidence Core no depende exclusivamente de `tools/`: el único invocador productivo es `pipeline_stages.py`; `tools/v5_1_r2_real_ist_regression.py` sigue siendo una herramienta de validación adicional, no el único camino. Las validaciones (`validate_evidence`, que incluye I-1/`sha256`/I-4/I-5) forman parte del camino productivo real: se ejecutan antes de `write_evidence`, dentro de `EXPORT`, en cada corrida real de `full`/`analyze`.

## 11. Independencia runtime / IA / adapter

- **Runtime:** AST sobre los 8 archivos de `legacy_documenter/evidence/*.py` (releído en esta ronda): 0 imports de `tools`/`tests`/`docs`/`prompts`. El único import fuera del propio paquete es `legacy_documenter.utils.atomic_write` (desde `persistence.py`). Dirección `tools → runtime` intacta; `runtime → tools` sigue sin existir.
- **IA:** búsqueda de texto sobre los mismos 8 archivos: 0 ocurrencias de `openai`/`anthropic`/`ollama`/`copilot`/`gemini`/`legacy_documenter.llm`. `build_evidence_artifacts` se ejecuta antes de que `AI_INTERPRETATION` (opt-in) se evalúe.
- **Technology Adapter boundary:** los 6 módulos "core" (`entities.py`, `reference.py`, `identity.py`, `invariants.py`, `projection.py`, `persistence.py`) siguen sin importar `legacy_documenter.extractors`/`legacy_documenter.analysis` (AST verificado en esta ronda). `REFERENCE_ADAPTER_ID`/`REFERENCE_ADAPTER_VERSION` siguen siendo parámetros de construcción de `builder.py`, no constantes de `entities.py`. Lo que R3.1/R3.2 añadieron al núcleo (`duplicate_ordinal`, `is_sha256_hex`, `CANONICAL_ID_KINDS`, `PROVENANCE_KINDS`, `build_reference_store`, `validate_provenance`) es genérico, no específico de VB.NET/WebForms/Oracle. No se implementó ningún adapter nuevo.

## 12. Suite final

`python -m unittest discover -s tests`, ejecutada de nuevo en esta ronda:

| Total | Failures | Errors | Skipped |
|---|---|---|---|
| 2 260 | 0 | 0 | 132 |

Los 132 skips son los `expected_fresh_clone_skips` de `PROJECT_STATE.json`, sin cambios desde R3/R3.1/R3.2.

## 13. Deuda técnica restante

**A. Deuda aceptable fuera del alcance actual (no bloquea el cierre):**

1. **D-5** — no existe lector `evidence/ → entidades normalizadas`; `index/` sigue proyectándose desde un `NormalizedEvidence` en memoria, no desde `evidence/*.json` releído de disco. Necesaria cuando una versión futura requiera integración/cache/reutilización directa desde `evidence/` persistido (candidata: V5.3 o una ronda de integración dedicada).
2. **I-7 sin caso real que ejercitar** — V5.1 no implementa ningún mecanismo de promoción `unresolved→confirmed`; la invariante está correctamente definida e implementada, pero no tiene datos reales que la disparen todavía.
3. **`source_span`/`textual` sin ejercitar en datos reales de IST** — ambos tipos de `EvidenceReference` están implementados y probados, pero el target real no generó ningún caso de ninguno de los dos (IST no tiene columnas de código con esa granularidad, y las 12 conexiones reales siempre trajeron `source_file`).
4. **Causa aguas arriba de D-1** — `VBProjExtractor` sigue emitiendo referencias `<Reference>` con `Include` vacío en 5 proyectos de IST; se preservan correctamente como ocurrencias distintas (`duplicate_ordinal`), pero la causa en el extractor no se tocó.
5. **Coste incremental de validación (I-4/I-5)** — 1.1–1.5 s sobre 454 010 entidades/686 010 referencias en IST real; medido, no optimizado, porque ninguna ronda lo pidió.
6. **`ExternalDependency` (assembly) referencia a `Project`, no directamente a `SourceArtifact`** — un salto de indirección (`ExternalDependency --entity--> Project --source--> SourceArtifact`) documentado y deliberado, no un defecto.

**B. Defecto que contradiga V5.1: ninguno.**

## 14. Conclusión de cierre

Los 13 criterios de cierre del prompt se cumplen: Evidence Core funciona desde producción real (`full`/`analyze`); identidades canónicas válidas en los 13 tipos (0 colisiones en IST real); `sha256` obligatorio operativo (15 138/15 138, 0 nulos); un fallo del Evidence Core invalida la ejecución (FAILED real, demostrado con sondeo controlado); `provenance`/`EvidenceReference` está integrado (454 010 entidades, 0 vacías); I-4/I-5 funcionan realmente en producción (686 010 referencias verificadas, 0 rotas); persistencia válida y determinista (24/24 particiones, manifest consistente, 0 diferencias entre corridas equivalentes); compatibilidad V4.3 mantenida (`index/`/`documentation/`/`RUN_SUMMARY.json` sin regresión funcional); runtime independence mantenida (0 imports prohibidos); AI independence mantenida (0 menciones de proveedor); Technology Adapter boundary mantenida (núcleo sin imports de extractors/analysis); suite completa sin failures/errors (2 260/0/0); y no queda ningún defecto B que contradiga el alcance o arquitectura de V5.1 — solo deuda A, explícitamente registrada.

V5_1_CLOSED
