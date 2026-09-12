# LEVANTAMIENTO TÉCNICO

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

## Alcance técnico

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Resumen tecnológico

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Organización de soluciones y proyectos

- [CONFIRMED] El inventario registra 113 soluciones representadas, 234 proyectos cubiertos y 259 proyectos clasificados. (`C001`; evidencia: COV-SYSTEM-METRICS)
  - Métrica: represented_solutions=113; alcance=SYSTEM_TOTAL; población=SOLUTIONS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: covered_projects=234; alcance=SYSTEM_TOTAL; población=PROJECTS_COVERED; agregación=unique_projects; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: total_projects=259; alcance=SYSTEM_TOTAL; población=PROJECTS; agregación=unique_projects; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
- [CONFIRMED] La clasificación de proyectos distingue los estados COVERED y PARTIALLY_COVERED, por lo que la cobertura del inventario no es uniforme. (`C003`; evidencia: COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-27-fb726ac225)

## Componentes técnicos identificados

- [CONFIRMED] Se identifican proyectos Web y proyectos de lógica o servicios dentro del inventario. (`C002`; evidencia: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e)

## Dependencias entre componentes

- [CONFIRMED] Existen límites no resueltos en parte de los flujos y en operaciones de vinculación de interfaces. (`C011`; evidencia: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004)

## WebForms y capa de presentación

- [CONFIRMED] La capa de presentación incluye componentes WebForms ASPX y controles de usuario ASCX. (`C004`; evidencia: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-08-501954e031, COV-WEBFORMS-09-5f02185bd8)
- [CONFIRMED] Se identifican 3.346 WebForms y 335 controles o archivos ASCX representados. (`C005`; evidencia: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-08-501954e031)
  - Métrica: represented_webforms=3346; alcance=SYSTEM_TOTAL; población=WEBFORMS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: webforms_partition_count=335; alcance=COVERAGE_PARTITION; población=WEBFORMS; agregación=count; fuente=COV-WEBFORMS-00-cd4b1b1a13, CTX-R72-6a1bc55d3fdb94201e23359e8652c89801d00a1b28f9cbc9cbe17814cc349327; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Lógica de aplicación / negocio

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Acceso a datos

- [CONFIRMED] El acceso a datos registra operaciones enlazadas y wrappers de repositorio asociados al proyecto. (`C006`; evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-07-b3c9737d10, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-01-f276b08996, COV-STORED_PROCEDURES-05-6df7f1d261, COV-STORED_PROCEDURES-06-52fea201fa, COV-SYSTEM-METRICS)
- [CONFIRMED] El inventario registra 2.009 operaciones de acceso a datos enlazadas. (`C007`; evidencia: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-07-b3c9737d10, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-01-f276b08996, COV-STORED_PROCEDURES-05-6df7f1d261, COV-STORED_PROCEDURES-06-52fea201fa, COV-SYSTEM-METRICS)
  - Métrica: data_access_partition_count=2009; alcance=COVERAGE_PARTITION; población=DATA_ACCESS; agregación=count; fuente=COV-DATA_ACCESS-00-6faf1dbadd, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Oracle / procedimientos almacenados / SQL

- [CONFIRMED] El inventario registra procedimientos almacenados Oracle identificados y procedimientos vinculados a paquetes y procedimientos. (`C008`; evidencia: COV-DATA_ACCESS-02-166407d645, COV-STORED_PROCEDURES-00-269aa51946, COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-STORED_PROCEDURES-03-43f9f4c933, COV-STORED_PROCEDURES-04-c1188ec189, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe)
- [CONFIRMED] El inventario registra 674 procedimientos almacenados Oracle identificados. (`C009`; evidencia: COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe)
  - Métrica: stored_procedures_partition_count=674; alcance=COVERAGE_PARTITION; población=STORED_PROCEDURES; agregación=count; fuente=COV-STORED_PROCEDURES-02-b6f2a6fa7f, CTX-R72-29d59b3dff565429bdc72075ce73ae69ee504fe07654aa64d7f3ea2fab194568; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Flujos técnicos representativos

- [INTERPRETED] Se representan 12.642 flujos y 1.265 relaciones registradas; los límites y el significado completo de esas relaciones no están determinados por la evidencia disponible. (`C010`; evidencia: COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-SYSTEM-METRICS, COV-WEBFORMS-04-b16d890b3a)
  - Métrica: represented_flows=12642; alcance=SYSTEM_TOTAL; población=FUNCTIONAL_FLOWS; agregación=represented_records; fuente=COV-SYSTEM-METRICS; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
  - Métrica: functional_flows_partition_count=1265; alcance=COVERAGE_PARTITION; población=FUNCTIONAL_FLOWS; agregación=count; fuente=COV-FUNCTIONAL_FLOWS-00-f888def72c, CTX-R72-bfbe9b3d6c02b015c0691b5bc0601547611e4093467a2260ae791601d6ce9ed3; snapshot=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Dependencias entre proyectos

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Dependencias externas y ensamblados

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Patrón de diseño / arquitectura

- [UNRESOLVED] La evidencia disponible no permite confirmar un patrón arquitectónico específico. (`C012`; evidencia: COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-SYSTEM-METRICS)

## Evidencia a favor del patrón

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Evidencia contradictoria o ambigua

- [UNRESOLVED] La evidencia no permite confirmar un patrón de diseño o arquitectura único para el sistema. (`C013`; evidencia: COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276)

## Riesgos técnicos observables

- [INTERPRETED] La cobertura disponible es parcial e incluye proyectos parcialmente cubiertos y relaciones no resueltas. (`C014`; evidencia: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-27-fb726ac225, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004)

## Información técnica no determinada

- [UNRESOLVED] No determinado con la evidencia validada disponible.

## Solicitudes de información adicional

- `TMI-001` [BLOCKING_FOR_APPROVAL] (TECHNICAL_ARCHITECTURE_PATTERN): ¿Qué patrón o arquitectura formal declara y aplica el sistema, y qué evidencia de código respalda esa clasificación?
  - Motivo: La evidencia muestra proyectos, WebForms, acceso a datos y procedimientos, pero no proporciona una definición arquitectónica autorizada ni relaciones completas suficientes para confirmarla.
  - Solicitudes originales: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:MI002:002, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:REQ-TECHNICAL-ASSESSMENT:001, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:M02:002, ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:M001:001, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:M4:004, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:MI002:002, ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:missing_4:004, ASSESS-99294976177afe9aa5a011f3e973b660fd1a6f5005357c2b70852ef9148117f5:MI001:001, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:MI002:002
  - Claims: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C003, ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C004, ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C005, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:CLM-005, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C07, ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:C012, ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:C013, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:C7, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:C003, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:C004, ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:claim_5, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C001, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C003, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C005; evidencias: COV-DATA_ACCESS-01-583d103a14, COV-DATA_ACCESS-02-166407d645, COV-DATA_ACCESS-05-68523c171e, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-09-fb92030580, COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-FUNCTIONAL_FLOWS-06-e2788b309c, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-STORED_PROCEDURES-07-1775b3de79, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe, COV-UNRESOLVED_BOUNDARIES-02-2e4ec1810b, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-03-6ef2e96894, COV-WEBFORMS-07-4bd9dd37d9
  - Paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf, CTX-R72-9179a76f5cb848ece79e96ca44dba9446268a107c221664c5eb80fb538d23113, CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e, CTX-SYN-7235ddd97ff1f5de632d20c409d49692256055a225cd8cf5bf20cac40f0332da, CTX-SYN-b6b0574c1164a1c6697a76abf4e79140c590241add9775a84235321e3f478a03, CTX-SYN-fec23c72cf0bf4ba923b8e41f31cd94e77061d8649dcba41114dc494c0af5bea; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-002` [IMPORTANT] (TECHNICAL_COMPONENT_RESPONSIBILITY): ¿Qué componentes implementan reglas de negocio y cómo se distribuyen entre proyectos Web, lógica y servicios?
  - Motivo: La evidencia confirma la existencia de proyectos Web y de lógica o servicios, pero no detalla responsabilidades funcionales.
  - Solicitudes originales: ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:M004:004
  - Claims: ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:C002; evidencias: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e
  - Paquetes: CTX-SYN-b6b0574c1164a1c6697a76abf4e79140c590241add9775a84235321e3f478a03; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-003` [IMPORTANT] (TECHNICAL_END_TO_END_FLOW): ¿Cuáles son los flujos completos desde los puntos de entrada WebForms hasta la lógica, el acceso a datos y los procedimientos Oracle?
  - Motivo: Los flujos incluidos tienen límites no resueltos o carecen de punto de entrada determinado; no se suministra evidencia semántica suficiente sobre las reglas de negocio.
  - Solicitudes originales: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:MI003:003, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:REQ-TECHNICAL-ASSESSMENT:003, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:M03:003, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:M3:003
  - Claims: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C003, ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C004, ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C005, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:CLM-005, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C03, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C04, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C05, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C06, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:C6; evidencias: COV-DATA_ACCESS-04-c8282c0544, COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-03-8c180a1076, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-STORED_PROCEDURES-06-52fea201fa, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276, COV-WEBFORMS-04-b16d890b3a, COV-WEBFORMS-07-4bd9dd37d9
  - Paquetes: CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e, CTX-SYN-7235ddd97ff1f5de632d20c409d49692256055a225cd8cf5bf20cac40f0332da, CTX-SYN-fec23c72cf0bf4ba923b8e41f31cd94e77061d8649dcba41114dc494c0af5bea; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-004` [IMPORTANT] (TECHNICAL_EXTERNAL_DEPENDENCIES): ¿Cuáles son las referencias de ensamblados, paquetes externos y versiones utilizadas por los proyectos cubiertos?
  - Motivo: El catálogo proporcionado no contiene un inventario determinista de dependencias externas y ensamblados.
  - Solicitudes originales: ASSESS-06251da4282aa5e6e4473da3739b9951a1c5f113e37b744c0f0c913f4d459f8a:MI002:002, ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:M003:003, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:M2:002
  - Claims: N/A; evidencias: COV-SYSTEM-METRICS
  - Paquetes: CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c, CTX-SYN-b6b0574c1164a1c6697a76abf4e79140c590241add9775a84235321e3f478a03, CTX-SYN-fec23c72cf0bf4ba923b8e41f31cd94e77061d8649dcba41114dc494c0af5bea; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-005` [IMPORTANT] (TECHNICAL_PROJECT_DEPENDENCIES): ¿Cuáles son las dependencias directas entre proyectos, ensamblados y componentes, y cuáles de las relaciones registradas son válidas fuera de copias de seguridad?
  - Motivo: El inventario identifica soluciones y proyectos, pero la evidencia disponible no proporciona un mapa completo y verificable de dependencias entre proyectos y ensamblados.
  - Solicitudes originales: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:MI001:001, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:REQ-TECHNICAL-ASSESSMENT:002, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:M01:001, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:M1:001, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:MI001:001, ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:missing_1:001, ASSESS-99294976177afe9aa5a011f3e973b660fd1a6f5005357c2b70852ef9148117f5:MI002:002, ASSESS-c235b68c33fbc3932a2ef65c9f3f9902ea9e3e8ab8cacddd0d13dc7e45add514:M1:001, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:MI001:001
  - Claims: ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C001, ASSESS-057e59167097a11e17c580e5fec17c34acc0e015414b27fbcf2251bb9cac7339:C002, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:CLM-002, ASSESS-0b706af36af1e00c07738c824e513e1f31c2a9ed3f99856a4140be0f1f2c6a20:CLM-005, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C01, ASSESS-1ebbd52c8a6956cac27854c055844e3755c15df26a92d40ee9d8510348ee1a35:C02, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:C1, ASSESS-58ad854b51e2b2e8250e06b38cebd3e6f494e43043ba5bfbe8cf046fb2c47f4d:C2, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:C001, ASSESS-68ecdc424fd62f20bad69fa18a37373073935b87a0fa35dbd520fdaa1ecc8b4a:C002, ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:claim_1, ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:claim_5, ASSESS-99294976177afe9aa5a011f3e973b660fd1a6f5005357c2b70852ef9148117f5:C005, ASSESS-c235b68c33fbc3932a2ef65c9f3f9902ea9e3e8ab8cacddd0d13dc7e45add514:C1, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C002; evidencias: COV-FUNCTIONAL_FLOWS-06-e2788b309c, COV-PROJECTS-00-30976fc95d, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-05-2c8c979f84, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-13-e1c7c5827e, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-21-8336b83b5d, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-27-fb726ac225, COV-PROJECTS-29-574b51a956, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e, COV-SOLUTIONS-00-450ccdb1d2, COV-SOLUTIONS-01-d77a8831d4, COV-SOLUTIONS-02-0b82866443, COV-SOLUTIONS-05-e164b3084e, COV-SOLUTIONS-06-1b3a64ec78, COV-SOLUTIONS-08-b17f5424b5, COV-SOLUTIONS-09-40fef1c102, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe
  - Paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf, CTX-R72-9179a76f5cb848ece79e96ca44dba9446268a107c221664c5eb80fb538d23113, CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e, CTX-SYN-7235ddd97ff1f5de632d20c409d49692256055a225cd8cf5bf20cac40f0332da, CTX-SYN-fec23c72cf0bf4ba923b8e41f31cd94e77061d8649dcba41114dc494c0af5bea; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-006` [BLOCKING_FOR_APPROVAL] (UNCLASSIFIED): ¿Qué clases, capas, referencias de proyecto y reglas de composición sustentan la identificación de un patrón arquitectónico específico?
  - Motivo: Los inventarios disponibles no resuelven una parte sustancial de las relaciones entre componentes y llamadas locales.
  - Solicitudes originales: ASSESS-06251da4282aa5e6e4473da3739b9951a1c5f113e37b744c0f0c913f4d459f8a:MI001:001
  - Claims: ASSESS-06251da4282aa5e6e4473da3739b9951a1c5f113e37b744c0f0c913f4d459f8a:C004, ASSESS-06251da4282aa5e6e4473da3739b9951a1c5f113e37b744c0f0c913f4d459f8a:C005; evidencias: COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973
  - Paquetes: CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-007` [IMPORTANT] (UNCLASSIFIED): ¿Cuáles son las relaciones concretas entre componentes, proyectos, interfaces y operaciones enlazadas?
  - Motivo: Se identifican límites no resueltos en parte de los flujos y en las operaciones de vinculación de interfaces.
  - Solicitudes originales: ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:M002:002
  - Claims: ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:C010, ASSESS-48b7fa40c99ae86d26ae7edf14ecacd795e35fc9a4711446307c13729f7cee88:C011; evidencias: COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004, COV-WEBFORMS-04-b16d890b3a
  - Paquetes: CTX-SYN-b6b0574c1164a1c6697a76abf4e79140c590241add9775a84235321e3f478a03; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-008` [IMPORTANT] (UNCLASSIFIED): ¿Qué ensamblados, paquetes o servicios externos utiliza cada proyecto?
  - Motivo: No se incluyen referencias de ensamblados ni un inventario de dependencias externas.
  - Solicitudes originales: ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:missing_2:002
  - Claims: ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:claim_5; evidencias: COV-SYSTEM-METRICS
  - Paquetes: CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-009` [IMPORTANT] (UNCLASSIFIED): ¿Qué reglas de negocio y responsabilidades funcionales implementan los componentes identificados?
  - Motivo: Los flujos funcionales tienen límites no resueltos y la evidencia disponible no describe suficientemente las reglas de negocio.
  - Solicitudes originales: ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:missing_3:003
  - Claims: ASSESS-7b368b9d42af7a0e9768162d11a383e307fbfe8d1a9641022a7d828cee67de52:claim_5; evidencias: COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-SYSTEM-METRICS
  - Paquetes: CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-010` [IMPORTANT] (UNCLASSIFIED): ¿Qué ensamblados y dependencias externas utiliza cada proyecto, incluyendo versiones y referencias verificadas?
  - Motivo: El catálogo suministrado no contiene un inventario detallado de ensamblados externos ni sus versiones.
  - Solicitudes originales: ASSESS-99294976177afe9aa5a011f3e973b660fd1a6f5005357c2b70852ef9148117f5:MI003:003
  - Claims: ASSESS-99294976177afe9aa5a011f3e973b660fd1a6f5005357c2b70852ef9148117f5:C002; evidencias: COV-PROJECTS-01-293506ef1b, COV-PROJECTS-09-1bd1d42d86, COV-PROJECTS-17-d801e1b9da, COV-PROJECTS-25-8bd9d8e48a, COV-SYSTEM-METRICS
  - Paquetes: CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-011` [BLOCKING_FOR_APPROVAL] (UNCLASSIFIED): ¿Existe documentación o evidencia de código suficiente para confirmar un patrón arquitectónico específico y sus límites de capa?
  - Motivo: Los datos de cobertura, flujos, WebForms y acceso a datos no bastan para confirmar un patrón arquitectónico; además, existen límites no resueltos.
  - Solicitudes originales: ASSESS-c235b68c33fbc3932a2ef65c9f3f9902ea9e3e8ab8cacddd0d13dc7e45add514:M2:002
  - Claims: ASSESS-c235b68c33fbc3932a2ef65c9f3f9902ea9e3e8ab8cacddd0d13dc7e45add514:C4, ASSESS-c235b68c33fbc3932a2ef65c9f3f9902ea9e3e8ab8cacddd0d13dc7e45add514:C5; evidencias: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004
  - Paquetes: CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

- `TMI-012` [IMPORTANT] (UNCLASSIFIED): ¿Qué dependencias externas, paquetes y ensamblados utiliza cada proyecto?
  - Motivo: No se proporcionan manifiestos completos de dependencias ni referencias de ensamblados; las fronteras no resueltas también limitan la determinación de relaciones.
  - Solicitudes originales: ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:MI003:003
  - Claims: ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C001, ASSESS-d08badd7f113e77912ef5e0472ef5748dfedfd6f3d5fc284be73fe28ede58755:C002; evidencias: COV-FUNCTIONAL_FLOWS-07-309fe4fa22, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-01-8cce049540
  - Paquetes: CTX-R72-9179a76f5cb848ece79e96ca44dba9446268a107c221664c5eb80fb538d23113; snapshots: 6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

## Cobertura técnica

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

- `C001` | CONFIRMED | claims locales: LOCAL-3c77033c-C001, LOCAL-4ac6b988-C1, LOCAL-98777ec3-claim_1 | evidencias: COV-SYSTEM-METRICS | paquetes: CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988
- `C002` | CONFIRMED | claims locales: LOCAL-2a31e6dc-C002, LOCAL-607e496e-CLM-002 | evidencias: COV-PROJECTS-00-30976fc95d, COV-PROJECTS-06-0c64cbc9b5, COV-PROJECTS-08-876df4ce32, COV-PROJECTS-14-be3f60075c, COV-PROJECTS-16-1d6e6bc7e3, COV-PROJECTS-22-9090632e2f, COV-PROJECTS-24-2cc1c34bdf, COV-PROJECTS-30-41dd7e8f34, COV-PROJECTS-32-7ef8e4136e | paquetes: CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e
- `C003` | CONFIRMED | claims locales: LOCAL-aa5927bf-C002 | evidencias: COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-27-fb726ac225 | paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf
- `C004` | CONFIRMED | claims locales: LOCAL-2a31e6dc-C003, LOCAL-4ac6b988-C2, LOCAL-607e496e-CLM-003, LOCAL-98777ec3-claim_2, LOCAL-b0539bd5-C003 | evidencias: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-01-a63076b2ea, COV-WEBFORMS-02-f0da207bfd, COV-WEBFORMS-06-607fefed73, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-08-501954e031, COV-WEBFORMS-09-5f02185bd8 | paquetes: CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e
- `C005` | CONFIRMED | claims locales: LOCAL-2a31e6dc-C003, LOCAL-98777ec3-claim_2 | evidencias: COV-SYSTEM-METRICS, COV-WEBFORMS-00-cd4b1b1a13, COV-WEBFORMS-07-4bd9dd37d9, COV-WEBFORMS-08-501954e031 | paquetes: CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3
- `C006` | CONFIRMED | claims locales: LOCAL-3c77033c-C003, LOCAL-4ac6b988-C3, LOCAL-607e496e-CLM-004, LOCAL-98777ec3-claim_3, LOCAL-b0539bd5-C004 | evidencias: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-07-b3c9737d10, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-01-f276b08996, COV-STORED_PROCEDURES-05-6df7f1d261, COV-STORED_PROCEDURES-06-52fea201fa, COV-SYSTEM-METRICS | paquetes: CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e
- `C007` | CONFIRMED | claims locales: LOCAL-3c77033c-C003, LOCAL-4ac6b988-C3, LOCAL-607e496e-CLM-004, LOCAL-98777ec3-claim_3, LOCAL-b0539bd5-C004 | evidencias: COV-DATA_ACCESS-00-6faf1dbadd, COV-DATA_ACCESS-03-2331fde6dd, COV-DATA_ACCESS-04-c8282c0544, COV-DATA_ACCESS-06-ca2fbbeaa3, COV-DATA_ACCESS-07-b3c9737d10, COV-DATA_ACCESS-08-087285d8b3, COV-STORED_PROCEDURES-01-f276b08996, COV-STORED_PROCEDURES-05-6df7f1d261, COV-STORED_PROCEDURES-06-52fea201fa, COV-SYSTEM-METRICS | paquetes: CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e
- `C008` | CONFIRMED | claims locales: LOCAL-38d23113-C004, LOCAL-98777ec3-claim_4, LOCAL-aa5927bf-C003, LOCAL-b0539bd5-C005 | evidencias: COV-DATA_ACCESS-02-166407d645, COV-STORED_PROCEDURES-00-269aa51946, COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-STORED_PROCEDURES-03-43f9f4c933, COV-STORED_PROCEDURES-04-c1188ec189, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe | paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf, CTX-R72-9179a76f5cb848ece79e96ca44dba9446268a107c221664c5eb80fb538d23113, CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3, CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5
- `C009` | CONFIRMED | claims locales: LOCAL-b0539bd5-C005 | evidencias: COV-STORED_PROCEDURES-02-b6f2a6fa7f, COV-UNRESOLVED_BOUNDARIES-00-6943a207fe | paquetes: CTX-R72-e7692429a48a97b9f7dd19cf1aa6f4e58a93c428ef209035b5db8fa2b0539bd5
- `C010` | INTERPRETED | claims locales: LOCAL-3c77033c-C005, LOCAL-aa5927bf-C004 | evidencias: COV-FUNCTIONAL_FLOWS-00-f888def72c, COV-FUNCTIONAL_FLOWS-01-fac30b9b29, COV-FUNCTIONAL_FLOWS-08-dacbbff82c, COV-FUNCTIONAL_FLOWS-09-6d694c26ee, COV-SYSTEM-METRICS, COV-WEBFORMS-04-b16d890b3a | paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf, CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c
- `C011` | CONFIRMED | claims locales: LOCAL-4ac6b988-C5, LOCAL-607e496e-CLM-005 | evidencias: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004 | paquetes: CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e
- `C012` | UNRESOLVED | claims locales: LOCAL-98777ec3-claim_5 | evidencias: COV-FUNCTIONAL_FLOWS-04-fb5f70d0be, COV-SYSTEM-METRICS | paquetes: CTX-R72-c2dab9825d78e70d6533db58f0a0819c3e1b7b3c1c3072080cf2053a98777ec3
- `C013` | UNRESOLVED | claims locales: LOCAL-2a31e6dc-C005, LOCAL-3c77033c-C004 | evidencias: COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-03-4d0ceb9973, COV-UNRESOLVED_BOUNDARIES-05-4ece18e276 | paquetes: CTX-R72-9fb83265f8a85f4fb744bcfd02e87e8dcd925a42b2d6163ebec8fc3b2a31e6dc, CTX-R72-c057398340f051638451783bb6eec485a6c905376f99062c8fc0b8283c77033c
- `C014` | INTERPRETED | claims locales: LOCAL-4ac6b988-C5, LOCAL-607e496e-CLM-005, LOCAL-aa5927bf-C002 | evidencias: COV-FUNCTIONAL_FLOWS-02-0f3dcb2864, COV-FUNCTIONAL_FLOWS-05-9843f32695, COV-PROJECTS-03-2554f44d4e, COV-PROJECTS-11-14351a3c5d, COV-PROJECTS-19-8ed0f1216d, COV-PROJECTS-27-fb726ac225, COV-SYSTEM-METRICS, COV-UNRESOLVED_BOUNDARIES-04-393e8ce004 | paquetes: CTX-R72-2f46f1c50055ff74bf66e2d9ccb486f9b02abfa31b395b5bc557f83eaa5927bf, CTX-R72-e059161b2b557eec6af1df528f98735f1f9bb10a7ce5a5f2266a3b7c4ac6b988, CTX-R72-ead13dc40d1b0f9b7fdf06a96a8a9763bc1287ee12cab4b8e5741f62607e496e

## Estado de revisión

```text
STATUS=APPROVED
HUMAN_REVIEW_REQUIRED=false
APPROVED=true
AI_KNOWLEDGE_ALLOWED=false
```
