# V5.2 R2 — Perfiles, Templates y Renderer Markdown: implementación

## 1. Estado

V5_2_R2_READY_FOR_R3

El motor de documentación humana de V5.2 está implementado, integrado en el pipeline productivo (`full`) de forma aditiva y verificado sobre IST real. No se declara V5.2 cerrada. No se modificó Evidence Core, V5.1, la documentación legacy (`documentation/`), el roadmap ni `PROJECT_STATE.json`; no hay commits.

## 2. Qué se implementó

Nuevo paquete `legacy_documenter/documentation_v52/`:

| Pieza | Responsabilidad |
|---|---|
| `transform.py` | Audience Transformation: evidencia → `AudienceDocumentModel` (agrega, clasifica, ordena, sanitiza) |
| `noise.py` + `defaults/noise/` | Technical Noise Policy declarativa |
| `config.py` + `defaults/profiles/` | Output Profiles, catálogos de idioma, carga con override y validación |
| `template.py` + `defaults/templates/` | Motor de templates declarativos (JSON) sobre una vista filtrada por el profile |
| `structure.py` | Documento estructurado neutral (contrato Template → Renderer) |
| `renderer.py` | Renderer Markdown: escape, links, nombres, particionado, determinismo |
| `engine.py` | Orquestación y escritura de `documentation_v52/` (+ `MANIFEST.json`) |
| `defaults/i18n/es.json` | Catálogo de idioma `es` |

Además: integración en `render_documentation` (etapa DOCUMENTATION de `full`), `tests/test_v5_2_r2_documentation_engine.py` (62 tests) y `tools/v5_2_r2_partition_measurement.py` (herramienta de medición, solo desarrollo).

## 3. Arquitectura final de R2

```
Evidence (índices en memoria del run / evidence/ persistido)
   ↓  AudienceTransformer(NoisePolicy)          → AudienceDocumentModel
   ↓  ProfileView(OutputProfile)                → qué ve la audiencia
   ↓  TemplateEngine(templates JSON, catálogo)  → StructuredDocument
   ↓  MarkdownRenderer(PartitionPolicy)         → archivos .md
documentation_v52/{general,developer}/  +  README.md  +  MANIFEST.json
```

Refinamiento respecto de R1 (no cambia el contrato): la política de ruido aporta *categorías, patrones y visibilidad por defecto*; el **profile** puede sobrescribir la visibilidad por categoría (`noise_visibility_overrides`). Así D-52-03 se cumple literalmente: la decisión de ocultar/mostrar pertenece al profile y nunca al renderer. El renderer no importa profile, política, evidencia ni templates (verificado por test).

## 4. General Overview

Cinco documentos en `general/` (5 archivos, 4,5 KB en total): `README.md` (sistema analizado, propósito, navegación), `modules.md`, `external-systems.md`, `data.md`, `limitations.md`. Muestra solo `KEEP_SIMPLE`, sin IDs, hashes ni JSON. Sin contenido INTERPRETED usa la frase neutral «El propósito funcional global no pudo determinarse únicamente desde la evidencia estática disponible.» y sigue siendo útil debajo (conteos, módulos principales, bibliotecas externas, proveedores de datos, paquetes de base de datos, limitaciones).

## 5. Developer Technical

`developer/README.md` (2 KB) → un documento por módulo `modules/<nombre>.md` con secciones Resumen, Puntos de entrada, Flujos, Acceso a datos, Dependencias e Información no resuelta → `modules/<nombre>/detail.md` con tablas completas partidas en partes navegables. Adicionalmente: `modules-index-part-000001.md` (índice completo de 260 módulos) y `configuration.md`. 832 archivos, ninguno mayor de 49 KB.

## 6. Profiles

Exactamente dos, como datos JSON: `general_overview` (categorías `KEEP_SIMPLE`, nivel máximo 2, sin documentos de detalle) y `developer_technical` (`KEEP_SIMPLE`+`KEEP_TECHNICAL`, nivel 4 bajo demanda, documentos de detalle). Controlan audiencia, nivel, categorías, ruido, idioma, comportamiento ante no resuelto, límite de filas del cuerpo y límites de partición. La validación rechaza `INTERNAL_ONLY` salvo `allow_internal_only` explícito, particiones inválidas y niveles fuera de rango.

## 7. Templates

Trece templates JSON declarativos (5 General + 8 Developer: los 7 de R1 más `dev.configuration`). Sin Markdown embebido en Python y sin ejecución de código: solo bloques tipados (`heading`, `paragraph`, `table`, `partitioned_table`, `bullets`, `link`, `interpreted`), condiciones con un vocabulario cerrado y fuentes/campos de una lista blanca. Un template solo ve valores humanos ya filtrados (los ids internos viven en el modelo pero no son direccionables). Varios templates pueden aportar secciones al mismo archivo (el documento de módulo compone `dev.module` + `dev.flow_summary` + `dev.data_access_summary` + `dev.dependency_summary` + `dev.unresolved_summary`).

## 8. Renderer Markdown

Único responsable de Markdown, escape (contexto de texto vs. code span; guiones bajos internos no se escapan), links relativos, nombres, particionado y escritura. Salida determinista: escritura atómica de bytes UTF-8 con LF (el manifiesto hashea esos bytes). Únicamente Markdown; HTML no se implementó (D-52-04). Un renderer futuro implementa el mismo contrato `StructuredDocument` sin tocar profiles ni templates.

## 9. Technical Noise Policy

`defaults/noise/default.json`: categorías (`lifecycle_boilerplate`, `transaction_control`, `resource_cleanup`, `exception_handling`, `ui_messaging`, `string_utility`, `platform_library`), patrones (`exact`/`prefix`/`regex` sobre `name`/`label`/`kind`) y visibilidad `hide`/`summarize`/`show`. El código Python no contiene nombres de métodos VB.NET (test). Extensible sin tocar código: un directorio custom con `noise/<id>.json` reemplaza al default (probado: cambiar una categoría a `show` cambia el cuerpo del documento). Lo oculto del cuerpo sigue en los documentos de detalle.

## 10. Idioma

El profile declara `language` (default `es`). Todos los textos fijos salen de un catálogo por clave (`defaults/i18n/es.json`); agregar un idioma es agregar un JSON (probado con un catálogo `en` parcial que cae a `es` por clave). Un idioma inexistente cae a `es` con advertencia. No hay funciones `*_es`/`*_en` nuevas (test) y no hay traducción automática.

## 11. Particionado

Límite combinado (D-52-01): una parte se cierra al alcanzar `max_items_per_part` **o** `max_bytes_per_part`. Determinista, nunca parte un elemento; un elemento mayor que el límite se escribe solo, con advertencia y sin truncar; enlaces Índice/Anterior/Siguiente y filas «a–b de N». Una tabla pequeña (≤ 1/8 del límite) se incrusta en su documento en lugar de generar archivos aparte.

**Medición sobre IST real** (`tools/v5_2_r2_partition_measurement.py`, mismos datos, 7 candidatos):

| items | bytes | archivos | partes | total MB | máx KB | p50 KB | p95 KB |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 32 768 | 1 223 | 701 | 7,83 | 26,3 | 5,1 | 14,7 |
| 200 | 65 536 | 794 | 272 | 7,66 | 58,2 | 5,0 | 28,6 |
| **300** | **65 536** | 653 | 131 | 7,61 | 65,3 | 4,6 | 40,3 |
| 300 | 131 072 | 653 | 131 | 7,61 | 65,3 | 4,6 | 40,3 |
| 500 | 131 072 | 568 | 46 | 7,58 | 104,6 | 4,2 | 58,3 |
| 500 | 262 144 | 568 | 46 | 7,58 | 104,6 | 4,2 | 58,3 |
| 1 000 | 524 288 | 529 | 7 | 7,57 | 145,7 | 4,1 | 68,1 |

Las filas de IST son compactas (~200 B), por lo que en la práctica limita la cantidad y el límite de bytes actúa como red de seguridad ante filas largas. **Defaults elegidos: 300 filas / 65 536 bytes** (partes de ≤ 65 KB, legibles en cualquier editor; menos de la mitad de archivos que 100/32 KB). Configurables por profile.

## 12. Custom templates

Un directorio custom con `templates/<id>.json` (más `profiles/`, `noise/`, `i18n/`): precedencia `custom válido → default`, override parcial por id, fallback automático si no existe. Validación previa (campos obligatorios, versión de contrato, ámbito, ruta de salida sin `..`/absolutas, tipos de bloque, fuentes y campos existentes, claves de idioma, condiciones). Custom inválido o JSON malformado → **warning visible** (resumen de ejecución, `MANIFEST.json`, README raíz y log) y fallback al default; con `strict_templates=True` → `ConfigError` legible. El modo estricto existe a nivel de biblioteca; no se creó CLI (R2 lo permitía). Un template no puede referenciar ids internos, escribir fuera del árbol ni ejecutar código.

## 13. GAPs encontrados

| GAP | Hallazgo | Tratamiento en R2 |
|---|---|---|
| **M1 — módulo** | Solo `Project` es demostrable (259 proyectos); `Solution` da pertenencia. Las rutas de proyecto de `.sln` son relativas al directorio de la solución: se resuelven con aritmética de rutas determinista (224 pertenencias distintas frente a 310 aristas `Solution -> Project`, algunas duplicadas por copias `Backup`) | «Módulo» = proyecto, declarado explícitamente en el texto y en la lista de gaps. Sin agrupación de negocio |
| **F1 — flujos/entry points** | Disponibles en `evidence/` como particiones *passthrough* (`entry_points`, `functional_flows`, `flow_unresolved`, `data_access`, `dependencies`…), no como entidades de primera clase del Core. Suficientes: regenerar `documentation_v52/` solo desde `evidence/` reproduce byte a byte la salida del pipeline (838/838) | Se consume esa proyección legitimada; no se duplicó análisis |
| **F2 — límites no resueltos** | La entidad `UnresolvedBoundary` no lleva `flow_id`, por lo que no puede asignarse a un módulo sin cruzar con `flow_unresolved` | Se usa `flow_unresolved` (mismo contenido persistido) |
| **F3 — flujo → código** | Los flujos no traen `archivo:línea` del manejador; el acceso a datos sí | El detalle de flujos muestra pantalla/evento/manejador/destino; queda pendiente enlazar al código |
| **X1 — sistemas externos** | `ExternalDependency` (assembly) es 1:1 con las aristas `Project -> DLL` (4 838); su `name` incluye versión/cultura | Se agrega por nombre base. El único `database_connection` tiene identificador tipo `CONN-<hash>` (no legible): solo se informa el conteo |
| **D1 — datos** | `DataObject`: 5 389 procedimientos con paquete (útil) y 3 operaciones SQL | Vista por paquete/esquema |
| **B1 — Backup** | No hay evidencia para distinguir producción de copias | No se clasifica: General no lo afirma; Developer lista rutas y anota, como hecho, que la ruta contiene «Backup» |
| **P1 — proyecto ausente** | 1 611 flujos y 923 operaciones de acceso a datos no tienen proyecto asignado | Módulo explícito «(sin proyecto asignado)», al final de los listados |
| **P2 — propósito** | No existe en la evidencia | Frase neutral + punto de extensión INTERPRETED |

## 14. Integración productiva

`render_documentation` (etapa DOCUMENTATION de `full`) llama, de forma aditiva, a `generate_documentation_v52` con los índices en memoria del run más `evidence/external_dependencies.json`. `analyze` no cambia. **Comportamiento de error:** una falla de V5.2 se registra como fallo de la etapa DOCUMENTATION (`documentation_v52: <Excepción>: <mensaje>`), la etapa queda `FAILED` y el run `PARTIAL` según el contrato existente; la documentación legacy ya generada se conserva. No se inventó ningún estado nuevo ni se tocó `StageId`. Las advertencias van al log y a `MANIFEST.json`.

Observación: `RUN_SUMMARY` lista `documentation` pero no `documentation_v52` entre las ubicaciones de salida (la lista es un contrato existente y con tests); se deja como deuda para R3.

## 15. Compatibilidad legacy

Verificado sobre IST: los 876 archivos de `documentation/` del run nuevo son **idénticos byte a byte** (SHA-256) a los del run V5.1 previo (216 MB, archivo máximo 12,9 MB). El motor nunca lee ni escribe `documentation/` (test). Dos archivos de test históricos se actualizaron solo para reconocer el nuevo paquete (recuentos e inventario de V4.1-R0, y `written` de 5 a 6 en el test de la etapa DOCUMENTATION).

## 16. Prueba real IST

`python main.py full "…\IST_40\Operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_2_r2_real_run_c" --verbose` (sin IA; exit 0; todas las etapas SUCCESS, IA `NOT_RUN`). Se generaron `documentation/` y `documentation_v52/`; corridas anteriores no se sobrescribieron.

| Medida | `documentation/` (legacy) | `documentation_v52/` |
|---|---:|---:|
| Tamaño total | 226,5 MB | 7,66 MB |
| Archivos | 876 | 838 `.md` + manifiesto |
| Archivo máximo | 12,9 MB | 49 KB |
| Perfiles | — | general (5 archivos, 4,5 KB), developer (832 archivos, 7,65 MB) |
| Módulos | — | 260 (259 proyectos + «sin proyecto») |
| Partes particionadas | — | 316 |

Distribución de tamaños (838 `.md`): <1 KB: 135 · <4 KB: 262 · <16 KB: 283 · <32 KB: 118 · <64 KB: 40 · ≥64 KB: 0. Además: 0 enlaces rotos; 0 archivos con patrones de ids/hashes (`FLOW-`, `PATH-`, `DAO-`, sha256…); 0 colisiones de nombre sin distinguir mayúsculas. El tamaño menor no se toma como criterio de calidad: lo es la lectura (sección 17).

Determinismo/independencia: regenerar solo desde `evidence/` produce los mismos 838 archivos byte a byte.

Un defecto real apareció y se corrigió durante la prueba: dos proyectos cuyos nombres solo diferían en mayúsculas producían el mismo archivo en Windows (259 documentos para 260 módulos). Los nombres ahora son únicos sin distinguir mayúsculas, `engine` falla en voz alta ante cualquier colisión y hay un test.

## 17. Revisión humana

Se leyeron físicamente los Markdown generados (general completo; módulos: simple `BLInterfazSAP`, medio `blLiquidacion`, complejo `WebPREPrevencion`/`blPENResoluciones`, con datos `sysPENResoluciones`, con no resuelto `blLiquidacion`, más `unassigned`, índice y configuración).

- **General Overview — ¿una persona no desarrolladora entiende a grandes rasgos el sistema?** Parcialmente. Entiende *qué se analizó* (113 soluciones, 259 proyectos, 12 642 flujos, 18,7 % con destino a datos confirmado), qué módulos concentran actividad, qué bibliotecas y proveedor de datos usa, qué paquetes de base de datos existen y qué no se pudo determinar. **No** entiende *qué hace el negocio*: la frase neutral lo declara y, además, los nombres de módulo son técnicos (`sysPENResoluciones`). Es lo que la evidencia estática permite; lo demás depende de INTERPRETED.
- **Developer Technical — ¿encuentra módulo, entrada, flujo, datos, dependencia, archivo?** Sí: README → módulo (índice o tabla) → pantallas con eventos, flujos con procedimiento de destino confirmado, objetivos de datos con `archivo:línea`, proyectos referenciados/usados y bibliotecas externas. Falta el `archivo:línea` del manejador de un flujo (F3).
- **Progressive disclosure:** sí. Raíz 0,7 KB, README developer 2 KB, documento de módulo hasta ~7 KB, detalle en partes ≤ 49 KB y solo bajo enlace («Se muestran 15 de 553: ver todos en el detalle técnico»).
- **Ruido:** dejó de dominar. En `blLiquidacion` se omitieron del cuerpo 242 operaciones transaccionales y 58 llamadas no resueltas de infraestructura (declaradas con conteo y categoría); ya no aparecen `InitializeComponent()`, `dbc.Commit()`, etc. Persisten como ruido residual llamadas a controles de interfaz (`Me.X.DataBind()`, `parametrosSalidaURL`) que el set por defecto aún no clasifica; se corrige agregando datos, no código.

## 18. Suite completa

`python -m unittest discover -s tests`: 2 322 tests, 0 fallas, 0 errores, 132 skips (los esperados de checkout limpio). 62 son nuevos (V5.2 R2). Cubren: ambos perfiles, separación profile/template/renderer (imports), categorías, `INTERNAL_ONLY` no visible, ruido (incluida política custom), templates default válidos, override parcial, custom inválido → warning + fallback, modo estricto, determinismo, particionado por items/bytes/overflow, links entre partes, idioma, frase neutral, INTERPRETED, AI OFF (sin imports de proveedores), independencia de `docs/`/`prompts/`/`tools/`, `documentation/` intacta e integración productiva (incluida una falla de V5.2 visible). Se actualizaron dos archivos de test históricos (el inventario V4.1-R0 con su registro de riesgo/clases/funciones/documentación, y el recuento de `written`) para reconocer el nuevo paquete.

## 19. Deuda pendiente

1. `documentation_v52` no figura en `RUN_SUMMARY.output_locations` (contrato con tests; requiere decisión).
2. Enlazar el manejador de cada flujo a su `archivo:línea` (F3).
3. Ampliar el set de ruido por defecto con controles de interfaz; validar con otro repositorio.
4. Los defaults JSON viajan dentro del paquete Python; el repositorio no tiene un `setup`/`pyproject` que declare *package data* (hoy se ejecuta desde el código fuente). Si se empaqueta, hay que declararlos.
5. Modo estricto sin CLI. INTERPRETED sin cargador desde el pipeline (solo API: `parse_interpreted_sections`/`load_interpreted_sections`); V5.5 lo conectará.
6. El Renderer HTML y el retiro de `documentation/` legacy (ronda posterior, con el criterio de paridad de R1) siguen fuera de alcance.
7. El módulo sigue definido como proyecto; una agrupación de negocio requiere interpretación externa.
8. La medición de particionado se hizo solo sobre IST; validar con otro repositorio antes de fijar los defaults definitivamente.

## 20. Evidencia para pasar a R3

- Corrida real: `C:\PruebasLegacyMapper\Resultados\v5_2_r2_real_run_c` (`documentation/` y `documentation_v52/`, `MANIFEST.json` con hash de cada archivo). Corridas auxiliares `v5_2_r2_real_run` y `v5_2_r2_real_run_b` (previas a dos correcciones de plantilla y de nombres).
- Legacy intacto: 876/876 archivos idénticos por SHA-256 frente al run V5.1.
- Reproducibilidad: regeneración desde `evidence/` = salida del pipeline (838/838).
- Herramienta y tabla de medición de particionado (sección 11); tests en `tests/test_v5_2_r2_documentation_engine.py`.
- Sugerencias de verificación para R3: prueba con un directorio custom real, lectura por otra persona del General Overview, revisión de `RUN_SUMMARY`, y decisión sobre la deuda 1–3.

V5_2_R2_READY_FOR_R3
