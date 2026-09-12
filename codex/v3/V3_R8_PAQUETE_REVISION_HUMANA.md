# LegacyMapper V3 — Revisión Humana

## 1. Estado

```text
FUNCTIONAL_DOCUMENT=DRAFT
TECHNICAL_DOCUMENT=DRAFT
HUMAN_REVIEW_REQUIRED=true
AI_KNOWLEDGE_ALLOWED=false
```

Este paquete no aprueba la documentación. La decisión final debe ser proporcionada explícitamente por el revisor humano.

## 2. System Coverage Summary

```text
PROJECTS_CLASSIFIED=259
SOLUTIONS_REPRESENTED=113
WEBFORMS_REPRESENTED=3346
FUNCTIONAL_FLOWS_REPRESENTED=12642
LINKED_DATA_OPERATIONS=19159
LINKED_STORED_PROCEDURES=5389
UNRESOLVED_RELATIONSHIPS=162914
STRUCTURAL_COVERAGE != COMPLETE_SEMANTIC_UNDERSTANDING
```

Los 259 proyectos están clasificados estructuralmente; esto no afirma comprensión semántica completa.

## 3. Functional Review

### 3.1 Confirmed

- `C01` — El aplicativo está representado por 259 proyectos clasificados, 113 soluciones, 3.346 WebForms y 12.642 flujos funcionales.
  - Evidencia: COV-SYSTEM-METRICS
- `C02` — La cobertura estructural registra 259 proyectos, 12.642 flujos representados y 3.346 WebForms representados.
  - Evidencia: COV-SYSTEM-METRICS
- `C03` — El inventario incluye áreas representadas por proyectos WebForms y bibliotecas, entre ellas WebCO.
  - Evidencia: COV-PROJECTS-01-293506ef1b, COV-PROJECTS-09-1bd1d42d86, COV-PROJECTS-17-d801e1b9da (+1 referencias)
- `C11` — Se identifican áreas o conjuntos de proyectos relacionados con WebMEDHospital y webMEDInvestigacion.
  - Evidencia: COV-PROJECTS-04-9034137262, COV-PROJECTS-12-f2d455006d, COV-PROJECTS-20-0624896acf (+1 referencias)
- `C05` — Existen WebForms y controles ASCX identificados como puntos de entrada, incluidos controles relacionados con las áreas inventariadas.
  - Evidencia: COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9 (+1 referencias)
- `C06` — Se identifican WebForms y controles de usuario como puntos de entrada; Register.aspx figura entre ellos.
  - Evidencia: COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-03-6ef2e96894
- `C07` — Los flujos funcionales representados incluyen rutas asociadas a proyectos como WebADHEspecial y otros proyectos inventariados.
  - Evidencia: COV-FUNCTIONAL_FLOWS-05-9843f32695
- `C08` — Existen flujos funcionales registrados con identificadores y caminos asociados a proyectos inventariados.
  - Evidencia: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-09-6d694c26ee
- `C09` — Las operaciones funcionales de datos incluyen wrappers de repositorio, transacciones y llamadas a procedimientos almacenados.
  - Evidencia: COV-DATA_ACCESS-01-583d103a14, COV-DATA_ACCESS-02-166407d645, COV-DATA_ACCESS-05-68523c171e (+6 referencias)
- `C10` — Las funcionalidades registradas se relacionan con operaciones de datos implementadas mediante wrappers y otros mecanismos de acceso a datos.
  - Evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-08-087285d8b3 (+2 referencias)

### 3.2 Interpreted

- `C04` — La evidencia permite interpretar áreas funcionales asociadas con administración, agenda, camas y otras áreas identificadas en el inventario.
  - Evidencia: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-06-0c64cbc9b5 (+10 referencias)
  - REQUIRES_HUMAN_CONFIRMATION

### 3.3 Unresolved

- `C12` — No está resuelta la conexión determinista entre los WebForms o controles identificados y los flujos funcionales correspondientes.
  - Evidencia: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-06-e2788b309c (+6 referencias)
- `C13` — La evidencia disponible no determina de forma específica qué flujo funcional o destino corresponde a cada punto de entrada identificado.
  - Evidencia: COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-07-309fe4fa22 (+4 referencias)

Detalle autoritativo: `output/LEVANTAMIENTO_FUNCIONAL.md`.

## 4. Functional Missing Information

- `FMI-001` | `FUNCTIONAL_DATA_SEMANTICS` | `IMPORTANT`
  - Pregunta: ¿Qué operación funcional concreta realiza cada WebForm, operación de datos y procedimiento almacenado, y cómo se relacionan entre sí?
  - Motivo: La evidencia proporciona inventarios y representantes, pero no una descripción completa de comportamiento ni de las relaciones funcionales.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-002` | `FUNCTIONAL_ENTRY_FLOW_MAPPING` | `BLOCKING_FOR_APPROVAL`
  - Pregunta: ¿Qué relación determinística existe entre cada WebForm o punto de entrada identificado, los flujos funcionales correspondientes y sus operaciones de datos o procedimientos almacenados?
  - Motivo: Los registros de flujos incluyen entry_point_id nulo y estados unresolved_boundary; los límites de datos presentan destinos terminales no determinados, por lo que no es posible atribuir los flujos a entradas concretas sin evidencia adicional.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-003` | `FUNCTIONAL_INTEGRATION_MAPPING` | `IMPORTANT`
  - Pregunta: ¿Qué flujos funcionales y reglas de negocio implementan las integraciones identificadas, incluida la interfaz SAP?
  - Motivo: La evidencia registra nombres de proyectos, wrappers y procedimientos, pero no establece la conexión completa entre integración, punto de entrada, flujo y comportamiento funcional.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-004` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Cuál es el destino funcional o sistema relacionado con cada flujo iniciado desde los puntos de entrada identificados?
  - Motivo: La evidencia no determina de forma específica los destinos asociados a los flujos o puntos de entrada.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-005` | `UNCLASSIFIED` | `BLOCKING_FOR_APPROVAL`
  - Pregunta: ¿Qué flujo funcional y destino funcional corresponden determinísticamente a cada WebForm o control de usuario identificado?
  - Motivo: La evidencia registra puntos de entrada y flujos, pero no aporta una asociación específica y verificable entre ambos.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-006` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué integraciones funcionales externas están implementadas y qué puntos de entrada o flujos las utilizan?
  - Motivo: No hay evidencia suficiente para confirmar integraciones concretas ni su vinculación con entradas o flujos.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-007` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué comportamiento funcional representan las operaciones de datos, transacciones y procedimientos almacenados dentro de cada flujo?
  - Motivo: La evidencia confirma operaciones de acceso a datos y procedimientos almacenados, pero no proporciona su semántica funcional completa ni su asignación determinista a funcionalidades de usuario.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

- `FMI-008` | `UNCLASSIFIED` | `INFORMATIONAL`
  - Pregunta: ¿Existe un patrón arquitectónico confirmado para la organización de proyectos, soluciones, WebForms, capas de acceso a datos y procedimientos almacenados?
  - Motivo: La evidencia enumera proyectos, soluciones, WebForms y acceso a datos, pero no confirma un patrón arquitectónico.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_FUNCIONAL.md — Solicitudes de información adicional`

## 5. Functional Human Checklist

- [ ] Are the identified functional areas correct?
- [ ] Are important functional areas missing?
- [ ] Are the described WebForms/entry points representative?
- [ ] Are interpreted functional conclusions reasonable?
- [ ] Are any CONFIRMED claims actually incorrect?
- [ ] Can I answer any FMI requests?
- [ ] Are any FMI requests unnecessary?
- [ ] Does the document adequately describe the application functionally?

## 6. Technical Review

### 6.1 Confirmed

- `C001` — El inventario registra 113 soluciones representadas, 234 proyectos cubiertos y 259 proyectos clasificados.
  - Evidencia: COV-SYSTEM-METRICS
- `C003` — La clasificación de proyectos distingue los estados COVERED y PARTIALLY_COVERED, por lo que la cobertura del inventario no es uniforme.
  - Evidencia: COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-19-8ed0f1216d (+1 referencias)
- `C002` — Se identifican proyectos Web y proyectos de lógica o servicios dentro del inventario.
  - Evidencia: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32 (+6 referencias)
- `C011` — Existen límites no resueltos en parte de los flujos y en operaciones de vinculación de interfaces.
  - Evidencia: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-SYSTEM-METRICS (+1 referencias)
- `C004` — La capa de presentación incluye componentes WebForms ASPX y controles de usuario ASCX.
  - Evidencia: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-01-a63076b2ea (+5 referencias)
- `C005` — Se identifican 3.346 WebForms y 335 controles o archivos ASCX representados.
  - Evidencia: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-07-4bd9dd37d9 (+1 referencias)
- `C006` — El acceso a datos registra operaciones enlazadas y wrappers de repositorio asociados al proyecto.
  - Evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544 (+7 referencias)
- `C007` — El inventario registra 2.009 operaciones de acceso a datos enlazadas.
  - Evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544 (+7 referencias)
- `C008` — El inventario registra procedimientos almacenados Oracle identificados y procedimientos vinculados a paquetes y procedimientos.
  - Evidencia: COV-DATA_ACCESS-02-166407d645, COV-STORED_PROCEDURES-00-269aa51946, COV-STORED_PROCEDURES-02-b6f2a6fa7f (+3 referencias)
- `C009` — El inventario registra 674 procedimientos almacenados Oracle identificados.
  - Evidencia: COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe

### 6.2 Interpreted

- `C010` — Se representan 12.642 flujos y 1.265 relaciones registradas; los límites y el significado completo de esas relaciones no están determinados por la evidencia disponible.
  - Evidencia: COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-08-dacbbff82c (+3 referencias)
  - REQUIRES_HUMAN_CONFIRMATION
- `C014` — La cobertura disponible es parcial e incluye proyectos parcialmente cubiertos y relaciones no resueltas.
  - Evidencia: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-PROJECTS-03-2554f44d4e (+5 referencias)
  - REQUIRES_HUMAN_CONFIRMATION

### 6.3 Unresolved

- `C012` — La evidencia disponible no permite confirmar un patrón arquitectónico específico.
  - Evidencia: COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-SYSTEM-METRICS
- `C013` — La evidencia no permite confirmar un patrón de diseño o arquitectura único para el sistema.
  - Evidencia: COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276

Detalle autoritativo: `output/LEVANTAMIENTO_TECNICO.md`.

## 7. Quantitative Technical Review

SYSTEM STRUCTURAL:

```text
linked_data_operations=19159
linked_stored_procedures=5389
```

COVERAGE PARTITION EXAMPLES:

```text
data_access_partition_count=2009
stored_procedures_partition_count=674
```

Estos valores tienen alcances deterministas diferentes y no son directamente contradictorios. El revisor debe verificar si la terminología comunica correctamente el sistema legado; los números no fueron modificados.

## 8. Technical Missing Information

- `TMI-001` | `TECHNICAL_ARCHITECTURE_PATTERN` | `BLOCKING_FOR_APPROVAL`
  - Pregunta: ¿Qué patrón o arquitectura formal declara y aplica el sistema, y qué evidencia de código respalda esa clasificación?
  - Motivo: La evidencia muestra proyectos, WebForms, acceso a datos y procedimientos, pero no proporciona una definición arquitectónica autorizada ni relaciones completas suficientes para confirmarla.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-002` | `TECHNICAL_COMPONENT_RESPONSIBILITY` | `IMPORTANT`
  - Pregunta: ¿Qué componentes implementan reglas de negocio y cómo se distribuyen entre proyectos Web, lógica y servicios?
  - Motivo: La evidencia confirma la existencia de proyectos Web y de lógica o servicios, pero no detalla responsabilidades funcionales.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-003` | `TECHNICAL_END_TO_END_FLOW` | `IMPORTANT`
  - Pregunta: ¿Cuáles son los flujos completos desde los puntos de entrada WebForms hasta la lógica, el acceso a datos y los procedimientos Oracle?
  - Motivo: Los flujos incluidos tienen límites no resueltos o carecen de punto de entrada determinado; no se suministra evidencia semántica suficiente sobre las reglas de negocio.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-004` | `TECHNICAL_EXTERNAL_DEPENDENCIES` | `IMPORTANT`
  - Pregunta: ¿Cuáles son las referencias de ensamblados, paquetes externos y versiones utilizadas por los proyectos cubiertos?
  - Motivo: El catálogo proporcionado no contiene un inventario determinista de dependencias externas y ensamblados.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-005` | `TECHNICAL_PROJECT_DEPENDENCIES` | `IMPORTANT`
  - Pregunta: ¿Cuáles son las dependencias directas entre proyectos, ensamblados y componentes, y cuáles de las relaciones registradas son válidas fuera de copias de seguridad?
  - Motivo: El inventario identifica soluciones y proyectos, pero la evidencia disponible no proporciona un mapa completo y verificable de dependencias entre proyectos y ensamblados.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-006` | `UNCLASSIFIED` | `BLOCKING_FOR_APPROVAL`
  - Pregunta: ¿Qué clases, capas, referencias de proyecto y reglas de composición sustentan la identificación de un patrón arquitectónico específico?
  - Motivo: Los inventarios disponibles no resuelven una parte sustancial de las relaciones entre componentes y llamadas locales.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-007` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Cuáles son las relaciones concretas entre componentes, proyectos, interfaces y operaciones enlazadas?
  - Motivo: Se identifican límites no resueltos en parte de los flujos y en las operaciones de vinculación de interfaces.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-008` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué ensamblados, paquetes o servicios externos utiliza cada proyecto?
  - Motivo: No se incluyen referencias de ensamblados ni un inventario de dependencias externas.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-009` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué reglas de negocio y responsabilidades funcionales implementan los componentes identificados?
  - Motivo: Los flujos funcionales tienen límites no resueltos y la evidencia disponible no describe suficientemente las reglas de negocio.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-010` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué ensamblados y dependencias externas utiliza cada proyecto, incluyendo versiones y referencias verificadas?
  - Motivo: El catálogo suministrado no contiene un inventario detallado de ensamblados externos ni sus versiones.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-011` | `UNCLASSIFIED` | `BLOCKING_FOR_APPROVAL`
  - Pregunta: ¿Existe documentación o evidencia de código suficiente para confirmar un patrón arquitectónico específico y sus límites de capa?
  - Motivo: Los datos de cobertura, flujos, WebForms y acceso a datos no bastan para confirmar un patrón arquitectónico; además, existen límites no resueltos.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

- `TMI-012` | `UNCLASSIFIED` | `IMPORTANT`
  - Pregunta: ¿Qué dependencias externas, paquetes y ensamblados utiliza cada proyecto?
  - Motivo: No se proporcionan manifiestos completos de dependencias ni referencias de ensamblados; las fronteras no resueltas también limitan la determinación de relaciones.
  - TRACEABILITY_AVAILABLE=true
  - Detalle: `output/LEVANTAMIENTO_TECNICO.md — Solicitudes de información adicional`

Familias especialmente relevantes: `TECHNICAL_ARCHITECTURE_PATTERN`, `TECHNICAL_PROJECT_DEPENDENCIES`, `TECHNICAL_EXTERNAL_DEPENDENCIES`, `TECHNICAL_COMPONENT_RESPONSIBILITY`, `TECHNICAL_END_TO_END_FLOW`.

## 9. Technical Human Checklist

- [ ] Are the identified technical components correct?
- [ ] Is the WebForms presentation description correct?
- [ ] Is the Oracle/data-access description correct?
- [ ] Are project/component responsibilities correctly represented?
- [ ] Do I know the architecture/pattern used by the system?
- [ ] Can I provide missing project dependency information?
- [ ] Can I provide external assembly/dependency information?
- [ ] Can I clarify end-to-end WebForm -> BL -> DAL/SYS -> Oracle flows?
- [ ] Are any CONFIRMED technical claims incorrect?
- [ ] Are INTERPRETED technical claims reasonable?
- [ ] Can I answer any TMI requests?
- [ ] Does the technical document adequately represent the system?

## 10. Critical Items for Approval

### FUNCTIONAL_BLOCKING_ITEMS

- `FMI-002` — ¿Qué relación determinística existe entre cada WebForm o punto de entrada identificado, los flujos funcionales correspondientes y sus operaciones de datos o procedimientos almacenados? — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE
- `FMI-005` — ¿Qué flujo funcional y destino funcional corresponden determinísticamente a cada WebForm o control de usuario identificado? — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE

### TECHNICAL_BLOCKING_ITEMS

- `TMI-001` — ¿Qué patrón o arquitectura formal declara y aplica el sistema, y qué evidencia de código respalda esa clasificación? — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE
- `TMI-006` — ¿Qué clases, capas, referencias de proyecto y reglas de composición sustentan la identificación de un patrón arquitectónico específico? — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE
- `TMI-011` — ¿Existe documentación o evidencia de código suficiente para confirmar un patrón arquitectónico específico y sus límites de capa? — disposición humana requerida: ANSWERED / ACCEPTED_AS_UNRESOLVED / NEEDS_ANALYSIS / NOT_APPLICABLE

## 11. Reviewer Response Template

```text
FUNCTIONAL_DECISION=PENDING
TECHNICAL_DECISION=PENDING

Valores permitidos al completar la revisión: APPROVED, NEEDS_CHANGES, NEEDS_MORE_INFORMATION, REJECTED.

FUNCTIONAL_COMMENTS=

TECHNICAL_COMMENTS=

FUNCTIONAL_MISSING_INFORMATION_RESPONSES=

TECHNICAL_MISSING_INFORMATION_RESPONSES=

GENERAL_COMMENTS=
```

## 12. Approval Rules

AI_KNOWLEDGE permanece bloqueado salvo que `FUNCTIONAL_DECISION=APPROVED` y `TECHNICAL_DECISION=APPROVED` sean decisiones humanas explícitas.

Un PASS de tests, un estado de Codex o la creación de este paquete no constituye aprobación.

## Review Observations

- Las solicitudes UNCLASSIFIED se conservaron separadas por cautela determinista; el revisor puede solicitar otra ronda de corrección.
- Los documentos fuente y su trazabilidad detallada permanecen autoritativos y sin cambios.
