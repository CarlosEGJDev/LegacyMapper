# LEVANTAMIENTO FUNCIONAL

## Metadata

```text
document_status=APPROVED
human_review_required=false
approved=true
knowledge_source_eligible=true
provider=COPILOT
model_id=gpt-5.6-luna
source_snapshots=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
```

## Alcance del levantamiento

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Resumen funcional del aplicativo

- [CONFIRMED] El aplicativo está representado por 259 proyectos clasificados, 113 soluciones, 3.346 WebForms y 12.642 flujos funcionales. (`C01`; evidencia: COV-SYSTEM-METRICS)
  - Métrica: total_projects=259; alcance=SYSTEM_TOTAL; población=PROJECTS; agregación=unique_projects; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: represented_solutions=113; alcance=SYSTEM_TOTAL; población=SOLUTIONS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: represented_webforms=3346; alcance=SYSTEM_TOTAL; población=WEBFORMS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: represented_flows=12642; alcance=SYSTEM_TOTAL; población=FUNCTIONAL_FLOWS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
- [CONFIRMED] La cobertura estructural registra 259 proyectos, 12.642 flujos representados y 3.346 WebForms representados. (`C02`; evidencia: COV-SYSTEM-METRICS)
  - Métrica: total_projects=259; alcance=SYSTEM_TOTAL; población=PROJECTS; agregación=unique_projects; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: represented_flows=12642; alcance=SYSTEM_TOTAL; población=FUNCTIONAL_FLOWS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: represented_webforms=3346; alcance=SYSTEM_TOTAL; población=WEBFORMS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Módulos o áreas funcionales identificadas

- [CONFIRMED] El inventario incluye áreas representadas por proyectos WebForms y bibliotecas, entre ellas WebCO. (`C03`; evidencia: COV-PROJECTS-01-293506ef1b, COV-PROJECTS-09-1bd1d42d86, COV-PROJECTS-17-d801e1b9da, COV-PROJECTS-25-8bd9d8e48a)
- [INTERPRETED] La evidencia permite interpretar áreas funcionales asociadas con administración, agenda, camas y otras áreas identificadas en el inventario. (`C04`; evidencia: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-27-fb726ac225, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e)
- [CONFIRMED] Se identifican áreas o conjuntos de proyectos relacionados con WebMEDHospital y webMEDInvestigacion. (`C11`; evidencia: COV-PROJECTS-04-9034137262, COV-PROJECTS-12-f2d455006d, COV-PROJECTS-20-0624896acf, COV-PROJECTS-28-f6d69f97a7)

## Funcionalidades por módulo/área

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Pantallas, WebForms o puntos de entrada relevantes

- [CONFIRMED] Existen WebForms y controles ASCX identificados como puntos de entrada, incluidos controles relacionados con las áreas inventariadas. (`C05`; evidencia: COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-09-5f02185bd8)
- [CONFIRMED] Se identifican WebForms y controles de usuario como puntos de entrada; Register.aspx figura entre ellos. (`C06`; evidencia: COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-03-6ef2e96894)

## Flujos funcionales identificados

- [CONFIRMED] Los flujos funcionales representados incluyen rutas asociadas a proyectos como WebADHEspecial y otros proyectos inventariados. (`C07`; evidencia: COV-FUNCTIONAL_FLOWS-05-9843f32695)
- [CONFIRMED] Existen flujos funcionales registrados con identificadores y caminos asociados a proyectos inventariados. (`C08`; evidencia: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-09-6d694c26ee)

## Integraciones funcionales detectadas

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Operaciones de datos relacionadas con funcionalidades

- [CONFIRMED] Las operaciones funcionales de datos incluyen wrappers de repositorio, transacciones y llamadas a procedimientos almacenados. (`C09`; evidencia: COV-DATA_ACCESS-01-583d103a14, COV-DATA_ACCESS-02-166407d645, COV-DATA_ACCESS-05-68523c171e, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-09-fb92030580, COV-STORED_PROCEDURES-00-269aa51946, COV-STORED_PROCEDURES-03-43f9f4c933, COV-STORED_PROCEDURES-04-c1188ec189, COV-STORED_PROCEDURES-07-1775b3de79)
- [CONFIRMED] Las funcionalidades registradas se relacionan con operaciones de datos implementadas mediante wrappers y otros mecanismos de acceso a datos. (`C10`; evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-STORED_PROCEDURES-06-52fea201fa)

## Dependencias funcionales relevantes

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Información no determinada

- [UNRESOLVED] No está resuelta la conexión determinista entre los WebForms o controles identificados y los flujos funcionales correspondientes. (`C12`; evidencia: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-06-e2788b309c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, COV-WEBFORMS-05-5dd6557395, COV-WEBFORMS-06-607fefed73)
- [UNRESOLVED] La evidencia disponible no determina de forma específica qué flujo funcional o destino corresponde a cada punto de entrada identificado. (`C13`; evidencia: COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-01-8cce049540, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-08-501954e031)

## Solicitudes de información adicional

- `FMI-001` [IMPORTANT] (FUNCTIONAL_DATA_SEMANTICS): ¿Qué operación funcional concreta realiza cada WebForm, operación de datos y procedimiento almacenado, y cómo se relacionan entre sí?
  - Motivo: La evidencia proporciona inventarios y representantes, pero no una descripción completa de comportamiento ni de las relaciones funcionales.
  - Solicitudes originales: ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-R2:002
  - Claims: ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-C2, ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-C3, ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-C5; evidencias: COV-DATA_ACCESS-07-b3c9737d10, COV-STORED_PROCEDURES-01-f276b08996, COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-09-5f02185bd8
  - Paquetes: CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-002` [BLOCKING_FOR_APPROVAL] (FUNCTIONAL_ENTRY_FLOW_MAPPING): ¿Qué relación determinística existe entre cada WebForm o punto de entrada identificado, los flujos funcionales correspondientes y sus operaciones de datos o procedimientos almacenados?
  - Motivo: Los registros de flujos incluyen entry_point_id nulo y estados unresolved_boundary; los límites de datos presentan destinos terminales no determinados, por lo que no es posible atribuir los flujos a entradas concretas sin evidencia adicional.
  - Solicitudes originales: ASSESS-1eb5308d51fd3cfdb8cb7bcf44108c3f61aa5a2fbc25129d84180dcec499614d:FA-R1:001, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:MI01:001, ASSESS-781963a298bb38a115b0f7cc0499cd57fd45b44d585034f8b7049da05906b24d:FA-R1:001, ASSESS-9119e05a94f0668a3141d48205e148d7c2d672347463c2c6f9a27eda37c96d2a:FA-R1:001, ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-R1:001, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:REQUEST-UNSPECIFIED:001, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:REQUEST-UNSPECIFIED:002, ASSESS-c179ba19845e8c681d6e956f3c3c0bc7189d9318d94c632327f8bab1e241397d:FA-R1:001, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-RQ1:001, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:MI001:001, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:MI002:002, ASSESS-d392255c971abb4d0da6e9dc30f4bab3d93bc316863e70852b209c2165730e86:FA-R1:001
  - Claims: ASSESS-1eb5308d51fd3cfdb8cb7bcf44108c3f61aa5a2fbc25129d84180dcec499614d:FA-C3, ASSESS-1eb5308d51fd3cfdb8cb7bcf44108c3f61aa5a2fbc25129d84180dcec499614d:FA-C5, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C05, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C06, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C07, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C08, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C12, ASSESS-781963a298bb38a115b0f7cc0499cd57fd45b44d585034f8b7049da05906b24d:FA-C3, ASSESS-781963a298bb38a115b0f7cc0499cd57fd45b44d585034f8b7049da05906b24d:FA-C5, ASSESS-9119e05a94f0668a3141d48205e148d7c2d672347463c2c6f9a27eda37c96d2a:FA-C3, ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-C3, ASSESS-a213e1ca62bd3670d79daaadaa8196edb9bee6cf345bfc62bc21b1c46ba81b69:FUN-C4, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:CLM-002, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:CLM-003, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:CLM-004, ASSESS-bd0b43bc2369ce794e3705eb3ba70d599ea8f010a03dffc8ee94d0b05180bb80:CLM-005, ASSESS-c179ba19845e8c681d6e956f3c3c0bc7189d9318d94c632327f8bab1e241397d:FA-C3, ASSESS-c179ba19845e8c681d6e956f3c3c0bc7189d9318d94c632327f8bab1e241397d:FA-C4, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C3, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C4, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C5, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:C002, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:C003, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:C005, ASSESS-ce0fe807fd36929e6b91cdc7b1200e542b13b9712eb3b1b6b72017ad47c50cd4:C006, ASSESS-d392255c971abb4d0da6e9dc30f4bab3d93bc316863e70852b209c2165730e86:FA-C3, ASSESS-d392255c971abb4d0da6e9dc30f4bab3d93bc316863e70852b209c2165730e86:FA-C5; evidencias: COV-DATA_ACCESS-06-ca2fbbeaa3, COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-FUNCTIONAL_FLOWS-06-e2788b309c, COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-PROJECTS-00-30976fc95d, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-07-3f46a4af13, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-15-76e0d072cf, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-23-899ea25d4c, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-27-fb726ac225, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-31-18fd5ff805, COV-PROJECTS-32-7ef8e4136e, COV-STORED_PROCEDURES-00-269aa51946, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe, COV-UNRESOLVED_BOUNDARIES-01-8cce049540, COV-UNRESOLVED_BOUNDARIES-02-2e4ec1810b, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-03-6ef2e96894, COV-WEBFORMS-04-b16d890b3a, COV-WEBFORMS-05-5dd6557395, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-08-501954e031, COV-WEBFORMS-09-5f02185bd8
  - Paquetes: CTX-R72-06a3d34304e3f9fbf9c54f723bc39ddb458e6d8e262fac8e8f5620a0b68da9fd, CTX-R72-22b8f76de82736d1614c93f8775c367107f8ead66c041f5d51de3e0e77b5d644, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568, CTX-R72-2c11eaff78ba5030e45441d3f1a12201271e6e07acb19b35bbd8d8e29c139d6f, CTX-R72-6a1bc55d3fdb94201e23359e8652c89801d00a1b28f9cbc9cbe17814cc349327, CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61, CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c, CTX-R72-bfbe9b3d6c02b015c0691b5bc0601547611e4093467a2260ae791601d6ce9ed3, CTX-SYN-4bc3be5211928a2a8dd2f7c84ac7ee482e15baffbc3b4dce753972eeb223b01e, CTX-SYN-91152975666af794eb58702aaf0de2220b4aea829a5485a02ebadcbcdfc2d883; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-003` [IMPORTANT] (FUNCTIONAL_INTEGRATION_MAPPING): ¿Qué flujos funcionales y reglas de negocio implementan las integraciones identificadas, incluida la interfaz SAP?
  - Motivo: La evidencia registra nombres de proyectos, wrappers y procedimientos, pero no establece la conexión completa entre integración, punto de entrada, flujo y comportamiento funcional.
  - Solicitudes originales: ASSESS-9119e05a94f0668a3141d48205e148d7c2d672347463c2c6f9a27eda37c96d2a:FA-R2:002
  - Claims: ASSESS-9119e05a94f0668a3141d48205e148d7c2d672347463c2c6f9a27eda37c96d2a:FA-C5; evidencias: COV-DATA_ACCESS-02-166407d645, COV-PROJECTS-03-2554f44d4e, COV-UNRESOLVED_BOUNDARIES-02-2e4ec1810b
  - Paquetes: CTX-R72-bfbe9b3d6c02b015c0691b5bc0601547611e4093467a2260ae791601d6ce9ed3; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-004` [IMPORTANT] (UNCLASSIFIED): ¿Cuál es el destino funcional o sistema relacionado con cada flujo iniciado desde los puntos de entrada identificados?
  - Motivo: La evidencia no determina de forma específica los destinos asociados a los flujos o puntos de entrada.
  - Solicitudes originales: ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:MI02:002
  - Claims: ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C07, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C08, ASSESS-381fd01a93b3ff2e741948f4a560e80ff1b6c8a3a7101c77cb822a30c225ddd2:C13; evidencias: COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-01-8cce049540, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-08-501954e031
  - Paquetes: CTX-SYN-4bc3be5211928a2a8dd2f7c84ac7ee482e15baffbc3b4dce753972eeb223b01e; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-005` [BLOCKING_FOR_APPROVAL] (UNCLASSIFIED): ¿Qué flujo funcional y destino funcional corresponden determinísticamente a cada WebForm o control de usuario identificado?
  - Motivo: La evidencia registra puntos de entrada y flujos, pero no aporta una asociación específica y verificable entre ambos.
  - Solicitudes originales: ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:MI01:001
  - Claims: ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:C04, ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:C05, ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:C07; evidencias: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-01-8cce049540, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-08-501954e031
  - Paquetes: CTX-SYN-2a4a5a535b97b657895b3e8321be4fd38427e3521c63234c9c0990e772efec93; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-006` [IMPORTANT] (UNCLASSIFIED): ¿Qué integraciones funcionales externas están implementadas y qué puntos de entrada o flujos las utilizan?
  - Motivo: No hay evidencia suficiente para confirmar integraciones concretas ni su vinculación con entradas o flujos.
  - Solicitudes originales: ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:MI02:002
  - Claims: ASSESS-91686e665442bc18fac9bc6b74d3a312a175c24f5515025389a667de59f5b499:C07; evidencias: COV-DATA_ACCESS-02-166407d645, COV-PROJECTS-03-2554f44d4e, COV-UNRESOLVED_BOUNDARIES-02-2e4ec1810b
  - Paquetes: CTX-SYN-2a4a5a535b97b657895b3e8321be4fd38427e3521c63234c9c0990e772efec93; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-007` [IMPORTANT] (UNCLASSIFIED): ¿Qué comportamiento funcional representan las operaciones de datos, transacciones y procedimientos almacenados dentro de cada flujo?
  - Motivo: La evidencia confirma operaciones de acceso a datos y procedimientos almacenados, pero no proporciona su semántica funcional completa ni su asignación determinista a funcionalidades de usuario.
  - Solicitudes originales: ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-RQ2:002
  - Claims: ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C1, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C5; evidencias: COV-DATA_ACCESS-03-2331fde6dd, COV-STORED_PROCEDURES-05-6df7f1d261, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973
  - Paquetes: CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `FMI-008` [INFORMATIONAL] (UNCLASSIFIED): ¿Existe un patrón arquitectónico confirmado para la organización de proyectos, soluciones, WebForms, capas de acceso a datos y procedimientos almacenados?
  - Motivo: La evidencia enumera proyectos, soluciones, WebForms y acceso a datos, pero no confirma un patrón arquitectónico.
  - Solicitudes originales: ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-RQ3:003
  - Claims: ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C1, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C2, ASSESS-c9336a10a09a08ebdfbf8ad7d4c36b8681fbbc5d8de95f029193f0d1f5438360:FA-C3; evidencias: COV-PROJECTS-04-9034137262, COV-PROJECTS-12-f2d455006d, COV-PROJECTS-20-0624896acf, COV-PROJECTS-28-f6d69f97a7, COV-SOLUTIONS-07-b0dfa566b6, COV-WEBFORMS-05-5dd6557395
  - Paquetes: CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Cobertura del levantamiento

```json
{
  "covered_projects": 234,
  "interpretation_coverage": {
    "semantic_coverage_percent": null,
    "units_planned": 87
  },
  "linked_data_operations": 19159,
  "linked_stored_procedures": 5389,
  "partially_covered_projects": 24,
  "priority_counts": {
    "P0": 33,
    "P1": 48,
    "P2": 6
  },
  "projects_without_usable_evidence": 1,
  "represented_flows": 12642,
  "represented_solutions": 113,
  "represented_unresolved_relationships": 162914,
  "represented_webforms": 3346,
  "structural_coverage": {
    "categories_inventory": [
      "PROJECTS",
      "SOLUTIONS",
      "WEBFORMS",
      "FUNCTIONAL_FLOWS",
      "DATA_ACCESS",
      "STORED_PROCEDURES",
      "UNRESOLVED_BOUNDARIES"
    ],
    "projects_classified": 259
  },
  "total_data_operations": 20082,
  "total_flows": 12642,
  "total_projects": 259,
  "total_solutions": 113,
  "total_stored_procedures": 5389,
  "total_webforms": 3346,
  "unresolved_ownership_projects": 0,
  "unresolved_relationships": 162914
}
```

- STRUCTURAL_COVERAGE describe inclusión/clasificación determinista; INTERPRETATION_COVERAGE no implica cobertura semántica total.

## Trazabilidad

- `C01` | CONFIRMED | claims locales: LOCAL-fc930b61-FUN-C1 | evidencias: COV-SYSTEM-METRICS | paquetes: CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61
- `C02` | CONFIRMED | claims locales: LOCAL-77b5d644-FA-C1 | evidencias: COV-SYSTEM-METRICS | paquetes: CTX-R72-22b8f76de82736d1614c93f8775c367107f8ead66c041f5d51de3e0e77b5d644
- `C03` | CONFIRMED | claims locales: LOCAL-ab194568-FA-C2 | evidencias: COV-PROJECTS-01-293506ef1b, COV-PROJECTS-09-1bd1d42d86, COV-PROJECTS-17-d801e1b9da, COV-PROJECTS-25-8bd9d8e48a | paquetes: CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568
- `C04` | INTERPRETED | claims locales: LOCAL-9c139d6f-FA-C2, LOCAL-d6ce9ed3-FA-C2, LOCAL-fc930b61-FUN-C2 | evidencias: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-27-fb726ac225, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e | paquetes: CTX-R72-2c11eaff78ba5030e45441d3f1a12201271e6e07acb19b35bbd8d8e29c139d6f, CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61, CTX-R72-bfbe9b3d6c02b015c0691b5bc0601547611e4093467a2260ae791601d6ce9ed3
- `C05` | CONFIRMED | claims locales: LOCAL-77b5d644-FA-C3, LOCAL-9c139d6f-FA-C3, LOCAL-fc930b61-FUN-C3 | evidencias: COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-09-5f02185bd8 | paquetes: CTX-R72-22b8f76de82736d1614c93f8775c367107f8ead66c041f5d51de3e0e77b5d644, CTX-R72-2c11eaff78ba5030e45441d3f1a12201271e6e07acb19b35bbd8d8e29c139d6f, CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61
- `C06` | CONFIRMED | claims locales: LOCAL-ab194568-FA-C3, LOCAL-b68da9fd-FA-C3 | evidencias: COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-03-6ef2e96894 | paquetes: CTX-R72-06a3d34304e3f9fbf9c54f723bc39ddb458e6d8e262fac8e8f5620a0b68da9fd, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568
- `C07` | CONFIRMED | claims locales: LOCAL-fc930b61-FUN-C4 | evidencias: COV-FUNCTIONAL_FLOWS-05-9843f32695 | paquetes: CTX-R72-9e3f9dc9e4fd3f25e5f0dfab360a62deb85d8bd49f38dd8a4d4d742efc930b61
- `C08` | CONFIRMED | claims locales: LOCAL-25f9691c-FA-C4 | evidencias: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-09-6d694c26ee | paquetes: CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c
- `C09` | CONFIRMED | claims locales: LOCAL-9c139d6f-FA-C4, LOCAL-b68da9fd-FA-C4, LOCAL-cc349327-CLM-004, LOCAL-d6ce9ed3-FA-C4 | evidencias: COV-DATA_ACCESS-01-583d103a14, COV-DATA_ACCESS-02-166407d645, COV-DATA_ACCESS-05-68523c171e, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-09-fb92030580, COV-STORED_PROCEDURES-00-269aa51946, COV-STORED_PROCEDURES-03-43f9f4c933, COV-STORED_PROCEDURES-04-c1188ec189, COV-STORED_PROCEDURES-07-1775b3de79 | paquetes: CTX-R72-06a3d34304e3f9fbf9c54f723bc39ddb458e6d8e262fac8e8f5620a0b68da9fd, CTX-R72-2c11eaff78ba5030e45441d3f1a12201271e6e07acb19b35bbd8d8e29c139d6f, CTX-R72-6a1bc55d3fdb94201e23359e8652c89801d00a1b28f9cbc9cbe17814cc349327, CTX-R72-bfbe9b3d6c02b015c0691b5bc0601547611e4093467a2260ae791601d6ce9ed3
- `C10` | CONFIRMED | claims locales: LOCAL-77b5d644-FA-C4, LOCAL-ab194568-FA-C5 | evidencias: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-STORED_PROCEDURES-06-52fea201fa | paquetes: CTX-R72-22b8f76de82736d1614c93f8775c367107f8ead66c041f5d51de3e0e77b5d644, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568
- `C11` | CONFIRMED | claims locales: LOCAL-25f9691c-FA-C2 | evidencias: COV-PROJECTS-04-9034137262, COV-PROJECTS-12-f2d455006d, COV-PROJECTS-20-0624896acf, COV-PROJECTS-28-f6d69f97a7 | paquetes: CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c
- `C12` | UNRESOLVED | claims locales: LOCAL-25f9691c-FA-C5, LOCAL-77b5d644-FA-C5, LOCAL-ab194568-FA-C4 | evidencias: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-06-e2788b309c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, COV-WEBFORMS-05-5dd6557395, COV-WEBFORMS-06-607fefed73 | paquetes: CTX-R72-22b8f76de82736d1614c93f8775c367107f8ead66c041f5d51de3e0e77b5d644, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568, CTX-R72-b65a197039f948c5c54e1db9e606b6d8605a6a53052e7e8cb09acd2b25f9691c
- `C13` | UNRESOLVED | claims locales: LOCAL-9c139d6f-FA-C5, LOCAL-b68da9fd-FA-C5, LOCAL-cc349327-CLM-005 | evidencias: COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-01-8cce049540, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-08-501954e031 | paquetes: CTX-R72-06a3d34304e3f9fbf9c54f723bc39ddb458e6d8e262fac8e8f5620a0b68da9fd, CTX-R72-2c11eaff78ba5030e45441d3f1a12201271e6e07acb19b35bbd8d8e29c139d6f, CTX-R72-6a1bc55d3fdb94201e23359e8652c89801d00a1b28f9cbc9cbe17814cc349327

## Estado de revisión

```text
STATUS=APPROVED
HUMAN_REVIEW_REQUIRED=false
APPROVED=true
AI_KNOWLEDGE_ALLOWED=false
```
