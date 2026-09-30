# V5.2 R3.2 — Identidad real de proyectos y claridad humana de la documentación

## 1. Estado

V5_2_R3_2_READY_FOR_HUMAN_REVIEW

No se modificó Evidence Core (`legacy_documenter/evidence/*`), V5.1, `documentation/` legacy, el roadmap ni `PROJECT_STATE.json`. Sin commits ni push. La aprobación humana sigue pendiente; esta ronda no cierra V5.2.

## 2. Resultado de investigación BLInterfazSAP

Investigado directamente sobre el repositorio legado (`C:\Users\cgalianj\source\IST_40\operacional`) y sobre `index/projects.json`/`index/solutions.json` de la corrida real de esta ronda:

1. **¿Existe `BLInterfazSAP.vbproj`?** Sí: `bl\BlInterfazSAP\BLInterfazSAP.vbproj`, verificado por lectura directa del archivo en el repositorio legado.
2. **Ruta real:** `bl\BlInterfazSAP\BLInterfazSAP.vbproj` (relativa a la raíz del repositorio).
3. **Registro en Evidence Core:** existe como registro `Project` completo en `index/projects.json`, con `assembly_name: BLInterfazSAP`, `output_type: Library`, `project_references` (a `SysInterfazSAP.vbproj`), `assembly_references` y `compile_items: ["AssemblyInfo.vb", "BLInterfazSAP.vb"]`.
4. **Solution a la que pertenece:** `SlnInterfazSAP` — relación demostrada por `index/solutions.json` (el `.sln` lista el `.vbproj` entre sus proyectos, resuelto por aritmética de rutas determinista).
5. **¿Existe también `BLInterfazSAP.vb`?** Sí, pero es uno de los `compile_items` **dentro** del propio proyecto (un archivo de código, `Component`/`SourceArtifact` en términos de Evidence Core), no un proyecto independiente.
6. **¿La documentación confunde estas entidades?** No, ni antes ni después de esta ronda: el motor de documentación (`transform.py`) construye un módulo únicamente a partir de `source.get("projects", [])` (los registros `Project` reales), nunca a partir de `compile_items`/`content_items`/nombres de clase. `BLInterfazSAP.vb` nunca generó ni genera un documento propio; solo existe `developer/modules/BLInterfazSAP.md`, correspondiente al `.vbproj`.

**Conclusión del caso obligatorio:** BLInterfazSAP **es un Project real**, con evidencia de identidad verificable (archivo `.vbproj`, ruta, registro en Evidence Core, pertenencia a solución). El prefijo `BL` **no** se usa en ningún punto del código para inferir esto — la identidad viene enteramente de la presencia del `.vbproj`. El hallazgo real de esta investigación no fue una identidad falsa, sino dos problemas de **presentación**: (a) el documento mostraba "Tipo de salida: Library" sin aclarar que es un valor técnico de compilación, lo que un lector podía confundir con "es una biblioteca común de utilidades" en vez de "es la salida DLL de este ensamblado .NET en particular"; y (b) su relación con `WebInterfazSAP` aparecía bajo un único encabezado "Proyectos referenciados" sin indicar dirección. Ambos se corrigieron (secciones 5 y 6).

## 3. Verificación de identidad de proyectos

El motor de documentación nunca determinó la identidad de un módulo por prefijo, carpeta, nombre de clase o coincidencia parcial; esto ya era así desde R2 (`transform.py`, comentario "Module == Project (GAP-M1)") y se confirmó y reforzó en esta ronda:

- `AudienceTransformer.transform()` construye `projects = {p["path"]: p for p in source.get("projects", []) if p.get("path")}` — la única fuente de módulos es la partición `projects` de Evidence Core, que a su vez solo contiene registros extraídos de un `.vbproj`/`.csproj` real (`legacy_documenter/extractors/vbproj_extractor.py`, que parsea el XML del archivo de proyecto).
- Ningún módulo se crea a partir de `compile_items`, `content_items`, `entry_points` sin proyecto o `flow_unresolved`: esos elementos, cuando no tienen proyecto identificado, se agrupan bajo `"(sin proyecto asignado)"` (`UNASSIGNED`), nunca bajo un proyecto inventado.
- Se verificó sobre IST real (259 proyectos en `index/projects.json`) que **todo** `module.values["path"]` de la documentación generada termina en `.vbproj` (no se observó ningún caso que no lo hiciera).
- El caso homónimo BLInterfazSAP/`BLInterfazSAP.vb` (sección 2) se generalizó a los 259 proyectos: el nuevo test `test_homonymous_class_file_does_not_create_a_fictitious_project` verifica el mecanismo directamente; no se necesitó ningún cambio de código porque el mecanismo ya era correcto — el trabajo de esta ronda fue **verificar y demostrar** esa corrección, no repararla.

## 4. Jerarquía Solution/Project/Component

Sin cambios de arquitectura (no autorizados por esta ronda). Se confirma que se respeta:

- **Solution → Project:** `_membership()` en `transform.py` resuelve la pertenencia por aritmética de rutas sobre el `.sln` real (no por nombre). Verificado con BLInterfazSAP: pertenece a `SlnInterfazSAP` únicamente (una sola solución en la evidencia real).
- **Un Project compartido entre Solutions no se duplica:** se agregó un test explícito (`test_project_shared_between_solutions_keeps_a_single_identity`) que registra un proyecto en dos soluciones sintéticas y comprueba que sigue existiendo un único módulo, con ambos nombres de solución listados ("Solutions: SlnA, SlnB"), no dos documentos.
- **Component / SourceArtifact:** siguen sin tener documento propio en `documentation_v52` — es la misma limitación ya declarada en R2 (GAP-M1/F1: la evidencia solo demuestra `Project` como agrupación de primera clase para este perfil). No se implementó una vista de componentes/archivos en esta ronda porque el prompt R3.2 lo prohíbe explícitamente ("no rediseñar la arquitectura", "no implementar funcionalidades V5.3+"); se deja como deuda (sección 11), no como regresión.
- **Elementos sin proyecto identificado:** se documentan como `"(sin proyecto asignado)"`, nunca como un Project inventado (verificado, sin cambios respecto de R3.1).

## 5. Tipo técnico de salida

Corregido literalmente como pedía el prompt: `dev.module.summary_text`/`summary_text_sol` en `legacy_documenter/documentation_v52/defaults/i18n/es.json` ahora dicen **"Tipo técnico de salida: {output_type}."** (antes "Tipo de salida"). Se agregó un campo separado, **"Tipo de proyecto"**, calculado en `AudienceTransformer._project_type()` (Audience Transformation, no Evidence Core ni Renderer) a partir de evidencia estructural real ya presente en el propio `.vbproj` (`content_items`, nunca el nombre ni el prefijo):

- Si el proyecto declara al menos un archivo `.aspx` o `Global.asax` entre sus `content_items` → *"Aplicación Web (ASP.NET Web Forms: el proyecto declara archivos .aspx o Global.asax)"*.
- Si solo declara `.ascx` (controles de usuario) sin `.aspx` propio → *"Biblioteca de controles de usuario Web (ASP.NET Web Forms: declara .ascx, sin páginas .aspx propias)"*.
- En cualquier otro caso, el campo queda vacío y el documento dice explícitamente: *"Tipo de proyecto: no pudo determinarse a partir de la evidencia disponible; el «tipo técnico de salida» de arriba es un valor de compilación (Library/Exe/WinExe) y no implica por sí mismo que se trate de una biblioteca de uso común."*

Verificado sobre IST real (259 proyectos, `index/projects.json`): 89 proyectos con evidencia de aplicación Web (.aspx/Global.asax), 22 con evidencia de biblioteca de controles (.ascx sin .aspx), 148 sin evidencia suficiente (campo omitido). **BLInterfazSAP cae en el tercer grupo** — pese al prefijo `BL` y a `output_type: Library`, el documento dice honestamente que no pudo determinarse el tipo de proyecto. **WebInterfazSAP** sí declara `Default.aspx`/`Global.asax` y se clasifica correctamente como Aplicación Web. Confirmado con la doc real generada (ver `human_review_sample`).

## 6. Dirección de dependencias

Corregido en la capa de Audience Transformation (`transform.py`) y Template (`dev.dependency_summary.json`, `dev.technical_detail.json`), sin tocar el Renderer:

- `module.slots["project_refs"]` (una sola lista con un campo `direction` mezclando ambos sentidos) se reemplazó por dos slots separados: `project_refs_out` (`entry["refs_out"]`, A → B: "lo que este proyecto usa") y `project_refs_in` (`entry["refs_in"]`, C → A: "lo que usa a este proyecto"). `config.py` (`MODULE_SLOT_FIELDS`) se actualizó para reflejar los nuevos nombres de fuente.
- El template `dev.dependency_summary.json` ahora renderiza dos tablas con encabezados distintos: **"Proyectos que este proyecto utiliza"** y **"Proyectos que utilizan este proyecto"**, cada una con columna `Ruta` (código, para distinguir homónimos) además de `Proyecto`. `dev.technical_detail.json` gana las particiones `deps-out`/`deps-in` correspondientes para que el enlace "ver todos" funcione también en dependencias (antes ese enlace apuntaba a un documento que no las incluía).
- **Caso obligatorio BLInterfazSAP/WebInterfazSAP verificado sobre IST real:** el documento `WebInterfazSAP.md` dice *"Proyectos que este proyecto utiliza: BLInterfazSAP"*; el documento `BLInterfazSAP.md` dice *"Proyectos que utilizan este proyecto: WebInterfazSAP"*. La dirección real (`WebInterfazSAP` → `BLInterfazSAP`, según `dependencies.json`, tipo `Project -> Project`) se preserva sin invertir.
- Las dependencias no demostradas siguen sin clasificar: un proyecto sin ninguna arista `Project -> Project` declarada muestra ambas tablas vacías (comprobado con `SysInterfazSAP` en el test `test_unproven_dependency_stays_unclassified_not_invented`); nunca se infiere una dependencia por nombre o prefijo.

## 7. Información no resuelta y ruido

Cambio puramente declarativo, en `legacy_documenter/documentation_v52/defaults/noise/default.json` (ninguna lógica Python nueva), como pedía el prompt. Se agregaron patrones a la categoría existente `ui_control_calls` (visibilidad `hide`, `detail_availability: true` — igual que `DataBind`, ya existente desde R3.1):

- `GetColumnByDataField` (nombre exacto de la llamada, sin ambigüedad).
- `System.Web.UI.WebControls.Unit(` y `Unit.Parse(` (por prefijo del `label` completo, no por el nombre corto "Unit" ni "Parse", para no arrastrar `Integer.Parse`/`Int64.Parse`, que sí son información funcional real).
- `Response.Write(` y `Me.Response.Write(` (por prefijo del `label` completo, no por el nombre corto "Write", para no arrastrar `sw.Write`/`file2.Write`, que son E/S de archivos real).

Ninguna de estas llamadas se declara "resuelta": siguen siendo `UnresolvedBoundary`/`flow_unresolved` en la evidencia; solo se les baja la prominencia en el cuerpo del documento (se excluyen de la tabla de "más frecuentes", igual que ya ocurría con `DataBind`) y quedan íntegras en el documento de detalle (`.../detail.md`).

**Verificado con evidencia real, antes/después, sobre el mismo proyecto (`WebFicha`):**

| | Antes (R3.1) | Después (R3.2) |
|---|---|---|
| Fila más frecuente en "Puntos no resueltos" | `DgrDeudaPrev.GetColumnByDataField( )` — 42 | `Me.tpaBusEmpresa.ParametrosAdicionales( )` — 24 (una llamada de negocio real) |
| "Se omiten del cuerpo N elementos de infraestructura" | 172 | 214 (+42, exactamente las apariciones de `GetColumnByDataField` reclasificadas) |
| ¿`GetColumnByDataField` sigue disponible? | En el detalle | En el detalle (verbatim, sin truncar) |

A escala de todo el repositorio: sobre 162 914 registros `flow_unresolved`, 7051 (4,3%) corresponden a estos tres patrones y ahora quedan relegados al detalle en todos los módulos afectados. Verificado con una búsqueda sobre los 860 documentos `developer/modules/*.md` de la corrida real: **0** documentos de módulo (cuerpo) contienen ya `GetColumnByDataField(`, `WebControls.Unit(` o `Response.Write(` literalmente; **17** documentos de detalle sí los conservan.

## 8. Compatibilidad con R3.1

Verificado, sin regresiones, ejecutando la suite completa de R3.1 sin modificar (`tests/test_v5_2_r3_1_human_semantic_corrections.py`, 29 tests, todos en verde) más una comprobación puntual adicional sobre la corrida IST real de esta ronda:

- **Métrica de 672 recorridos reales:** intacta. `general/README.md` de la corrida real dice textualmente *"Se observaron 12642 recorridos: 672 (5.3%) llegan a una operación real de datos [...] otros 1698 llegan solo a operaciones de control de transacciones"*.
- **Propiedad real de pantallas / recorridos originados vs. recibidos / acceso directo vs. indirecto:** sin cambios de código en `transform.py` más allá de lo descrito en las secciones 5-7; los tests de R3.1 que cubren estos puntos pasan sin modificación.
- **Clasificación prudente de dependencias externas, terminología humana, compatibilidad legacy:** sin cambios; `documentation/` legacy sigue con 876 archivos (mismo número que en la corrida de R3.1).
- **`documentation_v52` en RUN_SUMMARY:** confirmado en la corrida real (`Output locations` incluye `documentation_v52`).

## 9. Prueba IST

Corrida real nueva, sin sobrescribir corridas anteriores: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\run` (comando: `python main.py full "C:\Users\cgalianj\source\IST_40\operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\run" --verbose`).

- `full run: SUCCESS`; todas las etapas `SUCCESS` (AI_INTERPRETATION/PROPOSAL_GENERATION: `NOT_RUN`, sin IA solicitada). `Output locations` incluye `documentation_v52`.
- `documentation_v52/`: 866 archivos, 9,13 MB, 0 advertencias (`MANIFEST.json.warnings == []`).
- **0 enlaces internos rotos** sobre 2744 enlaces relativos revisados en los 866 documentos.
- **0** apariciones de ids internos (`FLOW-`, `PATH-`, `DAO-`, `EP-`, etc.) o claves de catálogo faltantes (`[[dev....]]`) en toda la salida humana.
- `documentation/` legacy: 876 archivos (mismo número que la corrida V5.2 R3.1 previa), no tocada por esta ronda.
- Verificación de identidad puntual: `bl\BlInterfazSAP\BLInterfazSAP.vbproj` y `WebInterfazSAP.vbproj` existen ambos como registros `Project` en `index/projects.json` de esta corrida, con `project_references` cruzadas exactamente como se documenta (`WebInterfazSAP.project_references` incluye `BLInterfazSAP.vbproj`).

## 10. Suite completa

`python -m unittest discover -s tests`: **2379 tests, 0 fallas, 0 errores, 132 skips** (los esperados de checkout limpio). Incluye los **28 tests nuevos** de `tests/test_v5_2_r3_2_project_identity_and_human_clarity.py` (identidad real de proyecto, homónimo sin proyecto ficticio, pertenencia Solution→Project, proyecto compartido entre soluciones, homónimos distinguibles por ruta, tipo de salida vs. tipo de proyecto, dependencias entrantes/salientes separadas y no invertidas, ruido declarativo relegado sin perder el detalle, contrato de template rechazando la fuente antigua `project_refs`, spot-check de no regresión R3.1, determinismo y `documentation/` legacy intacta). Los 91 tests previos de R2/R3.1 (`test_v5_2_r2_documentation_engine.py`, `test_v5_2_r3_1_human_semantic_corrections.py`) pasan sin modificación de sus aserciones.

## 11. Deuda restante

1. **Nivel Component/Archivo no documentado como entidad propia.** La jerarquía completa Sistema→Solutions→Projects→Componentes→Archivos que pide el prompt solo llega hasta Project en `documentation_v52`; Component/SourceArtifact existen en Evidence Core pero no tienen documento propio (mismo GAP-M1/F1 ya declarado en R2). Implementarlo es una ampliación de alcance del motor (nuevos templates, nuevo nivel de navegación), no una corrección de presentación puntual; se deja fuera de esta ronda por la restricción explícita de no rediseñar la arquitectura ni implementar funcionalidades V5.3+.
2. **Clasificación de "Tipo de proyecto" limitada a Web vs. no determinado.** No se intentó distinguir aplicaciones de escritorio (WinExe/consola) de bibliotecas de consola por falta de evidencia estructural igual de fuerte que `.aspx`/`Global.asax`; 148/259 proyectos reales quedan sin esta clasificación (correcto y honesto, pero es una limitación de la evidencia disponible, no un defecto).
3. Deudas ya declaradas en R2/R3/R3.1 y no afectadas por esta ronda: enlace flujo→archivo:línea del manejador (P-2), particionado del índice bajo límites extremos, defaults JSON no declarados como *package data*, modo estricto sin CLI, Renderer HTML y retiro de `documentation/` legacy fuera de alcance.

## 12. Ruta de muestra humana

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\human_review_sample\README.md`

Copias exactas (verificadas con `cmp`, sin edición manual) de: Vista General completa (5 documentos), índice Developer, `BLInterfazSAP` (caso obligatorio de identidad), `WebInterfazSAP` (caso obligatorio de dirección de dependencia), `WebMEDPabellon` (proyecto Web), `blPENResoluciones` (proyecto de lógica de negocio), `sysPENResoluciones` (acceso directo), `WebPENCalculoPensionIndem` (acceso indirecto), `WebFicha` + su detalle técnico (información no resuelta, con el antes/después de la sección 7 verificable en el propio documento), `WebADHTraspaso`/`WebADHTraspaso-2` (proyectos homónimos/copia Backup). 16 archivos. Los enlaces entre los documentos incluidos funcionan; los enlaces a proyectos fuera de la muestra no abren.

Documentación completa regenerada de esta ronda: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\run\documentation_v52\`.

## 13. Qué debe revisar el Technical Lead

Respuestas de este agente, con evidencia — no reemplazan la aprobación humana, que sigue pendiente:

1. **¿BLInterfazSAP es un Project real o un archivo/componente?** Es un Project real: existe `BLInterfazSAP.vbproj`, registrado en Evidence Core, con solución asociada demostrada. El archivo `BLInterfazSAP.vb` homónimo es un archivo de código dentro de ese mismo proyecto, no una entidad separada, y la documentación nunca lo trata como tal (sección 2).
2. **¿Los Projects documentados corresponden a proyectos reales?** Sí, verificado mecánicamente: todo módulo documentado proviene exclusivamente de `source["projects"]` y su ruta termina en `.vbproj`; no se observó ningún módulo construido por prefijo, carpeta o nombre de clase (sección 3).
3. **¿Se puede navegar de una Solution a sus Projects?** Sí, por ruta real (no por nombre); un proyecto compartido entre dos soluciones conserva una única identidad (sección 4, con test dedicado).
4. **¿Es claro qué depende de qué?** Ahora sí hay dos encabezados separados ("utiliza" / "es utilizado por"), verificado en el caso obligatorio BLInterfazSAP/WebInterfazSAP con la dirección real preservada (sección 6). Antes de esta ronda ambas relaciones aparecían mezcladas bajo un único título sin indicar sentido.
5. **¿Es claro qué significa "Library"?** Ahora se llama explícitamente "Tipo técnico de salida" y, cuando hay evidencia estructural suficiente, se agrega un campo separado "Tipo de proyecto" (p. ej. "Aplicación Web"); cuando no hay evidencia (como en BLInterfazSAP) el documento lo dice explícitamente en vez de guardar silencio o dejar que el lector infiera algo del prefijo (sección 5).
6. **¿La información no resuelta es más legible?** Sí: tres patrones de ruido de interfaz muy frecuentes (`GetColumnByDataField`, `System.Web.UI.WebControls.Unit`, `Response.Write`) ya no compiten por espacio con problemas funcionales reales en la tabla principal, sin declararse nunca "resueltos" y sin perder el detalle (sección 7, con caso antes/después real).
7. **¿La Vista General explica la estructura?** Sin cambios respecto de R3.1 (ya aprobado técnicamente en esa ronda); esta ronda no tocó `general/README.md` salvo lo que hereda automáticamente de los conteos actualizados.
8. **¿Se mantienen las correcciones de R3.1?** Sí, verificado con la suite de R3.1 intacta y una comprobación puntual sobre la corrida real (sección 8).

Puntos abiertos que el Technical Lead debe decidir explícitamente: si el nivel Component/Archivo debe convertirse en una futura ronda de ampliación de alcance (deuda 1, sección 11), y si la clasificación binaria "Aplicación Web / no determinado" de tipo de proyecto es suficiente para R4 o si se requiere evidencia adicional para otros tipos (deuda 2).

## 14. Conclusión

El caso obligatorio de la ronda (BLInterfazSAP) se investigó con evidencia directa del repositorio legado y de Evidence Core: es un proyecto real, correctamente identificado, y la documentación nunca lo confundió con el archivo homónimo — el mecanismo de identidad (módulo == `Project` real, nunca inferido por nombre/prefijo/carpeta) ya era correcto desde R2 y se verificó explícitamente en esta ronda con nuevos tests. Los problemas reales encontrados eran de presentación, no de identidad: la etiqueta "Tipo de salida" podía confundirse con una clasificación funcional, y la sección de dependencias mezclaba ambas direcciones bajo un único título. Ambos se corrigieron en la capa de Audience Transformation y de Templates (declarativos), sin tocar Evidence Core ni el Renderer, y sin invertir ninguna relación real. El ruido de tres llamadas de interfaz muy frecuentes se relegó por configuración declarativa, sin ocultar información ni declararla resuelta. Todo se verificó sobre una corrida real de IST completa (866 documentos, 0 advertencias, 0 enlaces rotos) y sobre 2379 tests (0 fallas, 0 errores), incluidos 28 tests nuevos específicos de esta ronda. Las correcciones de R3.1 se preservan. Queda pendiente, y fuera del alcance autorizado de esta ronda, la ampliación del nivel Component/Archivo como entidad documentada de primera clase (deuda 1). La aprobación humana sigue siendo obligatoria; este agente no puede otorgarla en nombre del Technical Lead.

V5_2_R3_2_READY_FOR_HUMAN_REVIEW
