# LegacyMapper V4.2 — Manual de Usuario

> Este manual describe el sistema **tal como está implementado en V4.2** (candidata a cierre formal; pendiente de aprobación final del Technical Lead — ver `docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md`). No reemplaza el [Manual de Usuario V4.1](../V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md) ni el [Glosario V4.1](../V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md), que siguen siendo válidos para los conceptos de fondo (hechos determinísticos, confianza, conocimiento canónico, AS_IS/TO_BE/HISTORICAL, GAP vs. CONFLICTO). Este documento se centra en lo que cambió operativamente en V4.2: los comandos `analyze`/`full`/`readiness`, la interpretación de IA opcional, la salida de ejecución (`RUN_SUMMARY`), y la documentación técnica generada — incluida su navegación a partir de V4.2-R8.

---

## 1. Qué hay de nuevo respecto a V4.1

V4.1 exponía un único comando de análisis determinístico. V4.2 lo reorganiza en tres subcomandos explícitos y agrega, de forma estrictamente opt-in, una pasada de interpretación por IA:

- `analyze` — el comportamiento determinístico pre-V4.2 (compatible hacia atrás).
- `full` — análisis determinístico + documentación técnica + un resumen de ejecución (`RUN_SUMMARY`). Es el comando recomendado por defecto.
- `readiness` — valida los prerrequisitos internos de LegacyMapper (no analiza ningún repositorio).

Ninguno de los tres comandos llama a un proveedor de IA real a menos que se pase explícitamente `--allow-ai-interpretation` a `full`.

---

## 2. Comandos disponibles

### 2.1 `analyze` (o invocación heredada sin subcomando)

```
python main.py analyze <repositorio> [--output <salida>] [--exclude <carpeta>] [--verbose] [--flow-max-depth <N>]
python main.py <repositorio> ...                     # atajo heredado, equivalente a `analyze`
```

Análisis determinístico únicamente: produce `index/*.json` y `context/*`. No genera documentación técnica en Markdown ni `RUN_SUMMARY`. Este es exactamente el comportamiento que existía antes de V4.2.

### 2.2 `full` (recomendado)

```
python main.py full <repositorio> --output <salida> [--exclude <carpeta>] [--verbose] [--flow-max-depth <N>] [--allow-ai-interpretation]
```

Ejecuta el análisis determinístico completo, genera la documentación técnica (ver sección 5) y escribe un resumen de ejecución (`RUN_SUMMARY.json`/`RUN_SUMMARY.md`) en la carpeta de salida. Hace **cero llamadas a IA/proveedor** salvo que se agregue `--allow-ai-interpretation`.

### 2.3 `readiness`

```
python main.py readiness
```

Verifica que las condiciones internas de LegacyMapper (evidencia, integridad de conocimiento, seguridad, etc.) estén dadas. No analiza ningún repositorio legado; es una validación del propio sistema.

---

## 3. Comportamiento de IA: apagado por defecto, opt-in explícito

Por defecto, **ningún comando de V4.2 contacta un proveedor de IA real**. Solo `full --allow-ai-interpretation` habilita una pasada adicional de interpretación por IA sobre la evidencia ya producida en esa misma ejecución.

Cuando esa pasada se ejecuta:

- La IA puede generar **propuestas** de interpretación.
- Ninguna propuesta se aprueba automáticamente. Queda pendiente de revisión del Technical Lead (ver sección 9 del [Manual de Usuario V4.1](../V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md)).
- Si la IA falla (proveedor no disponible, respuesta inválida, etc.), la ejecución no se cae: la etapa de interpretación queda marcada como fallida y la ejecución global pasa a `PARTIAL`, preservando toda la documentación determinística ya generada.

**Límite de aprobación:** la funcionalidad de `approve`/`reject`/`request-correction`, la persistencia de decisiones de aprobación (`ApprovalDecision`), y la promoción a conocimiento canónico **no están implementadas todavía** en V4.2 — existe únicamente un diseño aprobado (`docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`, `APPROVED_DESIGN_ONLY`). Toda propuesta generada por IA queda para revisión humana fuera de LegacyMapper mismo.

---

## 4. Estructura de salida de `full`

```
<salida>/
├── index/                 # hechos determinísticos, en JSON (evidencia autoritativa)
├── documentation/          # proyección legible por humanos (ver sección 5)
├── context/, ai_context/   # contexto estructurado para análisis posterior/IA
├── proposals/              # solo si --allow-ai-interpretation generó propuestas
├── RUN_SUMMARY.json        # resumen de la ejecución, en JSON
└── RUN_SUMMARY.md          # el mismo resumen, en Markdown legible
```

`RUN_SUMMARY.json`/`.md` siempre reportan: estado general de la ejecución, estado de cada etapa, si se solicitó/invocó IA, cuántas propuestas hay pendientes, las ubicaciones de salida generadas, y una "próxima acción" recomendada — sin que el usuario tenga que inferir nada de eso mirando el árbol de archivos.

---

## 5. Documentación técnica generada y su navegación (V4.2-R8)

`full` genera diez documentos Markdown de nombre fijo bajo `documentation/`, más un documento de navegación:

```
documentation/
├── README.md                   # empezar aquí (V4.2-R8)
├── PROJECT_OVERVIEW.md
├── SOLUTION_STRUCTURE.md
├── PROJECT_DEPENDENCIES.md
├── WEBFORMS_MAP.md
├── WEB_ENTRY_POINTS.md
├── FUNCTIONAL_FLOWS.md         # índice/resumen -- detalle en functional_flows/
├── DATABASE_ACCESS.md          # índice/resumen -- detalle en database_access/
├── UNRESOLVED_FINDINGS.md      # índice/resumen -- detalle en unresolved_findings/
├── CONFIGURATION_SUMMARY.md
├── ANALYSIS_WARNINGS.md
├── functional_flows/<grupo>.md
├── database_access/<grupo>.md
└── unresolved_findings/<categoría>.md
```

`documentation/README.md` es el punto de entrada: explica qué se analizó, dónde está cada tema, qué significan "confirmado" y "no resuelto", y cómo llegar a la evidencia legible por máquina (`index/*.json`) cuando se necesita más detalle del que muestra un documento humano.

### 5.1 Por qué tres documentos son "índice + detalle" y no un único archivo plano

El pilotaje real de V4.2-R7 (`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md`) encontró que, sobre un repositorio real de escala considerable, `FUNCTIONAL_FLOWS.md` (~44MB), `UNRESOLVED_FINDINGS.md` (~12.8MB) y `DATABASE_ACCESS.md` (~5.2MB) dejaban de ser prácticamente consumibles como un único documento plano. V4.2-R8 corrige esto sin perder ni un dato: cada uno de esos tres documentos pasa a ser un **índice/resumen** (Nivel 1), con enlaces hacia documentos de **detalle** (Nivel 2) partidos por un criterio semántico estable (proyecto, o categoría de hallazgo no resuelto). Los diez nombres de archivo de nivel superior **no cambian** — cualquier automatización o persona que ya sabía dónde buscar `DATABASE_ACCESS.md` lo sigue encontrando, solo que ahora ese archivo es un índice en vez del listado completo.

> Estos valores (~44MB/~12.8MB/~5.2MB) son observaciones históricas del pilotaje real de V4.2-R7. V4.2-R8 no vuelve a ejecutar el repositorio real, por lo que no reporta un nuevo tamaño medido — únicamente corrige el diseño de la documentación con datos sintéticos.

### 5.2 Cómo leer un enlace de detalle

Todo enlace entre documentos es una ruta **relativa** (por ejemplo `functional_flows/Web_MiProyecto_vbproj.md`), nunca una ruta absoluta del sistema de archivos del analista. El nombre de cada archivo de detalle se deriva de forma determinística y segura (nunca de contenido de IA, nunca de un timestamp o UUID) a partir de datos ya descubiertos por el análisis — por ejemplo, el proyecto al que pertenece un flujo o un acceso a base de datos.

### 5.3 "Confirmado" reforzado, no ocultado (F-01)

Un flujo funcional puede reportar `status: unresolved_boundary` (porque alguna llamada no relacionada quedó sin resolver) **y al mismo tiempo** haber alcanzado con éxito un procedimiento almacenado o consulta SQL confirmada. `FUNCTIONAL_FLOWS.md` y sus documentos de detalle muestran ambos hechos por separado (`Confirmed terminal reached` / `Unresolved boundary remains`) junto al estado tradicional, para que ninguno de los dos oculte al otro.

---

## 6. "Confirmado" vs. "no resuelto"

Ver la sección 8 del [Manual de Usuario V4.1](../V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md) para la explicación general. En V4.2, esta distinción se mantiene y se refuerza explícitamente en `FUNCTIONAL_FLOWS.md` (ver 5.3): que una parte de un flujo quede `unresolved` nunca implica que la parte confirmada del mismo flujo deje de ser confiable.

---

## 7. Códigos de salida

| Código | Significado |
|---|---|
| `0` | `SUCCESS` — la ejecución completó sin fallas. |
| `1` | `PARTIAL` — la ejecución produjo documentación/análisis útil, pero alguna etapa no deterministica (por ejemplo la interpretación de IA opcional) falló. |
| `2` | `CLI_USAGE_ERROR` — uso incorrecto de la línea de comandos (argumento faltante o inválido). |
| `4` | `FAILED` — la ejecución no produjo el mínimo resultado útil esperado. |

Este contrato (`SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4`) es estable desde V4.2-R5 y no cambia en V4.2-R8.

---

## 8. Comportamiento ante ejecuciones repetidas (rerun)

Ejecutar `full` dos veces sobre la **misma** carpeta `--output` es seguro:

- `index/`, `documentation/` (incluidos los subdirectorios `functional_flows/`, `database_access/`, `unresolved_findings/`), `context/` y `ai_context/` se sobrescriben con el contenido de la ejecución actual en cada corrida.
- Si una corrida anterior generó más archivos de detalle partido que la corrida actual (por ejemplo, porque un proyecto dejó de tener flujos), los archivos sobrantes de la corrida anterior se eliminan — nunca quedan mostrando información de una ejecución que ya no es la vigente.
- Un archivo que una persona haya colocado manualmente dentro de esas carpetas generadas (por ejemplo una nota propia) se preserva; LegacyMapper nunca borra un archivo que no reconoce como propio.
- `proposals/` (solo existe si se usó `--allow-ai-interpretation`) se limpia al inicio de cada corrida para que una propuesta de una ejecución anterior nunca aparente ser vigente.
- El repositorio legado analizado nunca se modifica, en ninguna de las dos corridas.

---

## 9. Qué NO está implementado en V4.2

Además de lo ya señalado en la sección 4 del [Manual de Usuario V4.1](../V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md) (Plugin runtime, V5, agnosticismo de lenguaje/framework/base de datos/IA):

- **La revisión/aprobación de propuestas no tiene un flujo de comandos propio.** No existen comandos `approve`/`reject`/`request-correction`; la superficie de aprobación está solo diseñada (`APPROVED_DESIGN_ONLY`), no implementada.
- **No hay promoción a conocimiento canónico automatizada en V4.2.** `canonical_knowledge_produced` permanece `false` en toda ejecución de V4.2.
- **El runtime de Plugin sigue sin implementarse** (`PLUGIN_RUNTIME=NOT_IMPLEMENTED`).
- **V5 sigue sin implementarse** (`V5_IMPLEMENTED=false`).

---

## 10. Estado de versión actual

- **V4** = FORMALMENTE CERRADO.
- **V4.1** = FORMALMENTE CERRADO.
- **V4.2** = candidata a cierre; pendiente de revisión final del Technical Lead tras V4.2-R8 (ver `docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md`).
- **Pruebas automatizadas (candidata V4.2-R8):** ver el conteo exacto reportado en el resultado de R8; no se repite aquí para evitar quedar desactualizado.
- **READY** es el estado de disponibilidad requerido antes de cualquier interpretación de IA.
- **Runtime de Plugin:** `NOT_IMPLEMENTED`.
- **V5:** no implementado.

---

Para definiciones de términos, ver el [Glosario V4.1](../V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md) (sigue vigente en V4.2).
Para detalles técnicos de implementación, ver el [Manual Técnico V4.2](LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md).
