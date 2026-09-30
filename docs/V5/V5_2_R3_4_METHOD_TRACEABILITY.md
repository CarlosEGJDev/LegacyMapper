# V5.2 R3.4 — Trazabilidad técnica por método

## 1. Estado

`V5_2_R3_4_READY_FOR_HUMAN_REVIEW`

La implementación, la suite completa (2423 pruebas, 0 fallas, 0 errores, 132
skips explicados) y una corrida real completa sobre
`C:\Users\cgalianj\source\IST_40\Operacional` están terminadas. Esta ronda
extiende, sin retroceder, la navegación Solution → Project → Archivo →
Componente de R3.3 con un nivel más: Método → Relaciones técnicas
disponibles. No se declara V5.2 cerrada ni lista para R4: falta la
aprobación explícita del Technical Lead, en particular sobre el punto
abierto de la sección 13 (escala documental).

## 2. Preflight de evidencia

Antes de escribir código se investigó, sobre el código real de
`legacy_documenter/evidence/` y de `legacy_documenter/documentation_v52/`
(no sobre la memoria de rondas anteriores), qué campos existen realmente:

- **`symbols`/`Component.members`**: cada miembro es un dict crudo
  `{kind, name, accessibility, shared}` — sin línea, sin firma, sin lista de
  parámetros. No existe una clase `Method`/`Symbol` propia en Evidence Core;
  un método es solo una fila dentro de `Component.members`.
- **`calls`** (partición cruda `evidence/calls.json`, `{file, calls:[...]}`,
  la misma forma que `evidence/builder.py._build_call_identities` lee): cada
  llamada trae `containing_class`, `containing_method` (identidad del
  llamador, por nombre), `expression`, `resolved_target` (cadena
  `"Clase.Método"` o `None`), `confidence` y `evidence.line`. **Esta
  partición NUNCA había sido consumida por `documentation_v52`** (no estaba
  en `EVIDENCE_PARTITIONS` de `engine.py` antes de esta ronda).
- **`data_access`**: cada registro ya trae `class`, `method`, `project`,
  `operation_kind`, `stored_procedure`/`sql_operation`, `confidence` y
  `evidence:[{file,line,expression}]` — es decir, granularidad de método
  desde siempre, solo que R3.3/R2 lo agregaban únicamente por proyecto.
- **`dependencies`**: `{source, target, dependency_type}` con
  `dependency_type` únicamente `Project -> Project | Project -> DLL |
  Project -> SourceFile`. Nunca incluye qué método usa la dependencia.
- **`flow_unresolved`**: tal como lo consume `documentation_v52`
  (`_collect_unresolved`), cada registro trae `flow_id`+`terminal_target`,
  sin ningún campo de método. El registro subyacente de
  `analysis/flow_resolver.py` sí trae una lista `nodes` (cadena de nodos
  `Method`/`Class`/`Project`/`DataAccessOperation` hasta el límite), pero
  extraer de ahí el último método antes del límite es una extracción nueva
  y no trivial sobre una estructura de grafo, no un campo plano.
- **Identidad de método** (sección 5 del prompt): la única noción de
  identidad de método en todo el repositorio es
  `analysis/_flow_key_labels.method_key = (class.lower(), method.lower(),
  project)` — nombre en minúsculas, sin parámetros, sin aridad. Dos
  sobrecargas del mismo nombre colapsan en la misma clave. El propio
  `call_resolver._resolve_method` ya refleja esta limitación: solo marca
  `confidence="confirmed"` cuando hay exactamente un candidato por
  `(clase.lower(), método)`; con 0 o 2+ candidatos deja `resolved_target =
  None`.

## 3. Relaciones realmente disponibles

| Relación | Resultado del preflight | Decisión |
| --- | --- | --- |
| A. Método → llamada | Viable a nivel de método: `containing_class`+`containing_method` identifican al llamador; `resolved_target` (cuando no es `None`) identifica al destino por nombre. | Implementada (llamadas salientes y, cuando el resolutor la marca `confirmed`, entrantes). |
| B. Método → dependencia | No disponible: `dependencies` nunca incluye método, solo proyecto. | GAP declarado (`gap.method_dependencies_not_available`); se mantiene el nivel de proyecto de rondas anteriores, sin cambios. |
| C. Método → operación de datos | Viable a nivel de método: `data_access` ya trae `class`/`method` por registro. | Implementada. |
| D. Método → información no resuelta | No disponible de forma segura al nivel en que se consume hoy la evidencia (sin campo de método en `flow_unresolved` tal como se lee); requeriría una extracción nueva sobre la cadena `nodes` de cada `FunctionalPath`, fuera del alcance de esta ronda (no es "nuevo análisis semántico del código fuente", pero sí un nuevo consumo estructural que no se implementó por prudencia bajo el tiempo de esta ronda). | GAP declarado (`gap.method_unresolved_not_attributable`); se mantiene el nivel de proyecto de rondas anteriores. |
| E. Método → archivo de origen | Trivial: ya resuelto por R3.3 vía el componente propietario. | Reutilizado sin cambios. |

No se trasladó nunca información de un proyecto o componente a un método
sin una relación individual verificable con ese método (ver sección 15,
pruebas específicas para esto).

## 4. Qué se implementó

En `legacy_documenter/documentation_v52/`:

- `categories.py`: nueva clase `MethodModel` (slug/values/slots) y
  `AudienceDocumentModel.methods`.
- `config.py`: nuevo scope `"method"` (slot/value field whitelists,
  `LINK_TYPES`, validación de `scope` en `validate_template`).
- `template.py`: el scope `"method"` recorre todo el motor de plantillas
  (contextos, resolución de parámetros, resolución de enlaces ida/vuelta
  Componente↔Método↔Archivo↔Proyecto).
- `transform.py`:
  - `_build_calls_indexes`: índices salientes
    `(archivo normalizado, clase.lower(), método.lower()) -> [(destino,
    confianza, origen)]` y entrantes `"clase.método".lower() ->
    [(llamador, origen)]` (solo cuando el resolutor marcó `confirmed`).
  - `_build_data_access_by_method`: índice
    `(proyecto, clase.lower(), método.lower()) -> [(tipo, destino,
    confianza, origen)]`.
  - `_build_methods_for_component`: por cada nombre de miembro único dentro
    de un componente, construye un `MethodModel` **solo si** tiene al menos
    una relación individual verificable; si el nombre se repite en el mismo
    componente (sobrecarga/homónimo), nunca atribuye la relación a una
    repetición específica — la declara como grupo ambiguo
    (`component.slots.ambiguous_methods`).
  - Corrección de la sección 9 (`img\aceptar.gif`): `_build_files_and_components`
    ahora distingue explícitamente "cero candidatos" (sigue siendo
    `(sin proyecto asignado)`) de "dos o más candidatos" (ahora
    `(pertenencia compartida o ambigua)`, con la lista de proyectos
    declarantes), en vez de usar la misma etiqueta para ambos casos.
- `engine.py`: se agregó `"calls"` a `EVIDENCE_PARTITIONS` y a
  `source_from_evidence_dir` (antes nunca se leía esa partición).
- Plantillas nuevas: `defaults/templates/dev.method.json` (vista de método:
  ubicación, tipo/visibilidad, llamadas salientes, llamadas entrantes,
  acceso a datos, nota de limitación de dependencias/no-resueltos).
  `dev.component.json` ahora enlaza el nombre de cada método a su detalle
  (cuando existe) y agrega una tabla de "nombres de método repetidos" para
  el caso ambiguo. `dev.file.json` distingue el texto de resumen entre
  archivo con proyecto (o sin evidencia) y archivo de pertenencia
  compartida.
- `defaults/i18n/es.json`: claves nuevas para todo lo anterior, en español,
  sin abreviar la limitación (nunca se oculta que una relación no está
  disponible).
- `defaults/profiles/developer_technical.json`: se agregó `"dev.method"` a
  la lista de plantillas del perfil (si no, el motor nunca lo genera).

No se tocó `legacy_documenter/evidence/`, ningún extractor, ni
`documentation/` legacy.

## 5. Presentación de métodos

Ejemplo real (`developer/modules/BLInterfazSAP/files/BLInterfazSAP/BLInterfazSAP/txTraerListArchivo.md`):

```
# Método txTraerListArchivo

- [Volver al componente](../BLInterfazSAP.md)

Componente: BLInterfazSAP. Proyecto: BLInterfazSAP. Archivo de origen: `BLInterfazSAP.vb`. Tipo: function. Visibilidad: Public. Compartido: Sí.

## Llamadas identificadas
| Llamada a | Confianza | Origen |
| `(no resuelto)` | no resuelto | `bl\BlInterfazSAP\BLInterfazSAP.vb:19` |
...
| `Sonda.Gestion.Nssmut.BL.InterfazSAP.BLInterfazSAP.creadatasetsap` | confirmado | `bl\BlInterfazSAP\BLInterfazSAP.vb:26` |

## Métodos que llaman a este
No se identificó ningún llamador de este método resuelto de forma inequívoca...

## Acceso a datos
| Tipo de acceso | Procedimiento/SQL | Confianza | Origen |
| Control de transacción | `(sin nombre identificado)` | confirmado | `bl\BlInterfazSAP\BLInterfazSAP.vb:19` |

> Las dependencias de biblioteca/proyecto y los límites de flujo no resueltos solo se determinan de forma confiable a nivel de proyecto/componente...
```

Coincide con el ejemplo conceptual de la sección 6 del prompt: ubicación,
información técnica, relaciones identificadas e información no resuelta
como secciones separadas y honestas (una sección vacía dice explícitamente
que no hay evidencia, nunca se omite en silencio ni se rellena con
deducciones del nombre).

## 6. Evidencia bajo demanda

Ningún documento ejecuta análisis adicional al abrirse: `dev.method.json`
solo reproyecta los índices ya calculados por `AudienceTransformer` en un
único paso previo. La estrategia determinista contra la explosión
documental (sección 7 del prompt): un método obtiene documento de detalle
**si y solo si** (a) su nombre es único dentro de su componente (sin
sobrecarga/homónimo) **y** (b) tiene al menos una llamada saliente, una
llamada entrante confirmada, o una operación de acceso a datos atribuida
individualmente. Un método conocido pero sin ninguna de esas relaciones
permanece como fila de la tabla de métodos del componente (nombre, tipo,
visibilidad, "Compartido"), sin enlace y sin documento nuevo — exactamente
lo que ya mostraba R3.3, sin repetirlo en un documento aparte.

## 7. Identidad y ambigüedades

Se respetó explícitamente la limitación de V5.1 (sección 5 del prompt): no
se inventó ningún identificador de método basado en firma/parámetros/línea,
porque el extractor no los registra. Cuando un componente declara el mismo
nombre de miembro más de una vez (sobrecarga real o, en algunos casos del
código real analizado, una property/función distintas que el analizador
solo puede nombrar igual), y ese nombre tiene alguna relación técnica
asociada, se declara como grupo ambiguo
("Nombres de método repetidos en este componente") **una sola vez por
nombre**, listando cuántas repeticiones existen — nunca se atribuye la
relación a una de ellas en particular ni se genera documento de detalle
individual. Ejemplo real: componente `FactoryProperties`
(`developer/modules/unassigned/files/a/FactoryProperties.md`),
`CreateParagraph` (3 repeticiones) y `GetHyphenation` (3 repeticiones).

Una llamada hecha por un miembro ambiguo sí puede aparecer, honestamente,
como "llamada entrante" en la página del método que la recibe (nombrada por
el nombre del llamador, ej. `BLInterfazSAP.Validar`, sin pretender saber
cuál de las repeticiones la hizo) — esto no es una atribución individual al
llamador ambiguo, es una relación real y verificable vista desde el
llamado.

## 8. Pertenencia ambigua de archivos

Corregido tal como pide la sección 9 del prompt. Antes (R3.3): un archivo
con 0 candidatos y un archivo con 2+ candidatos mostraban la misma etiqueta
literal `(sin proyecto asignado)` como si fuera un proyecto real (solo la
nota de ambigüedad, más abajo en el documento, distinguía el caso). Ahora:

- 0 candidatos → sigue siendo `(sin proyecto asignado)` (sin evidencia,
  nunca se afirma ambigüedad donde no la hay).
- 2+ candidatos → `(pertenencia compartida o ambigua)`, con la lista de
  proyectos declarantes en el mismo párrafo introductorio del documento
  (no solo en una nota aparte).

Verificado contra la corrida real (evidencia persistida real, no un
ejemplo fabricado):

```
img\aceptar.gif -> pertenencia: (pertenencia compartida o ambigua)
  "Coincide estructuralmente con 5 proyectos (WebInterfazSAP,
  WebMEDAgendaNew (WebMedAgendaNew.vbproj), WebMEDMovilizacion,
  WebPENConcurrencia, WebPENProcesoResoluciones); no se asigna la
  propiedad exclusiva a ninguno de ellos."
```

Documento real: `developer/modules/unassigned/files/aceptar.md`. No se
cambiaron las reglas de propiedad (`_resolve_owner`/`_owner_index` de
R3.3 quedan intactas); solo se corrigió cómo se presenta el caso de 2+
candidatos. Se encontraron además otros dos casos reales con la misma
ambigüedad (`img\btn\aceptar.gif`, 4 proyectos; `img\btn\aceptar2.GIF`),
corregidos de la misma forma.

## 9. Escala documental

Medido sobre la corrida real completa
(`C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation\documentation_v52\MANIFEST.json`):

| Métrica | R3.3 (referencia, ~25 160 docs) | R3.4 (esta ronda) |
| --- | --- | --- |
| Documentos totales | ~25 160 | **47 375** |
| Documentos de proyecto (`developer/modules/<slug>.md`) | — | 305 |
| Documentos de archivo (`.../files/<archivo>.md`) | — | 11 721 |
| Documentos de componente | — | 9 859 |
| Documentos de método (nuevos) | 0 | **22 215** |
| Otros (README/índices/partes de detalle) | — | 714 |
| Filas de método conocidas en total (en tablas de índice) | — | 33 610 |
| Filas de método que quedaron solo en el índice (sin documento) | — | 11 395 (34 %) |
| Grupos de nombre ambiguo declarados | — | 38 |
| Tamaño total | — | 52 942 344 bytes (~50.5 MiB) |
| Tamaño máximo de un archivo | — | 52 299 bytes (~51 KiB, `blParGenerales/detail-incoming-part-000002.md`, un documento heredado de R3.1, no de esta ronda) |

**Observación honesta para el Technical Lead**: el número de documentos casi
se duplicó (25 160 → 47 375). Esto no es redundancia — cada uno de los
22 215 documentos de método nuevos aporta información individual real que
no estaba antes en ningún documento (sus propias llamadas/accesos a datos),
y el 34 % de los métodos conocidos correctamente se quedó sin documento por
no tener relación individual que mostrar (la estrategia de la sección 7 sí
filtra). Aun así, la proporción de métodos que sí obtuvo documento (66 %)
es más alta de lo que se hubiera anticipado antes de medir contra datos
reales: refleja que, en un sistema legado real de este tamaño, la mayoría
de los métodos hacen al menos una llamada (incluso si no se resuelve) o
tocan una operación de base de datos. Ningún tamaño de archivo individual
es problemático (máximo ~51 KiB, y ese máximo no es de esta ronda). Este
punto se marca explícitamente como algo que el Technical Lead debe revisar
en la sección 15.

## 10. Compatibilidad con R3.3

Verificado, no solo afirmado:

- BLInterfazSAP conserva sus 31 métodos reales
  (`developer/modules/BLInterfazSAP/files/BLInterfazSAP/BLInterfazSAP.md`);
  los 31 obtuvieron documento de detalle (los 31 tienen al menos una
  llamada o acceso a datos en la evidencia real).
- Navegación Solution → Project → Archivo → Componente intacta (pruebas
  `test_v5_2_r3_3_component_navigation.py`, 32 pruebas, todas verdes salvo
  una que se actualizó a propósito — ver sección 13).
- Pantallas propias vs. flujos recibidos, acceso directo vs. indirecto,
  dirección de dependencias, tipo técnico de salida, métrica de 672
  recorridos reales, ruido técnico, `RUN_SUMMARY` con `documentation_v52`,
  custom templates, AI OFF, independencia de runtime: sin cambios de
  código ni de comportamiento; las pruebas correspondientes de rondas
  anteriores (R3, R3.1, R3.2) siguen verdes en la suite completa.
- Vista General simple: intacta (ver sección 12).

## 11. Prueba IST

Corrida real ejecutada:

```
python main.py full "C:\Users\cgalianj\source\IST_40\operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation" --verbose
```

Resultado: `LegacyMapper full run: SUCCESS`, todas las etapas `SUCCESS`
(SCAN, EXTRACTION, CALL_RESOLUTION, WEB_ENTRY_RESOLUTION,
DATABASE_RESOLUTION, FLOW_RESOLUTION, DEPENDENCY_RESOLUTION, EXPORT,
CONTEXT, DOCUMENTATION), `AI_INTERPRETATION: NOT_RUN` (no se solicitó IA).
No se sobrescribió `v5_2_r3_3_validation`; el destino es una carpeta nueva.

Verificación física de los siete casos exigidos por la sección 16 (todos
con evidencia real, ninguno fabricado):

1. **Método con llamadas relacionadas**: `txTraerListArchivo`
   (BLInterfazSAP) — 6 llamadas no resueltas + 1 llamada resuelta
   (`...BLInterfazSAP.creadatasetsap`, confianza confirmada).
2. **Método con acceso a datos demostrable**: `txTraerdatosreq`
   (`blADHds67Bit`, proyecto `blADHAdmCalculoDs67`) — acceso confirmado al
   procedimiento `PADH_D67_BIT.TRAERDATOSREQ`.
3. **Método sin relaciones suficientes**: `New`
   (componente `ChainedProperties`) — queda solo en el índice, sin enlace.
4. **Caso de nombre ambiguo**: `FactoryProperties.CreateParagraph`/
   `GetHyphenation` (3 repeticiones cada uno).
5. **BLInterfazSAP**: 31 métodos reales, ver sección 10.
6. **Proyecto Web**: `BlCobMorosidad` (Aplicación Web ASP.NET Web Forms,
   criterio de R3.2 preservado: declara `.aspx`/`Global.asax`).
7. **`img\aceptar.gif` corregido**: ver sección 8.

No hubo ninguna categoría sin evidencia demostrable que haya requerido
fabricar un ejemplo.

## 12. Suite completa

```
python -m unittest discover -s tests
```

Resultado: **2423 pruebas, 0 fallas, 0 errores, 132 omitidas** (mismo
número de omisiones esperado que documenta `PROJECT_STATE.json`
(`expected_fresh_clone_skips: 132`), todas ya explicadas en rondas
anteriores — ninguna omisión nueva de esta ronda).

Se agregó `tests/test_v5_2_r3_4_method_traceability.py` (16 pruebas
nuevas, todas contractuales sobre un fixture sintético — nunca solo un
snapshot de texto): relación por método sustentada en evidencia real
(llamada + acceso a datos), llamada no resuelta conservada (no descartada
ni adivinada), método sin relaciones (queda solo en el índice, sin
fabricar atribución proyecto→método), homónimos que nunca reciben relación
individual, distinción llamada saliente/entrante, ninguna fuga de
evidencia de un método a otro no relacionado, enlaces de ida y vuelta
verificados sobre un render real a disco, Vista General intacta,
reutilización del particionado existente (sin partición nueva), dos
corridas produciendo el mismo modelo (determinismo), un scope de plantilla
personalizado validado, "AI OFF" (verificado por ausencia de cualquier
referencia a proveedor de IA en el código de esta capa) y `documentation/`
legacy aún importable sin cambios.

Además se corrigieron, como consecuencia directa y esperada de este
cambio, dos pruebas existentes:

- `tests/test_v5_2_r3_3_component_navigation.py::AmbiguousOwnershipTests::
  test_file_matching_two_projects_is_declared_ambiguous_not_guessed`: esta
  prueba afirmaba literalmente el comportamiento que la sección 9 de esta
  ronda pide corregir (`module_name == "(sin proyecto asignado)"` para un
  archivo con 2 candidatos). Se actualizó para exigir la etiqueta correcta
  y, además, verificar explícitamente que ya NO es la etiqueta antigua.
- `tests/test_v4_1_r0_maintainability_inventory.py`: `config.py` cruzó el
  umbral HIGH → VERY_HIGH de esta herramienta de mantenibilidad al ganar un
  cuarto scope navegable ("method"). Es una prueba viviente que cada ronda
  anterior (R2, R3.1, R8) ya actualizó de la misma forma cuando un archivo
  cruzaba de categoría por crecimiento legítimo; se documentó el cambio con
  el mismo estilo de comentario que las rondas anteriores, sin
  reestructurar ni renombrar nada.

## 13. GAPs y deuda restante

- `gap.method_dependencies_not_available` (relación B): las dependencias
  declaradas no incluyen qué método las usa; solo se puede mostrar a nivel
  de proyecto, como en R3.3.
- `gap.method_unresolved_not_attributable` (relación D): los límites de
  flujo no resueltos, tal como se consumen hoy, no incluyen el método
  donde ocurren; solo se puede mostrar a nivel de proyecto, como en R3.3.
  Existe una vía real (parsear `nodes` de cada `FunctionalPath`) que
  quedó fuera de esta ronda por prudencia (es un cambio de consumo
  estructural nuevo, no un campo plano) — queda como trabajo futuro
  explícito, no como algo fabricado hoy.
- `gap.method_identity_no_signatures`: V5.1 no registra firmas/parámetros;
  dos métodos homónimos en un mismo componente nunca podrán distinguirse
  sin una extracción nueva en V5.1 (fuera del alcance de esta ronda).
- `gap.method_overloads_ambiguous`: se declara cuando existen grupos de
  nombre repetido con alguna relación asociada (38 casos reales en la
  corrida IST).
- **OPEN_DECISION real para el Technical Lead** (sección 9 de este
  documento): la escala documental casi se duplicó (25 160 → 47 375
  documentos). La implementación sigue fielmente la estrategia
  determinista pedida (documento de método solo con relación individual
  verificable), y ningún documento es redundante con su nivel superior,
  pero el crecimiento es sustancial y merece una decisión explícita: ¿se
  acepta esta escala tal cual, o se pide un criterio más estricto (por
  ejemplo, exigir 2+ relaciones, o excluir las llamadas puramente "no
  resueltas" del criterio de generación) antes de aprobar la ronda? No se
  tomó esa decisión unilateralmente porque el prompt no fija un umbral
  numérico y hacerlo por cuenta propia sería una decisión de producto, no
  una decisión técnica derivable de la evidencia.

## 14. Ruta de muestra humana

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation\human_review_sample\`

- `README.md`: índice de navegación con los siete recorridos exigidos por
  la sección 17 del prompt (enlaces relativos reales, verificados).
- `documentation_v52/`: copia exacta y completa (ambos perfiles,
  `general/` y `developer/`), sin ninguna edición manual, de la salida
  productiva real generada por la corrida IST de esta ronda. Se copió el
  árbol completo (no solo fragmentos) precisamente para que todos los
  enlaces relativos de cualquier recorrido dentro de la muestra funcionen
  igual que en la salida productiva completa, sin necesidad de reescribir
  ninguna ruta a mano.

## 15. Qué debe revisar el Technical Lead

1. La escala documental (sección 9/13): ¿se acepta el casi duplicado del
   número de documentos, o se pide un criterio de generación más
   estricto?
2. La presentación de método (sección 5): ¿es clara y suficiente, o falta
   algo para un desarrollador real?
3. La corrección de `img\aceptar.gif` (sección 8): ¿la redacción
   "pertenencia compartida o ambigua" es la deseada, o se prefiere otra
   frase?
4. Los dos GAP de relación (B: dependencias, D: no resueltos) — ¿se
   autoriza investigar la extracción desde `functional_paths.nodes` en una
   ronda futura, o se considera fuera de alcance de V5.2?
5. La muestra humana y los siete recorridos: navegarlos y confirmar que
   responden las preguntas de la sección 18 del prompt (esta ronda no
   puede autoaprobarse en nombre del Technical Lead).

## 16. Conclusión

Se implementó la trazabilidad técnica por método pedida, apoyada
exclusivamente en evidencia real y explícita sobre sus límites: se
identificaron con precisión, antes de escribir código, qué relaciones son
viables a nivel de método (llamadas, acceso a datos, archivo de origen) y
cuáles no lo son con la evidencia persistida de hoy (dependencias, límites
no resueltos), declarando estas últimas como GAP en vez de aproximarlas. Se
respetó la falta de identidad canónica de método de V5.1: ningún homónimo o
sobrecarga recibió una relación individual inventada. Se corrigió el
problema de presentación de pertenencia ambigua de archivos señalado en la
sección 9, verificado contra el caso real `img\aceptar.gif` y dos casos
adicionales de la misma clase encontrados en la corrida real. Se preservó
sin retroceso todo lo aprobado en R3, R3.1, R3.2 y R3.3. La suite completa
pasa (2423/2423, 0 fallas, 0 errores) y la corrida real sobre el
repositorio IST completo tuvo éxito en todas sus etapas. El punto que
requiere una decisión explícita del Technical Lead, y por el que esta
ronda no se declara aprobada por sí sola, es el crecimiento de la escala
documental (sección 13).

**V5_2_R3_4_READY_FOR_HUMAN_REVIEW**
