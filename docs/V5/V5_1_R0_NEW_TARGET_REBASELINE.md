# V5.1 R0 — New Target Rebaseline (Diagnóstico/Documental)

## STATUS

`V5_1_R0_REBASELINE_COMPLETE`

Ronda diagnóstico/documental. No se implementó V5.1, no se ejecutó IA real, no se modificó producción, tests ni `PROJECT_STATE.json`. No se encontró ningún `CONTRACT_CONFLICT`: los contratos de identidad definidos en V5.0 (`docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`) quedan validados empíricamente sobre un target real distinto del usado en R2/R2A/R3.

## LEE PRIMERO (confirmado)

`CLAUDE.md`, `AGENTS.md`, `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`, `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`, `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`.

## EXECUTIVE SUMMARY

Con la suite completa verde como precondición, se ejecutó un `full` determinista (sin `--allow-ai-interpretation`) sobre `C:\Users\cgalianj\source\IST_40\Operacional`, generando salida completa en `C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline` (933 archivos, ≈1.70 GB). El run terminó `SUCCESS` en las 10 etapas deterministas, sin errores. Se generó un inventario empírico completo (tamaños exactos, conteos por índice, `OUTPUT_MANIFEST.json`) y se comparó byte a byte contra el baseline histórico de R2 (`C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1`, capturado sobre la raíz de despliegue IIS `C:\inetpub\wwwroot\2010\IST\Operacional`, confirmado por su propio `repository.json`).

**Hallazgo de trazabilidad de target (no es un incumplimiento de la instrucción, pero debe quedar explícito):** el "target real fijo" indicado (`C:\Users\cgalianj\source\IST_40\Operacional`) es, por sistema de archivos insensible a mayúsculas de NTFS, la misma ruta física que la que `AGENTS.md` documenta como "Legacy Source Repository" (`C:\Users\cgalianj\source\IST_40\operacional`) — verificado por `Device`/`Inode` idénticos. Esto **no** es la "antigua ruta de Operacional" que la instrucción pide no reutilizar: esa ruta antigua es la raíz de despliegue IIS `C:\inetpub\wwwroot\2010\IST\Operacional`, usada para el baseline histórico de R2 y confirmada como tal por el campo `repository.root` del propio índice histórico. El `repository.json` de esta ronda confirma que el run se ejecutó sobre la raíz correcta y distinta (`C:\Users\cgalianj\source\IST_40\Operacional`), cumpliendo la instrucción tal como se dio.

**Resultado de la comparación:** 17 de 21 índices (`entry_points`, `event_bindings`, `functional_flows`, `functional_paths`, `flow_unresolved`, `functional_dependencies`, `calls`, `data_access`, `data_parameters`, `stored_procedures`, `sql_operations`, `symbols`, `webforms`, `solutions`, `logical_symbols`, `errors`, `flow_summary`) son **byte-idénticos** entre la copia desplegada (IIS) y la copia de control de versiones (source checkout), pese a ser dos árboles físicos distintos. Los 4 índices que difieren (`files`, `projects`, `dependencies`, `configuration`) y `repository.json` (ya excluido de D-01) difieren por **drift real y explicable del repositorio objetivo** entre ambas copias (artefactos de build/IDE, un archivo de configuración con una ruta ligeramente distinta), no por no-determinismo del motor. No se encontró ningún caso nuevo de regresión. El contrato de identidad de V5.0 (`EP/EVB/FLOW/DAO/SP/SQL/PATH` como identidad; `PAR/CALL/UNRES` solo `legacy_ref`) se reconfirma exactamente con los mismos números que R2 midió sobre el despliegue IIS.

## 1. TEST SUITE GATE (precondición)

```text
python -m unittest discover -s tests
```

Resultado: `2169 tests`, **0 failures, 0 errors**, `132 skips`. La suite quedó verde antes de tocar el target real, cumpliendo la precondición de la instrucción ("Si no queda verde, STOP"). No se procedió a modificar nada; se continuó directamente con el rebaseline.

## 2. DETERMINISTIC FULL RUN

Comando ejecutado:

```text
python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline" --verbose
```

Resultado (`RUN_SUMMARY.json`):

```json
{"status":"SUCCESS","ai_requested":false,"ai_invoked":false,"proposal_count":0,
 "canonical_knowledge_produced":false,"technical_lead_approval":false,
 "stages":[SCAN,EXTRACTION,CALL_RESOLUTION,WEB_ENTRY_RESOLUTION,DATABASE_RESOLUTION,
 FLOW_RESOLUTION,DEPENDENCY_RESOLUTION,EXPORT,CONTEXT,DOCUMENTATION -> todas SUCCESS;
 AI_INTERPRETATION, PROPOSAL_GENERATION -> NOT_RUN; FINAL_SUMMARY -> SUCCESS]}
```

Sin IA solicitada ni invocada (confirma `--allow-ai-interpretation` no se usó). Duración total del scan (`repository.json.duration_seconds`): **370.072 s** sobre esta máquina, para 15 138 archivos escaneados. `errors.json` = `[]` (sin errores estructurados).

## 3. EMPIRICAL INVENTORY

### 3.1 Tamaño de la salida completa

`OUTPUT_MANIFEST.json`: **933 archivos, 1 701 885 264 bytes (≈1.70 GB)** en total, verificado con SHA-256 por archivo.

| Directorio de salida | Tamaño exacto |
|---|---|
| `index/` | 996 416 389 B (≈950 MB) |
| `ai_context/` | 279 178 592 B (≈266 MB) |
| `documentation/` | 226 477 973 B (≈216 MB) |
| `consumer_projection/` | 198 913 444 B (≈190 MB) |
| `context/` | 896 897 B (≈876 KB) |
| `RUN_SUMMARY.json` / `.md` | 4 KB / 4 KB |

### 3.2 Tamaños e inventario de `index/*.json` (bytes exactos, orden ascendente)

| Índice | Bytes | Registros |
|---|---|---|
| `errors.json` | 2 | 0 |
| `logical_symbols.json` | 332 | 1 |
| `flow_summary.json` | 673 | (dict, 21 contadores) |
| `sql_operations.json` | 2 436 | 3 |
| `repository.json` | 83 439 | (dict) |
| `solutions.json` | 89 561 | 113 |
| `configuration.json` | 278 682 | 60 |
| `projects.json` | 1 267 216 | 259 |
| `files.json` | 3 794 268 | 15 138 |
| `webforms.json` | 4 479 511 | 3 346 |
| `stored_procedures.json` | 6 135 867 | 5 389 |
| `symbols.json` | 8 407 472 | 6 513 |
| `dependencies.json` | 8 917 658 | 26 960 |
| `event_bindings.json` | 9 781 396 | 12 662 |
| `data_access.json` | 26 610 868 | 20 082 |
| `entry_points.json` | 30 284 763 | 12 662 |
| `data_parameters.json` | 90 890 159 | 74 633 |
| `flow_unresolved.json` | 118 282 168 | 162 914 |
| `functional_paths.json` | 124 174 498 | 170 020 |
| `functional_flows.json` | 124 193 249 | 12 642 |
| `calls.json` | 211 588 538 | 4 328 archivos / 230 356 calls |
| `functional_dependencies.json` | 227 153 633 | 335 698 |

`flow_summary.json` (idéntico entre esta corrida y el baseline histórico): `total_flows=12 642`, `total_paths=170 020`, `unresolved_boundaries=162 914`, `paths_to_stored_procedure=1 121`, `paths_to_sql=1`, `paths_to_data_operation=4 612`, `dead_end_paths=1 372`, `flows_with_confirmed_terminal=2 370`, `flows_with_unresolved_boundary=11 368`, `unique_terminal_stored_procedures=338`, `cross_project_flows=2 187`, `max_observed_depth=6`, `average_path_depth=1.3`, `errors=0`.

## 4. COMPARISON AGAINST HISTORICAL BASELINE

Comparación SHA-256 archivo por archivo de `index/*.json` contra `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1` (baseline histórico de R2, capturado sobre `C:\inetpub\wwwroot\2010\IST\Operacional`):

| Resultado | Índices |
|---|---|
| **IDÉNTICO byte a byte** (17) | `calls`, `data_access`, `data_parameters`, `entry_points`, `errors`, `event_bindings`, `flow_summary`, `flow_unresolved`, `functional_dependencies`, `functional_flows`, `functional_paths`, `logical_symbols`, `solutions`, `sql_operations`, `stored_procedures`, `symbols`, `webforms` |
| **DIFERENTE** (4 + repository) | `configuration`, `dependencies`, `files`, `projects`, `repository` (excluido de D-01 por diseño) |

Todo el conocimiento de aplicación derivado (símbolos, llamadas, entry points, event bindings, acceso a datos, flujos funcionales, caminos, dependencias funcionales, WebForms, stored procedures/SQL) es **idéntico** entre la copia desplegada en IIS y la copia de control de versiones. Root cause de cada diferencia, verificado con evidencia (no asumido):

| Índice | Causa raíz verificada |
|---|---|
| `files.json` (15 151 → 15 138, −13) | 15 archivos presentes solo en la copia IIS ya no existen en el checkout de control de versiones (9 DLLs/config compilados bajo `bl\blCobMorosidad\Bin\`, 1 backup `.bak_20260908_174519`, `DLLCache.xml`, 1 archivo temporal `temp\ddljs\...`); 2 archivos existen solo en el checkout (`dll\SondaNetNxtProcesoLargo.exe`, `Nxt\PrintDotMatrix\RawCliPrint2.jar`); 258 archivos (mayormente `.vbproj.user`, `UpgradeLog*.htm/.XML`, 3 `.vbproj`) tienen tamaño ligeramente distinto por metadatos de Visual Studio (timestamps/rutas de usuario incrustadas) que difieren entre el entorno de despliegue y el de desarrollo. Ninguno de estos 275 archivos es código de aplicación VB.NET/WebForms/ASPX relevante para la extracción semántica. |
| `projects.json` (259/259, contenido distinto) | Consecuencia directa de los cambios de `.vbproj`/`.vbproj.user` arriba descritos (metadatos de proyecto, no estructura). |
| `dependencies.json` (26 961 → 26 960, −1) | Una arista `WebTransmisionMan.vbproj → My Project\Application.Designer.vb` desaparece porque ese archivo generado por el IDE no está presente (o difiere) en el checkout de control de versiones. |
| `configuration.json` (60/60, 1 archivo con contenido distinto) | `Web.config`: dos valores (`Sonda.Net.Configuracion.UrlXMLSondaExceptions`, `Sonda.Net:Configuracion.TraceDir`) están hardcodeados con una ruta absoluta que difiere entre ambas copias (`...\2010\IST\Operacional\...` en IIS vs. `...\2010\Operacional\...`, sin el segmento `IST`, en el checkout) — diferencia real de contenido del propio `Web.config` entre ambos árboles, no un defecto de extracción. |
| `repository.json` | `root` (ruta distinta, esperado), `duration_seconds` (ya excluido de D-01), y los conteos derivados de las 13 diferencias netas de `files.json`; listado de directorios ignorados difiere porque el checkout tiene `.git\` (excluido) y algunos `bin\`/`obj\` que la copia IIS no tiene en el mismo estado. |

Ninguna de estas diferencias afecta símbolos, entry points, llamadas, acceso a datos, flujos funcionales o WebForms: todos esos índices son byte-idénticos. No hay evidencia de no-determinismo del motor; toda diferencia se explica por drift real y verificado del target entre las dos copias físicas.

## 5. IDENTITY CONTRACT VALIDATION (D-02, DR-R2-01, FINAL IDENTITY CONTRACT de R3)

Detector de colisiones reejecutado sobre los índices reales de esta corrida (metodología idéntica a la de R2: agrupar por `id` persistido; para `CALL-`/`UNRES-`, recomputar con la misma `_stable_id` poly33 de `legacy_documenter/analysis/flow_resolver.py`):

| Kind | Contrato V5.0 | entity_count | unique_id_count | collision_count | Veredicto |
|---|---|---|---|---|---|
| `EP-` | identidad preservable | 12 662 | 12 662 | **0** | ✅ confirma contrato |
| `EVB-` | identidad preservable | 12 662 | 12 662 | **0** | ✅ confirma contrato |
| `FLOW-` | identidad preservable | 12 642 | 12 642 | **0** | ✅ confirma contrato |
| `DAO-` | identidad preservable | 20 082 | 20 082 | **0** | ✅ confirma contrato |
| `SP-` | identidad preservable | 5 389 | 5 389 | **0** | ✅ confirma contrato |
| `SQL-` | identidad preservable | 3 | 3 | **0** | ✅ confirma contrato |
| `PATH-` | identidad preservable | 170 020 | 170 020 | **0** | ✅ confirma contrato |
| `PAR-` | solo `legacy_ref` | 74 633 | 74 628 | **5** | ✅ confirma contrato (no es identidad única, como el contrato ya establece) |
| `CALL-` (derivado) | solo `legacy_ref` | 230 356 | 228 946 | **27** | ✅ confirma contrato |
| `UNRES-` (derivado) | solo `legacy_ref` | 217 581 total / 216 172 IDs únicos | — | **25** | ✅ confirma contrato |

Adicional: 880 grupos de tuplas `(file, line, expression, resolved_target)` idénticas en `calls.json`, con 2 263 registros totales en esos grupos (1 383 registros "extra" más allá del primero de cada grupo) — mismo hallazgo que R2 (`CALL-` no distingue instancias con la misma tupla).

**Conclusión de la validación:** el contrato de identidad de V5.0 (`EP/EVB/FLOW/DAO/SP/SQL/PATH` como identidad legacy preservable; `PAR/CALL/UNRES` únicamente como `legacy_ref`, nunca como identity key) se reconfirma con **exactamente los mismos números** que R2 midió sobre la copia de despliegue IIS. Esto es evidencia independiente doble (dos árboles físicos distintos, mismo resultado) de que el contrato no es un artefacto de una única captura: **no se declara `V5_1_R0_CONTRACT_CONFLICT`**.

## 6. NEW REGRESSION CASES

**No se encontraron casos nuevos de regresión.** Criterios verificados:

- Las 10 etapas deterministas terminaron `SUCCESS`; `errors.json = []`.
- Ningún stage produjo un fallo estructurado inesperado (a diferencia de la intermitencia investigada y corregida en la ronda anterior, que era específica de reruns sobre el mismo `--output` en la suite de tests, no del análisis de un repositorio real).
- El detector de colisiones de identidad no encontró ninguna colisión nueva ni inesperada en `EP/EVB/FLOW/DAO/SP/SQL/PATH` (0 en los 7, igual que R2).
- Las diferencias frente al baseline histórico están 100 % explicadas por drift real y verificable del target (ver sección 4), no por comportamiento no determinista o defectuoso del motor.
- `flow_summary.json` (el resumen agregado de 21 contadores) es byte-idéntico al histórico, confirmando que el grafo de flujos funcionales es estructuralmente idéntico entre ambas copias del repositorio.

## RISKS

1. `data_parameters.json` (74 633 registros, `PAR-` con 5 colisiones) y `calls.json`/`UNRES-` (27/25 colisiones) siguen sin identidad única, exactamente como contractualmente esperado (DR-R2-01) — riesgo ya aceptado, no nuevo.
2. La comparación de esta ronda cubre solo la raíz de control de versiones; no se re-verificó la raíz de despliegue IIS (`C:\inetpub\wwwroot\2010\IST\Operacional`) para confirmar que sigue produciendo exactamente el mismo resultado que capturó R2 en su momento — no se re-ejecutó esa ruta en esta sesión (fuera del alcance de esta instrucción, que fija el target nuevo).
3. Las 275 diferencias de archivos de metadatos IDE (`*.vbproj.user`, `UpgradeLog*`) y el `Web.config` con ruta distinta son drift esperable de cualquier copia de control de versiones frente a un despliegue vivo; si una ronda futura necesita bytes-idénticos entre ambas copias para algún propósito, requeriría sincronizar manualmente esos archivos, fuera del alcance de LegacyMapper.
4. `technical_documentation_renderer.py` y el riesgo intermitente de rerun (ya corregido en la ronda anterior) siguen siendo los riesgos heredados de V5.0/V5.1 pre-gate; ninguno se reevaluó aquí porque no aplica a un `full` de una sola pasada sin AI.

## FILES READ

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`, `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`, `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`, `legacy_documenter/analysis/flow_resolver.py` (fórmula `_stable_id`/`_call_ref`, para recomputar `CALL-`/`UNRES-`); índices `index/*.json` de `C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline` y de `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1` (comparación, solo lectura).

## FILES MODIFIED

- Creado: `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`.
- Generado (fuera del repositorio `C:\dev\LegacyMapper`, en el directorio de resultados de pruebas): `C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline\` (salida completa del `full` determinista) y su `OUTPUT_MANIFEST.json`.
- Ningún archivo de producción, test, prompt o `PROJECT_STATE.json` modificado. Ningún otro `.md` creado.

## NEXT STEP

No se crea ningún prompt siguiente, según lo instruido. Queda a la espera de revisión/aprobación humana sobre este rebaseline antes de cualquier paso posterior de V5.1.
