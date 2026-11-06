# LegacyMapper V5.4 — R1 Integrated Delivery
## Technology / DB Adapters

## 1. Objetivo

Implementar V5.4 en una sola ronda integrada, siguiendo el nuevo modelo de trabajo:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo de V5.4:

> Separar la lógica específica de tecnología/base de datos del core, preservando exactamente el comportamiento ya demostrado sobre IST.

WebForms/VB.NET/Oracle es el primer adapter real preservado.

Esta ronda NO es solo diseño ni solo implementación. Debe cubrir en secuencia:

```text
baseline mínimo
→ contrato/frontera
→ implementación
→ tests arquitectónicos y funcionales
→ regresión real
→ auditoría de mantenibilidad
→ documentación
```

No iniciar V5.5.

---

# 2. Estado de partida

V5.3 está cerrada y respaldada remotamente.

Commit de cierre V5.3:

`9425319cb2edbae896b96f7abfbdcd3764beb538`

Estado esperado:

```text
V5_3_CLOSED
V5_3_R4_PUSHED_TO_ORIGIN_MAIN
V5_4_READY_TO_START
```

`HEAD == origin/main` al cierre V5.3.

No existe tag `v5.3` por instrucción.

Pueden existir sin versionar los artefactos administrativos de verificación final:

- `docs/V5/V5_3_R4_1_GIT_PUSH_RESULT.md`
- `prompts/V5/V5_3_R4_1_FINAL_GIT_PUSH.md`

Clasificarlos y preservarlos. No eliminarlos.

---

# 3. Fuentes de autoridad

Leer antes de implementar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos finales de V5.0
- `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
- cierre final V5.1
- cierre final V5.2
- `docs/V5/V5_3_R4_CLOSURE.md`
- continuidad V5
- roadmap V5

Buscar específicamente las decisiones ya aprobadas sobre:

- adapter boundary;
- normalized core;
- extensions por adapter;
- provenance;
- IDs;
- unresolved;
- runtime independence;
- compatibility/rollback.

Regla de precedencia:

```text
contrato aprobado
> prompt actual
> conveniencia de implementación
```

Si el prompt contradice un contrato aprobado, detenerse y documentarlo.

---

# 4. Contrato heredado que NO puede romperse

El normalized core no debe conocer directamente:

- WebForms;
- VB.NET;
- `.vbproj`;
- Oracle;
- sintaxis ADO.NET específica;
- nombres concretos de extractores/parsers legacy.

Preservar:

- Evidence Core;
- IDs;
- determinismo;
- provenance;
- confirmed/inferred/unresolved;
- SourceArtifact;
- Project;
- Component;
- EntryPoint;
- Call;
- DataOperation;
- ExternalDependency;
- FunctionalPath;
- FunctionalFlow;
- EvidenceReference;
- outputs V5.1/V5.2;
- cache/incremental V5.3;
- CLI existente.

Principio:

```text
adapter interpreta tecnología
core consume contratos normalizados
```

---

# 5. Gate A — Baseline empírico mínimo

Antes de diseñar nuevas clases, inspeccionar el código real.

Crear un inventario de acoplamientos tecnológicos actuales.

Como mínimo revisar:

```text
legacy_documenter/extractors/
legacy_documenter/analysis/
legacy_documenter/models/
legacy_documenter/evidence/
legacy_documenter/cli/
legacy_documenter/pipeline*
```

Clasificar cada módulo relevante como:

- CORE;
- TECHNOLOGY_ADAPTER;
- DATABASE_ADAPTER / DB-SPECIFIC CAPABILITY;
- COMPOSITION/ORCHESTRATION;
- MIXED — requiere separación;
- LEGACY COMPATIBILITY.

Verificar contra el contrato V5.1, que ya identificó como tecnología específica, entre otros:

- VB.NET extractor;
- WebForms extractor;
- VBProj extractor;
- web events;
- web.config;
- solution parsing;
- call extraction;
- database extraction;
- call resolver;
- web entry resolver;
- database resolver;
- dependency resolver.

No asumir que la lista sigue exacta: verificar el código actual V5.3.

### Métricas mínimas

Registrar:

- módulos específicos encontrados;
- imports core → tecnología;
- imports tecnología → core;
- referencias textuales relevantes (`WebForms`, `VB.NET`, `Oracle`, `OleDb`, `OracleClient`, `.vbproj`, etc.);
- puntos de composición actuales;
- APIs públicas/import paths usados por tests/runtime;
- número de tests que importan extractores/resolvers directamente.

No hacer una corrida IST solo para este inventario.

---

# 6. Baseline canónico antes del refactor

Necesitamos una referencia exacta de V5.3 para comparar V5.4.

Preferencia:

1. reutilizar un output V5.3 reciente SOLO si se puede demostrar que:
   - corresponde exactamente al commit V5.3 cerrado;
   - misma fuente IST;
   - misma configuración;
   - misma versión/schema;
   - fuente no cambió;
2. de lo contrario ejecutar UNA baseline nueva antes de modificar producción.

Baseline recomendado:

```text
full/off
```

Guardar/snapshotear solo lo necesario para comparación determinista.

Usar el comparador aprobado V5.3.

No repetir calibración, changed-ratio ni matrices de cache.

---

# 7. Gate B — Diseño mínimo del adapter

Después del inventario, definir el diseño mínimo suficiente.

No construir un framework genérico enorme.

Debe existir una frontera explícita que permita:

```text
Technology Adapter
    ↓
Normalized Evidence
    ↓
Core
```

y para DB:

```text
technology-specific database parsing/resolution
    ↓
neutral DataOperation / DataObject / DataParameter / ExternalDependency
```

## Decisión obligatoria

Con evidencia del código, decidir entre:

### Opción A
Un adapter compuesto `vbnet-webforms-oracle` con capabilities internas.

### Opción B
Technology Adapter + Database Adapter separados y compuestos.

Elegir la opción más pequeña que respete los contratos existentes.

No separar interfaces únicamente porque el nombre V5.4 diga “Technology / DB Adapters”.

Documentar la decisión.

---

# 8. Contrato mínimo esperado

El diseño debe poder responder determinísticamente:

- qué adapter aplica a un repositorio/archivo;
- qué tipos de archivo soporta;
- qué capacidades declara;
- cómo extrae evidencia específica;
- cómo la proyecta al modelo normalizado;
- cómo conserva extensions específicas;
- qué sucede con tecnología desconocida/no soportada;
- cómo se compone el adapter desde CLI/pipeline;
- cómo participa en fingerprints/cache V5.3.

No imponer nombres de clases antes de inspeccionar el código.

Nombres candidatos, NO obligatorios:

```text
TechnologyAdapter
AdapterCapabilities
AdapterRegistry
AdapterSelection
DatabaseCapability
```

Preferir protocolos/interfaces pequeños.

---

# 9. Regla crítica de dependencias

La dirección debe ser:

```text
core ← contratos neutrales ← adapter
```

NO:

```text
core → webforms adapter
core → oracle adapter
core → vbnet parser
```

La composition root/pipeline sí puede seleccionar/inicializar adapters.

Agregar guard arquitectónico automatizado para impedir regresión futura.

---

# 10. Gate C — Implementación

Implementar la separación real.

Objetivo:

- mover o envolver la lógica específica bajo una frontera de adapter coherente;
- preservar comportamiento;
- evitar reescritura algorítmica innecesaria;
- mantener compatibilidad temporal de imports si es necesaria;
- eliminar dependencias core → tecnología.

Arquitectura candidata del roadmap:

```text
adapters/
    dotnet/
        webforms/
        modern_dotnet/
    java/
    python/
    javascript/
```

Es SOLO una arquitectura candidata.

No crear carpetas vacías para tecnologías no soportadas.

Para V5.4 basta una estructura real que represente correctamente WebForms/VB.NET/Oracle.

---

# 11. Compatibilidad de imports

Si extractores/resolvers existentes tienen consumidores directos:

- no romperlos gratuitamente;
- usar re-export/shim delgado si hace falta;
- documentar deprecation solo si existe una estrategia real.

Los shims NO deben contener nueva lógica.

La lógica canónica debe existir en un solo lugar.

Agregar tests que garanticen que los shims, si existen, siguen siendo puros.

---

# 12. Selección de adapter

La selección debe ser determinista.

No usar IA.

No adivinar tecnología por heurísticas frágiles si la evidencia disponible puede decidirla.

Registrar:

- criterios;
- prioridad;
- ambigüedad;
- unsupported.

Si no hay adapter aplicable:

- no inventar evidencia;
- preservar unresolved/unsupported de forma explícita;
- fallo claro si el contrato requiere no continuar.

No convertir unsupported en WebForms por default silencioso.

---

# 13. Adapter WebForms/VB.NET/Oracle

Este es el adapter real obligatorio.

Debe preservar la capacidad actual de:

- proyectos/solutions VB.NET;
- WebForms;
- eventos/puntos de entrada;
- calls;
- dependencias;
- acceso a datos;
- Oracle;
- web.config/app config relevante;
- flows posteriores;
- normalized evidence.

No cambiar semántica ni IDs para “limpiar” el modelo.

---

# 14. DB boundary

Auditar especialmente:

- `database_extractor`;
- helpers `_database_*`;
- `database_resolver`;
- patrones Oracle/ADO.NET;
- stored procedures;
- SQL;
- parámetros;
- transacciones;
- conexiones/dependencias.

El core debe recibir conceptos neutrales.

Vocabulario Oracle/ADO.NET puede sobrevivir únicamente en:

- adapter internals;
- `extensions[adapter_id]`;
- evidencia/provenance específica cuando el contrato lo permita.

No borrar información específica solo para hacer el core “bonito”.

---

# 15. Proof de extensibilidad sin implementar V5.9

Agregar una prueba de contrato con un adapter sintético/fake mínimo.

Objetivo:

demostrar que un segundo adapter puede:

- registrarse;
- seleccionarse;
- producir entidades normalizadas mínimas;

sin modificar el core.

Esto NO significa implementar Java/Python/modern .NET/SQL Server reales.

No iniciar el piloto multi-tecnología de V5.9.

---

# 16. V5.3 cache/fingerprints

Mover módulos puede cambiar fingerprints.

Revisar explícitamente:

- `ANALYZER_CODE_FINGERPRINT`;
- contrato de extraction cache;
- rutas incluidas en fingerprint;
- adapter/version identity.

Una modificación de implementación del adapter NO puede reutilizar extraction cache antigua si el contrato efectivo cambió.

Si hace falta extender fingerprint/versioning para incluir adapter code/version:

hacerlo y probarlo.

No invalidar cache por cambios puramente documentales.

---

# 17. Gate D — Tests obligatorios

Crear tests dirigidos para:

### Arquitectura
- core no importa implementación WebForms/VB.NET/Oracle;
- composition root sí puede;
- no circular dependencies;
- shims puros si existen.

### Contract
- selección determinista;
- capabilities;
- unsupported;
- fake adapter;
- extensions/provenance;
- error behavior.

### Compatibilidad
- imports públicos existentes;
- extractor/resolver behavior;
- IDs;
- normalized entities;
- outputs.

### DB
- stored procedure;
- SQL;
- parameters;
- transaction;
- unresolved target;
- Oracle-specific extension;
- dependency/connection mapping.

### Cache
- adapter/version change invalida lo correcto;
- mismo adapter/version puede reutilizar;
- no contaminación entre adapter identities.

No inflar tests duplicando casos ya cubiertos.

---

# 18. Gate E — Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Criterio:

- 0 failures;
- 0 errors.

Registrar total, skips y duración.

Si aparecen fallos:

- corregirlos dentro de R1 si pertenecen al mismo objetivo;
- no crear automáticamente R1.1.

Solo bloquear si hay contradicción arquitectónica o defecto que no pueda resolverse responsablemente en esta ronda.

---

# 19. Gate F — Regresión IST real

Después de que tests estén verdes, ejecutar la mínima regresión real necesaria.

Objetivo principal:

```text
V5.3 baseline
vs
V5.4 adapterized implementation
```

sobre IST.

Usar el comparador aprobado.

Debe resultar:

```text
added = 0
removed = 0
changed = 0
```

fuera únicamente de exclusiones contractuales ya aprobadas.

No agregar exclusiones para hacer pasar la comparación.

Comparar como mínimo:

- index;
- evidence;
- documentation legacy;
- documentation_v52;
- consumer projection;
- ai_context;
- cualquier output canónico presente en baseline.

---

# 20. IST: presupuesto de ejecución

No repetir IST innecesariamente.

Objetivo de R1:

- máximo razonable: baseline pre-refactor si no reutilizable;
- UNA corrida post-implementación para equivalencia;
- una corrida adicional solo si corrige un defecto real encontrado.

No ejecutar matrices completas de V5.3.

No repetir pruebas performance que no sean relevantes a V5.4.

---

# 21. Performance sanity check

Comparar tiempos de la corrida final contra baseline reciente.

No exigir igualdad exacta.

Investigar solo regresiones grandes/inexplicadas.

Medir especialmente:

- scan/extraction;
- resolvers;
- evidencia;
- documentación;
- total.

Una reorganización arquitectónica no debería multiplicar costes.

Documentar ruido I/O sin inventar causalidad.

---

# 22. Auditoría de arquitectura final

Después de implementar:

repetir el inventario inicial.

Mostrar antes/después:

- imports core → tecnología;
- módulos MIXED restantes;
- vocabulario tecnológico fuera de adapters;
- dependencias permitidas;
- deuda residual.

Criterio principal:

**la lógica específica debe haberse movido realmente fuera del core, no solo renombrado carpetas.**

---

# 23. Definition of Done de R1

R1 puede quedar `READY_FOR_HUMAN_REVIEW` si:

- frontera de adapter explícita;
- WebForms/VB.NET/Oracle funciona a través de ella;
- core no depende de implementación tecnológica;
- DB-specific behavior encapsulado;
- adapter fake demuestra extensibilidad;
- fingerprints/cache coherentes;
- suite completa verde;
- IST canónicamente equivalente;
- no regresión de IDs/provenance/unresolved;
- documentación actualizada;
- ninguna deuda BLOCKING.

Si queda solo deuda menor, NO crear R2 automáticamente.

---

# 24. Cuándo usar R2

R2 existe únicamente si la revisión humana encuentra defectos reales.

Ejemplos válidos:

- import tecnológico sigue en core;
- equivalencia IST diverge;
- cache mezcla adapters;
- selección ambigua incorrecta;
- compatibilidad pública rota;
- Oracle pierde evidencia.

No usar R2 para:

- cambios cosméticos;
- refactors opcionales;
- tecnologías futuras;
- deuda V5.9.

Si R1 queda limpio:

```text
R1 → R3
```

---

# 25. Fuera de alcance

NO implementar:

- V5.5 AI provider;
- rich flow segmentation V5.6;
- approval/canonical V5.7;
- plugin runtime V5.8;
- piloto real segunda tecnología V5.9;
- Java real;
- Python real;
- JavaScript real;
- modern .NET real;
- SQL Server/PostgreSQL/MySQL reales salvo código ya existente que deba preservar;
- nuevas funciones de IA;
- cambios de template sin necesidad;
- partial resolver recomputation;
- nuevo sistema de cache.

---

# 26. Seguridad

Preservar reglas existentes:

- sanitización antes de persistencia;
- no secretos en cache/log/report;
- no incluir source code crudo en reportes;
- no IA real;
- no modificar IST oficial;
- usar copia/snapshot cuando una prueba requiera mutación.

---

# 27. PROJECT_STATE

Al finalizar R1:

si todo está técnicamente correcto:

```text
current_version = V5.4
status = V5_4_IN_PROGRESS
latest_completed_round = V5.4-R1
latest_approved_round = V5.3-R4
round_status = V5_4_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
next = HUMAN_REVIEW
```

Después de revisión humana:

- si hay defectos → V5.4-R2;
- si no → V5.4-R3.

No marcar V5.4 CLOSED.

---

# 28. Continuidad

Actualizar solo estado vigente y ledger.

Registrar el nuevo modelo:

```text
V5.4+
R1 Integrated Delivery
R2 Targeted Corrections only if needed
R3 Final Verification & Closure
target max = 3 rounds
```

No reescribir historia anterior.

Incluir los documentos administrativos finales de V5.3 pendientes en el inventario Git.

---

# 29. Git

En esta ronda:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO clean;
- NO reset destructivo.

Registrar:

- branch;
- HEAD;
- origin/main;
- ahead/behind;
- archivos modificados/nuevos;
- administrativos V5.3 pendientes.

El checkpoint se hará después de revisión humana si R1 se aprueba.

---

# 30. Informe obligatorio

Crear:

`docs/V5/V5_4_R1_INTEGRATED_DELIVERY.md`

Debe incluir:

1. Objetivo.
2. Estado inicial.
3. Fuentes/contratos leídos.
4. Baseline de acoplamientos.
5. Decisión de arquitectura.
6. Contrato de adapter.
7. DB boundary.
8. Archivos cambiados.
9. Migración/compatibilidad.
10. Adapter WebForms/VB.NET/Oracle.
11. Fake adapter proof.
12. Fingerprints/cache.
13. Tests dirigidos.
14. Suite completa.
15. Baseline IST usada.
16. Corrida IST post-refactor.
17. Comparación canónica.
18. Performance sanity check.
19. Auditoría before/after.
20. Seguridad.
21. Deuda.
22. PROJECT_STATE.
23. Continuidad.
24. Git.
25. Recomendación: R2 o directo R3.
26. Estado final.

Opcional pero recomendado:

`docs/V5/V5_4_R1_INTEGRATED_DELIVERY.json`

con métricas y matrices machine-readable, sin contenido sensible.

---

# 31. Estados finales permitidos

Éxito:

```text
V5_4_R1_READY_FOR_HUMAN_REVIEW
```

y recomendar exactamente una:

```text
V5_4_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_4_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_4_R1_BLOCKED
```

Solo usar BLOCKED por:

- contradicción contractual;
- regresión canónica no resuelta;
- pérdida de evidencia;
- core todavía acoplado de forma material;
- suite roja;
- corrupción/seguridad;
- imposibilidad real de validar.

---

# 32. Regla final de ejecución

Esta ronda pretende reemplazar múltiples micro-rondas.

Dentro de R1:

```text
descubrir
→ diseñar
→ implementar
→ corregir
→ probar
→ validar IST
→ auditar
→ documentar
```

No detenerse después de cada subpaso para pedir otra ronda.

Sí detenerse si aparece una contradicción que requiera decisión humana.

Al terminar, detenerse para revisión humana.
