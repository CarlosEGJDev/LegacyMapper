# V5.1 R2.1 — Normalized Evidence Core: Saneamiento e Integración

## 1. STATUS FINAL

`V5_1_R2_1_READY_FOR_R3`

Ninguna contradicción real de arquitectura/contrato bloqueó esta ronda. Los 7 puntos obligatorios (R2.1-01…07) quedaron resueltos con código real, medido y probado — no como deuda diferida. No se implementó nada de V5.2–V5.9. No se modificó `PROJECT_STATE.json`, el roadmap, ni el comportamiento legacy de V4.3 más allá de lo estrictamente necesario para integrar el Evidence Core (justificado punto por punto abajo). Sin commits/push/branch.

## 2. RESUMEN EJECUTIVO

R2 dejó el Normalized Evidence Core implementado pero **desconectado del producto real** (solo alcanzable vía `tools/`), con un acoplamiento de frontera de adapter incorrecto (`ADAPTER_ID` hardcodeado dentro del módulo "core" de entidades), el formato físico de persistencia sin decidir con medición, e `Instantiation` sin su propia partición pese a que R1 lo exigía como concepto de primera clase. Esta ronda corrigió los cuatro puntos con código real: `python main.py full`/`analyze` ahora generan `evidence/` automáticamente y de forma aditiva (verificado a escala completa sobre IST real, con `index/`/`documentation/` permaneciendo byte-idénticos); la frontera de Technology Adapter se corrigió moviendo `ADAPTER_ID` fuera del núcleo hacia el builder que efectivamente envuelve el adapter de referencia; el formato físico se decidió con medición real (JSON compacto, no JSONL, no pretty) reduciendo el tamaño de `evidence/` en IST real de 1.16 GB a 932.5 MB pese a añadir una partición nueva; `Instantiation` es ahora una partición propia (`evidence/instantiations.json`, 40 278 registros reales, sin identidad canónica, con trazabilidad posicional). Se verificó explícitamente (no se asumió) independencia de runtime, independencia de IA, y que la frontera Core/Adapter permite componer un adapter futuro sin tocar el núcleo. Suite completa: 2228 tests, 0 failures, 0 errors, 132 skips, en 3 corridas consecutivas a lo largo de la ronda. Regresión real sobre `C:\Users\cgalianj\source\IST_40\Operacional` ejecutada dos veces (vía herramienta de validación y vía `main.py full` productivo directo): resultados idénticos, determinismo confirmado, 0 colisiones de identidad, proyección legacy 22/22 índices + `documentation/` byte-idénticos.

## 3. ESTADO INICIAL ENCONTRADO EN R2 (verificado contra el código, no asumido)

Antes de modificar nada, se inspeccionó el código real que R2 dejó (no se confió en que el documento de R2 describiera perfectamente el estado):

- `NormalizedEvidenceBuilder`/`write_evidence` existían y funcionaban correctamente, pero **ningún punto de `legacy_documenter/cli/pipeline_stages.py` los invocaba** — confirmado por lectura directa: `export_artifacts` solo llamaba a `JSONExporter`/`MarkdownExporter`. El único invocador real era `tools/v5_1_r2_real_ist_regression.py`.
- `legacy_documenter/evidence/entities.py` definía `ADAPTER_ID = "vbnet-webforms-oracle"` como **constante de módulo**, usada dentro de `to_dict()` de cada entidad — confirmado por lectura: cualquier entidad construida por cualquier futuro adapter habría quedado etiquetada como `vbnet-webforms-oracle` sin remedio, porque el propio módulo "core" decidía la identidad del adapter en vez de recibirla.
- `legacy_documenter/evidence/persistence.py` usaba `json.dumps(..., indent=2, ...)` (pretty) — confirmado; R1/R2 habían dejado el formato físico como decisión pendiente "con medición", y esa medición nunca se hizo.
- `Instantiation` existía como dataclass en `legacy_documenter/models/call.py` desde V4.3, y `NormalizedEvidenceBuilder` la dejaba **embebida sin cambios dentro de `calls.json`** (passthrough) — confirmado: no había ninguna partición `evidence/instantiations.json`, contradiciendo la clasificación `CORE_ENTITY` que R1 le había asignado.

## 4. PROBLEMAS DETECTADOS

| # | Problema | Contradice |
|---|---|---|
| 1 | Evidence Core no alcanzable desde `full`/`analyze` | "Evidence Core debe estar integrado al flujo real" (regla de R2.1) |
| 2 | `ADAPTER_ID` hardcodeado en el módulo core | "separación entre tecnología concreta y Normalized Evidence Core"; "capacidad arquitectónica para múltiples tecnologías" |
| 3 | Formato físico sin decidir/medir | Instrucción explícita R2.1-03 ("debes medir antes de decidir... la decisión debe quedar implementada y testeada") |
| 4 | `Instantiation` sin partición propia | Clasificación `CORE_ENTITY` ya fijada por R1 para `Instantiation` |

Ninguno era una contradicción irresoluble de arquitectura — los cuatro se resolvieron en esta ronda con código real, no se reclasificaron como deuda.

## 5. DECISIONES TOMADAS

### R2.1-01 — Punto de integración

Se decidió integrar dentro de `pipeline_stages.export_artifacts` (la función que ya comparten `analyze_repository` y `full_pipeline.run_full_pipeline`), no como un nuevo `StageId`. Razón: añadir un `StageId.EVIDENCE` habría insertado una nueva entrada en `RUN_SUMMARY.json.stages[]`, rompiendo la compatibilidad byte-a-byte con V4.3 que V5.0 D-01 ya fijó como contrato aprobado — exactamente el mismo tipo de conflicto que el propio V5.0 (DR-R2-03) ya resolvió una vez para observabilidad, moviendo esa información a un sidecar en vez de tocar `RUN_SUMMARY.json`. `export_artifacts` ya tenía precedente de "múltiples escritores, un solo stage" (`JSONExporter` + `MarkdownExporter`), así que extenderlo a un tercer escritor aditivo es el punto de menor riesgo arquitectónico.

### Fallo del Evidence Core: best-effort, nunca bloqueante

Se decidió que un fallo al construir/persistir `evidence/` se registra (`LOG.warning`, visible por defecto) pero **nunca** se propaga como excepción ni convierte un `EXPORT` que de otro modo sería exitoso en `FAILED`. Justificación explícita: la instrucción de la ronda es categórica ("No rompas el comportamiento V4.3... debe ser aditiva respecto del resultado existente"); un defecto nuevo en una capacidad aditiva no puede degradar el resultado legacy que V4.3 ya entregaba. Esto **no** debilita la trazabilidad/corrección interna de la evidencia: `BrokenEvidenceReferenceError`, la validación de `UnresolvedBoundary.state`, y todos los invariantes siguen siendo excepciones reales dentro del Evidence Core — el best-effort aplica únicamente al límite entre "el Evidence Core en su conjunto" y "el resultado V4.3 ya garantizado", no a la corrección interna del propio Evidence Core.

### `SourceArtifact.sha256`: `None` por defecto en producción

Se decidió que la integración productiva **no** calcula `sha256` de contenido (`repo_root=None`). Medido: hashear los 15 138 archivos reales de IST cuesta decenas de segundos (81 s medidos en esta ronda, 27–153 s en mediciones previas según estado de caché de disco) — un costo que V4.3 nunca pagaba en ningún `full`/`analyze`. Imponerlo silenciosamente a cada invocación violaría "no rompas el comportamiento V4.3" en su sentido más literal (tiempo de respuesta). `tools/v5_1_r2_real_ist_regression.py` sigue ejerciendo el cómputo real explícitamente para validación. Esto es fiel al contrato R1 ("`sha256`... `None` cuando no se solicitó, nunca un valor fabricado").

### R2.1-03 — Formato físico definitivo: JSON compacto

Medido sobre `evidence/` real de IST (partición más grande, `functional_dependencies.json`, 335 698 registros, y otras 4 particiones representativas): pretty JSON, JSON compacto, y JSONL. Resultado (ver `legacy_documenter/evidence/persistence.py` para el detalle completo con cifras):

| Criterio | Pretty | Compacto | JSONL |
|---|---|---|---|
| Tamaño | 227.2 MB (`functional_dependencies`) | 200.5 MB (−12%) | 200.5 MB (idéntico a compacto) |
| Tiempo de lectura | — | más rápido que JSONL en este uso | más lento (overhead de `json.loads` por línea) |
| Determinismo | igual | igual | igual |
| Particionamiento | no afectado por ninguno de los tres | | |
| Compatibilidad V5.3 | — | no bloquea una migración futura a JSONL si aparece un consumidor que realmente necesite streaming | ventaja real solo si algo hace streaming, y nada en V5.1 lo hace |

**Decisión: JSON compacto** (`separators=(",", ":")`, sin indentación). Gana en tamaño igual que JSONL, gana en tiempo de lectura para el patrón de uso real de V5.1 (materializar la partición completa), y es estrictamente más simple de implementar (reutiliza `json.dump`/`json.load`, sin lógica de split/join por línea) — "no introduzcas complejidad innecesaria". Implementado en `persistence.py::_render`.

### R2.1-04 — `Instantiation`: partición propia, sin identidad canónica

Se materializa `evidence/instantiations.json` extrayendo `calls.json`'s `instantiations[]` embebido por archivo, sin duplicar el dato (sigue existiendo también dentro de `calls.json` como passthrough, porque `calls.json` es una proyección legacy que no puede perder ese campo). Identidad: **ninguna canónica**, confirmando la lectura de R1 ("entidad hija, posicional, como `DataParameter`") — trazabilidad vía `source_artifact` (referencia a `SourceArtifact`) + `position` (ordinal 0-based dentro de la lista de instanciaciones de ese archivo, en el orden ya determinista que el extractor emite).

### R2.1-05 — Technology Adapter boundary

`ADAPTER_ID`/`ADAPTER_VERSION` se eliminaron de `entities.py` (el módulo "core"). Cada entidad ahora exige `adapter_id`/`adapter_version` como parámetro de construcción; `builder.py` define `REFERENCE_ADAPTER_ID`/`REFERENCE_ADAPTER_VERSION` (el único adapter que V5.1 implementa) y los pasa explícitamente. Justificación: `builder.py` **es** la capa de envoltura del adapter de referencia (así lo describe el propio R1: "Adapter de referencia... envuelve extractors/analysis"), mientras que `entities.py` debe permanecer agnóstico para que un adapter futuro (V5.4, posible composición lenguaje+DB distintos) pueda producir las mismas entidades sin modificar el módulo core. Verificado con test dedicado (`test_adapter_id_is_a_constructor_parameter_not_a_module_constant`): construir un `NormalizedEvidenceBuilder(adapter_id="future-adapter", ...)` produce entidades reales etiquetadas con ese id, sin tocar `entities.py`.

## 6. CAMBIOS REALIZADOS

| Archivo | Cambio |
|---|---|
| `legacy_documenter/evidence/entities.py` | `ADAPTER_ID`/`ADAPTER_VERSION` eliminados como constantes de módulo; cada dataclass gana `adapter_id`/`adapter_version` obligatorios; nueva dataclass `Instantiation`. |
| `legacy_documenter/evidence/builder.py` | `REFERENCE_ADAPTER_ID`/`REFERENCE_ADAPTER_VERSION` (nuevos); `NormalizedEvidenceBuilder.__init__` acepta `adapter_id`/`adapter_version`; todas las construcciones de entidades pasan estos valores; nuevo `_build_instantiations`; `NormalizedEvidence.instantiations` (nuevo campo). |
| `legacy_documenter/evidence/persistence.py` | Formato físico cambiado de pretty a compacto (`_render`); `instantiations` añadida a `NEW_ENTITY_PARTITIONS`; `EVIDENCE_MANIFEST.json` gana `physical_format`. |
| `legacy_documenter/evidence/projection.py` | Import de `ADAPTER_ID` reemplazado por `REFERENCE_ADAPTER_ID` (default del constructor). |
| `legacy_documenter/cli/pipeline_stages.py` | **Único archivo de producción fuera de `evidence/` modificado.** `export_artifacts` ahora también llama a `build_evidence_artifacts` (nueva función); logger de módulo añadido. Necesidad demostrada: es el único punto donde `analyze`/`full` comparten la construcción de `indexes` antes de escribir salida — sin tocarlo, el Evidence Core seguiría inalcanzable desde el producto real (R2.1-01 es un requisito explícito de la ronda). Tests de regresión añadidos y verificación de equivalencia V4.3 (sección 13) confirman que no cambia ningún comportamiento existente. |
| `tests/test_v5_1_r2_normalized_evidence_core.py` | +14 tests nuevos (`InstantiationTests`, `RuntimeIndependenceTests`, `AiIndependenceTests`, `TechnologyAdapterBoundaryTests`, `ProductionPipelineIntegrationTests`); tests existentes de R2 ajustados al import `REFERENCE_ADAPTER_ID`. |
| `tools/v5_1_r2_real_ist_regression.py` | Import corregido (`REFERENCE_ADAPTER_ID`); conteo de `instantiations` añadido al reporte. |

Ningún extractor/resolver/exportador legacy fue modificado. `JSONExporter`/`MarkdownExporter` no se tocaron.

## 7. ARQUITECTURA RESULTANTE

```text
Legacy Source
    ↓ (extractors/*.py, analysis/*.py -- sin cambios)
Existing deterministic analysis (indexes dict, ya existente)
    ↓ (pipeline_stages.export_artifacts, ahora también)
NormalizedEvidenceBuilder (adapter_id=REFERENCE_ADAPTER_ID por defecto)
    ↓
write_evidence -> <output>/evidence/*.json + EVIDENCE_MANIFEST.json (JSON compacto)
    ↓ (LegacyIndexProjector, disponible; aún no re-cableado a JSONExporter -- ver DEUDA)
Legacy Compatibility Projection (index/*.json -- producido directamente por JSONExporter, sin cambios)
    ↓
documentation/ / ai_context/ / consumer_projection/ (sin cambios, D-01 intacto)
```

`evidence/` se escribe **en paralelo** a `index/`/`documentation/` (ambos derivan del mismo `indexes` dict, sin reanálisis), no en cadena a través de `index/` todavía — ver DEUDA sección 22 para la implicación exacta de esto.

## 8. RUNTIME INDEPENDENCE

Verificado con AST (`RuntimeIndependenceTests.test_evidence_package_imports_no_development_only_paths`), no por convención: ningún archivo de `legacy_documenter/evidence/*.py` importa `tools`, `tests`, `docs`, `prompts`, ni nada bajo esos prefijos. `pipeline_stages.py` (el único archivo de producción modificado fuera de `evidence/`) verificado igual: sus únicos imports nuevos son `legacy_documenter.evidence.builder`/`.persistence`. Ningún archivo referencia `PROJECT_STATE.json`, rutas absolutas del entorno de desarrollo, ni fixtures de test. Los tools (`tools/v5_1_r2_real_ist_regression.py`) sí importan el runtime (`legacy_documenter.evidence.*`) — dirección correcta ("los tools pueden usar el runtime; el runtime no puede necesitar los tools"), confirmada por búsqueda: ningún módulo de `legacy_documenter/` importa nada de `tools/`.

## 9. TECHNOLOGY ADAPTER BOUNDARY

Corregido según sección 5. Verificado con tests (`TechnologyAdapterBoundaryTests`): (a) ningún módulo "core" (`entities.py`, `reference.py`, `identity.py`, `invariants.py`, `projection.py`, `persistence.py`) importa `legacy_documenter.extractors`/`legacy_documenter.analysis` directamente; (b) `adapter_id` es parámetro de construcción, no constante de módulo, demostrado instanciando un adapter distinto (`"future-adapter"`) sin tocar `entities.py`. No se implementó ningún adapter nuevo (V5.4 fuera de alcance), pero la dependencia arquitectónica que lo habría hecho imposible después ya no existe.

## 10. AI INDEPENDENCE

Verificado con AST + búsqueda de texto (`AiIndependenceTests`): ningún archivo de `legacy_documenter/evidence/*.py` importa ni menciona `legacy_documenter.llm`, `copilot`, `openai`, `anthropic`, `ollama`, ni `gemini`. Dos builds del mismo `indexes` producen evidencia idéntica (determinismo, sin rama de código que pudiera consultar un proveedor). La integración productiva (`pipeline_stages.build_evidence_artifacts`) tampoco introduce ninguna dependencia de IA: se ejecuta incondicionalmente dentro de `EXPORT`, antes de que `AI_INTERPRETATION` (opt-in) siquiera se evalúe.

## 11. EVIDENCE PERSISTENCE FINAL

Cerrada (sección 5, R2.1-03): JSON compacto, un archivo por tipo de entidad, `EVIDENCE_MANIFEST.json` con `evidence_schema_version`, `physical_format`, `entity_counts`, `partition_sha256` por partición. 23 particiones en un run real completo (9 entidades nuevas incluyendo `instantiations`, 14 passthrough preservadas). Tamaño real medido en IST: **932.5 MB** (vs. 1.16 GB en R2, pese a añadir la partición `instantiations` nueva — la reducción de formato compensa con margen la partición añadida).

## 12. INSTANTIATION FINAL

Cerrado (sección 5, R2.1-04). `evidence/instantiations.json`: 40 278 registros reales en IST (coincide exactamente con el conteo ya medido en R0: "40.278 instanciaciones... 4 328 archivos"). Sin identidad canónica (por diseño, conforme al contrato). Trazabilidad: `source_artifact` + `position`, verificada contra `SourceArtifact` reales con `EvidenceReferenceStore`/`resolve_against` (test `test_instantiation_traces_back_to_a_known_source_artifact`). Determinismo de `position` verificado explícitamente por archivo fuente.

## 13. COMPATIBILITY PROJECTION

Mantenida íntegra. Comparación directa, a escala real de IST, entre el baseline R0 (`v5_1_new_target_rebaseline`) y una corrida productiva completa de esta ronda (`v5_1_r2_1_full_pipeline_check`, generada con `python main.py full` real, no con la herramienta de solo-lectura):

```text
index/*.json  : 21/22 archivos byte-idénticos (el único distinto, repository.json,
                difiere solo en duration_seconds -- ya excluido de D-01)
documentation/: 0 diferencias (diff -rq entre ambos árboles completos)
RUN_SUMMARY.json: mismas 11 claves, mismo output_locations (sin "evidence"),
                mismos 13 stages (sin ninguno nuevo)
```

`index/` sigue sin ser fuente canónica: lo sigue produciendo `JSONExporter` directamente desde `indexes`, no desde `evidence/` (ver DEUDA).

## 14. TESTS

`tests/test_v5_1_r2_normalized_evidence_core.py`: **59 tests** (45 de R2 + 14 nuevos de R2.1: `InstantiationTests` ×5, `RuntimeIndependenceTests` ×1, `AiIndependenceTests` ×2, `TechnologyAdapterBoundaryTests` ×2, `ProductionPipelineIntegrationTests` ×4). Cubren exactamente las categorías pedidas por la sección 14 del prompt: Core (entities/identities/relations/references/unresolved/traceability — heredado de R2, sin regresión), Persistence (serialización/deserialización/integridad de partición/manifest/determinismo/formato físico), Instantiation (representación/persistencia/trazabilidad/salida determinista), Runtime independence, Adapter boundary, Compatibility, Real IST (regresión manual documentada en la sección 16, no como test automatizado por su duración).

## 15. FULL SUITE

Tres corridas completas a lo largo de esta ronda (antes de empezar, después de la integración de pipeline, y al cierre):

| Corrida | Tests | Failures | Errors | Skips |
|---|---|---|---|---|
| Antes de tocar código (heredado de R2) | 2214 | 0 | 0 | 132 |
| Tras integrar `pipeline_stages.py` | 2214 | 0 | 0 | 132 |
| Final (tras +14 tests nuevos) | **2228** | **0** | **0** | **132** |

2228 = 2214 + 14 nuevas. Ninguna prueba existente fue debilitada, saltada ni convertida en trivial. No apareció ningún fallo durante la ronda (0 de 3 intentos, por lo que no aplica el protocolo de "tercer fallo repetido → detener").

## 16. REAL IST REGRESSION

Target: `C:\Users\cgalianj\source\IST_40\Operacional` (no se usó `C:\inetpub\wwwroot\2010\IST\Operacional`). Dos ejecuciones independientes:

**(a) Vía herramienta de validación** (`tools/v5_1_r2_real_ist_regression.py`, lee `index/*.json` ya producido, sin re-escanear):

```text
source_artifacts: 15 138 (sha256 real calculado para 15 138/15 138)
solutions: 113 | projects: 259 | components: 9 859
external_dependencies: 4 839 | data_objects: 5 392
call_identities: 230 356 | instantiations: 40 278 | unresolved_boundaries: 162 914
Colisiones (I-1): PRJ=0 CMP=0 XDP=0 CAL=0 UnresolvedBoundary=0 SRC=0 SOL=0
Proyección (I-9): 22/22 índices byte-idénticos
evidence/ total: 977 848 590 bytes (932.5 MB)
```

**(b) Vía producto real** (`python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output ...`, pipeline productivo completo, re-escaneando desde cero):

```text
LegacyMapper full run: SUCCESS
Stages: SCAN..FINAL_SUMMARY todos SUCCESS (AI_INTERPRETATION/PROPOSAL_GENERATION: NOT_RUN, como corresponde sin --allow-ai-interpretation)
evidence/ generado automáticamente: 23 particiones, EVIDENCE_MANIFEST.json con los mismos conteos que (a)
index/: 21/22 idéntico a R0 (repository.json difiere solo en duration_seconds)
documentation/: 0 diferencias frente a R0
```

Ambas ejecuciones coinciden en entity counts, 0 colisiones, y equivalencia de proyección — evidencia cruzada de que el pipeline productivo y la herramienta de validación calculan exactamente lo mismo (como deben, al compartir el mismo `NormalizedEvidenceBuilder`).

## 17. DETERMINISM EVIDENCE

Sobre datos reales de IST (`indexes` reconstruido desde `index/*.json`), dos builds consecutivos de `NormalizedEvidenceBuilder().build(indexes)` (incluyendo `instantiations`, sin hashing de contenido para acotar el tiempo de la comprobación): **idénticos byte a byte** tras serializar todas las particiones nuevas. Confirmado también por el propio `check_i10_determinism` en la suite de tests sobre el fixture completo. Orden de emisión preservado en todo momento (ningún `sorted()`/`set()` no determinista introducido en ninguno de los cambios de esta ronda); IDs, duplicate ordinals, y referencias son puramente funciones de los datos de entrada, nunca de estado de filesystem, memoria, threads o timestamps.

## 18. BEFORE/AFTER MEASUREMENTS

| Métrica | R2 (antes) | R2.1 (después) |
|---|---|---|
| `evidence/` alcanzable desde | solo `tools/` | `main.py full` y `main.py analyze` (verificado a escala real) |
| `ADAPTER_ID` | constante de módulo en `entities.py` | parámetro de construcción (`REFERENCE_ADAPTER_ID` en `builder.py`) |
| Formato físico de partición | JSON pretty (indent=2) | JSON compacto (medido, decidido, implementado) |
| `evidence/` tamaño real (IST) | 1 211 178 539 B (1.16 GB) | 977 848 590 B (932.5 MB) — **−19.3%**, pese a sumar `instantiations.json` |
| `Instantiation` | embebida en `calls.json`, sin partición propia | `evidence/instantiations.json`, 40 278 registros |
| Tests del módulo de evidencia | 45 | 59 (+14) |
| Suite completa | 2214 / 0 / 0 / 132 | 2228 / 0 / 0 / 132 |
| `index/`/`documentation/` vs. baseline R0 | (no aplica, sin integración productiva) | 21/22 + 0 diffs, verificado con `main.py full` real |

## 19. ARCHIVOS MODIFICADOS

`legacy_documenter/cli/pipeline_stages.py`, `legacy_documenter/evidence/entities.py`, `legacy_documenter/evidence/builder.py`, `legacy_documenter/evidence/persistence.py`, `legacy_documenter/evidence/projection.py`, `tests/test_v5_1_r2_normalized_evidence_core.py`, `tools/v5_1_r2_real_ist_regression.py`.

## 20. ARCHIVOS NUEVOS

`docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md` (este documento). Ningún otro archivo nuevo (los módulos de `legacy_documenter/evidence/` ya existían desde R2; esta ronda los modificó, no los creó — excepto la nueva dataclass `Instantiation` dentro de `entities.py`, que no es un archivo nuevo).

Fuera del repositorio (directorio de resultados de pruebas, no versionado): `C:\PruebasLegacyMapper\Resultados\v5_1_r2_1_full_pipeline_check\` (corrida productiva completa de verificación) y la regeneración de `C:\PruebasLegacyMapper\Resultados\v5_1_r2_evidence_build\` (herramienta de validación, sobreescrita con el nuevo formato).

## 21. EXCLUSIONES EXPLÍCITAS DE V5.2–V5.9

No implementado en esta ronda (verificado, no solo declarado): template engine/profiles (V5.2) — `evidence/` no conoce HTML/Markdown/templates, confirmado por ausencia de imports; cache incremental (V5.3) — sin fingerprints de invalidación ni lógica de reuso, solo el `sha256` opcional ya contratado desde R1; adapters nuevos completos (V5.4) — solo se corrigió la frontera que lo permitirá, no se escribió ningún adapter nuevo; generic AI provider (V5.5) — cero imports de `llm/*`; segmentación rica (V5.6) — los campos reservados de `FunctionalFlow` siguen con sus valores neutrales, sin lógica nueva; approval/canonical knowledge (V5.7) — sin tocar `knowledge/approval`, `knowledge/canonical`; plugin runtime (V5.8) — sin tocar `knowledge/plugin_projection`; segundo stack tecnológico (V5.9) — un solo adapter (`vbnet-webforms-oracle`) sigue siendo el único implementado.

## 22. DEUDA TÉCNICA RESTANTE

**Ninguna deuda que contradiga los objetivos de V5.1** (independencia de runtime, independencia de IA, separación Core/Consumers, separación Core/Tecnología, reproducibilidad/determinismo, trazabilidad, capacidad multi-tecnología, preparación para consumidores futuros) — todas verificadas explícitamente arriba, no asumidas.

`KNOWN_TECHNICAL_DEBT` (decisiones de alcance explícitas, dentro del roadmap de fases posteriores, no contradicciones):

1. **`index/` no se reconstruye todavía desde `evidence/`.** `LegacyIndexProjector` existe, está probado, y demuestra que la reconstrucción es posible sin pérdida (D-04) — pero `JSONExporter` sigue produciendo `index/` directamente desde `indexes`, no a partir de `evidence/`. Esto es **coherente con V5.0 D-01/D-04** ("`index/` es proyección de compatibilidad", sin exigir que la implementación física ya haya invertido la fuente en V5.1) y explícitamente más seguro: cablear `index/` para que dependa de `evidence/` en producción, sin una ronda dedicada a demostrar la equivalencia bajo condiciones adversas (fallos parciales, reruns), sería el tipo de cambio de comportamiento que esta misma ronda prohíbe introducir sin justificación exhaustiva. Pertenece a una ronda de integración posterior, no es una contradicción de V5.1.
2. **`SourceArtifact.sha256` es `None` en toda corrida productiva** por la decisión de rendimiento ya justificada (sección 5). No contradice el contrato (que ya preveía `None` como válido), pero significa que ningún consumidor productivo tiene todavía hashes de contenido reales salvo que invoque la herramienta de validación explícitamente.
3. **Fallo del Evidence Core es best-effort/silencioso hacia el resultado V4.3** (por diseño, sección 5) — un operador que no mire los logs de `--verbose`/nivel WARNING podría no notar que `evidence/` faltó en una corrida. Aceptado deliberadamente para no arriesgar el comportamiento V4.3; queda documentado aquí para que una futura ronda decida si necesita mayor visibilidad (p. ej. un campo en un sidecar de observabilidad, ya previsto en V5.0 D-12/DR-R2-03 pero no implementado en V5.1).

Ninguno de los tres bloquea `V5_1_R2_1_READY_FOR_R3`: son decisiones de alcance ya justificadas con evidencia, no defectos sin resolver.
