# V5.2 R3.3 — Navegación Project → Component/Archivo y evidencia bajo demanda

## 1. Estado

V5_2_R3_3_READY_FOR_HUMAN_REVIEW

No se modificó Evidence Core (`legacy_documenter/evidence/*`), V5.1, `documentation/` legacy, el roadmap ni `PROJECT_STATE.json`. Sin commits ni push. La aprobación humana sigue pendiente; esta ronda no cierra V5.2 ni autoriza V5.4.

## 2. Qué se implementó

Navegación progresiva completa **Solution → Project → Component/Archivo → Métodos → Evidencia técnica detallada**, extendiendo únicamente la capa de Audience Transformation / Profile / Template (nunca Evidence Core, nunca el Renderer):

- **`categories.py`**: tres modelos neutrales nuevos — `SolutionModel`, `FileModel` (un `SourceArtifact`), `ComponentModel` (una clase-como-símbolo o un WebForm/UserControl/MasterPage). `AudienceDocumentModel` gana `solutions`/`files`/`components`.
- **`transform.py`**: pertenencia Project→Archivo derivada solo de evidencia real (`compile_items`/`content_items`, aritmética de rutas determinista, la misma que ya usa `apply_project_namespaces` del pipeline en vivo); un archivo con 0 coincidencias queda «sin proyecto asignado», con 2+ coincidencias queda declarado explícitamente **ambiguo** (nunca adivinado); un archivo puede tener varios `Component` (agrupados, nunca duplicados visualmente); un componente siempre conoce su archivo de origen; los métodos provienen únicamente de `Symbol.members` (nombre/tipo/visibilidad/compartido — nunca línea, porque el extractor no la produce; nunca se inventa); navegación Solution→Project reutilizando la pertenencia ya resuelta, con una sola identidad por proyecto aunque pertenezca a varias soluciones.
- **`config.py`**: tres ámbitos de template nuevos (`solution`, `file`, `component`), cada uno con su propia lista blanca de campos (ningún id interno queda accesible a un template).
- **`template.py`**: el motor de templates construye contextos para los tres ámbitos nuevos; resolución de enlaces "volver" ahora depende del ámbito de origen y destino (Método→Componente→Archivo→Proyecto→Solution, cada nivel con su propia clave de navegación); las celdas de tabla soportan enlaces `module|solution|file|component`; el mecanismo existente de tabla con "ver todos" (`overflow: detail`) ahora acepta apuntar a un template de detalle distinto del de proyecto (`dev.component_detail`).
- **`engine.py`**: nueva partición de evidencia `symbols`; `webform_components` (registros reales de WebForm, no solo el conteo que ya existía como `webforms`).
- **Templates nuevos** (JSON declarativos, sin Markdown embebido en Python): `dev.solution.json`, `dev.file.json`, `dev.component.json`, `dev.component_detail.json`. `dev.module.json` gana dos secciones aditivas («Soluciones», con enlaces; «Componentes y archivos», tabla particionada); `dev.index.json` gana un índice de soluciones.
- **`es.json`**: ~45 claves nuevas, sin jerga de motor ni de Evidence Core.
- **General Overview**: sin cambios de templates (`general_overview.json` no referencia ninguno de los templates nuevos) — nada de esto se filtra ahí, verificado por test y por lectura del `general/README.md` real (sección 9).

## 3. Navegación Solution → Project

`dev.solution.json` (ámbito `solution`, un documento por `.sln` real en `developer/solutions/<slug>.md`): nombre, ruta del `.sln`, cuántos proyectos reales contiene y una tabla con enlaces a cada documento de proyecto real. `dev.index.json` gana un índice completo de soluciones (particionado con la misma política que el resto). Un proyecto compartido entre varias soluciones (caso ya verificado en R3.2 con BLInterfazSAP/`SlnInterfazSAP`+`ModuloBL`) conserva una única identidad: la Solution solo enlaza al documento de proyecto ya existente, nunca lo duplica. Cada documento de proyecto gana una sección «Soluciones» con enlaces de vuelta a cada Solution a la que pertenece (antes solo mostraba el nombre como texto plano).

## 4. Navegación Project → Component/Archivo

Cada documento de proyecto gana la sección «Componentes y archivos»: una tabla particionada (índice de archivos) con archivo, tipo (`Código VB.NET` / `Formulario web (.aspx)` / `Control de usuario (.ascx)` / `Página maestra (.master)`) y cantidad de componentes, enlazando a un documento por archivo. Un archivo puede tener 0 (declarado, no oculto — ver sección 6), 1 o varios componentes; el documento de archivo lista cada uno con su tipo y cantidad de métodos, enlazando al documento de componente. El documento de componente muestra tipo, proyecto, archivo de origen, espacio de nombres, herencia/implementación (cuando la evidencia lo declara) y sus métodos (nombre/tipo/visibilidad/compartido), con «ver todos» hacia el detalle cuando excede el límite del cuerpo. Ningún nivel superior enumera cientos de archivos/componentes/métodos: el particionado combinado de R2 (`max_items_per_part`/`max_bytes_per_part`) se aplicó también aquí (sección 7).

## 5. Métodos y evidencia bajo demanda

Los métodos de un componente provienen exclusivamente de `Symbol.members` (extraído por `VBNetExtractor`: nombre, `Sub`/`Function`/`Property`, accesibilidad, si es `Shared`). El extractor **nunca** produce una línea para un miembro (a diferencia del acceso a datos, que sí trae `archivo:línea`): ningún documento de esta ronda muestra ni inventa una línea de método. Un componente sin miembros detectables lo declara explícitamente («No se identificaron métodos con evidencia suficiente... puede que el análisis estático no haya podido reconocerlos») en vez de guardar silencio o inventar. El documento de detalle bajo demanda (`dev.component_detail.json`, un documento por componente en `.../<componente>/detail.md`) es la misma evidencia ya recopilada, mostrada completa y particionada — no ejecuta ningún análisis ni IA al abrirse; se verificó explícitamente (sección 9, prueba de detalle) que el detalle nunca contiene datos ausentes del resumen.

## 6. Identidad y pertenencia

Se preservó estrictamente `Solution != Project != Component != SourceArtifact`, verificado sobre IST real:

- Ningún proyecto se crea a partir de un nombre de clase, carpeta, prefijo o archivo de código: los 259 módulos siguen viniendo exclusivamente de `source["projects"]` (mecanismo de R2/R3.2, no tocado).
- La pertenencia Project→Archivo se deriva solo de `compile_items`/`content_items` reales, con la misma aritmética de rutas que el pipeline en vivo ya usa para resolver `Symbol.project_path` (`apply_project_namespaces`); cuando el símbolo ya trae un `project_path` resuelto (caso no ambiguo, mayoría de los casos), se reutiliza directamente en vez de recalcularlo.
- **Ambigüedad real encontrada en IST** (no un caso sintético): `img\aceptar.gif` coincide con los `content_items` de 5 proyectos distintos (`WebInterfazSAP`, `WebMEDAgendaNew`, `WebMEDMovilizacion`, `WebPENConcurrencia`, `WebPENProcesoResoluciones`) — el motor lo declara explícitamente ambiguo y no lo asigna a ninguno, en vez de escoger uno por orden o por coincidencia parcial. Nuevo gap `gap.file_ownership_ambiguous`, presente en la corrida real.
- Un archivo declarado por un proyecto (`compile_items`/`content_items`) pero sin ningún componente extraíble (p. ej. `AssemblyInfo.vb`, que solo contiene atributos de ensamblado) **sigue apareciendo** en el índice de archivos del proyecto, con 0 componentes — nunca desaparece silenciosamente (hallazgo corregido durante esta misma ronda, sección 9).
- Un archivo homónimo en dos proyectos reales distintos (mismo nombre base, rutas físicas distintas) produce dos documentos de archivo distintos, sin colisión de nombre (slugs anidados bajo el proyecto).

## 7. Particionado

Se reutilizó literalmente el sistema combinado de R2 (`PartitionPolicy`, `max_items_per_part`/`max_bytes_per_part`, el mismo `MarkdownRenderer`) para: el índice de archivos de cada proyecto (`partitioned_table`), el índice de soluciones del sistema, y el detalle de métodos de cada componente. No se escribió ninguna lógica de particionado nueva. Verificado con un test sintético que fuerza un límite artificialmente bajo (10 elementos/parte) sobre 40 métodos de un componente inventado para la prueba: produce ≥2 partes navegables. Sobre IST real, el archivo más grande de todo `documentation_v52/` sigue siendo 52 299 bytes (perfil developer), muy por debajo del límite de 65 536.

## 8. Compatibilidad con R3.2

Verificado sin regresiones sobre la corrida IST real de esta ronda:

- Identidad real de BLInterfazSAP: intacta (`bl\BlInterfazSAP\BLInterfazSAP.vbproj`, solución `SlnInterfazSAP`, 31 métodos reales en su único archivo `.vb`).
- Solution→Project: ahora con documento propio y enlaces (antes solo nombres en texto).
- Proyecto compartido entre Solutions: `BLInterfazSAP` sigue siendo un único documento.
- Pantallas propias vs. flujos recibidos, acceso directo vs. indirecto: sin cambios de código; secciones intactas en `BLInterfazSAP.md`/`blLiquidacion.md` reales.
- Dirección de dependencias: `WebInterfazSAP.md` sigue diciendo «Proyectos que este proyecto utiliza: BLInterfazSAP»; `BLInterfazSAP.md` sigue diciendo «Proyectos que utilizan este proyecto: WebInterfazSAP».
- Tipo técnico de salida vs. tipo de proyecto: intactos (`WebInterfazSAP` → Aplicación Web; `BLInterfazSAP` → no determinado, con la misma explicación honesta de R3.2).
- Métrica real de acceso a datos: `general/README.md` real sigue diciendo «672 (5.3%) llegan a una operación real de datos [...] 1698 llegan solo a operaciones de control de transacciones».
- Ruido técnico: sin cambios de política; se sigue resumiendo con conteo y categoría.
- `RUN_SUMMARY`: `documentation_v52` sigue listado en `Output locations` de la corrida real.
- Custom templates, AI OFF, independencia de runtime: sin cambios de código; suite de R2 (`SeparationAndIndependenceTests`, `TemplateTests`) pasa sin modificar sus aserciones.

## 9. Validación IST

Corrida real completa, sin sobrescribir corridas anteriores: `python main.py full "C:\Users\cgalianj\source\IST_40\operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_2_r3_3_validation\run" --verbose`. Resultado: `full run: SUCCESS`, las 10 etapas deterministas `SUCCESS`, `AI_INTERPRETATION`/`PROPOSAL_GENERATION` `NOT_RUN` (sin IA solicitada). `Output locations` incluye `documentation_v52`.

Durante la lectura física de los documentos reales (no solo el código de salida) se encontraron y corrigieron dos defectos reales de esta ronda, ambos con test de regresión y verificados de nuevo sobre una regeneración real:

1. **Archivos declarados sin componente desaparecían del índice.** `BLInterfazSAP.md` decía «el proyecto declara 2 archivos de código» pero el índice nuevo solo mostraba 1 fila (`BLInterfazSAP.vb`); `AssemblyInfo.vb` (declarado en `compile_items`, sin clase extraíble) no aparecía. Corregido sembrando un `FileModel` con 0 componentes para todo archivo declarado por `compile_items`/`content_items` sin símbolo asociado — exactamente lo que el propio ejemplo conceptual de la sección 7 del prompt de esta ronda muestra («AssemblyInfo.vb → Ver detalle»). Verificado: ahora dice «2 archivos» y muestra 2 filas.
2. **Un componente WebForm mostraba su ruta completa como nombre.** `Componente proyectos\slnADHEmpresa\slnADHEmpresa\Default.aspx` en vez de `Componente Default.aspx` (Evidence Core usa la ruta completa como identidad interna de un WebForm; eso no debía filtrarse como nombre visible). Corregido usando el nombre base del archivo. Verificado sobre la misma corrida real regenerada.

Ambas correcciones se aplicaron regenerando `documentation_v52/` desde la `evidence/` ya persistida de la corrida real (mecanismo ya legitimado en R2/R3: misma evidencia, sin volver a correr los ~30 minutos de extracción), dos veces, hasta confirmar 0 advertencias.

**Medición final** (segunda regeneración, la que se leyó y se usó para la muestra humana): `documentation_v52/` = 25 160 archivos, 24,65 MB, **0 advertencias** (`MANIFEST.json.warnings == []`), archivo máximo 52 299 bytes. Perfil `general_overview`: 5 archivos, 8963 bytes (sin cambios). Perfil `developer_technical`: 25 154 archivos (antes de esta ronda, R3.2: 860).

Comprobaciones automáticas sobre la salida real completa:

- **Enlaces relativos**: muestra aleatoria de 2000/25 160 documentos, 3874 enlaces revisados — **0 rotos**.
- **Ids internos / hashes**: búsqueda de `CMP-`/`SRC-`/`PRJ-`/`SOL-`/`FLOW-`/`DAO-`/`PATH-`/`EP-`/`UNRES-`/`XDP-`/`CAL-` y hashes de 40-64 hex sobre los 25 154 documentos de `developer/` — **0 apariciones**.
- **Lectura física** (no solo scripts): `general/README.md` completo, `developer/README.md`, la cadena completa Solution→Project→Archivo→Componente→Método→Detalle de `BLInterfazSAP`, un proyecto Web (`WebInterfazSAP`) con su detalle, un proyecto con varios componentes reales por archivo (`blLiquidacion`/`LiquidacionCodeCompletion.vb`, 4 clases), y el caso real de ambigüedad de pertenencia (`aceptar.gif`).
- `documentation/` legacy: no tocada por esta ronda (el motor no la lee ni escribe; test existente sin modificar).

## 10. Suite

`python -m unittest discover -s tests`: **2407 tests, 0 fallas, 0 errores, 132 skips** (los esperados de checkout limpio) — confirmado en una corrida final limpia después de todas las correcciones de esta sección. Incluye los **28 tests nuevos** de `tests/test_v5_2_r3_3_component_navigation.py` (Project→SourceArtifact real vía `compile_items`/`content_items`, pertenencia de WebForm vía `content_items` y no por la dependencia que lo usa, ausencia de asignación por nombre/carpeta, archivo con pertenencia genuinamente ambigua declarada como tal con su gap de sistema, archivo declarado sin componente con documento de 0 componentes, archivo con varios componentes sin duplicación visual, homónimos en proyectos distintos distinguibles, métodos solo desde evidencia real sin línea inventada, componente sin miembros sin métodos inventados, WebForm sin métodos inventados, Solution→Project con proyecto compartido sin duplicar, navegación de ida y vuelta completa Método→Componente→Archivo→Proyecto→Solution verificada siguiendo los enlaces reales en disco, 0 enlaces rotos, ausencia de ids internos, evidencia de detalle idéntica al resumen, documentos principales pequeños, Vista General no afectada, particionado bajo límite forzado, determinismo, legado intacto, y el nombre visible correcto de un componente WebForm). Se actualizaron dos veces (dos correcciones de código distintas de esta ronda, cada una con su propio cambio en la métrica correspondiente) las aserciones de `tests/test_v4_1_r0_maintainability_inventory.py` (comparación frozen-vs-fresh del inventario de mantenibilidad V4.1-R0): el nuevo código de `transform.py`, al ganar funciones propias documentadas, desplaza el promedio relativo de cobertura de docstrings del repositorio (mecánica ya documentada y aplicada en R2/R3.1/R3.2 en cada ronda) y, por tamaño, entra al top-N de funciones más grandes — ninguna de las dos es una regresión de comportamiento; ambas están explicadas con comentarios en el propio test, igual que las de rondas anteriores.

## 11. GAPs y deuda restante

1. **Nuevo — ambigüedad de pertenencia de archivo.** `gap.file_ownership_ambiguous`: algunos archivos (casos reales encontrados en IST, p. ej. imágenes/recursos compartidos como `aceptar.gif`) coinciden estructuralmente con varios proyectos; se declaran ambiguos y no se asignan a ninguno. Es una limitación honesta de la evidencia (varios proyectos realmente declaran el mismo archivo físico), no un defecto.
2. **Heredado, sin cambios — método → archivo:línea del manejador de flujo (P-2, R3/R3.1).** No afecta a esta ronda: los métodos de un componente sí muestran su archivo de origen (a través del documento de archivo que los contiene); lo que sigue sin `línea` es el propio miembro (nunca lo tuvo el extractor) y el manejador de un evento de flujo (deuda ya declarada, no ampliada ni resuelta aquí).
3. **Terminología: "N archivos de código" vs. índice de archivos.** El párrafo heredado de R3.1 «El proyecto declara N archivos de código» (en `dev.module.own_text`) cuenta solo `compile_items` (archivos `.vb`/`.cs`, vía la relación `Project -> SourceFile` de `dependencies.json`); la nueva tabla «Componentes y archivos» de esta ronda incluye también `content_items` (`.aspx`/`.ascx`/`.master`/otros recursos declarados). Para un proyecto Web esto significa que el número de la frase y la cantidad de filas de la tabla pueden diferir legítimamente (cuentan cosas distintas), lo que puede leerse como inconsistente a primera vista. No se tocó el texto heredado (fuera del alcance autorizado de esta ronda modificar redacción ya aprobada en R3.1); se dimensiona como mejora textual menor para una ronda futura, no como defecto de datos.
4. **`Component`/`SourceArtifact` del ámbito .aspx/.ascx sin método cuando el código real vive en el code-behind.** Un WebForm (`Default.aspx`) nunca tiene métodos propios (correcto: su marcado no los declara); los métodos reales del formulario viven en su clase code-behind (`Default.aspx.vb`), que es un componente **distinto**, en un archivo distinto, con su propio documento — no están enlazados automáticamente entre sí más allá del campo informativo «Código subyacente» ya mostrado. Enlazar directamente el componente `.aspx` a su componente code-behind (cuando la evidencia lo permite, vía `codebehind`) es una mejora de navegación razonable para una ronda futura; no se implementó aquí para no ampliar el alcance más allá de lo pedido.
5. Deudas ya declaradas en R2/R3/R3.1/R3.2 y no afectadas por esta ronda: defaults JSON no declarados como *package data*; modo estricto sin CLI; INTERPRETED sin cargador desde el pipeline; Renderer HTML y retiro de `documentation/` legacy fuera de alcance; clasificación "Tipo de proyecto" limitada a Web vs. no determinado.

## 12. Ruta de muestra humana

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_3_validation\human_review_sample\README.md`

28 archivos: copias exactas (sin edición manual) de la corrida real regenerada, con los 10 elementos de la sección 19 del prompt y los documentos de destino reales necesarios para que los recorridos seleccionados —incluida la cadena completa Solution→Project→Archivo→Componente→Método→Evidencia detallada, con ida y vuelta— funcionen de punta a punta dentro de la propia muestra (verificado programáticamente: 51 enlaces internos de la muestra resueltos correctamente; los enlaces hacia contenido fuera de la selección quedan señalados como tales en el propio `README.md` de la muestra, permitido explícitamente por el prompt de esta ronda).

Documentación completa regenerada de esta ronda: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_3_validation\run\documentation_v52\`.

## 13. Qué debe revisar el Technical Lead

1. **¿La navegación Solution→Project→Archivo→Componente→Método→Detalle es clara y natural?** Seguirla en la muestra humana, empezando por `README.md` → el primer recorrido destacado.
2. **¿La distinción Component vs. SourceArtifact vs. Project vs. Solution queda clara para alguien sin conocer estos términos de antemano?** Revisar especialmente `BLInterfazSAP.vb` (archivo) vs. `BLInterfazSAP` (componente/clase) vs. `BLInterfazSAP.vbproj` (proyecto), los tres con el mismo nombre visible pero documentos y roles distintos.
3. **¿El caso de ambigüedad real (`aceptar.gif`, 5 proyectos) se explica de forma comprensible, sin sonar a error del sistema?**
4. **Deuda 3 (sección 11): ¿el desajuste entre «N archivos de código» y la tabla de archivos molesta lo suficiente como para pedir su corrección ahora, o queda para una ronda futura?**
5. **Deuda 4 (sección 11): ¿vale la pena, en una ronda futura, enlazar un componente `.aspx`/`.ascx` directamente a su componente code-behind cuando la evidencia lo permite?**
6. **¿El documento principal de cada proyecto sigue siendo suficientemente breve** (ejemplos reales de ~2 KB en la muestra) **pese a la nueva sección de componentes y archivos?**
7. Aprobar la muestra, pedir ajustes, o bloquear la ronda.

## 14. Conclusión

Se implementó la navegación progresiva completa que pedía la ronda — Solution → Project → Component/Archivo → Métodos → Evidencia técnica detallada — extendiendo solo Audience Transformation, Profile y Template (nunca Evidence Core, nunca el Renderer, sin Markdown construido a mano en Python: todo declarativo en JSON, siguiendo el patrón ya establecido en R1/R2). La pertenencia Project→Archivo se deriva exclusivamente de evidencia estructural real (`compile_items`/`content_items`), con la ambigüedad genuina declarada explícitamente (verificado con un caso real de IST, no solo sintético) en vez de adivinada; ningún método ni archivo se inventó nunca. El particionado combinado de R2 se reutilizó sin escribir lógica nueva. Durante la lectura física de la corrida real (no solo verificación de código de salida) se encontraron y corrigieron dos defectos genuinos de esta misma ronda —un índice de archivos incompleto y un nombre de componente que filtraba una ruta interna— ambos con test de regresión y reconfirmados sobre una regeneración real. La suite completa (2407 tests) y la corrida IST real (25 160 documentos, 0 advertencias, 0 enlaces rotos en una muestra de 3874, 0 ids internos en los 25 154 documentos de desarrollador) están verificadas de punta a punta. General Overview permanece exactamente como en R3.2 (sin código nuevo ni templates nuevos referenciados). Queda una deuda nueva menor de terminología (sección 11.3) y una mejora de navegación opcional para el futuro (sección 11.4), ninguna bloqueante. La aprobación humana sigue siendo obligatoria; este agente no puede otorgarla en nombre del Technical Lead.

V5_2_R3_3_READY_FOR_HUMAN_REVIEW
