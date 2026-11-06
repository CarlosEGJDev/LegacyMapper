# V5.1 R2.1 — Normalized Evidence Core — Saneamiento e Integración

## Rol

Actúa como ingeniero principal responsable de la implementación de LegacyMapper.

Debes trabajar sobre el repositorio:

`C:\dev\LegacyMapper`

Esta ronda continúa directamente el trabajo de:

* V5.0 — Architecture & Contracts
* V5.1 R0 — New Target Rebaseline
* V5.1 R1 — Normalized Evidence Contract
* V5.1 R2 — Normalized Evidence Implementation

Esta ronda es **V5.1 R2.1**.

---

# 1. Regla principal de esta ronda

En V5 establecimos explícitamente la regla:

> **No dejar deuda técnica conocida que contradiga los objetivos arquitectónicos de V5.**

Por lo tanto, no debes aceptar como "deferred" ningún problema de R2 que contradiga:

* independencia del entorno de desarrollo;
* independencia de proveedores de IA;
* separación entre Evidence Core y consumidores;
* separación entre tecnología concreta y Normalized Evidence Core;
* reproducibilidad/determinismo;
* trazabilidad;
* capacidad arquitectónica para múltiples tecnologías;
* preparación correcta para documentación humana, contexto AI y futuros consumidores.

Al mismo tiempo:

> **NO implementes anticipadamente V5.2, V5.3, V5.4, V5.5, V5.6, V5.7, V5.8 ni V5.9.**

Debes corregir las fronteras arquitectónicas y completar V5.1, no adelantar funcionalidades de versiones posteriores.

---

# 2. Documentos que debes leer primero

Antes de modificar código, lee obligatoriamente:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`
5. `docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md`
6. `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
7. `docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md`
8. `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`
9. `docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`

Además, inspecciona el código realmente modificado por V5.1 R2 y los tests de R2.

No asumas que el documento R2 describe perfectamente el estado actual: verifica las afirmaciones importantes contra el código.

---

# 3. Alcance obligatorio

Debes resolver los siguientes puntos.

## R2.1-01 — Integración real del Evidence Core

R2 dejó documentado que:

* `NormalizedEvidenceBuilder`
* `write_evidence`

se utilizan mediante:

`tools/v5_1_r2_real_ist_regression.py`

pero el pipeline productivo:

```text
main.py full
main.py analyze
```

todavía no genera Evidence Core como parte del flujo normal.

Esto debe corregirse.

El flujo productivo debe quedar conceptualmente:

```text
Legacy Source
    ↓
Existing deterministic analysis
    ↓
NormalizedEvidenceBuilder
    ↓
Canonical Evidence Persistence
    ↓
Compatibility Projection
    ↓
existing documentation / projections / future consumers
```

La integración debe ser parte del producto, no de `tools/`.

No debes duplicar el análisis ni crear un segundo scanner.

El Evidence Core debe consumir el resultado determinista existente.

### Importante

No rompas el comportamiento V4.3.

La incorporación del Evidence Core debe ser aditiva respecto del resultado existente.

---

# 4. R2.1-02 — Runtime independence

Verifica y corrige cualquier dependencia del runtime/producto respecto de:

* `tools/`
* `tests/`
* `docs/`
* prompts
* `PROJECT_STATE.json`
* resultados de Claude/Codex
* archivos de desarrollo
* rutas absolutas del entorno del desarrollador
* fixtures de tests
* artefactos históricos

Regla:

```text
Product Runtime
    ↓
production code + runtime configuration + runtime dependencies
```

No:

```text
Product Runtime
    ↓
development tooling/documentation/tests/prompts
```

Los tools pueden utilizar el runtime.

El runtime no puede necesitar los tools.

---

# 5. R2.1-03 — Evidence Persistence

R2 dejó pendiente decidir definitivamente el formato físico.

Actualmente se utiliza JSON pretty-printed y el resultado real ronda:

`~1.16 GB`

Debes analizar el problema con datos reales y decidir la representación física definitiva para V5.1.

Debes medir antes de decidir.

Evalúa como mínimo:

* tamaño;
* tiempo de escritura;
* tiempo de lectura;
* determinismo;
* facilidad de regeneración;
* facilidad de inspección;
* posibilidad de procesamiento incremental futuro;
* particionamiento;
* compatibilidad con V5.3;
* trazabilidad.

Puedes utilizar JSONL u otra representación si la evidencia experimental lo justifica.

No introduzcas complejidad innecesaria.

La decisión debe quedar implementada y testeada.

---

# 6. R2.1-04 — Instantiation

R1 definió `Instantiation` como concepto del Normalized Evidence Core.

R2 dejó las instanciaciones embebidas dentro de `calls.json`.

Debes resolver esta inconsistencia.

Determina mediante inspección del código y del contrato si corresponde materializar:

```text
evidence/instantiations.*
```

como partición explícita.

Si corresponde:

* crea la entidad/representación;
* define su identidad o ausencia de identidad según contrato;
* preserva trazabilidad;
* evita duplicación semántica;
* agrega tests;
* integra la persistencia;
* actualiza las proyecciones necesarias.

No inventes una identidad canónica si el contrato no la requiere.

---

# 7. R2.1-05 — Technology Adapter boundary

V5 no debe quedar arquitectónicamente diseñado como:

```text
LegacyMapper = VB.NET/WebForms analyzer
```

Debe quedar como:

```text
LegacyMapper Core
    +
Technology Adapter
```

El Core debe trabajar con el contrato Normalized Evidence.

Las particularidades de:

* VB.NET;
* WebForms;
* Oracle;
* estructuras específicas de IST;

no deben contaminar las entidades centrales.

### Importante

NO implementes todavía nuevos adapters completos.

Eso corresponde principalmente a V5.4.

Pero debes corregir cualquier dependencia arquitectónica que haga imposible hacerlo correctamente después.

Debes verificar especialmente:

* imports;
* tipos;
* builders;
* persistence;
* projection;
* naming;
* contratos;
* interfaces;
* dependencias entre módulos.

---

# 8. R2.1-06 — AI independence

V5.1 Evidence Core debe funcionar completamente sin IA.

No debe existir dependencia de:

* Copilot;
* Claude;
* OpenAI;
* Ollama;
* Gemini;
* cualquier SDK de proveedor;
* prompts de IA.

El Evidence Core debe producir exactamente la misma evidencia independientemente de que exista o no un proveedor AI.

No implementes todavía el Generic AI Provider de V5.5.

Solamente elimina cualquier acoplamiento que contradiga esta frontera.

---

# 9. R2.1-07 — Preparation for V5.2

V5.2 será:

```text
Template-Driven Documentation & Output Profiles
```

No implementes todavía el Template Engine completo.

Pero V5.1 debe dejar correctamente definida y separada la frontera:

```text
Normalized Evidence
        ↓
Projection / Profile
        ↓
Documentation
```

La Evidence no debe conocer:

* HTML;
* Markdown;
* Word;
* templates;
* renderer;
* formato visual;
* audiencia humana.

La documentación debe consumir Evidence.

No dupliques el análisis para producir documentación.

---

# 10. Human + AI consumers

La arquitectura final debe permitir:

```text
                  Normalized Evidence
                         │
             ┌───────────┼────────────┐
             ↓           ↓            ↓
        Human Docs    AI Context   Consumer
```

En V5.1 no debes implementar todo V5.2/V5.5/V5.8.

Pero debes verificar que Evidence Core no impida estos consumidores.

Especialmente:

* Human documentation no debe convertirse en fuente canónica;
* AI context no debe convertirse en fuente canónica;
* consumer projection no debe convertirse en fuente canónica.

La fuente canónica es:

```text
evidence/
```

---

# 11. Compatibility Projection

Debe mantenerse:

```text
Normalized Evidence
        ↓
Legacy Compatibility Projection
        ↓
V4.3-compatible indexes
```

`index/` NO es Evidence Core.

Debe seguir siendo una proyección de compatibilidad.

Debes mantener la equivalencia V4.3 ya demostrada.

No modifiques arbitrariamente el comportamiento legacy.

---

# 12. Determinism

La construcción de Evidence debe ser determinista.

Para la misma fuente, configuración y versión de código:

```text
same input
    →
same normalized evidence
```

Verifica especialmente:

* orden;
* IDs;
* duplicate ordinals;
* serialización;
* particiones;
* hashes;
* referencias;
* instantiation records.

No dependas de:

* orden accidental de filesystem;
* memoria;
* hash randomization;
* timestamps;
* threads;
* paths absolutos;
* entorno de desarrollo.

---

# 13. Real IST regression

Utiliza como target real:

`C:\Users\cgalianj\source\IST_40\Operacional`

NO utilices como nuevo target:

`C:\inetpub\wwwroot\2010\IST\Operacional`

El segundo es histórico y no debe volver a utilizarse para nuevas mediciones.

Usa como referencia:

`C:\PruebasLegacyMapper\Resultados\v5_1_new_target_rebaseline`

Debes ejecutar una regresión real.

Compara como mínimo:

* entry points;
* event bindings;
* flows;
* paths;
* data operations;
* stored procedures;
* calls;
* dependencies;
* unresolved boundaries;
* IDs;
* compatibility indexes;
* evidence counts;
* determinismo.

---

# 14. Tests

Debes agregar o modificar tests donde corresponda.

Como mínimo deben cubrir:

### Core

* entities;
* identities;
* relations;
* references;
* unresolved;
* traceability.

### Persistence

* serialization;
* deserialization;
* partition integrity;
* manifest;
* determinism;
* physical format.

### Instantiation

* representation;
* persistence;
* traceability;
* deterministic output.

### Runtime independence

Los tests deben demostrar que el runtime no necesita:

* tools;
* tests;
* docs;
* PROJECT_STATE;
* prompts.

### Adapter boundary

Los tests deben demostrar que el Core no depende directamente de VB/WebForms-specific implementation.

### Compatibility

Debe mantenerse la equivalencia V4.3.

### Real IST

Debe ejecutarse la regresión real.

---

# 15. Full test suite

Ejecuta la suite completa.

El baseline anterior fue:

```text
2214 tests
0 failures
0 errors
132 skips
```

No asumas que estos números siguen siendo idénticos después de los cambios.

Reporta:

* total;
* failures;
* errors;
* skips;
* nuevas pruebas;
* pruebas modificadas.

Si aparece un fallo:

1. diagnostica;
2. corrige si pertenece al alcance;
3. vuelve a ejecutar.

Si aparece el tercer fallo repetido del mismo problema:

> detén la implementación y documenta el bloqueo en el único resultado de esta ronda.

No generes documentos adicionales.

---

# 16. V5 roadmap boundary

Respeta estrictamente:

```text
V5.0 — Architecture & Contracts
V5.1 — Normalized Evidence Core
V5.2 — Template-Driven Documentation & Output Profiles
V5.3 — Incremental Engine & Cache
V5.4 — Technology / DB Adapters
V5.5 — Generic AI Provider + Context
V5.6 — Rich Flow Segmentation
V5.7 — Approval + Canonical Knowledge
V5.8 — Consumer / Plugin Contract
V5.9 — Real Multi-Technology Pilot
V5 Closure
```

No implementes en R2.1:

* cache incremental;
* nuevos adapters completos;
* generic AI provider;
* rich segmentation;
* approval;
* canonical knowledge;
* plugin runtime;
* segundo stack tecnológico.

Sí debes eliminar las dependencias arquitectónicas que impedirían esas futuras versiones.

---

# 17. No modificar innecesariamente V4.3

V4.3 está cerrado.

No hagas refactors generales.

No cambies:

* comportamiento legacy;
* índices legacy;
* extractores existentes;

salvo que sea estrictamente necesario para integrar el nuevo Evidence Core.

Si necesitas modificar algo legacy:

1. identifica exactamente por qué;
2. demuestra que es necesario;
3. agrega/regresa tests;
4. verifica equivalencia.

---

# 18. Regla Python descubre; IA interpreta

Mantén:

> **Python descubre; IA interpreta.**

El Evidence Core debe ser determinista.

No utilices IA para:

* descubrir archivos;
* decidir qué evidencia existe;
* inventar relaciones;
* determinar IDs;
* resolver datos estructurados que el código puede determinar.

La IA será consumidor/interprete posteriormente.

---

# 19. Regla de documentación de resultados

Esta ronda debe producir:

```text
docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md
```

Ese será el único documento nuevo de resultado de esta ronda.

NO crees:

* FIX_NOTES.md
* PATCH_RESULT.md
* DIAGNOSTICO_EXTRA.md
* TODO_FIX.md
* CORRECCION_R*.md
* cualquier otro documento auxiliar

No generes un prompt para la siguiente ronda.

No crees documentación adicional salvo que sea estrictamente necesaria como parte del código/producto y esté contemplada por el alcance V5.1.

---

# 20. Contenido obligatorio del resultado

El documento debe incluir:

1. Status final.
2. Resumen ejecutivo.
3. Estado inicial encontrado en R2.
4. Problemas detectados.
5. Decisiones tomadas.
6. Cambios realizados.
7. Arquitectura resultante.
8. Runtime independence.
9. Technology Adapter boundary.
10. AI independence.
11. Evidence persistence final.
12. Instantiation final.
13. Compatibility Projection.
14. Tests.
15. Full suite.
16. Real IST regression.
17. Determinism evidence.
18. Before/after measurements.
19. Archivos modificados.
20. Archivos nuevos.
21. Exclusiones explícitas de V5.2–V5.9.
22. Deuda técnica restante, si existe.

La sección de deuda debe distinguir:

```text
KNOWN_TECHNICAL_DEBT
```

Si existe algo que contradice los objetivos de V5.1, no lo clasifiques como deuda futura: debes resolverlo en esta ronda.

---

# 21. Status permitido

El documento debe terminar con uno de estos estados:

```text
V5_1_R2_1_READY_FOR_R3
V5_1_R2_1_BLOCKED
V5_1_R2_1_CONFLICT
V5_1_R2_1_OPEN_DECISION
```

Usa `V5_1_R2_1_READY_FOR_R3` solamente si:

* Evidence Core está integrado al flujo real;
* runtime es independiente del entorno dev;
* AI no es dependencia;
* Technology Adapter boundary es correcta;
* persistence está cerrada;
* Instantiation está resuelta;
* determinismo está demostrado;
* compatibility projection sigue funcionando;
* suite completa pasa;
* real IST regression pasa;
* no existe deuda técnica conocida dentro del alcance de V5.1.

---

# 22. Regla final

No busques simplemente conseguir tests verdes.

El objetivo es dejar:

```text
V5.1 = Normalized Evidence Core realmente integrado,
determinista, reproducible, independiente del entorno,
independiente de IA y correctamente desacoplado de la
tecnología concreta.
```

Y preparado para:

```text
V5.2 → Templates / Profiles
V5.3 → Cache
V5.4 → Adapters
V5.5 → AI Providers
V5.6 → Segmentation
V5.7 → Approval
V5.8 → Consumers / Plugins
V5.9 → Multi-Technology Pilot
```

Trabaja de forma autónoma dentro de este alcance.

No solicites confirmación para decisiones técnicas normales.

Si encuentras una contradicción real de arquitectura o contrato que no pueda resolverse sin cambiar el alcance de V5.1, detente y reporta `V5_1_R2_1_OPEN_DECISION` en el documento único de resultado.

Al finalizar, entrega únicamente el documento:

`docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md`
