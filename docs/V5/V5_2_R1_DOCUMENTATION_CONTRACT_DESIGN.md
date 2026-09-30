# V5.2 R1 — Perfiles, Templates y Contrato de Renderer

## 1. Estado

V5_2_R1_CONTRACT_READY

Ronda exclusivamente de contrato y diseño. No se modificó código productivo, V5.1, roadmap ni `PROJECT_STATE.json`. No se crearon templates, perfiles ni renderers físicos. Las decisiones D-52-01 a D-52-05 del Technical Lead se tratan como cerradas.

## 2. Principios V5.2

1. La documentación humana es una **proyección** del Evidence Core; nunca lo reemplaza ni lo modifica.
2. Una persona entiende primero el sistema y profundiza solo si lo necesita (progressive disclosure).
3. Nunca se inventa. Lo no resuelto se declara, pero se presenta resumido; el detalle completo queda a un enlace de distancia.
4. La documentación base funciona con **AI = OFF**. La IA, si existe, solo aporta contenido `INTERPRETED` opcional.
5. Separaciones obligatorias: Evidence ≠ Documentación; Profile ≠ Template ≠ Renderer; ninguno de los tres es IA.
6. Sin configuración adicional el usuario obtiene documentación legible (defaults completos).
7. Ningún diseño específico de VB.NET/WebForms en los contratos; solo en el set default del adapter actual.

Niveles de lectura: **N1** Qué es · **N2** Cómo funciona · **N3** Cómo está construido · **N4** Evidencia técnica detallada. Los niveles profundos nunca dominan visualmente a los superiores.

## 3. Arquitectura

```
Evidence Core (V5.1, autoridad, solo lectura)
      ↓
Audience Transformation   → AudienceDocumentModel (estructura preparada, sin formato)
      ↓
Output Profile            → decide qué se ve, cuánto detalle, idioma, ruido
      ↓
Template                  → decide cómo se organiza (secciones, orden, tablas, disclaimers)
      ↓
Renderer                  → decide cómo se escribe físicamente (Markdown, escape, archivos, partición)
      ↓
Documentación humana
```

Responsabilidad de cada capa, en una línea:

| Capa | Decide | Nunca decide |
|---|---|---|
| Audience Transformation | agregación, clasificación, orden, navegación | formato, propósito de negocio, IA |
| Profile | audiencia, nivel, categorías, ruido, idioma, política de no resuelto | sintaxis, tablas físicas, escape |
| Template | títulos, orden de secciones, bloques, condicionales, ubicación de disclaimers | qué es ruido, qué evidencia es válida, qué audiencia |
| Renderer | Markdown, escape, nombres de archivo, links, partición, escritura determinista | contenido, importancia, ruido, audiencia |

## 4. General Overview

**Audiencia:** administrador, analista, persona técnica no desarrolladora, nuevo integrante.

**Responde:** qué es el sistema, módulos principales, cómo se relacionan, procesos principales, sistemas externos, datos a grandes rasgos, qué no pudo determinarse.

**Nivel máximo:** N2. Categorías visibles: `KEEP_SIMPLE` (más un resumen agregado de `KEEP_TECHNICAL`).

**No muestra normalmente:** IDs internos, hashes, detalles del resolver, listas exhaustivas de métodos, evidencia cruda, JSON, mecánica interna de LegacyMapper.

**Secciones (contrato de templates default):** sistema analizado · módulos principales (lista corta, una frase por módulo) · relaciones principales (resumen de aristas, no el grafo completo) · procesos observados (priorizando los confirmados) · sistemas externos · datos utilizados (esquemas/paquetes agregados) · limitaciones conocidas.

**Sin IA (sección 14 de este documento):** el documento se genera completo con información determinista. Para el propósito global usa una frase neutral fija:

> «El propósito funcional global no pudo determinarse únicamente desde la evidencia estática disponible.»

No se genera ninguna narrativa. Si existe una `InterpretedSection` para el sistema, se inserta marcada como interpretada (sección 13).

## 5. Developer Technical

**Audiencia:** desarrollador, mantenedor, arquitecto técnico.

**Responde:** organización, módulos/proyectos y su responsabilidad, puntos de entrada, flujo de una operación, componentes participantes, ubicación del código, acceso a datos, dependencias externas, partes no resueltas.

**Nivel máximo:** N4, pero solo bajo demanda. Categorías visibles: `KEEP_SIMPLE` + `KEEP_TECHNICAL`; `DETAIL_ON_DEMAND` solo como enlace.

**Navegación progresiva** (Resumen → Detalle técnico → Evidencia bajo demanda), sin IDs como interfaz principal:

```
Developer README
   ↓
Módulo
   ├─ Resumen
   ├─ Puntos de entrada
   ├─ Flujos
   ├─ Acceso a datos
   ├─ Dependencias
   └─ Detalle (partes / evidencia bajo demanda)
```

Los IDs existen detrás de los enlaces y en el nivel N4; nunca en el texto de navegación ni en prosa de N1–N3.

## 6. Output Profile

Un **Output Profile** es la declaración de *qué* ve una audiencia, independiente de *cómo* se escribe.

**Controla:** audiencia, nivel máximo de detalle, categorías visibles, política de ruido técnico, idioma, inclusión/exclusión de secciones, comportamiento ante información no resuelta, política de enlaces a `DETAIL_ON_DEMAND`, y los límites de partición relevantes para esa audiencia.

**No controla:** sintaxis Markdown/HTML, formato físico de tablas, escape, contenido inventado, lógica de extracción del Evidence Core.

Profiles iniciales: exactamente dos (`general_overview`, `developer_technical`). R0 no encontró evidencia de necesitar un tercero.

## 7. Categorías de contenido

| Categoría | Significado | Regla |
|---|---|---|
| `KEEP_SIMPLE` | Comprensible sin conocimiento técnico (nombres, listas cortas, proporciones, sistemas externos) | Visible en el cuerpo de ambos profiles |
| `KEEP_TECHNICAL` | Útil a un desarrollador (tablas Clase.Método→Objetivo→archivo:línea, entradas, dependencias agrupadas) | Cuerpo principal solo si el profile lo permite; en General Overview solo como resumen |
| `DETAIL_ON_DEMAND` | Exhaustivo (todos los caminos, parámetros, lista completa de no resueltos) | Accesible por enlace/documento hijo; nunca domina el documento principal |
| `INTERNAL_ONLY` | Mecánica interna (ids sha256, punteros a índices, versiones de esquema, bloques de disclaimer repetidos, marcas del resolver) | **Nunca** aparece por defecto en documentación humana |

La clasificación es puramente de presentación: ningún dato se elimina del Evidence Core. Cada elemento del `AudienceDocumentModel` lleva su categoría; el profile filtra por ella.

## 8. Technical Noise Policy

Contrato de configuración (**datos, no código**) que un profile referencia (D-52-03). Agnóstico de tecnología.

**Campos mínimos:**
- `noise_categories`: lista de categorías abstractas de llamada/elemento consideradas ruido (p. ej. `exception_handling`, `transaction_control`, `ui_messaging`, `string_utility`, `resource_cleanup`).
- `patterns`: por categoría, reglas de coincidencia declarativas (nombre exacto, prefijo, expresión, tipo de entidad) que asignan un elemento a esa categoría.
- `body_visibility`: por categoría, `hide` | `summarize` | `show` en el cuerpo principal.
- `detail_availability`: por categoría, si permanece accesible en DETAIL_ON_DEMAND (por defecto sí; lo oculto del cuerpo nunca se pierde).

**Extensión sin modificar código:** los sets se cargan desde archivos de datos con precedencia `usuario → default del adapter`, con fusión por categoría. Se marca cada regla con su origen para trazabilidad.

**Default:** un set inicial para el adapter actual (equivalente conceptual a `PRESENTATION_TECHNICAL_METHOD_NAMES`) empaquetado como dato del adapter, no del renderer ni del núcleo.

**No le corresponde:** decidir formato, ni modificar `technical_noise_candidate` del Evidence Core (el Core conserva todo; la policy solo afecta presentación).

## 9. Template

Un **Template** define la *forma* de un documento a partir de un `AudienceDocumentModel` ya filtrado por el profile.

**Controla:** títulos, encabezados, orden de secciones, bloques, tablas (columnas/orden), inclusión condicional (p. ej. omitir una sección vacía), layout textual, posición de disclaimers (una vez por documento, no por elemento), y enlaces entre niveles.

**No decide:** qué es ruido, qué evidencia es válida, qué datos existen, qué nivel necesita una audiencia, lógica del profile, ni llamadas a IA. Un template no tiene acceso de escritura al Evidence Core ni ejecuta código.

**Templates default** (solo nombres y responsabilidades; sin archivos físicos aún):

*General Overview*
- `overview.system` — sistema analizado, propósito (o frase neutral), sección `INTERPRETED` opcional.
- `overview.modules` — módulos principales, una frase cada uno.
- `overview.external_systems` — sistemas externos.
- `overview.data` — datos a grandes rasgos.
- `overview.limitations` — limitaciones conocidas y resumen de lo no resuelto.

*Developer Technical*
- `dev.index` — punto de entrada (Developer README).
- `dev.module` — resumen y enlaces por módulo.
- `dev.flow_summary` — flujos con entrada, evento y destino.
- `dev.data_access_summary` — acceso a datos.
- `dev.dependency_summary` — dependencias proyecto→proyecto agrupadas y externas.
- `dev.unresolved_summary` — resumen de no resuelto por módulo, con enlace al detalle.
- `dev.technical_detail` — documentos N4 particionados.

## 10. Templates custom

Requisitos y contrato conceptual:

- Un usuario aporta un directorio de templates; **no se modifica código**.
- **Override parcial:** se sustituye por `TemplateDescriptor.id`; los demás siguen siendo default.
- **Precedencia:** `custom (si existe y es válido) → default`. Si el custom no existe, fallback automático y silencioso al default. Si existe pero es **inválido**, error legible (qué archivo, qué regla, qué línea) y, según política del profile, fallback al default con advertencia visible o detención; la elección de comportamiento por defecto queda como decisión abierta menor (sección 20).
- **Validación previa a renderizar:** identidad conocida, campos del modelo referenciados existentes, ausencia de referencias a categorías `INTERNAL_ONLY`, versión de contrato compatible.
- **Aislamiento:** un template recibe una vista de solo lectura del modelo; no puede alterar el Evidence Core ni el modelo, ni ejecutar lógica arbitraria (formato declarativo, sin código embebido).
- No se implementa loader en V5.2 R1.

## 11. Renderer

**Único responsable de:** convertir estructura preparada → formato físico; Markdown; escape; nombres de archivo; links; partición física; límites por cantidad y tamaño; escritura determinista.

**No decide:** audiencia, importancia, ruido, qué datos incluir, interpretación de negocio.

**Contrato (`RendererContract`):** entrada = documento estructurado (post-profile, post-template) + `PartitionPolicy`; salida = conjunto de archivos con contenido y nombres deterministas. Misma entrada ⇒ mismos bytes.

**Extensibilidad (D-52-04):** V5.2 implementa solo Markdown. HTML queda fuera del alcance mínimo. Un renderer futuro implementa el mismo contrato sin tocar Profiles ni Templates, porque estos nunca contienen sintaxis física.

Reutilizable de hoy: `sanitize_label`/`build_partition_filenames` de `_documentation_partitioning.py`.

## 12. Particionado

Contrato combinado (D-52-01), responsabilidad del renderer, con **límites configurables provistos por el profile**:

- `max_items_per_part` — límite por cantidad.
- `max_bytes_per_part` — límite aproximado por tamaño físico. Una parte se cierra cuando **cualquiera** de los dos se alcanza.
- Partición determinista: orden estable de elementos ⇒ mismas partes en cada corrida; nunca se parte un elemento a la mitad.
- Nombres deterministas (`<base>-part-000001.md`, reutilizando la convención actual).
- Navegación entre partes: enlaces anterior/siguiente y a un índice.
- Índice principal pequeño; los documentos raíz solo enlazan.
- Un elemento individual mayor que el límite de bytes se emite solo en su parte y se registra como advertencia (no se trunca).

**No se fijan cifras.** R0 midió el problema (archivo de 9,9 MB con límite solo por cantidad); R2 medirá defaults reales sobre IST.

## 13. INTERPRETED

Contrato de inserción futura (D-52-02). Todo contenido tiene una etiqueta de naturaleza: `DETERMINISTIC` o `INTERPRETED`.

`InterpretedSection`: contenido opcional adjuntable a un nivel (sistema, módulo, flujo) con origen declarado.

Reglas:
- Puede **faltar**: su ausencia no rompe nada ni impide General Overview.
- Nunca reemplaza ni oculta evidencia determinista; se muestra **visualmente diferenciada** y con su origen.
- Debe indicar su origen (persona, IA con proveedor/modelo, sistema externo) y fecha.
- Sin contenido INTERPRETED, la documentación indica claramente que ese contexto no está disponible.
- La fuente puede ser V5.5 u otra; V5.2 solo define el punto de extensión y no importa ningún proveedor de IA.

## 14. Idioma

El profile declara `language`. Default: `es`.

Arquitectura: los textos fijos (títulos, frases neutrales, etiquetas) se resuelven por **claves de mensaje** contra un catálogo por idioma (datos), no mediante funciones duplicadas `_es`/`_en`. Añadir un idioma = añadir un catálogo. Sin traducción automática. Clave ausente en un idioma ⇒ fallback al catálogo `es` con marca visible en pruebas. El contenido determinista extraído del código (nombres, archivos) no se traduce.

## 15. Transición legacy

Objetivo (D-52-05): reemplazo gradual sin dos sistemas permanentes.

- **Coexistencia:** la nueva documentación se escribe en un directorio propio (nombre conceptual `documentation_v52/`, con subcarpetas por profile: `general/`, `developer/`). `documentation/` legacy no se toca durante la transición.
- **Sin sobreescritura accidental:** los dos árboles nunca comparten ruta; el renderer nuevo se niega a escribir en `documentation/`.
- **Consumidores existentes:** siguen leyendo `documentation/`, `index/`, `ai_context/`, `consumer_projection/` sin cambios.
- **Comparación/regresión:** ambos árboles se generan desde el mismo Evidence Core en la misma corrida, permitiendo comparar cobertura (nada relevante presente en legacy debe faltar en V5.2, salvo lo reclasificado como `INTERNAL_ONLY`).
- **Retiro:** ronda posterior explícita (fuera de V5.2 R1) que: (a) verifica paridad, (b) renombra `documentation_v52/` al destino definitivo, (c) elimina el generador legacy y sus tests. Criterio de cierre: no queda ningún generador legacy ni doble ruta.

## 16. Contratos conceptuales

Solo conceptuales; no se implementan clases. Se evitan schemas excesivos.

**OutputProfile** — Propósito: declarar qué ve una audiencia.
Mínimos: `id`, `audience`, `max_detail_level`, `visible_categories`, `language`, `noise_policy_ref`, `unresolved_behavior` (`summary_with_link`|`inline`|`hidden`), `partition_policy_ref`.
Opcionales: `section_include/exclude`, `detail_link_policy`.
Responsable de: filtrar. No le corresponde: formato, escape, extracción.

**TemplateDescriptor** — Propósito: identificar y describir un template.
Mínimos: `id`, `profile_compat`, `contract_version`, `sections` (orden + condiciones), `source` (`default`|`custom`).
Opcionales: `title_keys`, `disclaimer_position`, `table_layouts`.
Responsable de: forma. No le corresponde: ruido, validez de evidencia, IA, código.

**RendererContract** — Propósito: transformar documento estructurado en archivos.
Mínimos: `format_id`, entrada (documento + `PartitionPolicy`), salida (lista de archivos con nombre/bytes).
Opcionales: `escape_rules`, `link_style`.
Responsable de: escritura determinista. No le corresponde: contenido, audiencia.

**PartitionPolicy** — Propósito: límites físicos.
Mínimos: `max_items_per_part`, `max_bytes_per_part`.
Opcionales: `overflow_behavior`, `naming_pattern`.
Responsable de: acotar tamaño. No le corresponde: decidir qué contenido entra.

**TechnicalNoisePolicy** — sección 8.
Mínimos: `noise_categories`, `patterns`, `body_visibility`.
Opcionales: `detail_availability`, `origin`.

**AudienceDocumentModel** — Propósito: estructura neutral preparada para humanos.
Mínimos: nodos de documento (sistema→módulo→elemento), cada uno con `category` (sección 7), `nature` (`DETERMINISTIC`/`INTERPRETED`), texto/valores agregados, `detail_refs` (enlaces a evidencia con trazabilidad).
Opcionales: métricas agregadas, orden de presentación.
Responsable de: agregar, resumir determinísticamente, clasificar, ordenar, preparar navegación, preservar trazabilidad. No le corresponde: Markdown, inventar propósito, IA, modificar Evidence Core.

**InterpretedSection** — sección 13.
Mínimos: `target` (nivel/entidad), `content`, `origin`, `created_at`.
Opcionales: `confidence_note`, `language`.
Responsable de: transportar contenido interpretado. No le corresponde: reemplazar evidencia ni generarse dentro de V5.2.

**Audience Transformation** (nombre conceptual: `AudienceTransformer`): función pura Evidence Core + `TechnicalNoisePolicy` → `AudienceDocumentModel`; determinista, sin efectos, sin IA. Se dejó fuera del profile a propósito: el profile filtra lo ya clasificado; la transformación clasifica.

## 17. Defaults

Sin configuración, IA ni templates custom el usuario obtiene ambos profiles.

| | General Overview | Developer Technical |
|---|---|---|
| Nivel máximo | N2 | N4 (bajo demanda) |
| Categorías en cuerpo | `KEEP_SIMPLE` (+ resumen `KEEP_TECHNICAL`) | `KEEP_SIMPLE`, `KEEP_TECHNICAL` |
| `DETAIL_ON_DEMAND` | enlace mínimo o ausente | enlaces + documentos hijo |
| `INTERNAL_ONLY` | nunca | nunca |
| Ruido | oculto del cuerpo | resumido; disponible en detalle |
| No resuelto | una línea/resumen | resumen por módulo + enlace |
| Idioma | `es` | `es` |
| Particionado | límites por defecto a medir en R2 | ídem |

## 18. Gaps detectados

1. **Propósito de negocio del sistema:** no existe en el Evidence Core (esperado; se cubre con `INTERPRETED`).
2. **Clasificación producción vs. copia de respaldo** (`Backup`, `_back`, etc.): no existe como atributo; hoy `CONFIGURATION_SUMMARY.md` no la distingue. Requiere GAP formal si se desea distinguirla; V5.2 no puede inventarla.
3. **Agrupación en "módulos" para el lector:** el Evidence Core tiene `Solution`/`Component`; no se verificó en esta ronda si una noción de "módulo de alto nivel" (agrupación de proyectos) es derivable determinísticamente. R2 debe confirmar o registrar GAP.
4. **Flujos, caminos y puntos de entrada:** los flujos humanos de V4.3 provienen de los índices V4.3; el Evidence Core de V5.1 puede no exponerlos como entidades de primera clase. R2 debe verificar la fuente de datos de `dev.flow_summary` y, si falta, registrar GAP en lugar de modificar V5.1.
5. **Sistemas externos y datos agregados:** `ExternalDependency` y `DataObject` existen; la agregación por esquema/paquete debe confirmarse en R2.
6. **Ruido técnico como categoría abstracta:** hoy es una lista de nombres de método; la clasificación por categoría abstracta requiere definir el set default inicial (trabajo de R2, no un cambio al Core).
7. **`SYSTEM_CONTEXT.md` en inglés** dentro de `ai_context/`: fuera del alcance de V5.2 (no es documentación humana de esta arquitectura).

## 19. Plan de validación R2/R3

R2 (medición y prototipo de contrato) y R3 (verificación) deberán comprobar como mínimo:

- documentación determinista (misma entrada ⇒ mismos bytes);
- reproducibilidad de partición y nombres;
- profiles separados (cambiar de profile no altera el Evidence Core ni el otro profile);
- **ausencia de `INTERNAL_ONLY` por defecto** (prueba de búsqueda de patrones de ids/hash en la salida N1–N3);
- progressive disclosure (el documento principal no supera un tamaño acotado; el detalle está a un enlace);
- límites de tamaño respetados por archivo (medidos sobre IST, definiendo los defaults reales);
- custom templates: override parcial, fallback al default, error legible en template inválido, imposibilidad de modificar el Evidence Core;
- compatibilidad legacy (`documentation/` intacto; sin doble escritura);
- independencia de runtime y de IA (sin imports de proveedores; ejecución con AI = OFF);
- General Overview completo sin `INTERPRETED`, con frase neutral;
- prueba real sobre IST comparando contra la línea base R0 (152,3 MB en `flujos_humanos/`, archivo máximo 9,9 MB).

## 20. Decisiones abiertas reales

Ninguna bloquea R1. Quedan a decidir antes o durante R2:

1. **Template custom inválido:** ¿fallback al default con advertencia, o detención? (Recomendación: fallback con advertencia visible en el resumen de ejecución; detención con flag estricto.)
2. **Ubicación/formato de los archivos de datos** de noise policy y catálogos de idioma (formato declarativo simple; a fijar en R2).
3. **Nombre definitivo de directorios** de transición (`documentation_v52/` es conceptual).
4. **Gaps 2–5 de la sección 18:** si el Technical Lead desea que algún dato adicional entre al Evidence Core, requiere ronda propia sobre V5.1 (no se toca silenciosamente).

## 21. Conclusión

El diseño separa cuatro responsabilidades que hoy están mezcladas en generadores Python con Markdown embebido: preparar el contenido para una audiencia (Audience Transformation), decidir qué se ve (Profile, incluyendo ruido técnico), decidir la forma (Template) y escribirlo físicamente con límites de cantidad y tamaño (Renderer). Con dos perfiles, cuatro categorías de contenido, un punto de extensión `INTERPRETED` opcional y una transición con coexistencia y retiro explícito, se resuelven los dos problemas bloqueantes de R0 (no existe vista general; el particionado solo por cantidad produce archivos inmanejables) sin alterar el Evidence Core ni depender de IA. Los gaps se registran para R2; ninguno impide cerrar el contrato.

V5_2_R1_CONTRACT_READY
