# V4.3 — R1 — Contrato de proyección consumible — Resultado

## Estado de esta ronda

`V4_3_R1_RESULT_DRAFTED_PENDING_HUMAN_REVIEW`. Esta ronda es de **diseño de contrato**, no de implementación:
define la forma, el vocabulario y las reglas de las tres superficies pedidas por
`prompts/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT.md`, sin modificar `legacy_documenter/`, sin generar
código nuevo y sin tocar `PROJECT_STATE.json`. La implementación real de estas superficies corresponde a
rondas posteriores (ver sección 9). Por el `Gate` del propio prompt, **no se avanza a R2** hasta que este
resultado sea revisado y aprobado por el Líder Técnico. El cierre y versionado formal de V4.3 sigue
correspondiendo exclusivamente a R9, sin cambios respecto de lo ya registrado en el resultado de R0.

## 1. Objetivo de esta ronda

Diseñar el contrato estable que separa la evidencia interna exhaustiva (los índices `index/*.json` y los
artefactos `ai_context/*.json` ya producidos de forma determinista) de tres proyecciones consumibles
derivadas de ella: `human_documentation`, `ai_projection` y `consumer_projection`. Este contrato es la base
que R2 (hidratación y selección de evidencia), R3 (documentación humana), R4 (escalado y particionamiento),
R5 (presupuesto de contexto de IA) y R6 (proyección de IA y consumidor) deberán implementar.

## 2. Definición fundamental: referencia vs. registro hidratado

Se fijan dos conceptos distintos, ya distinguibles hoy en el código pero sin un nombre de contrato explícito:

- **Referencia** (`REFERENCE`): un identificador puro que apunta a evidencia sin incluir su contenido. Es
  exactamente lo que `ContextResolver.resolve()`/`ContextComposer.compose()` producen hoy en `records`
  (`{"ref": <id>, "priority": "P0".."P4", "category": "flow_refs"|"path_refs"|"data_access_refs"|
  "evidence_refs"|"unresolved_refs"}`). Una referencia por sí sola no es información legible ni interpretable;
  requiere abrir el índice exhaustivo correspondiente para tener significado (esto es exactamente `EEE-03` del
  resultado de R0).
- **Registro hidratado** (`HYDRATED_RECORD`): la misma referencia, resuelta a un conjunto fijo y cerrado de
  campos ya existentes de forma determinista en los índices/artefactos actuales (nunca inventados), suficiente
  para interpretar el elemento sin volver a abrir el índice completo. Un registro hidratado nunca añade un
  campo que no exista ya en alguna fuente determinista (`SYSTEM_CONTEXT.json`, `FUNCTIONAL_FLOWS.json`,
  `TRACEABILITY.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`,
  `index/sql_operations.json`); solo cambia su forma de composición y ubicación.

Regla de contrato: `ai_projection` y `consumer_projection` transportan **registros hidratados**, nunca
referencias sueltas, salvo en el caso explícito de contenido deliberadamente excluido por presupuesto (ver
`truncation`/`continuation_refs`, ya existente en `ContextComposer`), donde una referencia sin hidratar es
aceptable siempre que quede marcada como excluida, nunca presentada como si fuera contenido completo.

### 2.1 Forma cerrada de un registro hidratado de `PATH`

Ilustrativa, no normativa a nivel de código; fija los campos y su origen determinista, para que R2 los
implemente sin inventar estructura adicional:

```text
HydratedPathRecord:
  path_id            <- FUNCTIONAL_FLOWS.json / index/functional_paths.json (path_id)
  flow_id            <- FUNCTIONAL_FLOWS.json (flow_id)
  entry_point        <- resuelto desde index/entry_points.json (id, webform, event, handler)
  nodes               <- FUNCTIONAL_FLOWS.json (nodes), cada nodo con su label ya existente en ARCHITECTURE_GRAPH.json
  terminal_type       <- FUNCTIONAL_FLOWS.json (terminal_type)
  terminal_target      <- resuelto: DAO/SP/SQL id + su nombre/etiqueta desde index/{data_access,stored_procedures,sql_operations}.json
  confidence          <- FUNCTIONAL_FLOWS.json (confidence: confirmed | inferred | unresolved)
  evidence_refs        <- TRACEABILITY.json (path_to_references.call_references)
  source_index_pointer  <- ruta exhaustiva de origen (p. ej. "index/functional_paths.json#<path_id>"), para trazabilidad sin obligar a abrirla
```

Ningún campo de esta forma es narrativo ni generado por IA: todos provienen de índices deterministas ya
existentes. La "hidratación" es composición y resolución de referencias cruzadas, no interpretación.

`source_index_pointer` se conserva exclusivamente para fines de procedencia/auditoría (poder rastrear un
registro hidratado hasta su índice exhaustivo de origen), **no** como mecanismo de completitud. `ai_projection`
y `consumer_projection` deben ser autocontenidas: un consumidor no necesita acceder al archivo apuntado por
`source_index_pointer` para comprender el registro hidratado — si comprenderlo requiere abrir ese archivo, el
registro está incompleto y el defecto está en la hidratación (R2), no en la ausencia del puntero. En
consecuencia, `source_index_pointer` nunca puede usarse para suplir un campo omitido de la proyección: un
campo que la forma cerrada (sección 2.1 y las que R2 defina) declara como parte del registro debe estar
presente en el registro mismo, nunca delegado implícitamente al índice referenciado.

## 3. Vocabulario de estado: `CONFIRMED` / `INTERPRETED` / `UNRESOLVED`

Este contrato fija el vocabulario de estado para las tres superficies, alineado con el que ya exige
`legacy_documenter/documentation/interpretation.py::AssessmentValidator` (una entrada con
`source_type=AI_INTERPRETATION` nunca puede tener `status=CONFIRMED`) y con las etiquetas de confianza ya
producidas por el pipeline determinista (`confirmed` / `inferred` / `unresolved` en `FUNCTIONAL_FLOWS.json`,
`entry_points`, etc.):

| Estado del contrato | Origen permitido | Regla |
|---|---|---|
| `CONFIRMED` | Únicamente evidencia determinista (`confidence=confirmed` en el índice de origen) | Nunca se asigna a una afirmación cuyo `source_type` sea `AI_INTERPRETATION` |
| `UNRESOLVED` | Evidencia determinista sin resolución (`confidence=unresolved`, terminal no resuelto, referencia rota) | Se preserva explícitamente; nunca se oculta ni se completa con una suposición |
| `INTERPRETED` | Exclusivamente contenido producido por IA (`source_type=AI_INTERPRETATION`) | Siempre adjunto como capa adicional sobre un registro hidratado, nunca sustituye ni reescribe sus campos `CONFIRMED`/`UNRESOLVED` |

`confidence=inferred` (ya existente en el modelo V1–V3) se mantiene como una variante determinista intermedia
propia de la evidencia de código, distinta de `INTERPRETED`: `inferred` es una conclusión determinista de baja
certeza calculada por Python; `INTERPRETED` es, por definición, un aporte de IA. Ninguna ronda de V4.3 debe
fusionar ambos conceptos.

## 4. IDs y trazabilidad

Ninguna superficie introduce un espacio de identificadores nuevo. Se reutilizan, sin modificación, los IDs ya
deterministas del pipeline V1–V3/V4 (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`, IDs de `entry_points`, y el
prefijo `KNO-` de V4 cuando el contenido proyectado provenga del conocimiento canónico en vez de la evidencia
de código). Para la identidad de un paquete/documento de proyección en sí (no de sus elementos), se reutiliza
el patrón ya existente `CTX-<sha256>` de `ContextResolver`/`ContextComposer` (`package_id`), extendido con un
prefijo propio por superficie para no colisionar con los paquetes de contexto actuales:

| Superficie | Prefijo de paquete propuesto | Reutiliza |
|---|---|---|
| `ai_projection` | `AIP-<sha256>` | Mismo método de cálculo que `package_id` (SHA-256 canónico sobre el cuerpo serializado) |
| `consumer_projection` | `CPJ-<sha256>` | Idéntico método |
| `human_documentation` | Ninguno nuevo; la trazabilidad es por archivo (`document_path`) y por marcador `<!-- knowledge_id: ... -->` ya definido en R11 cuando aplica a conocimiento canónico, o por el propio `FLOW-*`/`PATH-*` cuando la superficie documenta evidencia de código directamente | Patrón de R11 (`legacy_documenter/knowledge/projection/markdown_renderer.py`) |

Todo registro hidratado conserva, sin excepción, el/los ID(s) determinista(s) que lo originan. Ninguna
superficie puede presentar contenido sin que su(s) ID(s) de origen sean recuperables.

## 5. Las tres superficies

### 5.1 `human_documentation`

- **Prioridad**: máxima frente a las otras dos superficies cuando compiten por espacio o esfuerzo de
  implementación (según el propio prompt).
- **Idioma**: español por defecto (`EEE-07`), excepto identificadores técnicos, código, comandos, nombres de
  contrato, rutas y nombres oficiales de tecnología/producto, que permanecen intactos — misma regla ya vigente
  en `docs/GENERATED_ARTIFACT_POLICY.md` §"Idioma de la documentación para humanos", extendida aquí
  explícitamente a la documentación generada por el producto (`exporters/technical_documentation_renderer.py`
  hoy en inglés, ver D-05 de R0), no solo a la documentación del propio repositorio.
- **Orden de lectura**: resumen antes de detalle. Reutiliza y generaliza el patrón navegación/detalle que
  V4.2-R8 ya introdujo (`*_navigation()` + `*_partitions()`) a las vistas que hoy carecen de él o que R0
  clasificó como aún planas/ruidosas (`D-06`, incluye el ruido `InitializeComponent()` de `F-06`).
- **Relación con lo existente**: superficie sobre evidencia de código (nueva, a implementar en R3/R4) y
  superficie sobre conocimiento canónico (ya existente, R11, `knowledge/projection/`) — este contrato no
  fusiona ambas en un solo mecanismo; declara que ambas son instancias válidas de `human_documentation` con la
  misma regla de idioma y el mismo principio resumen-antes-que-detalle, pero orígenes de datos distintos
  (índices deterministas de código vs. `CanonicalKnowledgeCollection`).
- **schema/versión**: se introduce `HUMAN_DOCUMENTATION_PROJECTION` como nombre de familia de contrato,
  versión `1.0`, aplicable a la proyección de evidencia de código (distinta de `R11`'s propio
  `DocumentProjection`, que ya tiene su propio contrato y no se renombra ni se toca).

### 5.2 `ai_projection`

- **Contenido**: registros hidratados (sección 2), nunca referencias sueltas salvo exclusión explícita por
  presupuesto.
- **Compacidad**: presupuesto real y obligatorio, no solo seleccionable. Corrige `D-01`: el contrato exige que
  todo paquete `ai_projection` declare y respete un presupuesto propio (`max_records`/`max_characters`/
  `max_estimated_tokens`), reutilizando los perfiles ya existentes (`TINY`/`SMALL`/`MEDIUM`/`LARGE`), pero
  **sin** admitir `FULL` (ilimitado) como perfil válido para esta superficie — un paquete `ai_projection` sin
  techo de presupuesto no es conforme a este contrato.
  Se aclara explícitamente que este presupuesto propio del paquete **no basta, por sí solo, para autorizar una
  llamada al proveedor**: es un límite sobre el contenido de `records`, no sobre el payload final que
  efectivamente viaja al proveedor. R5 debe medir y limitar, además, el **payload final serializado del
  request** — es decir, el conjunto realmente enviado: `system_instruction`, `user_instruction`, el `schema`
  de salida estructurada, el sobre (`envelope`: `package_type`, `schema_version`, `package_id`,
  `source_snapshot`, etc.), los `records` hidratados, `statistics` y `truncation`, y cualquier otro contenido
  que forme parte del `LLMRequest` real. Un paquete `ai_projection` dentro de su propio presupuesto puede, aun
  así, producir un `LLMRequest` serializado que exceda el límite del proveedor una vez sumados
  `system_instruction`/`user_instruction`/`schema`/sobre; ese caso debe tratarse en R5, nunca ignorarse.
  Una llamada cuyo payload final serializado exceda el límite aplicable debe reducirse o particionarse antes
  del envío, o bien devolver `CONTEXT_TOO_LARGE` (estado ya existente en `legacy_documenter/llm/core.py`,
  `STATUSES`); nunca debe enviarse ciegamente al proveedor confiando solo en el presupuesto de `ai_projection`.
  La implementación de ambos límites (presupuesto de `ai_projection` y límite del payload final del request)
  corresponde a R5.
- **Autocontenido**: debe satisfacer el criterio de la sección 8 (no depender de abrir `FUNCTIONAL_FLOWS.json`
  completo).
- **Instrucción de IA**: todo `LLMRequest` construido a partir de un paquete `ai_projection` debe incluir,
  en su `system_instruction`, una prohibición explícita de uso de herramientas y una instrucción de devolver
  únicamente la estructura solicitada (`EEE-05`, `D-04`). Este contrato fija el requisito; la redacción exacta
  de la instrucción corresponde a R5/R6, sobre `legacy_documenter/documentation/interpretation.py`.
- **AI nunca sustituye evidencia determinista, y `AI_HYDRATED_PROJECTION 1.0` no transporta `INTERPRETED` por
  defecto**: un paquete `ai_projection` contiene **exclusivamente evidencia determinista hidratada**
  (`CONFIRMED`/`UNRESOLVED`, sección 3) — nunca genera campos `CONFIRMED`/`UNRESOLVED` a partir de una
  respuesta de IA. Esta regla ya está impuesta en código para el resultado del lado del proveedor
  (`AssessmentValidator`: `"invalid confirmed"` si `source_type` es `AI_INTERPRETATION`); este contrato la
  extiende explícitamente a la entrada. Además, por defecto un paquete `AI_HYDRATED_PROJECTION 1.0` **no
  incluye** resultados `INTERPRETED`/`AI_INTERPRETATION` de ejecuciones de IA anteriores: es la entrada que se
  envía a un proveedor, no un acumulador de interpretaciones previas. Una interpretación de IA ya generada
  pertenece a una capa de salida separada — `AI_INTERPRETATION` (el propio `LLMResponse`/`parsed_output`),
  `proposals` (R8, si esa interpretación se formaliza como propuesta), o `human_documentation` (si se proyecta
  para lectura humana) — nunca al paquete de entrada `ai_projection`. Este contrato **no crea** todavía ningún
  mecanismo de interpretación recursiva (una IA reinterpretando su propia interpretación previa, o la de otra
  ejecución, como si fuera evidencia de entrada); si una necesidad así surge, requiere su propio diseño
  explícito en una ronda futura, no una extensión implícita de `AI_HYDRATED_PROJECTION 1.0`.
- **schema/versión**: `AI_HYDRATED_PROJECTION 1.0`, transportado dentro del sobre (`envelope`) de paquete ya
  existente (`package_type`, `schema_version`, `package_id`, `source_snapshot`, `statistics`, `truncation`),
  añadiendo un campo `records` cuyo elemento es ahora `HydratedRecord` en vez de `Reference` — cambio aditivo
  de contenido, no de sobre.

### 5.3 `consumer_projection`

- **Formato**: JSON estable, análogo en espíritu a `LegacyMapperPluginKnowledge 1.0` (R12,
  `legacy_documenter/knowledge/plugin_projection/`), pero para la capa de evidencia de código hidratada, no
  para conocimiento canónico aprobado. No implementa Plugin Runtime (`PLUGIN_RUNTIME_NOT_IMPLEMENTED` se
  mantiene sin cambios).
- **Estabilidad**: mismo principio que R12 — `SILENT_ENTRY_OMISSION=FORBIDDEN`, contenido siempre acompañado
  de `contract_name`/`contract_version`, y ningún campo de metadata arbitraria se proyecta sin control
  explícito.
- **Independencia**: al igual que R12 respecto de R11 (`R11_DEPENDENCY=NONE`), `consumer_projection` no
  depende de `human_documentation` ni la importa; ambas se derivan, de forma independiente, de los mismos
  registros hidratados.
- **schema/versión**: `LegacyMapperConsumerProjection 1.0`. Nombre deliberadamente distinto de
  `LegacyMapperPluginKnowledge` (R12) para no implicar que sustituye o reemplaza el contrato de conocimiento
  canónico: `consumer_projection` proyecta evidencia de código hidratada; `LegacyMapperPluginKnowledge`
  proyecta conocimiento canónico aprobado por el Líder Técnico. Son capas distintas y este contrato no las
  fusiona.

## 6. Índices exhaustivos como fuente técnica

Invariante explícito de este contrato: `index/*.json`, `ai_context/SYSTEM_CONTEXT.json`,
`ai_context/FUNCTIONAL_FLOWS.json`, `ai_context/TRACEABILITY.json` y `ai_context/ARCHITECTURE_GRAPH.json`
siguen siendo la fuente técnica exhaustiva y autoritativa. Ninguna de las tres superficies los sustituye,
resume de forma destructiva, ni se convierte en la fuente de verdad en su lugar — son siempre una proyección
derivada, y todo registro hidratado conserva un puntero de vuelta al índice exhaustivo de origen
(`source_index_pointer`, sección 2.1) para que el detalle completo siga siendo recuperable cuando se necesite.

## 7. Compatibilidad con V4.2

La compatibilidad que exige este contrato es **estructural y de contratos/rutas**, según lo definido abajo —
no byte-identical para la superficie `human_documentation`:

- Ningún artefacto existente (`SYSTEM_CONTEXT.json`, `FUNCTIONAL_FLOWS.json`, `TRACEABILITY.json`,
  `ARCHITECTURE_GRAPH.json`, el sobre de paquete de `ContextResolver`/`ContextComposer`,
  `knowledge/projection/` R11, `knowledge/plugin_projection/` R12) cambia de nombre, de ruta ni de campo
  existente. Estos son los artefactos **machine-readable** cuyo schema no debe romperse salvo un cambio
  explícitamente versionado (nuevo `schema_version`/`contract_version`, documentado como tal).
- Las tres superficies nuevas se añaden junto a lo existente, no en su lugar.
- El **contenido humano** generado por `exporters/technical_documentation_renderer.py` (`WEB_ENTRY_POINTS.md`,
  `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`) queda explícitamente excluido de
  cualquier expectativa de estabilidad byte-a-byte: V4.3 puede, e intencionalmente va a, cambiar ese contenido
  para pasar a español por defecto (`EEE-07`), aplicar resumen-antes-de-detalle, filtrar o re-presentar ruido
  ya identificado (`F-06`) y añadir nuevas proyecciones. Lo que se preserva de V4.2 para estos documentos es
  su **rol y ubicación** (siguen siendo la documentación técnica determinista en `documentation/`), no su
  texto exacto.
  - La partición navegación/detalle introducida en V4.2-R8 (`*_navigation()`/`*_partitions()`) se reutiliza y
    generaliza como mecanismo (sección 5.1); su salida de texto puede cambiar por las razones anteriores.
- El fixture comprometible de V4.2-R7 (`tests/fixtures/v4_2_r7_full_sample/`) y sus pruebas de caracterización
  asociadas no requieren cambios por este contrato de diseño; cualquier prueba que dependa del texto exacto
  (no solo de la estructura/campos) de la documentación humana deberá revisarse en la ronda de implementación
  correspondiente (R3/R4), no en R1.

## 8. Criterio de aceptación de este contrato

> Un consumidor no debe necesitar abrir `FUNCTIONAL_FLOWS.json` completo para comprender un flujo.

Este contrato lo traduce en una condición verificable para rondas posteriores: dado un `flow_id`, el paquete
`ai_projection` (o `consumer_projection`) correspondiente a ese flujo, con presupuesto `MEDIUM` o inferior,
debe permitir reconstruir, sin abrir `ai_context/FUNCTIONAL_FLOWS.json`:

1. el punto de entrada y su forma web/evento/handler;
2. cada `PATH` del flujo, su tipo de terminal y su confianza (`confirmed`/`inferred`/`unresolved`);
3. el nombre/etiqueta resuelta del terminal (procedimiento almacenado, operación SQL o límite no resuelto),
   no solo su ID;
4. la referencia de evidencia (`evidence_refs`) que sustenta cada `PATH`.

Este criterio, junto con los cuatro casos reales de aceptación externa (A–D) ya registrados en el resultado de
R0, es el que R7 (aceptación interna) y el piloto real externo deberán validar contra una implementación
concreta — no contra este documento.

## 9. Fuera de alcance de esta ronda

- No se implementa hidratación real (`R2`).
- No se implementa la generación de documentación humana en español para evidencia de código (`R3`).
- No se implementa particionamiento/escalado (`R4`).
- No se implementa el presupuesto obligatorio de `ai_projection` ni la instrucción de sistema sin
  herramientas (`R5`).
- No se implementa `consumer_projection` como JSON real (`R6`).
- No se modifica ningún archivo bajo `legacy_documenter/`, `tools/` ni `PROJECT_STATE.json`.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).

## 10. Revisión humana obligatoria (pendiente) — Gate para R2

Pendiente de aprobación por el Líder Técnico antes de iniciar R2:

- [ ] este resultado R1 (`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`);
- [ ] la definición referencia vs. registro hidratado (sección 2) y su forma cerrada de ejemplo (2.1);
- [ ] el vocabulario `CONFIRMED`/`INTERPRETED`/`UNRESOLVED` (sección 3);
- [ ] el esquema de IDs/prefijos de paquete propuestos (sección 4: `AIP-`, `CPJ-`);
- [ ] las tres superficies y sus nombres/versiones de contrato propuestos (sección 5:
      `HUMAN_DOCUMENTATION_PROJECTION 1.0`, `AI_HYDRATED_PROJECTION 1.0`, `LegacyMapperConsumerProjection 1.0`);
- [ ] `AI_HYDRATED_PROJECTION 1.0` limitada a evidencia determinista hidratada, sin `INTERPRETED` por defecto,
      y sin mecanismo de interpretación recursiva (sección 5.2);
- [ ] el límite de presupuesto propio de `ai_projection` frente al límite, separado y obligatorio en R5, del
      payload final serializado del request (`system_instruction`/`user_instruction`/`schema`/envelope/
      records/statistics/truncation) y su salida `CONTEXT_TOO_LARGE` (sección 5.2);
- [ ] `source_index_pointer` como provenance/auditoría únicamente, con `ai_projection`/`consumer_projection`
      autocontenidas y sin poder suplir campos omitidos (sección 2.1);
- [ ] la compatibilidad estructural/de contratos con V4.2, no byte-identical para `human_documentation`
      (sección 7);
- [ ] el criterio de aceptación verificable (sección 8).
