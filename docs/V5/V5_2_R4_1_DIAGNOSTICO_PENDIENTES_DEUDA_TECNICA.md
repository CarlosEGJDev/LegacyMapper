# V5.2 R4.1 — Diagnóstico de pendientes y deuda técnica

Convención: **[NUEVO: R4.1]** = comprobación ejecutada en esta ronda; **[HEREDADO]** = cifra o afirmación tomada de un informe anterior sin remedir; **[NO VERIFICADO]** = no comprobado en esta ronda.

## 1. Estado y alcance

Ronda **solo de lectura**. No se modificó código, tests, prompts, documentación existente, outputs, roadmap ni `PROJECT_STATE.json`. No se implementó ninguna corrección. No se cerró V5.2 ni se inició V5.3. Sin commits, push ni operaciones de Git que cambien estado. El único archivo creado es este informe.

Conclusión resumida: **no se encontró ningún defecto que bloquee el cierre de V5.2** en el producto; sí hay (a) un hallazgo material sobre la ruta IST (H-2: las dos rutas **no** son equivalentes), (b) un riesgo real de continuidad (H-3: todo el trabajo V5 sin versionar), (c) una brecha de pruebas pequeña (H-4: el reintento de `atomic_write` no tiene test propio) y (d) dos afirmaciones inexactas en el informe R4 (H-4 y H-5).

## 2. Fuentes revisadas y comprobaciones realmente ejecutadas

**Leído:** `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, el prompt R4.1, `docs/V5/V5_2_R4_DOCUMENTATION_CLOSURE.md`, cabeceras y cifras de tests de `V5_2_R2`, `R3`, `R3_1`, `R3_2`, `R3_3`, `R3_4`, `R3_4_1`, `PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`, `V5_1_R4_CIERRE_FINAL.md`, los tres documentos de continuidad modificados y `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md`.

**Ejecutado [NUEVO: R4.1]** (todo de solo lectura):

| # | Comprobación | Resultado |
|---|---|---|
| C1 | `git status`, `git diff --stat`, `git diff` de los tres archivos de producción modificados | 26 entradas: 12 modificadas/borradas, 14 rutas sin seguimiento (incluye directorios completos) |
| C2 | Comparación byte a byte de `prompts/V5_0/V5_0_R0_…PROMPT.md` contra la versión borrada de `docs/V5_0/` en `HEAD` (ignorando saltos de línea) | 0 diferencias: fue **movido**, no perdido |
| C3 | Búsqueda de usos de `_replace_with_retry` y de tests que lo cubran | Usado en `atomic_write.py` y en `documentation_v52/engine.py`; **0 tests** lo invocan directamente |
| C4 | Búsqueda de tests de `documentation_v52` en `compute_output_locations` | Existen (`test_v5_2_r3_1_human_semantic_corrections.py` líneas 303 y 308: presente si DOCUMENTATION es SUCCESS, ausente si falla) |
| C5 | Comparación reproducible de las dos rutas IST (ver H-2) | Ver H-2 |
| C6 | Cifras de tests por informe | Ver H-6 |
| C7 | Existencia de `pyproject.toml`/`setup.py`/`MANIFEST.in` | No existe ninguno |

**No ejecutado:** suite completa de tests, ninguna prueba dirigida, corrida IST, verificación de enlaces, hash de `documentation/` legacy. Justificación: el prompt lo prohíbe por rutina y no fueron indispensables. Los archivos temporales de la comparación IST se escribieron fuera del repositorio (directorio temporal de la sesión).

## 3. Hallazgos H-1 a H-6

| ID | Evidencia | Impacto | Decisión pendiente | Tratamiento propuesto |
|---|---|---|---|---|
| **H-1** | `PROJECT_STATE.json`: `current_version: V4.3`, `next: V5_DESIGN_PENDING`, `v5_implemented: false`, `tests: 2169`, `latest_completed_round: V4.3-R9`. Fuentes autoritativas del estado real: `docs/V5/V5_1_R4_CIERRE_FINAL.md` (V5.1 cerrada), `V5_2_R3_4_1_…` (2 441 tests, aprobación humana 29-09-2026 registrada en R4 §2) y la nota de continuidad del 29-09-2026 en `LEGACYMAPPER_V5_ROADMAP.md`. `AGENTS.md` declara este archivo como puntero autoritativo. [NUEVO: R4.1] confirmado; ninguna ronda V5 lo actualizó. | Real pero de gobernanza: un agente nuevo que siga `AGENTS.md` leería que V5 no existe. No afecta al producto. | Quién: el **Technical Lead** debe autorizar; el prompt de cierre debe permitir editarlo. | `DOCUMENTAR_Y_ACEPTAR_EXPLICITAMENTE` hasta el cierre; actualizar **en la ronda de cierre formal** (campos: `current_version`, `current_version_status`, `latest_completed_round`, `latest_approved_round`, `round_status`, `tests`, `next`, rutas de handover/roadmap V5, `v5_implemented`). Cerrar V5.2 dejando este archivo así sería inadecuado según `AGENTS.md`. |
| **H-2** | [NUEVO: R4.1] Ver §3.1. Las rutas **no son equivalentes**. | Alto para V5.3 (usa la corrida IST como regresión) y para cualquier cifra citada. No afecta a la validez de V5.2, cuyas cifras vienen de `IST_40`. | Technical Lead: declarar la ruta oficial. | `ANTES_DEL_CIERRE` (decisión, no código). |
| **H-3** | [NUEVO: R4.1] Ver §3.2. | Riesgo real de continuidad: ~25 000 líneas de trabajo V5 y `legacy_documenter/evidence/`, `documentation_v52/`, 7 módulos de tests, 3 tools y `docs/V5/` no están en ningún commit. Un fallo de disco pierde V5.0–V5.2. | Technical Lead administra Git. | `ANTES_DEL_CIERRE` (acción del usuario). |
| **H-4** | [NUEVO: R4.1] Ver §3.3. Origen **sí** documentado; falta test directo del reintento. | Bajo: riesgo concreto y acotado (ver §3.3). R4 lo describió como «no descritos con detalle»; eso es **inexacto**. | Autorizar test y corrección de la frase de R4. | Test nuevo: `ANTES_DEL_CIERRE` (opcional, recomendado). Corrección de R4: requiere autorización (ver §7). |
| **H-5** | [NUEVO: R4.1] Ubicación efectiva: los 25 prompts V5 (R0 a R4.1) están en `prompts/V5_0/`. No existe `prompts/V5/`. `docs/V5/` sí existe y contiene los resultados. La convención `prompts/V5/` aparece en `LEGACYMAPPER_V5_ROADMAP.md:243`, `…PROJECT_HISTORY…:1057` y `LESSONS_LEARNED:846`; el segundo ya avisa «puede haber referencias antiguas a `prompts/V5_0/`: comprobar la ruta real». | Nulo en el producto. Riesgo menor de que un agente busque en una ruta inexistente. Además `docs/V5/` y `prompts/V5_0/` no coinciden en sufijo (asimetría). | Elegir convención. | `DOCUMENTAR_Y_ACEPTAR_EXPLICITAMENTE`: proponer «prompts nuevos bajo `prompts/V5/` a partir de V5.3; los existentes permanecen en `prompts/V5_0/`». No mover archivos. R4 lo clasificó bien como menor. |
| **H-6** | [NUEVO: R4.1] Cifras de suite completa por informe: R2 = R3 = 2 322; R3.1 = 2 351; R3.2 = 2 379; R3.3 = 2 407; R3.4 = 2 423; R3.4.1 = 2 441. Crecimiento monótono (+29, +28, +28, +16, +18) coherente con tests añadidos cada ronda. Sin caídas. Baseline V4.3: 2 169 (`PROJECT_STATE.json`) → 2 322 tras V5.1+R2 [NO VERIFICADO el desglose intermedio]. | Ninguno: crecimiento del conjunto, no discrepancia. La cifra de 2 441 sigue siendo [HEREDADO]. | Ninguna. | `SIN_ACCION_POR_FALTA_DE_EVIDENCIA`. |

### 3.1 H-2 — comparación reproducible de las dos rutas IST [NUEVO: R4.1]

**Alcance:** solo lectura. Listado de archivos y SHA-256 (con y sin normalizar CRLF→LF) de los archivos de código y configuración relevantes: extensiones `vb, cs, aspx, ascx, asmx, ashx, master, config, vbproj, csproj, sln, asax, js, sql`. **Exclusiones:** `.git/`, `.vs/`, `bin/`, `obj/`. Procedimiento repetible con `find` + hash en Python (comparar conjuntos de rutas relativas y hash por archivo común).

| Dato | `C:\Users\cgalianj\source\IST_40\Operacional` (A) | `C:\inetpub\wwwroot\2010\IST\Operacional` (B) |
|---|---|---|
| Rama Git | `main` | `feature_df/nec_11_01` |
| `HEAD` | `4ba8719…` | `151dde2…` |
| Entradas en `git status` | 41 | 21 276 |
| Archivos totales (con `.git`) | 18 455 | 20 628 |
| Archivos relevantes | 9 475 | 10 831 |

Resultados: 9 455 archivos en común; **20 solo en A; 1 376 solo en B** (p. ej. `BlSUBSubsidioNew/*.vb` y su `.vbproj` existen solo en B). De los comunes: **9 174 idénticos, 0 diferentes solo por saltos de línea, 281 con contenido distinto** (p. ej. `Jvs/sondanetwebui.js`, `My Project/Resources.Designer.vb`, `Nxt/Workflow/*.ascx`). Ambas son repositorios Git distintos, en ramas y commits distintos, y B tiene un árbol de trabajo con decenas de miles de cambios locales.

**Conclusión:** las rutas **no son el mismo input**. La diferencia no es ambiental (saltos de línea). Las cifras de V5.2 (259 proyectos, 12 642 flujos, 46 567 documentos) provienen de A [HEREDADO: todos los informes R0–R3.4.1 citan A; no se verificó por hash qué versión de A se analizó, y A pudo cambiar desde la corrida]. Toda cifra comparada contra B no sería comparable. **Limitación:** no se comparó el contenido de archivos de otros tipos ni el estado de A en el momento de la corrida.

### 3.2 H-3 — estado de Git [NUEVO: R4.1]

- Modificados (12): `CLAUDE.md`, 3 documentos de continuidad, `pipeline_stages.py`, `run_summary_presenter.py`, `atomic_write.py`, 4 tests históricos (`test_v4_1_r0_maintainability_inventory.py`, `test_v4_2_r3_…`, `test_v4_r13_…`, `test_v4_r14_…`).
- Borrado (1): `docs/V5_0/V5_0_R0_…PROMPT.md` — **movido** a `prompts/V5_0/` (idéntico, C2). Git lo verá como delete + add.
- Sin seguimiento: `docs/V5/` (28 archivos), `prompts/V5_0/` (26 archivos, incluye este prompt), `legacy_documenter/evidence/` (8), `legacy_documenter/documentation_v52/` (31, incluidos defaults JSON), 7 módulos de tests V5, 3 herramientas en `tools/`.
- **Pertenece a V5 (evidencia por rutas y por informes):** todo lo sin seguimiento; `pipeline_stages.py` (+71: construcción de `output/evidence/` y llamada a `generate_documentation_v52`; documentado en V5.1 R2.1/R3.1 y V5.2 R2 §14); `run_summary_presenter.py`; `atomic_write.py`; los 4 tests históricos (ajustes de inventario/manuales para reconocer los paquetes nuevos, según R2 §14).
- **Posiblemente ajeno a V5:** `CLAUDE.md` (añade las reglas de creación de documentación; sin relación con el código) y los 3 documentos de continuidad (mantenimiento de continuidad, no de producto). **No hay archivos claramente ajenos**; la atribución exacta a cada ronda de los 4 tests históricos es [NO VERIFICADO].
- Aviso de Git: `LF will be replaced by CRLF` en 5 archivos (configuración de saltos de línea del sistema); no es un defecto pero puede ensuciar los diffs si se commitea sin `.gitattributes`.
- Existen worktrees de agentes en `.claude/worktrees/` excluidos por `.git/info/exclude`; no afectan al estado.

### 3.3 H-4 — `atomic_write.py` y `run_summary_presenter.py` [NUEVO: R4.1]

**`atomic_write.py` (+35 líneas):** añade `_replace_with_retry` (5 intentos, retroceso desde 50 ms, ~1,55 s máx.) solo ante `PermissionError` en `os.replace`. **Origen y decisión: documentados** en `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md` (causa raíz: bloqueo transitorio de Windows por antivirus/indexador; corrección mínima explícita; ese informe dice que no tocó tests). Por tanto la frase de R4 H-4 («no descritos con detalle en los informes leídos») es inexacta: R4 no leyó ese informe. No atribuyo autoría.
Riesgos concretos:
1. **Sin test directo:** ningún test simula `PermissionError` transitorio, ni agotamiento de reintentos, ni que otras excepciones no se reintentan. Un cambio futuro podría romperlo sin aviso. Comportamiento sin prueba.
2. `documentation_v52/engine.py:15` importa el nombre privado `_replace_with_retry` desde otro paquete (acoplamiento a un símbolo «privado»). Mantenibilidad, no defecto.
3. Efecto en la documentación: el informe PRE_V5_1 declara la intermitencia `r6_intermittent_test` con causa identificada, pero `PROJECT_STATE.json` sigue diciendo «NON_REPRODUCIBLE» (ver H-1).

**`run_summary_presenter.py` (+4):** añade `documentation_v52` a `output_locations` cuando la etapa DOCUMENTATION es SUCCESS. **Origen y decisión documentados** en `V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md` (P-1, «recomendado corregir antes de cerrar») y `V5_2_R3_1_…md` línea 56; **con test** (C4, ambos casos). La afirmación de R4 («no se localizó informe») también es inexacta. Riesgo: ninguno observado.

## 4. Inventario íntegro de deudas de R4 §8.2 (15 entradas)

Tratamientos: **AC** = `ANTES_DEL_CIERRE`, **DA** = `DOCUMENTAR_Y_ACEPTAR_EXPLICITAMENTE`, **FF** = `FASE_FUTURA_POR_CONTRATO`, **SA** = `SIN_ACCION_POR_FALTA_DE_EVIDENCIA`. Ninguna se resolvió aquí. Ninguna requiere cambiar el Evidence Core salvo donde se indica.

| # | Deuda | Qué se observó y evidencia | Clasificación revisada | Efecto real | ¿Ahora sin cambiar contratos? | Acción, riesgo y aceptación | Tratamiento |
|---|---|---|---|---|---|---|---|
| 1 | `gap.method_dependencies_not_available` | R3.4 §: el Evidence Core no relaciona dependencias con el método que las usa. Declarado como *gap* visible en `MANIFEST.json`. | Limitación explícita del contrato (V5.1) | Usuario: no ve «qué método usa esta biblioteca». Sin regresión. | No. Requiere ampliar extracción V5.1. | Ampliar evidencia en fase propia; riesgo: cambia IDs/particiones del Core. Aceptación: relación con provenance y tests de determinismo V5.1. | FF |
| 2 | `gap.method_unresolved_not_attributable` | R3.4: límites no resueltos sin método; vía posible parsear `nodes` de `FunctionalPath`, no implementada. | Limitación explícita | El usuario ve el no resuelto a nivel de proyecto, no de método. | Técnicamente sí en la capa de presentación, pero **no recomendado**: parsear texto de `nodes` en presentación arriesga fabricar atribución (`AGENTS.md`: no fabricar relaciones). | Decidir en fase de evidencia; aceptación: cada atribución con `evidence_refs` y `unresolved` intacto. | FF |
| 3 | `gap.method_identity_no_signatures` / `overloads_ambiguous` | V5.1 no registra firmas ni parámetros; 36 grupos de nombre ambiguo [HEREDADO]. | Limitación explícita | Sobrecargas no distinguibles; declarado. | No. | Cambio de extracción V5.1; riesgo: identidad canónica de métodos/IDs. | FF |
| 4 | `.aspx`/`.ascx` → code-behind | R3.3 §11.4 «mejora opcional». No se verificó si la evidencia actual lo permite [NO VERIFICADO]. | Funcionalidad futura | Navegación menos directa; sigue accesible por el archivo del proyecto. | Solo si la evidencia lo permite (R3.3 dice «cuando lo permita»). | Investigar en medición de V5.3+; riesgo: enlace inventado. Aceptación: enlace solo con evidencia determinista. | FF |
| 5 | P-2 flujo → `archivo:línea` del manejador | R2 F3 / R3. | Funcionalidad futura | Trazabilidad menos fina. | No sin nueva evidencia de línea [NO VERIFICADO]. | Fase posterior. | FF |
| 6 | Texto «N archivos de código» vs. tabla | R3.3 §11.3: dos conteos distintos (ver R3.3 línea 115: «deuda nueva menor de terminología»). | **Defecto menor actual de redacción** (no de datos) | Un lector puede creer que las cifras se contradicen. Impacto bajo. | Sí: cambio de texto en template/i18n declarativo, sin código ni contrato. | Aclarar el rótulo en la plantilla en español; aceptación: test de i18n de R3.3 verde y texto sin ambigüedad sobre lo que cuenta cada cifra. Riesgo: cambia el Markdown (afecta hashes del manifest). | **DA** (o AC si el Technical Lead lo prefiere; coste mínimo) |
| 7 | Clasificación de tipo de proyecto (148/259 sin clasificar) | R3.2 §: solo Web vs. no determinado; 89 Web, 22 controles, 148 sin evidencia suficiente. | Limitación honesta de evidencia | El documento dice «no pudo determinarse»; es correcto, no engañoso. | Posible ampliación con `output_type` del proyecto (ya presente en el ejemplo de BLInterfazSAP) pero exige decisión de diseño [NO VERIFICADO si el campo es fiable en los 259]. | Fase posterior o mejora acotada con verificación. | FF (`SIN_ACCION` para el cierre) |
| 8 | Defaults JSON sin *package data*; modo estricto sin CLI; INTERPRETED sin cargador (V5.5); Renderer HTML y retiro de `documentation/` legacy | R2 §19 puntos 4–5. [NUEVO: R4.1] C7: no hay `pyproject.toml`/`setup.py`; hoy se ejecuta desde el código fuente, así que el punto de *package data* no tiene efecto actual. | Funcionalidad futura / no aplicable hoy | Ninguno hoy. | — | Declarar los defaults si algún día se empaqueta; aceptación: instalar el paquete y ejecutar sin error de defaults. | FF |
| 9 | Ruido residual `Me.X.DataBind()` | R3 P-3: 83 apariciones en 514 documentos; se resuelve con un JSON custom de configuración. | Observación; ajuste por configuración | Algo de ruido en cuerpos de módulo. | Sí, por datos (no por código). | Añadir patrón al set por defecto sería cambio de comportamiento; aceptación: conteo declarado y baja de `Me.X.DataBind()`. | DA |
| 10 | Validación de particionado y defaults solo sobre IST | R2 §19. | Limitación de validación | Riesgo de sobreajuste a IST. | No sin otro repositorio. | Validar con otro repositorio cuando exista; aceptación: partición y defaults correctos sin editar código. | FF |
| 11 | GAP-M1: «módulo» = proyecto | R2. | Funcionalidad futura (V5.5+) | Sin agrupación funcional; declarado. | No. | Requiere interpretación (IA/humana), fuera de V5.2. | FF |
| 12 | Caso «solo transaccional, sin llamadas» no observado en IST | R3.4.1 §12; probado con fixture sintético. | Observación | Ninguno. | — | — | SA |
| 13 | Intermitencia `test_deterministic_run_then_ai_enabled_rerun_same_output` | `PROJECT_STATE.json` (`NON_REPRODUCIBLE`). [NUEVO: R4.1] `PRE_V5_1_RERUN_INTERMITTENCY_…` ya identificó y corrigió una causa raíz (reintento en `atomic_write`); el estado no lo refleja. | Deuda administrativa (estado desactualizado) más el hueco de test de H-4 | Sin recurrencia registrada. | Sí (documental, con H-1). | Reflejar la causa en el estado al cerrar; cubrir el reintento con test. | AC (junto con H-1/H-4) |
| 14 | Escala documental (46 567 docs, ~56 MiB) | R3.4/R3.4.1: aceptada; criterio más estricto delegado al Technical Lead. | Decisión pendiente, no defecto | Volumen alto para revisión humana; enlaces verificados solo por muestra. | Depende de decisión. | Decidir si se acepta la escala actual. Aceptación: decisión registrada. | DA |
| 15 | Mantenibilidad: `technical_documentation_renderer.py`, `transform.py`, `config.py` crecieron; los tests del inventario V4.1-R0 se ajustaron ronda a ronda | R3.x; 4 tests históricos modificados (H-3). | Deuda técnica evitable, pero de refactor | Cada ronda exige retocar el inventario; riesgo de regresión al tocar. | Refactor propio, fuera de este cierre. | Extraer módulos en ronda dedicada, con la suite completa como red. | FF (declarar riesgo alto ya en `PROJECT_STATE.json.maintainability_debt`) |

(La tabla de R4 §8.2 tiene 15 filas; todas están cubiertas en el mismo orden. La fila 8 agrupa varios puntos de R2 §19.)

**Ninguna entrada eleva V5.2 a bloqueo.** Ninguna funcionalidad futura fue tratada como bloqueo. `POST_VERSION` de R4 no fue equiparado con deuda aceptable: las filas 6, 13 y 15 se separan explícitamente como deuda evitable.

## 5. Propuesta acotada antes del cierre (sin implementar)

Ordenada por dependencia:

1. **Decisión de ruta IST oficial (H-2)** — Technical Lead. Sin código. Bloquea la validez de V5.3 como regresión.
2. **Versionar el trabajo V5 (H-3)** — usuario. Preferible antes de cualquier ronda de corrección, para poder revertir. Nota sobre CRLF/LF (§3.2).
3. **Test unitario de `_replace_with_retry` (H-4/fila 13)** — único cambio de código propuesto; solo tests: (a) éxito tras un `PermissionError`; (b) se relanza tras agotar intentos; (c) otra excepción no se reintenta; (d) el temporal se limpia. Simulando `os.replace` y `time.sleep` (sin esperas reales). Aceptación: 4 tests verdes; la suite no cambia salvo el recuento.
4. **Rótulo «N archivos de código» (fila 6)** — opcional, de texto; solo si el Technical Lead lo quiere antes del cierre; si no, `DA`.
5. **Ronda de cierre formal con actualización de estado (H-1, fila 13)** — el prompt debe autorizar editar `PROJECT_STATE.json` y el roadmap, y corregir las frases de R4 sobre H-2 y H-4.

Total: **5 asuntos propuestos antes del cierre** (3 administrativos/de decisión: 1, 2, 5; 2 técnicos: 3 y, opcional, 4). Solo el 3 es código (tests).

## 6. Compatibilidad, pruebas y aceptación de una eventual ronda de corrección

- **Contratos:** el test del punto 3 no toca el Evidence Core, IDs, provenance, confidence, unresolved, compatibilidad V4.3 ni la independencia del runtime. El punto 4 cambia solo la plantilla/i18n; no toca evidencia.
- **Riesgo del punto 4:** modifica el Markdown generado y por tanto el hash/tamaño del manifest y la comparabilidad byte a byte con la corrida heredada; habría que regenerar solo desde evidencia persistida (nunca extraer IST de nuevo).
- **Pruebas necesarias:** los 4 tests nuevos; para el punto 4, tests de i18n/navegación de R3.3 y regeneración dirigida; suite completa una sola vez al final, sin concurrencia.
- **Ninguna propuesta afecta**: separación evidencia/interpretación, IA (fuera de alcance de V5.2), documentación legacy.

## 7. Decisiones que necesita el Technical Lead

1. **Ruta IST oficial** (H-2). Dato clave: son repos distintos (rama `main` vs. `feature_df/nec_11_01`), 281 archivos comunes con contenido distinto y 1 376 archivos relevantes solo en B. Recomendación: mantener A (`IST_40`) como baseline vigente de V5.2 porque respalda todas las cifras; registrar por escrito la decisión y el hash/commit de A usado.
2. **Git** (H-3): cuándo y con qué agrupación versionar; confirmar el tratamiento de los saltos de línea.
3. **Estado** (H-1): autorizar la actualización de `PROJECT_STATE.json` y roadmap en la ronda de cierre.
4. **Corrección de R4:** R4 contiene dos afirmaciones inexactas (H-2 clasificada como observación y H-4 «no descrita»). Según `CLAUDE.md` no se crean documentos retroactivos; se requiere autorización para corregir R4 o para anotarlo en el informe de cierre.
5. Si se quiere test de la suite completa fresca antes del cierre (la cifra de 2 441 es heredada).
6. Tratamiento de filas 6 (AC o DA) y 14 (aceptar escala).
7. Convención `prompts/V5/` vs `prompts/V5_0/` (H-5).

## 8. Archivos creados o modificados

- Creado: `docs/V5/V5_2_R4_1_DIAGNOSTICO_PENDIENTES_DEUDA_TECNICA.md` (este informe).
- Ningún otro archivo del repositorio fue modificado. Temporales fuera del repositorio (listados de archivos y script de comparación en el directorio temporal de la sesión). Los cachés locales del intérprete podrían haberse creado por lecturas; no son salidas de proyecto.

## 9. Estado final y siguiente checkpoint

**V5_2_R4_1_DIAGNOSIS_READY_FOR_HUMAN_REVIEW**

Sin cambios de código, sin commits/push, V5.2 **no** cerrada, V5.3 **no** iniciada. Siguiente checkpoint: revisión humana de este diagnóstico y decisión sobre los puntos de la sección 7 antes de cualquier ronda de corrección o de cierre.
