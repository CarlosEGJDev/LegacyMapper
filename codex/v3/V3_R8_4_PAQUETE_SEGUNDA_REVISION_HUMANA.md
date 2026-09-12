# LegacyMapper V3 — Segunda Revisión Humana

## Estado

```text
C04=HUMAN_CONFIRMED
FUNCTIONAL_DOCUMENT_DECISION=PENDING
TECHNICAL_DOCUMENT_DECISION=PENDING
AI_KNOWLEDGE_ALLOWED=false
```

Las recomendaciones son informativas y no son decisiones humanas. Todos los ítems comienzan en `PENDING`.

## Resumen

- Candidatos resueltos: 3.
- Candidatos parciales: 14.
- Evidencia agotada / información externa: 3.

## Revisión de los 20 ítems

### FMI-001

- Pregunta original: ¿Qué operación funcional concreta realiza cada WebForm, operación de datos y procedimiento almacenado, y cómo se relacionan entre sí?
- Estado candidato: `PARTIALLY_RESOLVED_WITH_INTERPRETATION`
- Resumen: PATTERN_SUPPORTED: The evidence supports the presence of an ASP.NET Web Forms pattern through Web Forms controls and pages with code-behind and Inherits directives; it does not establish MVC.
- Evidencia representativa (5 de 7): DEEP-INT-000f278d0f060571, DEEP-INT-00198ff54b4ffed9, DEEP-INT-00647ea337391a19, DEEP-INT-0086b24c4a36fc1c, DEEP-INT-00ab23ebd603a580
- Incertidumbre restante: The target-specific meaning of FMI-001 is not supplied.; The evidence does not establish the broader application architecture beyond the identified Web Forms artifacts.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-002

- Pregunta original: ¿Qué relación determinística existe entre cada WebForm o punto de entrada identificado, los flujos funcionales correspondientes y sus operaciones de datos o procedimientos almacenados?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-003

- Pregunta original: ¿Qué flujos funcionales y reglas de negocio implementan las integraciones identificadas, incluida la interfaz SAP?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-004

- Pregunta original: ¿Cuál es el destino funcional o sistema relacionado con cada flujo iniciado desde los puntos de entrada identificados?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-005

- Pregunta original: ¿Qué flujo funcional y destino funcional corresponden determinísticamente a cada WebForm o control de usuario identificado?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-006

- Pregunta original: ¿Qué integraciones funcionales externas están implementadas y qué puntos de entrada o flujos las utilizan?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### FMI-007

- Pregunta original: ¿Qué comportamiento funcional representan las operaciones de datos, transacciones y procedimientos almacenados dentro de cada flujo?
- Estado candidato: `EXTERNAL_INFORMATION_REQUIRED`
- Resumen: NO_PATTERN_CONFIRMED: The supplied records show assembly references and integration indicators, but do not identify the target-specific pattern or provide enough context to interpret FMI-007.
- Evidencia representativa (5 de 27): COV-DATA_ACCESS-03-2331fde6dd, COV-STORED_PROCEDURES-05-6df7f1d261, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, DEEP-ASM-000d083620195457, DEEP-ASM-001d31483ea17632
- Incertidumbre restante: Business purpose cannot be confirmed from structural/source naming alone.
- Recomendación informativa: `ACCEPTED_AS_UNRESOLVED_EXTERNAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_3/TARGET_REEVALUATION.json`

### FMI-008

- Pregunta original: ¿Existe un patrón arquitectónico confirmado para la organización de proyectos, soluciones, WebForms, capas de acceso a datos y procedimientos almacenados?
- Estado candidato: `RESOLVED_WITH_INTERPRETATION`
- Resumen: PATTERN_SUPPORTED: The available indicators support a WebForms-oriented application pattern; they do not support concluding that MVC is present.
- Evidencia representativa (3 de 3): R81-ARCH-00, R81-ARCH-03, R81-SUMMARY-counts-webforms
- Incertidumbre restante: The evidence does not establish whether additional architectural patterns coexist with WebForms.
- Recomendación informativa: `HUMAN_CONFIRMED`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-001

- Pregunta original: ¿Qué patrón o arquitectura formal declara y aplica el sistema, y qué evidencia de código respalda esa clasificación?
- Estado candidato: `EXTERNAL_INFORMATION_REQUIRED`
- Resumen: The evidence indicates a project-reference landscape containing both resolved and unresolved relationships, but it does not establish the target-specific dependency structure.
- Evidencia representativa (5 de 39): COV-DATA_ACCESS-01-583d103a14, COV-DATA_ACCESS-02-166407d645, COV-DATA_ACCESS-05-68523c171e, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-09-fb92030580
- Incertidumbre restante: Formal architecture is not declared in repository evidence.
- Recomendación informativa: `ACCEPTED_AS_UNRESOLVED_EXTERNAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_3/TARGET_REEVALUATION.json`

### TMI-002

- Pregunta original: ¿Qué componentes implementan reglas de negocio y cómo se distribuyen entre proyectos Web, lógica y servicios?
- Estado candidato: `RESOLVED_WITH_INTERPRETATION`
- Resumen: PATTERN_SUPPORTED: The supplied excerpts support a legacy ASP.NET WebForms presentation pattern, including .aspx pages and .ascx user controls with code-behind and Inherits declarations. This does not establish an MVC architecture.
- Evidencia representativa (5 de 6): DEEP-INT-000f278d0f060571, DEEP-INT-00198ff54b4ffed9, DEEP-INT-00647ea337391a19, DEEP-INT-0086b24c4a36fc1c, DEEP-INT-00ab23ebd603a580
- Incertidumbre restante: The evidence does not establish the architecture of components without corresponding UI excerpts.; The evidence does not establish whether any MVC components coexist elsewhere.
- Recomendación informativa: `HUMAN_CONFIRMED`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-003

- Pregunta original: ¿Cuáles son los flujos completos desde los puntos de entrada WebForms hasta la lógica, el acceso a datos y los procedimientos Oracle?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-004

- Pregunta original: ¿Cuáles son las referencias de ensamblados, paquetes externos y versiones utilizadas por los proyectos cubiertos?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-005

- Pregunta original: ¿Cuáles son las dependencias directas entre proyectos, ensamblados y componentes, y cuáles de las relaciones registradas son válidas fuera de copias de seguridad?
- Estado candidato: `RESOLVED_BY_DETERMINISTIC_EVIDENCE`
- Resumen: La evidencia determinista resolvió el inventario solicitado.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `HUMAN_CONFIRMED`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-006

- Pregunta original: ¿Qué clases, capas, referencias de proyecto y reglas de composición sustentan la identificación de un patrón arquitectónico específico?
- Estado candidato: `PARTIALLY_RESOLVED_WITH_INTERPRETATION`
- Resumen: The evidence supports a data-access-heavy system with substantial stored-procedure involvement, but it does not establish the associated business rules or ownership boundaries.
- Evidencia representativa (2 de 2): R81-ARCH-02, R81-SUMMARY-counts-stored_procedures
- Incertidumbre restante: The evidence does not identify the data-access technologies, layering, or business rules.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-007

- Pregunta original: ¿Cuáles son las relaciones concretas entre componentes, proyectos, interfaces y operaciones enlazadas?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-008

- Pregunta original: ¿Qué ensamblados, paquetes o servicios externos utiliza cada proyecto?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-009

- Pregunta original: ¿Qué reglas de negocio y responsabilidades funcionales implementan los componentes identificados?
- Estado candidato: `PARTIALLY_RESOLVED_WITH_INTERPRETATION`
- Resumen: HYBRID_PATTERN: The evidence supports a mixed dependency landscape containing confirmed project references, assembly references, and integration indicators, while several project references remain unresolved. The supplied records are insufficient to determine the complete runtime dependency or integration architecture.
- Evidencia representativa (5 de 18): DEEP-ASM-000d083620195457, DEEP-ASM-001d31483ea17632, DEEP-ASM-00331e5a00290b97, DEEP-ASM-006457330b7cada9, DEEP-ASM-0067cd48eb72aad0
- Incertidumbre restante: The unresolved project references cannot be semantically resolved from the supplied evidence.; Runtime dependency direction and integration behavior are not established.; The complete architecture cannot be determined from the focused evidence set.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-010

- Pregunta original: ¿Qué ensamblados y dependencias externas utiliza cada proyecto, incluyendo versiones y referencias verificadas?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

### TMI-011

- Pregunta original: ¿Existe documentación o evidencia de código suficiente para confirmar un patrón arquitectónico específico y sus límites de capa?
- Estado candidato: `EXTERNAL_INFORMATION_REQUIRED`
- Resumen: The evidence indicates substantial external-dependency and integration activity, but it does not identify the target-specific integrations or their semantics.
- Evidencia representativa (5 de 23): COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, DEEP-ASM-000d083620195457, DEEP-ASM-001d31483ea17632
- Incertidumbre restante: Authoritative architecture/layer boundary specification is absent.
- Recomendación informativa: `ACCEPTED_AS_UNRESOLVED_EXTERNAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_3/TARGET_REEVALUATION.json`

### TMI-012

- Pregunta original: ¿Qué dependencias externas, paquetes y ensamblados utiliza cada proyecto?
- Estado candidato: `PARTIALLY_RESOLVED`
- Resumen: La evidencia determinista aporta cobertura parcial y conserva incertidumbre.
- Evidencia representativa (0 de 0): Sin referencia adicional
- Incertidumbre restante: La porción no resuelta permanece explícita en la evidencia canónica.
- Recomendación informativa: `ACCEPTED_AS_PARTIAL`
- Decisión humana: `PENDING`
- Trazabilidad: `output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json`

## Representación arquitectónica

- La evidencia de presentación orientada a ASP.NET WebForms está soportada.
- Existe evidencia `.aspx`/`.ascx`, code-behind e `Inherits`.
- MVC no está establecido.
- La ausencia de referencias a `System.Web.Mvc` no prueba que MVC nunca existiera ni que no coexistan componentes MVC.
- No se encontró declaración formal autoritativa de arquitectura ni especificación autoritativa de límites de capas.
- Pueden coexistir otros patrones; no debe forzarse una etiqueta arquitectónica.

## Información externa

- `FMI-007`: ¿Qué comportamiento funcional representan las operaciones de datos, transacciones y procedimientos almacenados dentro de cada flujo?
  - Establecido: NO_PATTERN_CONFIRMED: The supplied records show assembly references and integration indicators, but do not identify the target-specific pattern or provide enough context to interpret FMI-007.
  - Desconocido: Business purpose cannot be confirmed from structural/source naming alone.
  - Agotamiento: evidencia canónica y búsqueda dirigida aplicable completadas.
  - Para resolver: información externa autoritativa sobre propósito funcional o arquitectura/límites formales, según el ítem.
- `TMI-001`: ¿Qué patrón o arquitectura formal declara y aplica el sistema, y qué evidencia de código respalda esa clasificación?
  - Establecido: The evidence indicates a project-reference landscape containing both resolved and unresolved relationships, but it does not establish the target-specific dependency structure.
  - Desconocido: Formal architecture is not declared in repository evidence.
  - Agotamiento: evidencia canónica y búsqueda dirigida aplicable completadas.
  - Para resolver: información externa autoritativa sobre propósito funcional o arquitectura/límites formales, según el ítem.
- `TMI-011`: ¿Existe documentación o evidencia de código suficiente para confirmar un patrón arquitectónico específico y sus límites de capa?
  - Establecido: The evidence indicates substantial external-dependency and integration activity, but it does not identify the target-specific integrations or their semantics.
  - Desconocido: Authoritative architecture/layer boundary specification is absent.
  - Agotamiento: evidencia canónica y búsqueda dirigida aplicable completadas.
  - Para resolver: información externa autoritativa sobre propósito funcional o arquitectura/límites formales, según el ítem.

## Regla de aprobación

Un documento puede aprobarse con ítems `ACCEPTED_AS_PARTIAL` o `ACCEPTED_AS_UNRESOLVED_EXTERNAL` si la incertidumbre es explícita, no se promueven claims sin soporte, los bloqueantes reciben disposición, la trazabilidad permanece válida y el humano acepta expresamente las limitaciones.

La aprobación significa que el documento representa correctamente lo conocido y desconocido; no que todo el legado sea conocido.
