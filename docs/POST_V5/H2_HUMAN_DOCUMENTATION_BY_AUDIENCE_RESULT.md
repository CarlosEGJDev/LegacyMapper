# H2 — Documentación humana por audiencia: resultado

Estado final: **`H2_READY_FOR_HUMAN_REVIEW`** (suite completa verde, §10). Sin commit, push ni tag. No se inició H3. La aceptación humana **no** se declara: el material de revisión está preparado (§9).

## 1. Línea base empírica (IST real y fixture pequeño)
Salida determinista IST real (`IST_REAL_AI`: 259 proyectos, 113 soluciones, 3 346 pantallas, 12 642 recorridos, 5 389 procedimientos almacenados):
* `general/` = **5 documentos, 9 KB** (muy resumido, solo tablas "top 12"); `developer/` = **46 561 documentos, 59 MB** (máx. 52 KB por parte; navegación Solución→Proyecto→Archivo→Componente→Método).
* Brecha: nada entre ambos extremos. No existía una vista por proceso/pantalla/dato para analistas ni una vista de capas/dependencias para arquitectos; el detalle técnico (métodos, clases) domina el perfil `developer`; la propiedad proyecto/solución es confiable (containment de `.sln` y `.vbproj`); el propósito de negocio y la agrupación funcional no se deducen (GAP existente) y se declaraban solo al final; la procedencia se muestra como "archivo:línea" en el detalle técnico y no en las vistas resumidas; lo no resuelto aparece solo agregado.
* Muestra representativa para revisión: ver §9.

## 2. Contratos de audiencia implementados
| Perfil | Audiencia | Evita por defecto | Responde |
|---|---|---|---|
| `executive` | gerencia/producto/negocio | métodos, clases, rutas fuente, listas de ids | qué es, áreas principales, capas, datos e integraciones, qué no se sabe |
| `functional` | analistas/soporte/QA | métodos y clases | áreas (una página por solución), procesos observables (pantalla → evento → objeto de datos), pantallas, datos, integraciones, no resuelto |
| `technical_overview` | arquitectos/devs nuevos | detalle de método/clase | proyectos por capa, página por proyecto (dependencias, pantallas, datos, no resuelto), dependencias; enlaza al detalle completo del output original |
Idioma: español. Sin secciones decorativas vacías (las páginas de soluciones sin proyectos identificados no se generan; sin IA no hay secciones de IA).

## 3. Arquitectura y reutilización
Se extiende el motor V5.2 (Evidence → AudienceTransformer → Perfil → Template → Renderer); no hay motor paralelo. Los perfiles y templates son **datos JSON**; el único código nuevo de proyección es `documentation_v52/audience.py` (enriquecimiento del modelo: capas, áreas, procesos, datos, integraciones, no resuelto y la superposición opcional de conocimiento). Sin cambios en Evidence Core, analyzer (`f05b2de4…`), adapters, review, provider ni esquemas.
Jerarquía semántica usada: Sistema → Áreas (soluciones) → Proyectos/Capas → Pantallas → Procesos → Datos → Integraciones → No resuelto. **Nada se fuerza**: el "área funcional" es la **solución real** (única agrupación demostrada); una agrupación por función de negocio se declara no determinable.

## 4. Etiquetado hecho / inferencia / IA
`Confirmado` (conteos y contención leídos de Evidence) · `Inferido (regla estructural)` (la **capa** de un proyecto: pantallas propias → presentación; sin pantallas con accesos directos a datos → acceso a datos; recibe recorridos o tiene referencias → lógica/servicios; si no, `No resuelto`/sin clasificar; los nombres no se usan) · `No resuelto` · `Interpretación de IA (no aprobada)` · `Canónico (aprobado por una persona)`. Precedencia: evidencia > canónico > IA. Una propuesta aprobada pasa a canónico y desaparece de la lista de IA; una rechazada no se lista. La superposición lee **archivos JSON** de la corrida (`proposals/`, `knowledge/`); no importa el servicio de revisión (guardia V5.7 intacta) ni resuelve ningún provider.

## 5. Interfaz
`python main.py docs <output-existente> [--output <dir>] [--audience executive|functional|technical_overview]... [--ai-run <dir>] [--verify-evidence fast|hash] [--long-paths]`. Por defecto escribe `<baseline>\audience_docs\documentation_v52\<perfil>\`. Reutiliza el gate de baseline de H1 (inválido → `DOCS_INPUT_INVALID`, exit 4, no escribe). `full` **no cambia** (sigue generando `general/` y `developer/`); los perfiles son opt-in. No reescanea y no llama a IA.

## 6. Archivos cambiados
Producción: `documentation_v52/audience.py` (nuevo), `cli/docs_command.py` (nuevo), `documentation_v52/{engine,template,config}.py`, `cli/{parser,router}.py`, `main.py`, `fingerprints/configuration.py` (clasificación de opciones/parámetros). Datos: `defaults/profiles/{executive,functional,technical_overview}.json`, 14 templates (`exec.*`, `func.*`, `tech.*`, `aud.*`), `defaults/i18n/es.json` (+161 claves). Tests: `tests/test_post_v5_h2_audience_docs.py` (nuevo, 21 tests); ajustados `test_v4_1_r0_maintainability_inventory.py` (294 módulos; snapshot vivo → `docs/POST_V5/H2_AUDIENCE_DOCS_INVENTORY.json`) y `test_v5_2_r2_documentation_engine.py` (los perfiles *por defecto* siguen siendo dos; hay 3 opt-in). Docs: `README.md`, `docs/V5/V5_OPERATIONS_GUIDE.md` §12, roadmap post-V5 (incluida la higiene de H1: AI-only ya no figura como capacidad futura, UX-02 resuelto, nombre fijado), `PROJECT_STATE.json`.

## 7. Validación pequeña (fixture `v4_2_r7_full_sample`, 3 proyectos)
Ejecutivo 2 docs; funcional 8; técnico 9. Capas: Web = Presentación, CustomerRepository = Acceso a datos, CustomerService = Lógica (por evidencia, no por nombre). Ejecutivo sin métodos ni rutas de archivo; funcional con pantalla `CustomerPage.aspx` → `PKG_CUSTOMER.SAVE_CUSTOMER`; enlaces resueltos; reejecución byte-idéntica; baseline sin cambios; fuente eliminada.

## 8. Validación en IST real (output persistido `IST_REAL_AI`, sin reanalizar)
| Medida | Resultado |
|---|---|
| Tiempo de generación | 16–19 s (3 perfiles) |
| Documentos | ejecutivo **2** (8 KB) · funcional **97** (309 KB) · técnico **267** (430 KB) |
| Documento más grande | 57 KB (`processes-part-000001.md`, partición del perfil) |
| Enlaces | 733 verificados, **0 rotos** |
| Secciones vacías/de bajo valor | 0 (tras no generar páginas de áreas sin proyectos: antes 27) |
| No resuelto visible | `unresolved.md` (25 destinos y 20 proyectos con más elementos) + recuento en cada vista; 11 368 de 12 642 recorridos señalados como detenidos |
| Secciones de IA etiquetadas | 3 documentos (1 propuesta Fake del run de H1) |
| Reejecución | byte-idéntica (368 archivos) |
| Baseline determinista | 0 añadidos / 0 eliminados / 0 cambiados (tamaño+mtime de todo el output) |
| Proveedor / fuente | 0 llamadas; fuente no escaneada |
Áreas: 86 de 113 soluciones tienen proyectos identificados (las 27 restantes no generan página y se informa en el ejecutivo). Capas en IST: 111 presentación, 108 acceso a datos, 17 lógica/servicios, 23 sin clasificar (259 en total).

## 9. Muestra de revisión humana (no es aceptación)
`C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\` — `documentation_v52/` completo de IST (los enlaces funcionan) + `REVIEW_GUIDE.md` con el área representativa `slnPREPrevencion_2010` (proyecto web de 106 pantallas, proyecto con 440 operaciones de datos, integraciones, no resuelto, IA etiquetada) y las cinco preguntas por perfil. La corrida de IA adjunta es de un provider **Fake**.

## 10. Pruebas
* Nuevas: 21 (`test_post_v5_h2_audience_docs`), 0 fallas: perfiles existen y son opt-in; tres niveles de abstracción distintos; ejecutivo oculta método/clase/archivo; funcional muestra pantallas/datos/integraciones; técnico muestra proyectos/capas/dependencias; reglas de capa estructurales y estados; propuesta de IA nunca como confirmada; canónico distinguible y rechazada no listada; sin IA funciona; con `--ai-run` sin invocar provider; enlaces resueltos; reejecución byte-idéntica; baseline intacto y sin fuente; ningún stage determinista invocado; baseline inválido rechazado sin escribir; selección de audiencia; ayuda del CLI.
* Dirigidos (inventario, documentación V5.2, review V5.7, fingerprints, H1, H2): 228 tests OK.
* **Suite completa: 3145 tests, 0 failures, 0 errors, 132 skips** (3124 de H1 + 21 nuevos). La duración que imprime unittest en esa corrida (164 706 s) es un artefacto de suspensión del equipo durante la ejecución, no un tiempo real; una corrida anterior del mismo código tardó 559 s.

## 11. Limitaciones conocidas
* "Área" = solución; no es función de negocio. La agrupación por prefijos de nombre (p. ej. ADH, MED, PEN) **no** se implementó: sería inferencia no demostrable (queda como idea para una fase asistida por IA etiquetada).
* La capa es una regla estructural sobre la evidencia, no una verdad arquitectónica: p. ej. `blPrePrevencion` queda como "Acceso a datos" porque sus 48 operaciones directas de datos lo determinan, aunque su nombre sugiera lógica de negocio.
* Los nombres de pantallas, eventos y objetos son los técnicos del código (el propósito de negocio de cada proceso no se infiere).
* Las listas de procesos se particionan (hasta ~57 KB por parte).
* Sin visuales (H3) ni empaquetado HTML/PDF (H4); sin validación humana (H5).
* Los perfiles nuevos no se generan en `full`; requieren `docs` (decisión para no alterar el output y las líneas base de V5).
* Cambiar los defaults de templates/i18n cambia `template_profile_fingerprint`, por lo que una caché de proyección previa se considera obsoleta en la siguiente corrida de `full` (comportamiento esperado de V5.3; la extracción no se invalida).

## 12. Deuda introducida
Ninguna bloqueante. Observaciones: decidir si `full` debe generar los perfiles de audiencia por defecto (impacta tamaño/regresión IST); decidir el tratamiento de una agrupación funcional asistida por IA (H-posterior); UX-01 (`full` con repo inexistente) sigue abierta.

## 13. Git
Cambios sin commitear en el árbol de trabajo (H1 + H2 acumulados; H1 tampoco está commiteado); prompt `prompts/POST_V5/H2_…md` sin versionar. Tag `v5` intacto.

## 14. Recomendación
Revisar la muestra (§9) y decidir: (a) aprobar H1+H2 y autorizar commit/push; (b) si los perfiles deben integrarse a `full`; (c) siguiente: `H3_STRUCTURED_VISUAL_PROJECTIONS` (no iniciado).

## H2-R2 Targeted Functional Readability Correction

Estado: **`H2_READY_FOR_FINAL_HUMAN_REVIEW`** (la suite completa está registrada abajo). Alcance: solo la proyección `functional`; sin tocar H1, la arquitectura H2, Evidence, analyzer ni adapters. Revisión previa conservada: Ejecutivo = PASS, Técnico general = PASS, Funcional = PARCIAL. **No se declara aceptación humana.**

**Hallazgo corregido.** El perfil funcional seguía siendo un inventario de trazas (`pantalla → evento → procedimiento almacenado`) sin valor de lectura funcional.

**Clasificación de acciones (solo presentación).** Evidence no trae tipo de operación de lectura/escritura (`operation_kind` solo distingue `transaction`, `stored_procedure`, `sql`…), por lo que se añadió un clasificador conservador y determinista en `documentation_v52/audience.py` (`classify_target` / `classify_action`): lee solo el nombre técnico de la operación (la parte posterior al último punto; el paquete no cuenta), por *tokens*; categorías `read | create | update | delete | mixed | unknown`; tokens cortos (`CON`, `SEL`, `INS`, `UPD`, `DEL`, `MOD`, `GET`, `ALTA`) solo por coincidencia exacta; varios tipos distintos, o un tipo reconocible junto a uno no reconocible, se informan como **mixta**, nunca se reducen a uno; lo no reconocido es **tipo no determinado** (p. ej. `SAVE_CUSTOMER`, `GENERARDETALLECERTIFICADO`). Nunca expresa intención de negocio.

**Arquitectura de información funcional.** Orden de lectura: Área → *Resumen funcional observable* (conteos por tipo + "propósito de negocio: no determinado por evidencia") → *Pantallas con actividad identificada* → secciones por tipo (*Interacciones de consulta / registro-creación / modificación / eliminación*, *Operaciones mixtas*, *Operaciones no clasificadas*; las vacías se omiten) → *Procesos cuya finalidad de negocio no puede determinarse* → datos que usa el área → *Trazabilidad técnica* (proyectos y enlace al listado técnico). `functional/README.md` abre con el mismo resumen.
`functional/processes.md`: resumen por tipo, proyectos con más interacciones, pantallas con más interacciones y lo no sabido **antes** de las filas técnicas; las filas completas (ahora con la columna "Tipo de interacción") siguen en `processes-part-*.md` como detalle de trazabilidad.
`functional/unresolved.md` (plantilla propia `func.unresolved`; el técnico conserva `aud.unresolved`): qué significa "no resuelto", cuánto comportamiento afecta, áreas y proyectos más afectados, por qué se detiene el análisis, qué no debe inferirse y recién después el detalle técnico (`dbc.Rollback()`, `InitializeComponent()`…). Los conteos no se redujeron.

**Antes / después (área `slnPREPrevencion_2010`, IST real).**
Antes: tabla de 15 filas `Proyecto | Pantalla | Evento | Termina en` (p. ej. `ucPreContactosDir2.ascx | Click | PPRE_CONTACTOS.GRABA_DIRECCIONES`) bajo "Procesos observables", precedida solo por una frase de totales.
Después: resumen (16 consulta · 3 registro/creación · 1 modificación · 2 eliminación · 1 mixta · 4 no determinadas = 27 interacciones; 17 pantallas con actividad), y la interacción anterior aparece en *Interacciones de registro / creación* con "Acción observable: interacción de escritura (registro / creación) detectada", la operación técnica `PPRE_CONTACTOS.GRABA_DIRECCIONES` como trazabilidad y "propósito de negocio no determinado por evidencia"; ya no hay una afirmación del tipo "actualiza la dirección de una empresa".

**IST (output persistido, sin reanalizar).** Funcional regenerado: 97 documentos, 443 KB, máx. 64.6 KB (límite de partición 64 KB); 672 interacciones = 672 flujos que llegan a datos (ahora incluye las 49 que nacen en pantallas sin proyecto identificable, bajo "sin proyecto identificado"): 407 consulta, 61 registro/creación, 20 modificación, 18 eliminación, 97 mixtas, 69 no determinadas; unresolved 11 368 de 12 642 recorridos (89.9%), sin reducción. **Ejecutivo y técnico general regenerados byte-idénticos** a la versión revisada (mismos SHA-256 de directorio). Reejecución funcional byte-idéntica (368 archivos); enlaces 829, **0 rotos**; secciones vacías 0; baseline determinista 0 añadidos / 0 eliminados / 0 cambiados; llamadas a provider 0; fuente no escaneada.
Muestra refrescada: `C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\` (`documentation_v52/` completo regenerado + `REVIEW_GUIDE.md` actualizado; incluye `functional/areas/slnPREPrevencion_2010.md`, `functional/processes-part-000001.md` y `functional/unresolved.md`).

**Tests.** Nuevos `tests/test_post_v5_h2_r2_functional.py` (15): clasificador (vocabulario, ejemplo del brief, tokens cortos y look-alikes, mixto/no determinado sin colapsar, determinismo) y proyección (resumen primero, escritura clasificada y trazable, variante de lectura omite categorías vacías, operación no reconocida no se adivina, intención de negocio no inventada, resumen global antes de filas y filas alcanzables, README abre con el resumen, explicación de unresolved antes del detalle con conteos conservados, ejecutivo/técnico sin vocabulario funcional, reejecución byte-idéntica y enlaces, 0 provider/0 etapas de análisis). Ajustado `test_post_v5_h2_audience_docs.py` (regex de la tabla de proyectos) y el snapshot de inventario.
**Suite completa: 3160 tests, 0 failures, 0 errors, 132 skips** (3145 + 15 nuevos; 660 s). Dirigidos H1/H2/H2-R2 + inventario + fingerprints: OK.

**Limitaciones.** El tipo de interacción depende de convenciones del *nombre* de la operación (69 de 672 "no determinadas", 97 "mixtas" en IST); nombres en inglés fuera del vocabulario (`SAVE_…`) quedan sin determinar a propósito; los proyectos con copias (`Backup`) repiten su actividad (el output no sabe cuál es producción); los nombres de pantallas, eventos y objetos siguen siendo los técnicos; el recuento "pantallas" por categoría puede solaparse (una pantalla con varios tipos). Sin visuales (H3) ni HTML/PDF (H4).

**Git.** Cambios sin commitear (H1 + H2 + H2-R2 acumulados); prompts `prompts/POST_V5/*` sin versionar. Tag `v5` intacto.

**Recomendación.** Confirmar la muestra refrescada (sección *Preguntas de confirmación final* de `REVIEW_GUIDE.md`); con confirmación, autorizar commit/push de H1+H2(+R2) y pasar a `H3_STRUCTURED_VISUAL_PROJECTIONS`.
