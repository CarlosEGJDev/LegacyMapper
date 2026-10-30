# H4-R4 — Prototipo de documentación conductual: resultado

Estado final: **`H4_BEHAVIORAL_PROTOTYPE_READY_FOR_HUMAN_REVIEW`**. Ronda excepcional de corrección de H4 (la revisión humana halló que el paquete H4 reorganiza documentación técnica en vez de explicar cómo funciona el software). No reabre H1–H3, no inicia H5, no cierra H4 globalmente. Sin commit, push ni tag. La revisión humana decide si este modelo se generaliza.

## 1. Hallazgos empíricos (IST, `WebPREPrevencion`, baseline persistido + fuentes en solo lectura)
* **Módulo: `NO_SAFE_MODULE_STRUCTURE`.** 121 vistas (elementos de contenido `.ascx/.aspx` del archivo de proyecto): 106 en una sola carpeta propia con un único espacio de nombres (`Sonda.Gestion.NSSMUT.Web.PREPrevencion`) y 15 controles compartidos de otros espacios de nombres en la raíz (`Cabecera`, `Login`, menús…); sin subproyectos con vistas, sin menús declarados; 59 familias por prefijo de nombre (convención, no frontera). Regla: módulos solo con ≥ 2 carpetas, cada una con ≥ 3 vistas del espacio de nombres propio. Un primer borrador clasificó «CONFIRMED» por error (raíz vs. carpeta propia); se corrigió y quedó la regla anterior.
* **Las «vistas» son controles de usuario** cargados por un shell (`default.aspx?url=<carpeta>/<vista>`); abrir una vista = literal `url=…` con parámetros (`selrow`, `ctrvis`, `ctrhid`).
* **Lo que el baseline persistido NO guarda y el prototipo lee del origen (solo lectura):** árbol de controles del marcado, textos/títulos, literales `url=…`, `MsgBox`/`alert`, parámetros recibidos (`parametrosURL`, `QueryString`). Es la principal brecha de evidencia para productizar.

## 2. Vistas elegidas (criterio determinista)
`ucPreMantEmpadronamiento` (persistencia), `ucBusSuc` (ventana emergente de selección; 26 sitios de llamada), `ucPreMantDepPrevencion` (lógica: más procedimientos/clases), `ucPreEstadisticasAccidentes` (flujo complejo/no resuelto), `ucPreMantMetas` (ordinaria). Criterio por casilla registrado en `baseline.pilot_selection` del JSON.

## 3. Cobertura de la reconstrucción (§16; para decisiones, no narrativa)
| Medida | Valor (de 121 vistas) |
|---|---|
| Con marcado / con code-behind | 121 / 107 |
| Con eventos o acciones | 107 |
| Alcanzan clase de negocio o DAO / operación de datos / procedimiento | 17 / 17 / 17 |
| Con invocaciones entrantes / salientes (literales `url=`) | 8 / 32 |
| Soportan wireframe documental | 117 |
| Acciones con llamadas de negocio no resueltas y sin destino de datos | 102 |
| Diálogos de búsqueda inferidos | 3 |
Lectura honesta: solo 17 vistas llegan *con certeza* a datos; en el resto, las llamadas a clases de negocio (`PrePrvDeptoPrv.txtraer`, `txcrear`…) quedan como destino no resuelto. El prototipo las muestra como «llamadas de negocio observadas, destino no resuelto» en vez de ocultarlas o completarlas.

## 4. Contrato de interpretación
`Evidencia determinista → paquete de contexto conductual (evidence.py) → interpretación → explicación estructurada (model.py) → validación determinista (validate.py) → renderizado (render.py)`. En este prototipo la «interpretación» es un explicador determinista de plantillas (**no se llamó a ningún proveedor de IA**; AGENTS.md no lo autoriza en esta ronda). El punto de entrada para una IA existe y está probado: `validate.apply_ai_overlay` acepta afirmaciones estructuradas, las valida y las fuerza a `AI_INTERPRETATION`.

## 5. Modelo estructurado (`behavior/model.py`)
`SolutionExplanation`, `ProjectExplanation`, `ModuleExplanation`, `ViewExplanation`, `ActionExplanation`, `BehaviorPath`, `DataInteractionExplanation`, `ViewInvocation`, `UIReconstruction`, `UnresolvedExplanation` (+ `ClassRole`, `ViewMessage`, `BehavioralDocument`). Cada afirmación importante es un `Claim{text,status,source_refs,basis,origin,entities}`. Estados: CONFIRMED / INFERRED / UNRESOLVED / AI_INTERPRETATION / CANONICAL.

## 6. Validación determinista (`behavior/validate.py`)
Verifica: la vista existe; evento/método/clase/procedimiento citados existen; `source_refs` resuelven (ids de baseline, `src:archivo:línea` dentro del archivo real, proyecto/solución conocidos); CONFIRMED exige soporte (si no, se degrada a UNRESOLVED); INFERRED exige base; UNRESOLVED se conserva; una afirmación de origen IA solo puede ser AI_INTERPRETATION (se degrada, nunca se promueve); CANONICAL no puede salir del explicador; refs/entidades fabricadas → **rechazo**; un control de wireframe fuera del marcado → rechazo; destino de invocación inexistente → anotado. En IST: 0 rechazos, 2 anotaciones (literales a vistas que no existen en el repositorio). Durante el desarrollo el validador detectó un defecto real del explicador (referencia a archivo sin extensión) que se corrigió.

## 7. Wireframe
Determinista desde el marcado de la vista: esqueleto tabla/fila/celda, etiquetas, cuadros de texto, listas desplegables, botones/enlaces (con el nombre del ícono si no hay texto), grillas con sus columnas visibles, paneles; campos ocultos listados aparte, no dibujados. Rotulado «RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE PANTALLA»; sin estilos ni datos; si no hay controles → `WIRE_FRAME_UNAVAILABLE_FROM_CURRENT_EVIDENCE`. SVG con solo `rect/text` (también se incrusta como vector en el PDF).

## 8. Salidas del prototipo
`C:\PruebasLegacyMapper\Resultados\post_v5_h4_behavioral_doc_prototype\`: `prototype\index.html` (+ `assets\` con los SVG de wireframes, rutas e invocaciones), `Entendiendo_WebPREPrevencion.pdf` (50 p.), `structured_explanation\{explanations,validation_report}.json`, `wireframes\`, `REVIEW_GUIDE.md`. Orden: portada, cómo leer, 1 solución, 2 proyecto, 3 módulos (por qué no), 4 catálogo (121), 5 cinco capítulos A–K, 6 entre vistas, 7 datos, 8 no resuelto, 9 apéndice (mediciones). Los conteos no encabezan la narrativa (caja de hechos plegada; mediciones al final).

## 9. Código y pruebas
Nuevo paquete `legacy_documenter/behavior/` (9 módulos; sin cambios en Evidence, analyzer, adapters, provider, review, H2/H3/H4); `tests/test_post_v5_h4_r4_behavioral.py` (27 tests: parser, módulo no inventado, vistas existen, refs resuelven, ruta evidenciada, confirmado exige soporte, inferido se conserva, no resuelto se conserva, wireframe solo con controles evidenciados, trazabilidad de invocaciones y destinos faltantes, renderizado determinista, rechazo de refs/entidades fabricadas, IA nunca confirmada, sin proveedor). Inventario: 317 módulos (snapshot `H4_R4_BEHAVIORAL_INVENTORY.json`). **Suite completa:** **3281 tests, 0 failures, 0 errors, 132 skips, 772.5 s, exit code 0** (3254 + 27 nuevos).

## 10. Validación IST
Generación 22 s; proveedor 0; escáner/analizador 0 (guardas); baseline 0 añadidos / 0 eliminados / 0 cambiados; reejecución byte-idéntica (HTML, JSON, SVG y PDF); fuente solo leída.

## 11. Limitaciones
* Sin narrativa de IA: el lenguaje es plantilla (correcto pero seco); la IA aportaría síntesis, no hechos.
* Evidencia de origen leída fuera del baseline persistido (ver §1): productizar exige extractores deterministas de UI y navegación que persistan en Evidence (cambio de contrato, fuera de esta ronda).
* El «propósito» de una pantalla se infiere de título + acciones + efectos por nombre; nunca de negocio.
* Las llamadas a clases de negocio de otros proyectos no se siguen (límite del baseline); 102 de 121 vistas quedan sin destino de datos confirmado.
* El catálogo de 121 filas incluye controles compartidos (Cabecera, Login…) que no son vistas de negocio; el catálogo los marca como «sin eventos propios».
* Verificación del PDF con rasterizador de apoyo, no con visor real.

## 12. Recomendación para productizar
Si la revisión confirma el modelo: (1) persistir en Evidence el árbol de controles y los literales de navegación/mensajes (nuevo extractor determinista, con contrato y versión); (2) resolver llamadas a clases BL entre proyectos para elevar el 17/121; (3) conectar el contrato `Claim` a la interpretación de IA ya existente (H1) con `apply_ai_overlay` como compuerta; (4) generalizar el selector de vistas piloto a «todas las vistas con acciones» con capítulos plegables; (5) reemplazar el paquete H4 actual por este orden macro→micro. Hasta entonces H4 no debe darse por cerrado.

## 13. Estado / Git
H4 packaging = técnicamente validado; concepto de documentación humana de H4 = reabierto por la revisión humana; prototipo conductual = resultado (este documento); H5 = NOT_STARTED. Cambios H1–H4 + R4 sin commitear; tag `v5` intacto.

---

## H4-R5 Final Behavioral Documentation Correction

Estado final: **`H4_BEHAVIORAL_AI_READY_FOR_HUMAN_REVIEW`**. Ronda excepcional (quinta de H4); no hay R6. H4 **no** se marca cerrado; H5 = NOT_STARTED; sin commit/push/tag.

**Proveedor/modelo.** Arquitectura existente (COPILOT), `provider_id=copilot-local`, `model_id=gpt-6-luna`; **6 solicitudes** reales (5 vistas + proyecto), 6 correctas, 113777 caracteres de entrada y 106152 de salida en total. En este entorno el SDK no podía lanzar su runtime descargado (acceso denegado); se usó el CLI de Copilot ya instalado fijando `COPILOT_CLI_PATH` solo para el proceso (sin instalar nada). Una corrida real previa devolvió JSON con caracteres de control en una vista (INVALID_STRUCTURED_OUTPUT); se añadió una lectura tolerante (`strict=False`, contenido sin reescribir) y la corrida final dio 6/6 válidas. El paquete de revisión se generó re-validando esas respuestas guardadas con el validador final (sin nuevas llamadas; `replayed_from_real_run` en el manifest; respuestas crudas en `ai_audit\`).

| Solicitud | Estado | Entrada (car.) | Salida (car.) | s |
|---|---|---|---|---|
| ucPreMantEmpadronamiento | SUCCESS | 26395 | 24672 | 53.6 |
| ucBusSuc | SUCCESS | 17869 | 17707 | 45.4 |
| ucPreMantDepPrevencion | SUCCESS | 20919 | 20772 | 44.5 |
| ucPreEstadisticasAccidentes | SUCCESS | 24035 | 20188 | 48.9 |
| ucPreMantMetas | SUCCESS | 18467 | 19143 | 39.2 |
| WebPREPrevencion | SUCCESS | 6092 | 3670 | 17.6 |

**Contrato de contexto conductual.** Por vista: identidad/título, controles del marcado (id, tipo, etiqueta, oculto, enlazado a evento, columnas de grilla), eventos y manejadores, rutas confirmadas, operaciones de datos y procedimientos, llamadas de negocio no resueltas, parámetros y sesión, invocaciones entrantes/salientes, mensajes y errores, y evidencia de uso. Cada hecho lleva una `ref` real (EP-/FLOW-/DAO-/`src:archivo:línea`); la IA solo puede citar esas refs. 32–63 hechos por vista (10–19 mil caracteres); nunca el repositorio.

**Esquema estructurado de IA.** `view_id`, `simple_summary`, `observable_purpose`, `usage_status`+`usage_reasoning`, `inputs[]`, `main_actions[]` (por manejador), `data_behavior`, `related_classes[]`, `messages_popups[]`, `known/inferred/unresolved[]`; cada ítem con `text`, `source_refs`, `reasoning_basis`, `entities[]`. Todo se almacena como `AI_INTERPRETATION` (origen `ai`); nunca confirmado ni canónico.

**Modelo de uso observable** (`behavior/usage.py`). Escalera EXISTS_IN_SOURCE → REACHABLE_FROM_OBSERVED_FLOW → OBSERVABLY_USED; estados `ACTIVE_OBSERVABLE` (invocación entrante confirmada desde otra vista existente, sin contar copias Backup), `POSSIBLY_ACTIVE` (comportamiento + referencia por nombre), `UNRESOLVED_USAGE` (el shell abre vistas por nombre: `default.aspx?url=…`), `LEGACY_CANDIDATE` (solo con todos los indicadores alineados; redacción cautelosa), `ISOLATED` (no implica obsolescencia). Las palabras de obsolescencia se rechazan en la salida de IA. IST/`WebPREPrevencion`: {'ACTIVE_OBSERVABLE': 7, 'UNRESOLVED_USAGE': 114}.

**Vistas.** Se conservaron las cinco de R4; `NO_SAFE_MODULE_STRUCTURE` sin cambios.

**Antes / después (ucPreMantDepPrevencion).** Antes (R4, plantilla): «Al pulsar el ícono «guardar» se ejecuta hypGuardar_Click. La ruta confirmada llega a 1 operación(es) de datos (registro / creación, tipo deducido del nombre).» Después (IA validada): «Al pulsar guardar, el manejador pasa los datos recuperados de dpaDeptoPrevencion a PrePrvDeptoPrv.txcrear o PrePrvDeptoPrv.txmodificar y alcanza el procedimiento PPRE_PRV_DEPTO_PRV.GRABAR. La evidencia no permite precisar la condición que determina cuál de esos métodos se llama.» Y en «En una frase»: «Esta pantalla, titulada Departamento de Prevención, presenta campos y acciones para buscar una persona y gestionar datos de un departamento de prevención.»

**Validación determinista del texto de IA** (`ai.check_item` / `merge_view` / `merge_project`): refs deben haber sido ofrecidas y resolver; entidades (control/evento/método/clase/procedimiento/vista/parámetro/mensaje) deben existir en el contexto (los controles, además, en el marcado); símbolos entre «» deben existir; palabras de obsolescencia → rechazo; el `usage_status` propuesto por la IA no sustituye al determinista (se anota); acción citada sin documentar → anotación. Resultado en IST: **92 afirmaciones aceptadas, 7 rechazadas** (nombres de mensaje descriptivos inexistentes como «error al usuario» y un símbolo mal escrito `pre gesmeta.txcrear`), 4 anotaciones (Page_Init sin acción documentada) y 2 destinos de invocación inexistentes preservados sin enlace (`WebPrePrevencion\ucPreDirecContactosMant`, `webPrevencion\ucBusEmp`). Una versión inicial del validador era demasiado estricta (rechazaba clases con prefijo punteado y `método()`); se ajustó a «cualquier identificador presente en los hechos entregados», sin admitir símbolos ajenos.

**HTML/PDF.** Orden macro→micro; capítulos A–L; la IA en recuadros violeta rotulados («Interpretación de IA — no aprobada», «Basada en: refs»); catálogo de 121 vistas, mediciones y trazabilidad de IA en el apéndice (filtro de tabla local). Detalles técnicos plegados en HTML y omitidos del flujo principal del PDF.

**Pruebas.** Nuevas 18 (`tests/test_post_v5_h4_r5_behavioral_ai.py`): reglas de uso (ACTIVE requiere evidencia positiva, Backup no cuenta, ISOLATED no es obsoleto, LEGACY cauteloso, shell → UNRESOLVED_USAGE), esquema, validación de narrativa (símbolo/procedimiento/ref fabricados, obsolescencia, estado siempre AI_INTERPRETATION, controles del wireframe), `run_ai` con proveedor de prueba (la suite nunca llama a uno real), render separado y determinista, catálogo como apéndice. Ajustadas las de R4 al nuevo orden. **Suite completa:** **3299 tests, 0 failures, 0 errors, 132 skips, 753.8 s, exit code 0** (3281 + 18 nuevos).

**Integridad del baseline.** Delta 0/0/0; sin escáner/analizador; lectura adicional de marcado y código-behind = *read-only enrichment* (igual que R4); reejecución byte-idéntica = True.

**Limitaciones.** La IA a veces repite cifras del contexto; el vocabulario de mensajes se rechaza si no es literal; 114 de 121 vistas siguen con uso no resuelto (límite estático); solo 5 vistas + proyecto tienen narrativa de IA (alcance acotado); la evidencia de UI/navegación se sigue leyendo del origen; PDF verificado con rasterizador de apoyo.

**Ruta de revisión humana.** `C:\PruebasLegacyMapper\Resultados\post_v5_h4_behavioral_doc_prototype\` (`prototype\index.html`, `Entendiendo_WebPREPrevencion.pdf`, `AI_INTERPRETATION_MANIFEST.json`, `ai_audit\`, `REVIEW_GUIDE.md`).

**Git.** Cambios H1–H4 + R4 + R5 sin commitear; tag `v5` intacto.

**Recomendación.** Revisar con la guía. Si la lectura macro→micro y la explicación por vista satisfacen («ahora entiendo cómo funciona el proyecto»), productizar: persistir UI/navegación en Evidence, resolver llamadas BL entre proyectos, extender a todas las vistas con acciones por lotes y generalizar el selector. Si no, re-diagnosticar el modelo de producto (sin H4-R6).

---

## Human Template Productization (post-H4-R5, no es R6)

Estado: **`H4_HUMAN_TEMPLATE_READY_FOR_HUMAN_REVIEW`**. Trabajo de productización de la dirección aprobada (no una ronda exploratoria); H5 = NOT_STARTED; sin commit/push/tag.

**Sistema de plantillas.** `templates/human/default/{template.yaml, document.html, styles.css, pdf.css, assets/}` + `templates/human/README.md` + `templates/ai/README.md`
(IA: reservado y documentado, sin runtime). Contrato `LegacyMapperHumanTemplate 1.0` (`behavior/template.py`): `template_id`, `template_version`, `audience`, `language`,
`sections` (orden y visibilidad), `view_chapter` (orden de las partes del capítulo), `styles`, `assets`, `required_fields`/`optional_fields`, `labels`.
Descubrimiento: directorio de usuario (`--template-dir`) antes que `templates/` del repositorio; `--template human/default`. Seguridad: datos, no código — placeholders de un
conjunto cerrado (`{{title}} {{content}} {{style}} …`), sin expresiones/bucles/includes; `document.html` sin scripts ni manejadores; CSS sin `@import`/`url()`/expresiones;
archivos solo por nombre plano; campos requeridos validados contra el modelo; la plantilla recibe el modelo ya validado y no puede promover `AI_INTERPRETATION`, ocultar
`UNRESOLVED`, cambiar `source_refs`, mutar el baseline ni invocar proveedor (verificado en pruebas: el modelo estructurado es idéntico antes y después de renderizar con otra plantilla).

**Documento.** Orden: portada → aviso de IA (una vez) → contenido → solución → proyecto → módulos → vistas importantes → capítulos → entre vistas → datos → uso observable → no
resuelto → apéndice (catálogo, mediciones, fidelidad visual, trazabilidad de IA). Capítulo: título, una frase, qué hace y cómo se usa, evidencia de uso, reconstrucción visual,
flujo técnico simple, acciones, datos, clases, vistas/ventanas, mensajes, sabemos/inferimos/no sabemos, evidencia técnica. El aviso largo aparece una vez; en el cuerpo, la marca
compacta «IA» (el estado `AI_INTERPRETATION` permanece en el modelo y como `data-status` en el HTML). Jerarquía tipográfica en CSS/pdf.css (título 2.6rem > sección 1.9 > vista 1.45 >
subsección 1.12 > cuerpo; evidencia/técnico menores); la presentación no está en los objetos del modelo. Índice: barra lateral fija con anclas estables (HTML) y página de contenido de
2 niveles con marcadores y numeración (PDF).

**Diagrama de cajas** (`behavior/flowboxes.py`): una fila por acción — vista → evento/manejador → negocio/servicio → DAO/repositorio → procedimiento/SQL → base de datos/límite;
solo capas con evidencia (se omiten las ausentes), lo no resuelto se dibuja explícito (negocio no seguido, destino de datos no resuelto), orden fijo, `source_refs` en cada caja.

**Investigación de estilos IST** (`WebPREPrevencion`, 112 `.ascx`): 1161 atributos `style`, 2579 `Width`, clases CSS (`NombreCampo`, `HyperLink`, `Boton`, `Titulo`, `TablaCabecera`,
`FondoGrupo`…), 31 iconos referenciados de los que 30 existen en `img/`; la hoja `Styles.css` está enlazada por el shell `default.aspx` y define esas clases; no hay skins; 4 páginas maestras
(ninguna de este proyecto); `Tipo` pertenece a controles compilados (DLL no disponible → inferido); 762 asignaciones `.Visible =` y 7 bloques de script (no reconstruibles).
**Capacidad** (`STRUCTURE_ONLY | STYLE_PARTIAL | STYLE_HIGH_CONFIDENCE`) sobre las 121 vistas: {'STRUCTURE_ONLY': 7, 'STYLE_HIGH_CONFIDENCE': 5, 'STYLE_PARTIAL': 109}; vistas piloto: STYLE_PARTIAL. Reconstrucción mejorada solo con evidencia: fondo/color/borde/ancho
declarados, grupos de celda (`FondoGrupo`), iconos reales incrustados (si existen y ≤16 KB), nunca JavaScript ni aplicación en ejecución; rótulo «RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE
PRODUCCIÓN» y declaración de fidelidad.

**Deuda.** (8) UI/navegación: se persiste un sidecar versionado (`ui_navigation_evidence.json`, con hashes de los fuentes) y el informe de estilos; **Evidence Core no se modificó**: la
persistencia en Evidence queda abierta. (9) Llamadas BL entre proyectos: **sin cambios** (siguen no resueltas; requiere resolución entre proyectos/DLL). (10) Estado y roadmap sincronizados
con la revisión humana. UX-01 y UX-03 no se tocaron.

**Pruebas.** Nuevas 25 (`tests/test_post_v5_h4_template_productization.py`): descubrimiento (incorporada/usuario/ids inválidos), plantilla por defecto y personalizada, 13 plantillas
inválidas rechazadas, campos requeridos, subconjunto YAML estricto, plantillas = datos, jerarquía de tamaños (HTML y PDF), estilo de PDF desde `pdf.css`, aviso de IA una vez + marcador +
estado preservado, plantilla que reordena sin cambiar la verdad, anclas del índice, contenido y marcadores del PDF, determinismo, cajas solo con capas evidenciadas y no resuelto explícito,
CSS en lista blanca, estilos/iconos solo declarados, fidelidad conservadora. Ajustadas las de R4/R5 al orden de capítulos por plantilla. **Suite completa:** **3324 tests, 0 failures, 0 errors, 132 skips, 660.2 s, exit code 0** (3299 + 25 nuevos).

**Validación IST.** Delta de baseline 0/0/0; sin escáner/analizador ni nuevas llamadas a proveedor (se re-validaron las respuestas
guardadas de la corrida real); reejecución byte-idéntica = True. Paquete: `C:\PruebasLegacyMapper\Resultados\post_v5_human_template_productization\`.

**Limitaciones.** Fidelidad visual parcial por diseño; PDF verificado con rasterizador de apoyo; el proyecto de 3 vistas rechaza una afirmación del resumen del proyecto que citaba una vista
fuera del alcance (validación correcta); sin visor PDF real; Evidence no modificada.

**Recomendación.** Revisar con la guía; si el formato es adecuado como plantilla humana genérica, planificar (a) persistir UI/navegación en Evidence, (b) resolución de llamadas BL entre
proyectos, (c) una segunda plantilla (p. ej. ejecutiva) para validar la separación plantilla/análisis. H5 sigue sin iniciarse hasta la aprobación humana.

---

## Final Human Template Polish (post-productization, no es R7)

Estado: **`H4_HUMAN_TEMPLATE_READY_FOR_FINAL_HUMAN_APPROVAL`**. Pulido global de presentación; sin commit/push/tag; H5 = NOT_STARTED; modelo sin rediseñar.

**Cambios (a nivel de plantilla/renderizador, no por documento).**
* Título centrado (`.doc-title`, `title_alignment`), subtítulos de vista centrados (`h3.view-title`, `.h2` en `pdf.css`), párrafos explicativos justificados (`.doc-main p`, `.body`),
  figuras y pies centrados, ritmo vertical (márgenes antes/después por nivel) en `styles.css` y `pdf.css`; bloque `layout:` validado en `template.yaml`
  (`title_alignment`, `view_title_alignment`, `paragraph_alignment`, `diagram_alignment`, `ai_marker`).
* SVG: nuevo `behavior/svgtext.py` (ajuste de texto determinista con métricas WinAnsi, partición de tokens largos en separadores o caracteres); cajas de flujo, rutas,
  cruces y reconstrucción adaptan alto y lienzo; el texto no sale de su caja. Más de 8 filas: nota «+ N acciones más».
* IA: el aviso largo aparece una vez al principio; en el cuerpo, un solo marcador «IA» por capítulo/bloque (política `ai_marker: chapter|none`); el resto de bloques de IA solo
  llevan un tinte sutil; el estado `AI_INTERPRETATION` permanece intacto en el modelo y como `data-status`. Desaparece la etiqueta larga repetida.
* Portada: frase de procedencia exacta (`provenance_sentence`): corrida real de IA revalidada de forma determinista, sin nuevas llamadas al proveedor ni nuevo análisis del código.
* PDF: encabezados centrados/justificados y espaciado desde `pdf.css`, contenido y marcadores a 2 niveles (vistas y secciones), mismos tamaños relativos que el HTML.

**Pruebas.** 10 nuevas (`FinalPolishTests`) y 2 ajustadas en `tests/test_post_v5_h4_template_productization.py`: ganchos CSS/pdf.css, ganchos del renderizador, frase de portada,
política de marcadores y `layout` inválido rechazado, ajuste SVG determinista y contenido, cajas de flujo con texto dentro, PDF con título/subtítulos centrados y párrafos justificados,
determinismo del PDF. Inventario: 323 módulos (`svgtext.py`). **Suite completa:** **3334 tests, 0 failures, 0 errors, 132 skips, 2266.7 s, exit code 0**.

**Validación IST.** Delta de baseline 0/0/0; reejecución byte-idéntica = True; sin nuevas llamadas a
proveedor. Paquete: `C:\PruebasLegacyMapper\Resultados\post_v5_human_template_productization\` (con `REVIEW_GUIDE.md` y 10 preguntas).

**Limitaciones.** PDF verificado con rasterizador de apoyo, no con visor real; fidelidad visual STYLE_PARTIAL en las vistas piloto; persistencia de UI/navegación en Evidence y
resolución BL entre proyectos siguen abiertas; UX-01/UX-03 sin tocar. Aprobación humana final pendiente.

