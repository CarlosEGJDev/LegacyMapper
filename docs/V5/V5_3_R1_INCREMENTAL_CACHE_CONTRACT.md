# V5.3 R1 — Contrato y diseño del motor incremental y caché

Estado final: **V5_3_R1_CONTRACT_READY**

Ronda de contrato. No se modificó producción, tests, `PROJECT_STATE.json`, manifests, IDs ni Evidence Core. No se creó schema real en código, ni caché, ni incremental. Sin IA. Sin commit, tag ni push. Se ejecutaron **cuatro experimentos de solo lectura en el scratchpad** (fuera del repo) para sustentar decisiones; sus resultados están en §2 (M1–M5).

Fuentes leídas: R0, R0.1, V5.2 R4.3, V5.2 R4.4, V5.1 R4, roadmap V5, historia V5, lecciones aprendidas, reglas de trabajo, `PROJECT_STATE.json`, `AGENTS.md`, `CLAUDE.md`, más el código que este contrato toca (`context/hydration.py`, `documentation_v52/engine.py`, `evidence/persistence.py`, `utils/atomic_write.py`, `utils/sanitizer.py`, `cli/pipeline_stages.py`, `analysis/call_resolver.py`, extractores).

## 1. Objetivo

Convertir las mediciones de R0/R0.1 en decisiones cerrables para implementar V5.3: qué se cachea, con qué clave, cuándo se invalida, cuándo se cae a `full`, cómo se prueba la equivalencia con una corrida completa y en qué orden se implementa.

**Decisión central (DEC-00).** *La corrección se obtiene recomputando; el ahorro se obtiene memoizando y evitando escrituras idénticas.* Toda salida derivada se vuelve a calcular en memoria desde los índices de la corrida (determinista, barato una vez corregida la hidratación) y se compara por contenido contra lo ya escrito; solo se escribe lo distinto. Las únicas cachés persistidas que sustituyen cómputo son la de extracción por archivo y el estado de archivos. Esto elimina la clase de errores que más amenaza a una caché (dependencia no rastreada → salida obsoleta) para el 92 % del tiempo medido, y deja la invalidación fina solo donde ahorra poco y arriesga más (resolvers, proyecciones) **diferida detrás de una medición** (§6, §8).

## 2. Hechos empíricos usados

**De R0/R0.1** (los 15 hechos del prompt se respetan; se citan los que fundan decisiones): análisis puro SCAN→DEPENDENCY 75,9 s (4,3 %); `CALL_RESOLUTION` 1,1 s; `FLOW_RESOLUTION` 9,3 s; EXPORT 63,4 s (Evidence Core 33,8 s, `index/` 29,3 s); CONTEXT 580 s; DOCUMENTATION 1 035 s (v52 486,6 s); total 1 755 s; 2 × 12 642 hidrataciones = 1 099 s (62,6 %); varianza frío/caliente ×2–3; memoria pico 2,62 GB; `SourceArtifact.sha256`, `partition_sha256`, `documentation_v52/MANIFEST.json` reutilizables; un renombre de método cruza proyectos (3 medido); insertar una línea cambió 3 flows por IDs `CAL-` dependientes de la línea; CRLF/LF no altera la extracción, el BOM sí; IST = CRLF homogéneo (8 538 de 8 542 archivos de texto analizados).

**Medidos en R1** (scripts temporales en el scratchpad; producción intacta):

| ID | Medición | Resultado |
|---|---|---|
| M1 | Causa de la hidratación lenta. `EvidenceHydrator.hydrate_flow(flow_id, ix)` reconstruye **5 diccionarios** (flows, entry points, data_access, stored_procedures, sql_operations) y **recorre los 170 020 paths** filtrando por `flow_id` en **cada llamada**; `_parameters` además recorre los 74 633 `data_parameters`. Coste O(flows × entidades). | Real: 40,7 ms/flow (muestra de 100) → 515 s por pasada (coherente con 1 099 s para 2 pasadas). Prototipo en scratchpad (mismos algoritmos, índices por `flow_id`/id construidos **una vez**, 0,06 s): **7,0 ms/flow → 89,9 s por pasada** para los 12 642 flows. Salida **idéntica** (JSON canónico) en 400 flows muestreados de 12 642 (no es una verificación exhaustiva). El residuo de 7 ms es el barrido de `data_parameters` por flow (indexable por `caller`). La lógica de hidratación no es el cuello: lo es la indexación repetida. |
| M2 | `documentation_v52`: generación vs escritura. | Generar + renderizar los **46 567 documentos en memoria: 9,3 s**; hash SHA-256 de todos: 0,1 s. Los ~477 s restantes de los 486,6 s son **disco** (por archivo: `mkstemp` + `fsync` + `os.replace`, `mkdir`, barrido `rglob` de huérfanos, manifest). Microbenchmark en este disco (3 000 archivos de 1,3 KB): escritura atómica 5,83 ms/archivo (→ 271 s ×46 567) frente a escritura simple 2,02 ms/archivo (→ 94 s); el resto hasta 477 s (mkdir/barridos/antivirus) no se aisló. |
| M3 | Rutas de `documentation_v52` (MAX_PATH). | Ruta relativa más larga (con `documentation_v52/`): **165** caracteres; p99 133; p50 95; 0 archivos > 200. El temporal de escritura añade `len(nombre)+14` (`.{nombre}.{8 aleatorios}.tmp`). Presupuesto: raíz de `--output` ≤ 259 − 14 − 1 − 165 = **79 caracteres** para v52 (sin contar otros árboles). La corrida fallida de R0.1 tenía el `.tmp` en exactamente 260. |
| M4 | Sanitización sobre la extracción de IST (registros por archivo). | `symbols` 0/6 513, `web_events` 0, `data_access_indexes` 0, `webforms` 0, `projects` 0, `solutions` 0 cambian con `sanitize_data`; **`calls` 4 de 4 328** y **`configuration` 38 de 60** cambian; `sanitize_data` es idempotente en todos. Conclusión: persistir extracción **cruda** guardaría secretos en reposo (prohibido por `AGENTS.md`); persistirla **saneada** cambiaría 42 registros frente a una corrida full. |
| M5 | Pureza de los extractores. | `grep` de `glob/iterdir/listdir/exists/is_file/rglob` en los 8 extractores: **0 coincidencias**; cada uno lee solo su archivo (+ `root` para la ruta relativa). La extracción por archivo es una función pura de (bytes, ruta relativa, tipo). `scan` usa `rglob` una vez (1,0 s). |

**Proyección de tiempos (estimación de R1, no medición; R2 debe verificarla).** Con R2.1 (hidratación indexada y compartida): 1 755 − 1 099 + ≈ 90–180 ≈ **750–840 s** incluso en una corrida `full`. Con además evitar escrituras idénticas en una repetición sin cambios: v52 ≈ 10 s en vez de 487 s, más menos escritura de `index/`, evidencia y particiones → del orden de **300–400 s** (≈ −80 %). Los números de R2 se fijan midiendo, no con esta tabla.

## 3. Invariantes

| ID | Invariante |
|---|---|
| C-1 | **Equivalencia:** `mismo input + mismas versiones + misma configuración` ⇒ salida lógica idéntica a `full` (§12). |
| C-2 | La caché **nunca es fuente de verdad**: borrarla no cambia ningún resultado, solo el tiempo. |
| C-3 | **Fallback seguro:** sin evidencia suficiente para reutilizar una unidad ⇒ recomputar; jamás reutilizar caché dudosa. |
| C-4 | No cambian IDs, `provenance`, `confidence`, `unresolved`, contratos de Evidence Core V5.1, `index/`, `EVIDENCE_MANIFEST`, `RUN_SUMMARY` ni los manifests existentes. |
| C-5 | Sin IA en huellas, invalidación, selección de caché ni decisión full/incremental. |
| C-6 | Caché válida ⇔ existe `CACHE_MANIFEST.json` final válido (escrito último, validado por checksum). |
| C-7 | Sin secretos en reposo: lo persistido pasa por el sanitizador (§6.B, M4). |
| C-8 | No se mezclan salidas de repositorios distintos (identidad del repositorio en el manifest). |
| C-9 | El camino `full` sin caché existe siempre y es el comportamiento V5.2 (§19). |
| C-10 | Métricas no deterministas fuera de artefactos byte-estables (§13). |
| C-11 | Independencia de runtime: nada de esto lee docs, prompts, tests, `PROJECT_STATE.json`, gobernanza, IA ni Copilot (§17). |
| C-12 | Ningún objeto mutable de la caché se comparte con las etapas: los resolvers mutan en sitio (`call["resolved_target"] = …`); la caché se carga de disco en cada corrida y se persiste **antes** de resolver. |

## 4. Versionado

**Regla general.** Una versión solo entra en una **clave** si hay una caché persistida que sustituye el cómputo que esa versión gobierna. Con DEC-00 esa caché es únicamente la de extracción (+ estado de archivos); el resto de versiones se **registran** en el manifest como metadata/diagnóstico y pasan a ser **claves** solo si una fase posterior persiste esa proyección (§8.D/E).

| Componente | Definición | Ubicación | Incrementa cuando | ¿Clave hoy? |
|---|---|---|---|---|
| `ANALYZER_VERSION` | entero | constante única en un módulo de versiones del runtime (p. ej. `legacy_documenter/versions.py`) | todo cambio que pueda alterar la salida de extractores, normalización de namespaces/partial (`apply_project_namespaces`, `consolidate_partial_symbols`), `scanner`/clasificación, o `sanitizer` | **Sí** (extracción) |
| `ANALYZER_CODE_FINGERPRINT` | SHA-256 de los fuentes de los módulos que determinan la extracción (`extractors/`, `models/`, `scanner/`, `utils/sanitizer.py`, `config.py`, y las funciones de extracción/normalización de `pipeline_stages`) calculado en ejecución | runtime | automático | **Sí** (red de seguridad) |
| `EVIDENCE_SCHEMA_VERSION` | **reutiliza** `legacy_documenter.evidence.entities.EVIDENCE_SCHEMA_VERSION = "1.0"` (ya persistido en `EVIDENCE_MANIFEST.evidence_schema_version`). No se crea un segundo valor equivalente. | existente | contrato V5.1 | Metadata (y clave si en el futuro se cachea evidencia) |
| `RENDERER_VERSIONS` | **mapa por familia**, no un único entero | constantes por familia | cambio de salida de esa familia | Metadata (clave solo en cachés de proyección futuras) |
| `TEMPLATE_PROFILE_FINGERPRINT` | SHA-256 del contenido canónico de `documentation_v52/defaults/{templates,profiles,i18n,noise}/*` (+ custom dir si se usa) + idioma + perfiles activos | runtime | automático | Metadata |
| `CONFIG_FINGERPRINT` | SHA-256 del JSON canónico de la configuración efectiva (§4.2) | runtime | automático | **Sí** |
| Git commit / rama | informativo | manifest | — | **No** (solo metadata) |

**Por qué no el commit como versión única:** un commit que no toca el analizador invalidaría todo; un cambio sin commit no invalidaría nada; un árbol sucio no tiene identidad estable.

**Red de seguridad anti-olvido.** Además de `ANALYZER_VERSION` (declarada), el manifest guarda `ANALYZER_CODE_FINGERPRINT` calculado del código realmente instalado. Si difiere, la caché de extracción se descarta aunque nadie haya subido la versión; si los fuentes no son legibles (distribución solo `.pyc`), la caché de extracción queda **desactivada** (full). Un test de R2 falla si cambia el código de extracción sin cambiar `ANALYZER_VERSION` (el valor esperado vive en el test, no en runtime).

**Renderers: familias y justificación.** Se reutilizan las constantes ya existentes y se añaden solo las que faltan, para no duplicar:

| Familia | Fuente de versión | Estado |
|---|---|---|
| `legacy_markdown` (MarkdownExporter + renderers técnicos legados) | — | **crear** (no existe constante) |
| `human_documentation` | `MODEL_VERSION`/`SCHEMA_VERSION` de `human_flow_documentation.py` (V4.3-R3, 1.0) y `human_documentation_scaling.py` (V4.3-R4, 1.0) | existe |
| `consumer_projection` | `CONTRACT_VERSION`/`SCHEMA_VERSION` = 1.0 | existe |
| `ai_context` | `MODEL_VERSION` de `system_context_builder.py` (V2-R5), `ai_projection` 1.0 | existe |
| `hydration` | `MODEL_VERSION` de `hydration.py` (V4.3-R3) | existe |
| `documentation_v52` | `CONTRACT_VERSION = "1"` de `documentation_v52/config.py` + fingerprint de plantillas | existe |

Versión por familia (no una sola) porque las familias cambian de forma independiente y una versión única obligaría a invalidar las cinco cuando cambia una. Como esas constantes no se incrementan por mecanismo, R2 añade el mismo guardián por fingerprint de código que para el analizador antes de usarlas como claves.

### 4.2 `CONFIG_FINGERPRINT` — contenido mínimo

`DEFAULT_EXCLUDES` (de `config.py`) + `--exclude` (ordenado, normalizado) + `flow_max_depth` (hoy 12; existe en `analyze_repository`/`run_full_pipeline`) + idioma/perfiles/`custom_dir`/`strict_templates` de v52 + `allow_ai_interpretation` **excluido** (la IA no entra en la caché; es una etapa posterior opt-in que no se cachea) + cualquier opción futura que cambie análisis o proyección. Regla: toda opción nueva de CLI debe declarar si afecta al fingerprint (test de R2 que enumera el parser y falla si una opción no está clasificada).

## 5. Fingerprints

Dos conceptos separados que conviven:

| | Hash de integridad | Hash semántico de invalidación |
|---|---|---|
| Qué es | SHA-256 de bytes crudos (**el actual**, `SourceArtifact.sha256`) | SHA-256 de los bytes tras normalizar saltos de línea |
| Para qué | integridad, trazabilidad, compatibilidad; **siempre** reflejado en `evidence/source_artifacts.json` | **clave de la caché de extracción** y detección de "cambio real" |
| Cuándo **no** se usa | — | nunca como integridad; nunca para archivos binarios/no analizados; nunca sustituye al crudo en evidencia |
| Normalización | ninguna | solo `\r\n` → `\n` y `\r` suelto → `\n`; **BOM preservado**; **espacios preservados** (M: el BOM cambió la extracción; los espacios finales no, pero ocultarlos no aporta y el riesgo es asimétrico) |
| Tipos | todos los escaneados (15 138) | solo tipos de texto **analizados**: los `file_type` que tienen extractor (`solution`, `vb_project`, `vb_source`, `aspx`, `ascx`, `master`, `web_config`). Resto: solo crudo |

- **Una sola lectura** por archivo produce ambos hashes (y entrega los bytes a la extracción si hay *miss*): hoy el repo se lee dos veces (extracción y `hashlib.file_digest` del Evidence Core) y los `.vb` tres.
- `SourceArtifact.sha256` **no se modifica** en V5.3; se sigue calculando con los bytes actuales en cada corrida (un cambio solo de line endings cambia `source_artifacts` pero **no** dispara re-extracción).
- Hash de archivo **no** basado en mtime por defecto. `(tamaño, mtime_ns)` solo se usa como prefiltro en el modo opt-in `--trust-mtime`, nunca por defecto (un checkout puede conservar mtime; fallo silencioso inaceptable, C-3).
- **Huella de una unidad de extracción** = `(ruta relativa normalizada, hash semántico, file_type, ANALYZER_VERSION, ANALYZER_CODE_FINGERPRINT, CONFIG_FINGERPRINT parcial de extracción)`. La ruta entra en la clave porque la salida contiene `file`/`project` y los IDs derivan de la ruta.

## 6. Arquitectura de caché

```text
<cache_dir>/                       (por defecto  <output>/_cache_v53/ ; --cache-dir lo cambia)
  CACHE_MANIFEST.json              (escrito ÚLTIMO; válido ⇔ presente + checksums OK)
  file_state.json                  (capa A: un solo archivo, ~15 k registros ordenados por ruta)
  extraction/ex-000.json … ex-255.json   (capa B: 256 shards por hash de ruta; nunca un archivo por fuente)
  artifacts.json                   (capa E: huellas de salidas derivadas pequeñas; ver E)
  RUN_METRICS.json                 (§13; no determinista; fuera de los checksums del manifest)
```

Rutas cortas y numéricas a propósito (MAX_PATH, §14). La carpeta vive dentro de `--output` por defecto para no mezclar repositorios (C-8) pero el manifiesto de salida opt-in de V4.3 (`build_output_manifest`, recorre `rglob` completo) **debe excluirla** (cambio de R2 declarado en §21 plan).

### A. File State

Por archivo (uno por registro de `file_state.json`): `path` (relativa, normalizada a `/`), `size`, `sha256_raw`, `sha256_semantic` (solo tipos analizados, si no `null`), `file_type`, `project_path` (del mapeo vbproj→compile_items si existe), `mtime_ns` (metadata, solo para `--trust-mtime`), `status` ∈ {`unchanged`, `modified`, `added`, `deleted`, `renamed_candidate`}.

- `status` **se calcula** en cada corrida comparando el escaneo actual con el `file_state.json` válido anterior; no se persiste como verdad.
- **Rename:** la identidad es la ruta (el `SRC-` id es hash de la ruta) ⇒ un renombre = `deleted` + `added`. No se reutiliza extracción entre rutas distintas (las salidas contienen `file`). Si el hash semántico coincide con un `deleted`, se registra `renamed_candidate` **solo como métrica**.
- Registros de archivos **excluidos** (`DEFAULT_EXCLUDES`, `--exclude`) no entran al estado; un cambio de excludes cambia `CONFIG_FINGERPRINT` ⇒ full.

### B. Extraction Cache

Unidad: **archivo**. Se cachea la salida cruda del extractor de ese archivo **antes** de la normalización global y antes de los resolvers:

| Tipo de archivo | Registros persistidos |
|---|---|
| `vb_source` | `symbols` del archivo + `calls` (CallExtractor) + `web_events` + `data_access_indexes` |
| `aspx`/`ascx`/`master` | `webform` |
| `vb_project` | `project` (incl. `compile_items`, `root_namespace`) |
| `solution` | `solution` |
| `web_config` | `configuration` |
| todos | `errors` de extracción de ese archivo (un error de extracción **también se cachea**, pero ver bypass) |

Reglas:

1. **Sin secretos en reposo (C-7, M4):** se persiste `sanitize_data(registro)`. Como 42 registros de IST (calls 4, configuration 38) cambian al sanear y eso alteraría la entrada de los resolvers, **todo archivo cuyo registro cambie al sanear queda marcado `cache_bypass` y se re-extrae en cada corrida** (≈ 0,3 % de los archivos: coste despreciable, equivalencia exacta). La comparación `sanitize_data(x) != x` decide el bypass; el test de R2 lo verifica.
2. **Persistir inmediatamente tras extraer**, antes de `apply_project_namespaces`/resolvers que mutan en sitio (C-12).
3. **Normalización global no se cachea:** `apply_project_namespaces` y `consolidate_partial_symbols` (cruzan proyecto↔símbolo y partial classes multi-archivo) **se ejecutan siempre** sobre todos los registros cargados. Por tanto un cambio en un `.vbproj` (RootNamespace, compile items) o en una parte `Partial` **no requiere invalidar la extracción de otros archivos**: basta re-extraer el `.vbproj` (la extracción por archivo no lee otros archivos, M5) y recomputar la normalización.
4. **Clave y validación:** huella de unidad (§5); un shard es válido si su checksum coincide con el manifest; un registro dentro del shard es válido si su huella coincide con la del archivo actual. Shard dañado ⇒ se descartan sus registros (no toda la caché) y se cuenta como *miss*; más de un shard dañado o manifest inválido ⇒ full (§11).
5. **Escritura:** se reescriben solo los shards con cambios (una modificación = 1 shard de ~1/256 del total).
6. **Gate de inclusión en R2:** la extracción cuesta 61,5 s (3,5 %, caliente) a 129,8 s (frío). Leer+parsear el equivalente persistido se estima en segundos (R0: parseo JSON ~7 s por GB). R2 implementa la capa B **solo si** la medición en IST muestra que cargar shards + validar es más rápido que extraer; si no, queda diferida. El File State (A) se implementa igualmente: es la base de métricas y del estado `changed`.

### C. Resolver State — decisión

**No hay estado persistido de resolvers. `CALL_RESOLUTION`, `WEB_ENTRY_RESOLUTION`, `DATABASE_RESOLUTION`, `FLOW_RESOLUTION` y `DEPENDENCY_RESOLUTION` se recalculan siempre** a partir de la extracción (cacheada o no).

Base (R0.1): `CALL_RESOLUTION` 1,1 s y `FLOW_RESOLUTION` 9,3 s (juntos ≈ 14 s, < 1 % del total); `CallResolver` es global (depende de todo el conjunto de clases/miembros; un renombre cruzó 3 proyectos y una clase duplicada cambió la resolución de 13 llamadas en 8 archivos). Invalidar parcialmente ahorraría a lo sumo ~14 s y exigiría índices inversos y una prueba de cierre transitivo con riesgo de resultados obsoletos. **Invalidación parcial de resolvers: FUTURE_PHASE**, solo si tras R2 los resolvers pasan a dominar (p. ej. repositorios ≫ IST). El criterio seguro medido en R0.1 (clave del resolver por archivo) queda documentado como punto de partida para esa fase, no como requisito de R2.

### D. Hydrated Flow Cache — **prioridad alta** (decisión en dos niveles)

**Nivel 1 — obligatorio en R2.1, no persistido: `HydrationView` compartida por corrida.**

- **Unidad:** un flow (`flow_id`).
- **Qué cambia:** los lookups (`flow_id → flow`, `id → entry_point`, `id → data_access/stored_procedure/sql_operation`, `flow_id → [paths]`, `caller → nombres de parámetro`) se construyen **una vez por corrida** a partir de `indexes`; `hydrate_flow` los consulta en O(1). Memoización por `flow_id` dentro de la corrida.
- **Quién la comparte:** `consumer_projection`, `HUMAN_DOCUMENTATION`/`flujos_humanos`, `ai_context`/`ai_projection` (los dos últimos la usan hoy o pueden usarla) y cualquier consumidor futuro reciben el mismo objeto; un flow se hidrata **a lo sumo una vez por corrida**, no dos (M1: 25 284 llamadas = 2 × 12 642 hoy).
- **Clave / dependencias / invalidación:** vive solo en memoria y se reconstruye en cada corrida ⇒ no hay invalidación que razonar. Su salida debe ser **idéntica** a la de `hydrate_flow` actual (registro completo incluido `model_version` y `provenance`); `EvidenceHydrator.MODEL_VERSION` no cambia porque el contrato de salida no cambia.
- **Beneficio medido (M1):** 1 099 s → ≈ 90 s por pasada (prototipo) y 90 s en total si se hidrata una sola vez; `_parameters` indexado por `caller` reduce aún más. Es el cambio de mayor retorno de V5.3 y beneficia también a las corridas `full`.
- **Por qué no es "caché" en disco:** el coste era de indexación repetida, no de la hidratación; corregirlo elimina el problema sin ningún riesgo de obsolescencia.

**Nivel 2 — caché persistida de flows hidratados: DIFERIDA con gate.** Se implementa solo si, **después de R2.1**, R2 mide que *leer y validar* los registros hidratados persistidos es **más rápido que recomputarlos** (criterio comparativo, sin porcentaje arbitrario). Clave hipotética (documentada para esa fase): hash de (flow, sus paths, su entry point, las entradas `data_access/SP/sql` referenciadas, los `data_parameters` de sus callers, `hydration.MODEL_VERSION`). Requiere el índice inverso `archivo → flows` (§8), hoy inexistente.

### E. Projection Cache — decisión: **derivar y comparar** (write-skip por contenido)

Para `documentation_v52`, `HUMAN_DOCUMENTATION`, `consumer_projection`, `ai_context`, `index/`, `evidence/` y la documentación legada:

1. La proyección **se vuelve a generar en memoria siempre** (M2: v52 completo = 9,3 s).
2. Antes de escribir cada archivo se compara su SHA-256 con el registrado en el manifest previo; **si coincide, no se escribe** (tampoco `fsync`/`replace`/`mkdir`); si difiere o no existe, se escribe con el mecanismo atómico actual. Los huérfanos se eliminan con los mecanismos existentes (`sync_generated_*`, `_write_tree`).
3. **Sin abrir 46 567 archivos para decidir:** la decisión usa **un solo manifest leído** (`documentation_v52/MANIFEST.json`, 10 MB, ya contiene `path/size/sha256` por documento) + una verificación barata del disco:
   - verificación por defecto `fast`: el archivo existe y su `size` y `mtime_ns` coinciden con lo registrado por la propia caché cuando lo escribió (capta ediciones en sitio sin releer contenido);
   - `--verify-cache=hash`: releer y hashear (estricto; coste ≈ lectura de 46 k archivos, R0: 272 s en frío);
   - R2 **debe medir** el coste de la verificación `fast` sobre 46 k archivos antes de declarar el umbral de aceptación.
4. Mismo patrón para el resto: `index/*.json` (22 archivos, 996 MB: el ahorro es la escritura de 1 GB idéntico), particiones de evidencia (`partition_sha256` del `EVIDENCE_MANIFEST` ya existe), `consumer_projection/parts`, `flujos_humanos`, `ai_context`. Las salidas que no tienen manifest propio se registran en `artifacts.json` (path, size, sha256, mtime_ns; ≈ 1,2 k entradas).
5. **Equivalencia por construcción:** el contenido escrito es siempre el que produciría `full`; lo único que cambia es qué bytes se vuelven a escribir.

Consecuencia: los `RENDERER_VERSIONS` y el fingerprint de plantillas **no son claves** en R2 (la comparación por contenido es exacta); se registran para diagnóstico y para la futura caché persistida de proyecciones.

**Política de `fsync` (candidato R2.2, con gate):** M2 mostró 5,83 ms/archivo con `mkstemp+fsync+replace` frente a 2,02 ms con escritura simple. Para el árbol derivado `documentation_v52` (re-derivable, protegido por manifest final + checksum) R2 puede evaluar escribir sin `fsync` por archivo y validar al final. **No** se cambia el mecanismo de `RUN_SUMMARY`, `index/` ni `evidence/` (contrato V4.2-R6/V5.1). Se adopta solo si la medición lo justifica y el test de interrupción (§22) lo respalda.

## 7. Persisted Cache Manifest

`CACHE_MANIFEST.json` (JSON canónico, claves ordenadas). Contenido contractual (esquema de ejemplo; **no** es código):

```json
{
  "contract": "LegacyMapperCacheManifest",
  "cache_schema_version": "1",
  "state": "COMPLETE",
  "versions": {
    "analyzer_version": 1,
    "analyzer_code_fingerprint": "<sha256>",
    "evidence_schema_version": "1.0",
    "renderer_versions": {"human_documentation": "...", "consumer_projection": "1.0", "ai_context": "...", "documentation_v52": "1", "legacy_markdown": "..."},
    "template_profile_fingerprint": "<sha256>"
  },
  "config_fingerprint": "<sha256>",
  "config": {"excludes": ["..."], "flow_max_depth": 12, "v52_profiles": ["..."], "language": "es"},
  "repository_identity": {"root_normalized": "<ruta absoluta normalizada>", "root_fingerprint": "<sha256 de root_normalized>"},
  "informative": {"git_head": "<opcional>", "git_branch": "<opcional>", "generated_at": "<ISO-8601>"},
  "file_state": {"path": "file_state.json", "sha256": "<sha256>", "file_count": 15138},
  "extraction_shards": {"count": 256, "sha256": {"ex-000.json": "<sha256>", "...": "..."}},
  "artifacts": {"path": "artifacts.json", "sha256": "<sha256>"},
  "validity": {"complete": true}
}
```

- **Timestamps y `informative` no deterministas**: nunca forman parte de ningún checksum ni de ninguna clave.
- `repository_identity`: ruta absoluta normalizada (minúsculas en Windows, `/`); **no** se compara con el HEAD de Git (un checkout de otra rama en la misma ruta es el mismo repositorio; lo detecta el File State). Si `root_fingerprint` no coincide ⇒ full y la caché se reescribe (C-8).
- **Patrón seguro de escritura:** (1) borrar el `CACHE_MANIFEST.json` previo; (2) escribir `file_state.json`, shards y `artifacts.json` con escritura atómica; (3) **validar** releyendo checksums; (4) escribir `CACHE_MANIFEST.json` al final, atómico. Sin manifest (o con `state != COMPLETE`, o checksum inválido) ⇒ **la caché no existe** y se hace full (C-6). Es el mismo patrón que `EVIDENCE_MANIFEST` (se borra antes, se escribe al final).
- **Compatibilidad:** el manifest de caché es nuevo y vive aparte; no modifica `EVIDENCE_MANIFEST`, `documentation_v52/MANIFEST.json` ni `OUTPUT_MANIFEST`.

## 8. Índices inversos

Con DEC-00, los resolvers y las proyecciones se recomputan siempre ⇒ **ningún índice inverso es necesario para la corrección**. Solo serían necesarios para recomputar proyecciones *selectivamente* (fase posterior).

| Índice | Consulta que responde | Decisión |
|---|---|---|
| archivo → proyecto | ¿a qué proyecto pertenece un archivo? | **Obligatorio en R2** (campo `project_path` de File State; derivable de `compile_items`) — alimenta métricas y scope `project` |
| archivo → símbolos | ¿qué símbolos declara un archivo? | **Obligatorio en R2** como parte natural de los shards de extracción (clave = archivo) |
| símbolo/nombre → llamadas candidatas | llamadas cuyo `method_name`/receptor coincide con un nombre | **Pospuesto** (solo para invalidación parcial de resolvers, §6.C) |
| símbolo → llamadas entrantes | quién llama a X | **Pospuesto** |
| archivo → flows afectados | flows que dependen de un archivo | **Pospuesto** a la caché persistida nivel 2 (§6.D). **No** derivar de "flow toca archivo" por prefijos de nodos: R0.1 demostró que esa heurística no es fiable (subestimó 1, 2 y 5b; sobreestimó el caso 4) |
| proyecto → proyectos dependientes | cierre de dependientes | **Pospuesto** (scope `project` extendido) |
| flow → documentos/proyecciones | qué salidas genera un flow | **Pospuesto** (proyección selectiva); hoy el write-skip no lo necesita |
| evidencia → documentos | qué documentos nacen de qué evidencia | **Pospuesto**; v52 no registra origen por documento |

Cuando se implementen, deberán derivarse **solo de datos deterministas** ya calculados (símbolos, llamadas resueltas, paths) y validarse contra una corrida full antes de fiarse de ellos (R0.1 §7).

## 9. Matriz de invalidación

Convenciones: **EXT** = caché de extracción; **RES** = resolvers (siempre recomputados); **PROY** = proyecciones (siempre regeneradas en memoria, write-skip por contenido); **FULL** = descartar la caché y recomputar todo (la caché se reescribe). "Recomputa" indica lo que cambia de verdad; la regeneración en memoria de PROY ocurre siempre.

| Caso | Mínimo alcance seguro | Reutiliza | Recomputa | ¿Fuerza full? |
|---|---|---|---|---|
| Solo cuerpo (sin tocar nombres/llamadas/líneas siguientes) | el archivo | EXT del resto; escritura de salidas idénticas | EXT del archivo; RES; PROY (write-skip) | no |
| Cambio de línea (insertar/borrar líneas) | el archivo | EXT del resto | EXT del archivo; los IDs `CAL-` de **todas** las llamadas posteriores de ese archivo cambian (R0.1 caso 1: 3 flows) — sale natural de re-extraer y recomputar | no |
| Cambio de firma sin cambiar nombre | el archivo | EXT del resto | EXT del archivo (la salida puede resultar idéntica: R0.1 2b no cambió ningún índice); el hash semántico sí cambia ⇒ se re-extrae | no |
| Cambio de nombre de método/miembro | el archivo | EXT del resto | EXT del archivo; RES completo (afecta llamadas de otros archivos y proyectos: 8 archivos / 3 proyectos medido) | no (RES es global y siempre se recomputa) |
| Símbolo (clase) nuevo | archivo nuevo | EXT del resto | EXT del nuevo; RES completo (puede crear ambigüedad: 13 llamadas en R0.1 5b) | no |
| Símbolo eliminado | archivo con el símbolo | EXT del resto | EXT de ese archivo; RES | no |
| Cambio de namespace / `RootNamespace` | el `.vbproj` | EXT de todo lo demás | EXT del `.vbproj`; `apply_project_namespaces` siempre; RES | no |
| Clase `Partial` (cualquier parte) | el archivo cambiado | EXT del resto | EXT del archivo; `consolidate_partial_symbols` siempre | no |
| `.aspx` / `.ascx` | el archivo | EXT del resto | EXT del webform; RES (entry points/flows) | no (R0.1: texto sin efecto, `Inherits` cambió `webforms`/`dependencies`) |
| `.vbproj` | el `.vbproj` | EXT de los `.vb` | EXT del proyecto; normalización y RES | no |
| `.sln` | el `.sln` | EXT del resto | EXT de la solución; `dependencies` | no |
| `web.config` / configuración | el archivo | EXT del resto | EXT de configuración (`cache_bypass` si contiene secretos); `external_dependencies`/`data_access` asociados | no |
| Archivo nuevo | el archivo | EXT del resto | EXT del nuevo; RES | no |
| Archivo eliminado | su registro | EXT del resto | retirar EXT; RES; huérfanos de salida (sync) | no |
| Rename de archivo | `deleted` + `added` | EXT del resto | re-extraer en la nueva ruta; retirar la antigua | no |
| Cambio de template | ninguno de EXT | EXT completa | PROY de v52 (comparación por contenido) | no |
| Cambio de profile | ninguno de EXT | EXT completa | PROY de v52 | no |
| Cambio de idioma | ninguno de EXT | EXT completa | PROY de v52 | no |
| Cambio de configuración de análisis (`--exclude`, `flow_max_depth`, `DEFAULT_EXCLUDES`) | todo el repositorio | nada de EXT si afecta al escaneo/extracción; si solo afecta a resolvers (`flow_max_depth`) EXT completa | según el caso | **Sí** si cambia `excludes` (alcance de archivos); `flow_max_depth` solo RES |
| Cambio de `ANALYZER_VERSION` o de su fingerprint de código | todo | nada de EXT | todo | **Sí** |
| Cambio de `EVIDENCE_SCHEMA_VERSION` | todo | nada | todo | **Sí** |
| Cambio de `RENDERER_VERSION` | la familia | EXT completa | PROY de esa familia | no (en R2 la comparación por contenido ya lo cubre) |
| Cambio de branch (muchos archivos a la vez) | los archivos que difieren | EXT de los iguales | EXT de los distintos; RES; PROY | no por correctitud; umbral de coste configurable (§11) |
| Caché corrupta (manifest inválido, >1 shard dañado) | todo | nada | todo | **Sí** |
| Caché incompleta / interrumpida (sin manifest final) | todo | nada | todo | **Sí** |
| `repository_identity` distinta | todo | nada | todo | **Sí** |
| Edición en sitio de una salida derivada (size/mtime distinto) | esa salida | resto | reescribir esa salida | no |

## 10. Scopes

| Scope | Semántica contractual | Orden | Fase |
|---|---|---|---|
| `repository` | comportamiento actual + (si hay caché) el mecanismo de este contrato; salida completa | 1 | R2 |
| `changed` | **no es una salida parcial**: es el modo incremental que produce la salida **completa** del repositorio aprovechando la caché (File State + extracción + write-skip). Su resultado es equivalente a `repository`/`full` (§12). Informa qué archivos cambiaron (estado de File State) | 2 | R2 |
| `project` | proyección **filtrada** a las unidades de un proyecto **calculada sobre el análisis global** (la resolución es global, no local). Equivalencia definida como *restricción* de la salida full. Un renombre cruza proyectos ⇒ el cierre no se infiere; no se recortan resolvers | 3 | posterior (R3+/V5.3 tardío) |
| `component` | igual que `project`, unidad = componente; los flows cruzan componentes | 4 | posterior |
| `folder` | **no es unidad segura**: una carpeta cruza proyectos y viceversa. Solo listado/filtrado de salida, nunca base de invalidación ni de cómputo parcial | 5 | posterior (último) |

Orden recomendado por el prompt confirmado. Justificación de `changed` antes de `project`: es la única que aprovecha lo ya persistido (R0 §8) y no introduce un segundo significado de "salida parcial". `project/component/folder` solo filtran salidas; ninguno permite saltarse RES global.

## 11. Full vs incremental

**Full obligatorio** (la caché se descarta y se reescribe): falta de `CACHE_MANIFEST.json` válido o `state != COMPLETE`; `cache_schema_version` desconocida; `ANALYZER_VERSION` o `ANALYZER_CODE_FINGERPRINT` distinto; `EVIDENCE_SCHEMA_VERSION` distinto; `CONFIG_FINGERPRINT` distinto por `excludes`/alcance; `repository_identity` distinta; checksum de `file_state.json` inválido; más de un shard de extracción dañado; interrupción detectada; fuentes del analizador ilegibles; `--cache-mode refresh|off`.

**Incremental (por defecto si hay caché válida):** cualquier conjunto de archivos cambiados. La **correctitud no depende del porcentaje de cambio**: si cambian todos los archivos, la extracción se recomputa entera y el resultado sigue siendo equivalente a full.

**Umbral de coste (configurable, sin valor por defecto inventado).** El prompt prohíbe fijar porcentajes sin evidencia y R0/R0.1 no midieron el punto de equilibrio. Contrato: existe el parámetro `--incremental-max-changed-ratio` **sin valor por defecto (desactivado)**; R2 debe **medir** (p. ej. variando la fracción de archivos modificados sobre la copia de IST, como en R0.1 §7) el punto en que leer y validar la caché cuesta más que re-extraer, y fijar entonces el valor por defecto con esa evidencia. Mientras tanto, un cambio masivo (cambio de branch) no rompe nada: solo puede ser menos eficiente que full.

**Decisión de modo**, 100 % determinista: se evalúan en orden las condiciones de full; si ninguna, incremental. La razón se registra en métricas (`fallback_reason`).

## 12. Equivalencia incremental vs full

**Contrato:** para `mismo input + mismas versiones (analyzer, evidence schema, renderers) + misma configuración + mismas plantillas/perfiles/idioma`, la salida de una corrida incremental es **lógicamente idéntica** a la de una corrida `full` sobre ese mismo estado.

"Idéntica" significa, verificable por máquina:

1. **IDs**: mismo conjunto de IDs de evidencia, flows, paths, calls, componentes y documentos.
2. **Relaciones**: mismas aristas/dependencias (`functional_dependencies`, `dependencies`, paths), mismo orden canónico.
3. **Estados**: mismos `confirmed/inferred/unresolved`; `flow_unresolved` y `unresolved_boundaries` idénticos (un archivo nuevo puede resolver un unresolved previo; debe ocurrir igual que en full).
4. **Particiones lógicas**: mismas particiones (incluidas las que quedan vacías y las huérfanas eliminadas).
5. **Documentación**: `documentation_v52` y `flujos_humanos`: mismo contenido y mismo SHA-256 por documento; mismo `MANIFEST.json`.
6. **Manifests lógicos**: `EVIDENCE_MANIFEST.json`, `documentation_v52/MANIFEST.json`, `CONSUMER_PROJECTION.json` idénticos; `index/` idéntico **salvo** `repository.duration_seconds` (ya excluido desde V5.0, D-01).
7. **Bytes**: en R2 la verificación es **byte a byte** de todo `--output` excepto el conjunto declarado de campos/archivos no deterministas: `index/repository.json.duration_seconds`, `RUN_METRICS.json`, `CACHE_MANIFEST.json.informative`, la propia carpeta `_cache_v53/`.

Con DEC-00 la equivalencia es casi trivial para proyecciones (siempre regeneradas). El riesgo real de divergencia se concentra en la **caché de extracción**: por eso C-7/M4 (bypass de registros sensibles), C-12 (no compartir mutables) y la prueba de equivalencia sobre IST (§22) son obligatorias. No se implementó ninguna comparación en R1.

## 13. Métricas

Persistidas en `<cache_dir>/RUN_METRICS.json` (no determinista; **fuera** de `RUN_SUMMARY.json`, cuyo test de igualdad exacta (V5.0 R2 D-12) no se toca, y fuera de `index/`, `evidence/`, `documentation_v52/`). Una corrida sobrescribe el archivo; R2 puede conservar las últimas N en un arreglo.

| Campo | Notas |
|---|---|
| `mode` | `full` / `incremental` / `off` / `refresh` |
| `fallback_reason` | código de §11 o `null` |
| `stage_seconds` | por stage y sub-stage (mismo desglose medido en R0.1: SCAN, EXTRACTION, CALL, WEB_ENTRY, DATABASE, FLOW, DEPENDENCY, EXPORT{json, markdown, evidence_core}, CONTEXT{project_contexts, ai_context, consumer_projection}, DOCUMENTATION{legacy, human, v52}, FINAL_SUMMARY) |
| `total_seconds` | |
| `cache_hits` / `cache_misses` | por capa (file_state, extraction) |
| `files_reused` / `files_recomputed` / `files_added` / `files_deleted` / `renamed_candidates` | |
| `flows_hydrated` / `flows_reused` | `flows_hydrated` debe ser 12 642, **no 25 284** tras R2.1 |
| `documents_reused` / `documents_regenerated` / `documents_skipped_write` | write-skip |
| `bytes_read` / `bytes_written` | contadores del proceso |
| `peak_memory_bytes` | Windows: `PeakWorkingSetSize` vía `ctypes` (sin `psutil`, que no está instalado); otras plataformas: `resource` si existe; `null` si no hay forma estándar |
| `versions` | las del manifest |
| `cache_verification` | `fast` / `hash` |

Instrumentación mediante un envoltorio de stages en el orquestador (el mismo enfoque del arnés temporal de R0.1, ahora permanente y de bajo coste); `perf_counter`. No se añaden métricas a `RUN_SUMMARY` ni a manifests byte-estables.

## 14. MAX_PATH (Windows)

**Decisión (combinación): validar antes de escribir + extended-length opt-in. No se mapean nombres a hash.**

1. **Preflight obligatorio** (R2.2): antes de que cada stage escriba, se calcula en memoria el conjunto de rutas destino (v52 conoce todas las claves de `all_files` antes de `_write_tree`; el resto, por sus escritores) y se comprueba `len(ruta_absoluta_final) + 14 (temporal) ≤ 259` en Windows (límite MAX_PATH de 260 incluyendo el terminador; M3: el `.tmp` fallido medía exactamente 260). Si alguna lo supera y las rutas largas no están habilitadas, se aborta **antes de escribir nada del stage** con un error accionable: código `OUTPUT_PATH_TOO_LONG`, la ruta más larga, su longitud, el límite y el **`--output` máximo sugerido** (`259 − 14 − 1 − longitud_relativa_máxima`; para v52 en IST: raíz ≤ 79 caracteres). Nunca un `FileNotFoundError` del `.tmp`.
2. **`--long-paths`** (opt-in): escribe/lee con el prefijo extendido `\\?\` dentro de LegacyMapper. Los nombres y las rutas relativas de manifests/enlaces **no cambian**, así que no se pierde trazabilidad. Advertencia: otras herramientas (Explorador, antivirus, editores) pueden no abrir esas rutas.
3. **Por qué no hash de nombres:** cambiaría el contrato v52 (`MANIFEST.json`, enlaces de navegación, slugs legibles) y rompería la trazabilidad que V5.2 garantiza; las rutas reales de IST (máx. 165) caben con una raíz razonable. Se descarta para V5.3; puede reconsiderarse si un repositorio futuro supera el límite incluso con raíz corta.
4. **Compatibilidad con la caché:** `_cache_v53/` usa nombres cortos numéricos; el preflight también cubre sus rutas. La misma función de preflight sirve a cualquier árbol (`index/`, `evidence/`, `consumer_projection/`).
5. Soporte de rutas largas del SO (registro/manifest de Windows): se **detecta** (no se modifica configuración del SO, `AGENTS.md`); si está habilitado, el preflight no aborta.

## 15. IDs dependientes de línea

**Opción A (por defecto y vigente): se mantiene el contrato actual de IDs.** `CAL-…` incluye la línea y la expresión (`evidence/builder.py`); por tanto insertar/borrar líneas cambia los IDs de las llamadas posteriores del mismo archivo y, vía evidencia, los flows que las atraviesan (R0.1 caso 1: 24 llamadas, 3 flows, 3 entry points).

Diseño alrededor de ese hecho: la invalidación se hace **por archivo completo** (cualquier cambio del hash semántico re-extrae el archivo entero) y todo lo demás se recomputa/compara; no existe "invalidación por símbolo" que pudiera dejar IDs viejos. **No se cambia ningún ID en V5.3.** Una opción B (IDs estables ante desplazamiento de línea, p. ej. ordinal dentro del método) queda registrada como propuesta para una fase futura que exigiría autorización explícita, migración de Evidence Core y regeneración de manifests (D-14, FUTURE_PHASE).

## 16. Persistencia

| Criterio | JSON actual (compacto) | JSONL | SQLite | 
|---|---|---|---|
| Lectura parcial | no (lista completa) | sí (por línea/bloque) | sí |
| Escritura atómica | `atomic_write_text` existente | requiere rotación/append controlado | transacciones propias |
| Lookup por clave | no (R0: sin índice) | no sin índice | sí |
| Tamaño | ya medido (≈ 2,63 GiB de salidas; evidencia 1 GB) | similar | suele ser menor/mayor según esquema |
| Compatibilidad | total con `index/`, `evidence/`, manifests | nueva | nueva dependencia y binario opaco |
| Complejidad | mínima | media | alta (esquema, migraciones, concurrencia) |
| Recuperación ante corrupción | descartar el shard | descartar el bloque | reparación/WAL |
| Inspección humana | trivial | trivial | requiere herramienta |

**Decisión: JSON (mismo estilo determinista) + sharding + un manifest final es suficiente para R2.** El cuello medido es el *número de archivos*, no los bytes (R0: 46 568 archivos = 272 s de lectura; 1 GB en 22 archivos = 1,2 s), y la caché usa 256 shards + 3 archivos. M1/M2 mostraron además que los costes dominantes no eran de formato. **No se introduce JSONL ni SQLite.** D-11 (JSON vs JSONL de `evidence/persistence.py`) se reevalúa solo si R2 mide que cargar shards es el cuello; queda FUTURE_PHASE. SQLite solo si una fase futura necesita lookups inversos por clave a escala que JSON no cubra, con medición previa.

## 17. Runtime independence

El motor incremental/caché solo depende del paquete `legacy_documenter` y de la biblioteca estándar. **No** lee `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`, archivos de gobernanza, IA ni Copilot. Las constantes de versión viven en el runtime; los valores de control (qué versión "debería" tener el código) viven en tests, no en runtime. El cálculo del fingerprint de código lee los fuentes **del propio paquete**, no del repositorio de desarrollo. Un test de R2 verifica por import/`grep` que los módulos nuevos no importan ni abren esas rutas (mismo estilo que los tests de independencia de IA existentes).

## 18. Migración

| Situación | Comportamiento |
|---|---|
| No existe caché | **full**; al terminar correctamente crea `_cache_v53/` (manifest al final). Mismos bytes de salida que V5.2. |
| Caché V5.3 válida | incremental (§11). |
| Existe salida V5.2 en `--output` pero no caché V5.3 | **full** y se crea la caché. Las salidas V5.2 existentes se **sobrescriben con el mecanismo normal** (el write-skip solo se aplica si hay manifest de huellas válido; sin él se escribe todo). No se asume que lo que hay en disco es válido. |
| `cache_schema_version` distinta | full + caché reescrita (no hay migración de caché: es descartable, C-2). |
| `ANALYZER_VERSION`/fingerprint distinto | full (§11). |
| Caché dañada | shard dañado ⇒ miss de sus archivos; más de uno / manifest inválido ⇒ full; nunca error fatal por caché. |
| Corrida interrumpida | no hay manifest final válido (se borró al empezar) ⇒ la siguiente corrida es full; los temporales `.tmp` huérfanos se barren al inicio (§20). |

La primera ejecución sin caché es full y deja estado reutilizable. Un fallo al **escribir** la caché no debe convertir una corrida válida en fallida: se registra advertencia en métricas y la salida principal es válida (C-2).

## 19. Rollback

- `--cache-mode off`: no lee ni escribe caché, no aplica write-skip; ejecuta **exactamente el camino V5.2** (mismas funciones, mismo orden, mismas escrituras).
- `--cache-mode refresh`: ignora la caché existente, hace full y la reescribe.
- `--cache-mode auto` (por defecto en R2 una vez validado; hasta R4 el valor por defecto puede ser `off`, decisión de cierre).
- Borrar `_cache_v53/` (o `--cache-dir` a una ruta nueva) equivale a `refresh` sin riesgo (C-2).
- El camino `full` nunca se elimina. R2.1 (hidratación indexada) no es un modo: es una corrección de rendimiento con salida idéntica, por lo que su "rollback" es el revert del commit; se protege con el test de salida byte-idéntica (§22).

## 20. Seguridad y consistencia

- **Escritura atómica:** `atomic_write_text` (texto) y el equivalente binario de v52 (`_atomic_write` exacto en bytes LF) para todo archivo de caché; `os.replace` con el reintento acotado existente.
- **Manifest final + checksum:** §7; validación de checksums al cargar y al cerrar.
- **Temporales:** al inicio de cada corrida se eliminan `.*.tmp` huérfanos bajo `_cache_v53/` y bajo los árboles derivados que el motor gestiona (patrón `.{nombre}.{8}.tmp`).
- **Huérfanos:** archivos de salida que ya no corresponden (archivo eliminado ⇒ su documento) se retiran con los `sync_generated_*` y `_write_tree` existentes; los registros de shards de archivos eliminados se purgan.
- **Sin secretos (C-7):** la caché de extracción persiste solo datos saneados y aplica `cache_bypass` a los registros que el sanitizador modifica (M4); `file_state.json` contiene rutas, tamaños y hashes (sin contenido); el manifest no incluye variables de entorno ni cadenas de conexión. `sanitize_data` ya es idempotente (M4).
- **Sin mezcla entre repositorios:** `repository_identity` (§7) + el `--output`/`--cache-dir` por repositorio; identidad distinta ⇒ full y reescritura.
- **Interrupción:** ver §18; el peor caso es repetir full.

## 21. Plan de implementación R2

Orden por **retorno medido** (no por el orden ilustrativo del prompt): el cuello que domina (hidratación y escritura de v52) es independiente de la caché persistida y se corrige primero, con riesgo mínimo y beneficio también en corridas `full`. Cada paso termina con tests y una medición sobre IST; no se encadena al siguiente sin pasar sus criterios. Si R2 resulta demasiado grande, la decisión de dividirlo es humana (no se crean rondas por iniciativa del agente).

| Paso | Contenido | Criterio de aceptación (sustentado en datos) |
|---|---|---|
| **R2.1** Hidratación indexada y compartida (§6.D nivel 1) | `HydrationView` por corrida; `consumer_projection`, `HUMAN_DOCUMENTATION` y `ai_context/ai_projection` la reutilizan; `_parameters` indexado por `caller`. Sin cambiar contratos de salida ni `MODEL_VERSION` | Salida **byte-idéntica** (consumer_projection, flujos_humanos, ai_context) y hidratación total en IST ≤ 200 s (prototipo M1: 180 s para dos pasadas; con una sola pasada compartida ≈ 90 s); `flows_hydrated = 12 642` |
| **R2.2** Write-skip de v52 + preflight MAX_PATH (§6.E, §14) | comparación por SHA-256 contra `MANIFEST.json` previo; verificación `fast`; preflight `OUTPUT_PATH_TOO_LONG`; `--long-paths`; evaluar escritura sin `fsync` por archivo solo para v52 | repetición sin cambios: etapa v52 ≤ 10 % de los 486,6 s (≈ 49 s; M2 midió 9,3 s de generación + 0,1 s de hash, margen ×5 para verificación a medir); manifest v52 idéntico; ruta > límite ⇒ error claro antes de escribir; cero `FileNotFoundError` de `.tmp` |
| **R2.3** Versionado y fingerprints (§4, §5) | módulo de versiones, `ANALYZER_CODE_FINGERPRINT`, `CONFIG_FINGERPRINT`, `TEMPLATE_PROFILE_FINGERPRINT`, hash semántico; tests guardianes | tests de deriva de código/versión y de clasificación de opciones de CLI; hashes reproducibles |
| **R2.4** Cache manifest + File State (§6.A, §7) | capa A, escritura con patrón seguro, validación | cold/warm/corrupta/incompleta conforme a §9/§11/§18 |
| **R2.5** Extraction cache (§6.B) — **con gate** | shards, bypass de sanitización, recarga con normalización global siempre | implementar solo si cargar+validar < re-extraer medido en IST; equivalencia byte a byte full vs incremental |
| **R2.6** Write-skip del resto de salidas (§6.E.4) | `index/`, evidencia (`partition_sha256`), `consumer_projection`, `flujos_humanos`, `ai_context`, legado vía `artifacts.json` | salida idéntica a full; bytes escritos medidos por debajo de full en repetición sin cambios |
| **R2.7** Métricas (§13) | envoltorio de stages, `RUN_METRICS.json` | métricas presentes y fuera de artefactos byte-estables; `RUN_SUMMARY` intacto |
| **R2.8** Modos y fallback (§11, §18, §19) | `--cache-mode`, `--cache-dir`, `--verify-cache`, `--trust-mtime`, `--incremental-max-changed-ratio`, `--long-paths`; `fallback_reason` | matriz de §9 conforme; `off` ≡ V5.2 |
| **R2.9** Equivalencia y regresión IST | comparador full vs incremental; IST como regresión; medición del punto de equilibrio del umbral | todos los tests de §22; fijar valores por defecto con datos |

Cambios adicionales de compatibilidad a tratar en R2: `build_output_manifest` excluye `_cache_v53/`; el parser de CLI debe declarar la clasificación de cada nueva opción respecto a `CONFIG_FINGERPRINT`; actualización de tests existentes que enumeran opciones/estructura de salida, **si** el comportamiento por defecto cambia (hasta el cierre, `--cache-mode` por defecto = `off` para no alterar la salida por defecto de V5.2).

## 22. Matriz de tests R2

| Test | Qué comprueba |
|---|---|
| cache cold | sin caché ⇒ full; se crea caché válida; salida ≡ V5.2 |
| cache warm | segunda corrida sin cambios ⇒ 0 re-extracciones, 0 escrituras de salidas idénticas, salida byte-idéntica |
| archivo sin cambios | hit en extracción y file state |
| cuerpo de método | re-extrae 1 archivo; IDs coherentes con full |
| cambio de línea | IDs `CAL-` posteriores cambian igual que en full |
| rename de método | RES global recomputado; resolución ≡ full |
| símbolo nuevo / clase duplicada | ambigüedad ≡ full |
| símbolo eliminado | llamadas/flows afectados ≡ full |
| `.aspx`/`.ascx` (texto y `Inherits`) | webforms/dependencies ≡ full |
| `.vbproj` (RootNamespace, items) | normalización recomputada; ≡ full |
| partial class | consolidación ≡ full |
| line endings | CRLF↔LF: no re-extrae, pero `source_artifacts` refleja el hash crudo nuevo; BOM: sí re-extrae |
| config | `--exclude`/`flow_max_depth` ⇒ full o RES según §9 |
| template / profile / idioma | solo PROY de v52 regenerada; resto idéntico |
| renderer version | familia afectada regenerada; write-skip correcto |
| analyzer version / code fingerprint | full; guardián de deriva de código |
| cache corrupta (1 shard) | miss parcial, salida ≡ full |
| cache corrupta (>1 shard / manifest inválido) | full |
| cache incompleta (sin manifest) | full |
| interrupción a mitad de escritura | sin manifest ⇒ full; sin archivos parciales visibles |
| fallback a full (`refresh`, `off`) | `off` ≡ V5.2; `refresh` reescribe |
| equivalencia full vs incremental | comparación byte a byte con el conjunto de no deterministas declarado (§12.7), sobre fixtures y sobre la copia de IST con los 9 cambios de R0.1 |
| determinismo | dos corridas incrementales idénticas ⇒ mismos bytes |
| sanitización / secretos | `cache_bypass` para los registros que el sanitizador cambia; ningún secreto en `_cache_v53/` (escaneo con el mismo regex del sanitizador) |
| mutación | las etapas no alteran la caché ya cargada (C-12) |
| `_parameters`/hidratación | `hydrate_flow` indexado ≡ original sobre **todos** los flows de IST (no solo muestra) |
| runtime independence | módulos nuevos no importan/abren docs, prompts, tests, `PROJECT_STATE`, IA |
| Windows path largo | preflight `OUTPUT_PATH_TOO_LONG` con mensaje accionable; `--long-paths` escribe; sin `FileNotFoundError` |
| verificación `fast` vs `hash` | edición en sitio detectada (mtime/size) y por hash |
| métricas | campos presentes; `flows_hydrated = 12 642`; fuera de artefactos byte-estables |
| rollback | `--cache-mode off` no toca `_cache_v53/` |
| no mezcla de repositorios | identidad distinta ⇒ full |

Además: suite completa existente (`python -m unittest discover -s tests`) debe seguir verde (2 449 pruebas al cierre de V5.2).

## 23. Deuda técnica clasificada

| ID | Hallazgo / decisión | Clase |
|---|---|---|
| D-5 | Hidratación duplicada: **resuelta en diseño** (R2.1, §6.D); causa real = indexación repetida (M1) | **CURRENT_PHASE** (R2.1) |
| D-6 | `documentation_v52` escribe 46 567 archivos siempre; generar = 9,3 s (M2) | **CURRENT_PHASE** (R2.2) |
| D-13 | MAX_PATH: contrato definido (§14); implementación R2.2 | **CURRENT_PHASE** (R2.2) |
| D-1 | Métricas por stage: contrato definido (§13) | **CURRENT_PHASE** (R2.7) |
| D-2 | Versionado: contrato definido (§4) | **CURRENT_PHASE** (R2.3) |
| — | Manifests de caché / fallback full / equivalencia: definidos (§7, §11, §12) | **CURRENT_PHASE** (R2.4–R2.9) |
| D-3 | `duration_seconds` no determinista en `repository.json`: se trata como no determinista declarado (§12.7); migración a métricas sigue abierta | **NEXT_ROUND** |
| D-7 | Índices inversos (archivo→flows, símbolo→llamadas, etc.): pospuestos detrás de medición (§8) | **FUTURE_PHASE** |
| D-14 | IDs `CAL-` dependientes de la línea: se preserva (§15); opción B futura | **FUTURE_PHASE** (requiere autorización) |
| D-4 | `CallResolver` global: no es el cuello (1,1 s); invalidación parcial de resolvers diferida | **FUTURE_PHASE** |
| D-15 (nuevo) | Constantes de versión de renderers existen pero no hay mecanismo que obligue a subirlas al cambiar la salida | **CURRENT_PHASE** (guardián por fingerprint en R2.3) |
| D-16 (nuevo) | Los registros de extracción contienen texto sin sanear en `calls` y `configuration` (42 en IST), saneados solo al exportar | **OBSERVATION** (se resuelve para la caché con `cache_bypass`; no se cambia el comportamiento de extracción) |
| D-17 (nuevo) | `build_output_manifest` (V4.3) recorrería `_cache_v53/` | **NEXT_ROUND** (excluir en R2) |
| D-11 | JSON vs JSONL: se concluye JSON + shards (§16) | **OBSERVATION** |
| D-12 | `technical_documentation_renderer.py` alto riesgo de mantenibilidad | **FUTURE_PHASE** |
| D-9 | Process exit: no reproducido (R0.1) | **OBSERVATION** |
| — | BLOCKING | ninguno |

## 24. Riesgos

| Riesgo | Mitigación en el contrato |
|---|---|
| Reutilización de caché obsoleta | DEC-00: proyecciones siempre regeneradas y comparadas por contenido; solo extracción persistida, con huella que incluye versión + fingerprint de código + configuración |
| Olvidar subir `ANALYZER_VERSION` | fingerprint de código en runtime + test guardián |
| Divergencia por sanitización (42 registros) | `cache_bypass` (M4) + test específico |
| Mutación de objetos cacheados por resolvers | recarga por corrida y persistencia previa a resolvers (C-12) + test |
| `_parameters`/hidratación idéntica solo verificada en 400 flows | R2.1 exige comparar **todos** los flows de IST |
| Ediciones en sitio de salidas | verificación `size+mtime_ns` por defecto, `hash` opcional |
| Coste de verificación `fast` sobre 46 k archivos no medido | R2.2 lo mide antes de fijar el umbral |
| Benchmarks con caché de disco variable (×2–3) | R2 mide frío y caliente; criterios relativos a la misma máquina/estado |
| Estimaciones de §2 (300–400 s) no medidas | se declaran estimación; los criterios de R2 son mediciones |
| Fallo al escribir la caché | no invalida la corrida (C-2), advertencia en métricas |
| Cambios masivos (branch) más lentos que full | umbral configurable con calibración obligatoria en R2.9; correctitud no afectada |
| Crecimiento de memoria (pico 2,62 GB hoy) | la `HydrationView` añade índices, no copias (verificar pico en R2.1) |
| MAX_PATH en otras rutas (evidence, legado) | preflight genérico por árbol |
| Contrato `RUN_SUMMARY`/`index/` | C-4: no se tocan |
| Generalización de 9 cambios sobre 1–2 componentes | R2.9 amplía a más casos (`web.config`, `Partial`, `.sln`, branch) |

## 25. Archivos modificados

| Archivo | Cambio |
|---|---|
| `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md` | Creado (entregable único) |
| `prompts/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md` | Movido desde `prompts/V5_0/` (convención `prompts/V5/` desde V5.3) |

Sin cambios en código, tests, `PROJECT_STATE.json`, manifests, IDs ni documentos previos. Temporales fuera del repo (scratchpad de la sesión): `hyd_probe.py`, `v52_probe.py`, `san_probe.py`, microbenchmark de escritura (su carpeta `output/_w` dentro del repo se eliminó al terminar). Se creó y borró también `output/_x` (salida vacía de una sonda de v52). `git status` solo muestra los archivos sin versionar listados abajo. Repositorio legado solo lectura.

**Archivos sin versionar al cierre (solo consulta, sin commit):** `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`, `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`, `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`, `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`, `prompts/V5/` (R0, R0.1, R1). Rama `main`, HEAD `6c32c4c` (tag `v5.2`); sin diferencias en archivos versionados.

## 26. Estado final

Decisiones cerradas: versionado (§4), fingerprints y line endings (§5), arquitectura de caché con DEC-00 (§6), manifest (§7), índices (§8), matriz (§9), scopes (§10), full vs incremental (§11), equivalencia (§12), métricas (§13), MAX_PATH (§14), IDs (§15), persistencia (§16), independencia de runtime (§17), migración (§18), rollback (§19), seguridad (§20), plan (§21) y tests (§22). Abiertas con criterio de decisión **medible en R2** (no bloquean): umbral de cambio masivo (§11), nivel 2 de hidratación persistida (§6.D), inclusión de la caché de extracción (§6.B), política de `fsync` de v52 (§6.E) y el coste real de la verificación `fast`.

No se implementó ninguna parte de V5.3: sin caché, sin análisis incremental, sin invalidación en producción, sin índices persistidos, sin cambios en Evidence Core, IDs, `CallResolver` ni manifests. `v5_3_started` permanece `false` (no se actualizó `PROJECT_STATE.json`, no lo pedía el prompt). No se inició R2. Detenido para revisión humana.

**V5_3_R1_CONTRACT_READY**
