# LegacyMapper V5.0 R2A — Contract Corrections

## MODELO RECOMENDADO

Claude Sonnet 5, medium.

Usar Opus solo ante un bloqueo arquitectónico real que Sonnet no resuelva tras aproximadamente tres intentos bien acotados.

---

# OBJETIVO

Aplicar únicamente las correcciones contractuales justificadas por evidencia en:

```text
docs/V5/V5_0_R2_CONTRACT_VALIDATION.md
```

Esta ronda existe porque R2 terminó en:

```text
V5_0_R2_CONTRACT_CHANGES_REQUIRED
```

R2A es una ronda:

```text
DOCUMENTAL / CORRECCIÓN DE CONTRATO
```

NO es una ronda de implementación.

NO debe modificar producción.

---

# ROOT

```text
C:\dev\LegacyMapper
```

---

# LEE PRIMERO

Obligatorio:

```text
CLAUDE.md
AGENTS.md
docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT.md
docs/V5/V5_0_R2_CONTRACT_VALIDATION.md
docs/continuity/LEGACYMAPPER_V5_ROADMAP.md
```

No releer indiscriminadamente el repositorio.

R2 ya contiene la evidencia empírica necesaria.

---

# ESTADO DE PARTIDA

```text
V5_0_R1_CONTRACT_READY
V5_0_R2_CONTRACT_CHANGES_REQUIRED
```

R2 identificó cuatro conflictos contractuales que deben resolverse antes de R3/V5.1:

```text
DR-R2-01 — identidades / colisiones
DR-R2-02 — tabla de entidades incompleta
DR-R2-03 — observabilidad
DR-R2-04 — EvidenceReference
```

También clasificó los 4 tests rojos y recomendó:

```text
RECOMMENDED_TEST_BASELINE_FIX = Option A
```

---

# PRINCIPIOS OBLIGATORIOS

```text
Python descubre; IA interpreta.
```

Preservar:

- determinismo;
- provenance;
- evidence_refs;
- unresolved;
- no auto-approval;
- no auto-canonicalization;
- Runtime Independence;
- compatibilidad V4.3;
- provider opcional;
- templates no alteran verdad;
- IST como baseline real.

---

# REGLA DE DOCUMENTACIÓN

Claude NO debe crear archivos `.md` adicionales por iniciativa propia.

En esta ronda solo está autorizado a crear:

```text
docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md
```

NO crear:

```text
R2B
R2C
R3 prompt
FIX_NOTES.md
PATCH_RESULT.md
CORRECCION_EXTRA.md
DIAGNOSTICO_EXTRA.md
TODO_FIX.md
WORKAROUND.md
```

Todo hallazgo debe quedar dentro del único documento de resultado.

---

# TAREA R2A

## 1. Aprobar y formalizar DR-R2-01 — Identidades y colisiones

Incorporar al contrato corregido:

### IDs legacy preservados como identidad

Los siguientes IDs V4.3 pueden seguir siendo identidad persistida:

```text
EP-
EVB-
FLOW-
DAO-
SP-
SQL-
PATH-
```

R2 midió 0 colisiones reales en IST para estos kinds.

### IDs legacy NO únicos / NO persistidos como identidad

Los siguientes no deben tratarse como identidad canónica V5:

```text
PAR-
CALL-
UNRES-
```

Deben conservarse como:

```text
legacy_ref
```

para compatibilidad/trazabilidad legacy.

No renombrarlos ni migrarlos retroactivamente.

### Nuevas identidades V5

Las entidades que no tenían ID persistido/estable en V4.3 deben recibir IDs V5 SHA-256 completos:

```text
Project            → PRJ-
Component          → CMP-
ExternalDependency → XDP-
Call               → CAL-
```

Para `UnresolvedBoundary`, usar identidad V5 derivada de forma estable del `path_id` terminal, sin depender de `UNRES-`.

Definir las claves naturales con precisión:

```text
Project
→ path normalizado

Component
→ kind + source artifact + name + discriminador determinista si hace falta

ExternalDependency
→ tipo + source + target + metadata mínima estable

Call
→ source artifact + containing symbol + line + expression + duplicate ordinal determinista

UnresolvedBoundary
→ path_id + boundary type/target cuando sea necesario
```

No usar ordinal basado en orden no determinista.

### EntryPoint → FunctionalFlow

Corregir:

```text
1:1
```

por:

```text
1:0..1
```

porque existen EntryPoints unresolved sin flow.

---

## 2. Aprobar y formalizar DR-R2-02 — Completar Normalized Evidence

Extender el contrato para cubrir toda la evidencia V4.3.

Agregar o representar explícitamente:

```text
Solution
Method / MethodReference
FlowGraph
DataObject
DataParameter
Instantiation
Import
EventBinding
ConfigurationEntry
ScanSummary
```

y las vistas/relaciones:

```text
dependencies
functional_dependencies
flow_unresolved
flow_summary
logical_symbols
outgoing_calls
```

Reglas:

- si un concepto es evidencia primaria, modelarlo como entidad/relación;
- si es derivable sin pérdida, declararlo como projection;
- si es específico de tecnología, usar `extensions[adapter_id]`;
- no duplicar como evidencia canónica algo que puede derivarse de forma exacta;
- preservar el orden legacy cuando sea necesario para D-01.

Debe quedar explícito qué grupos de R2 pasan a:

```text
core entity
core relation
adapter extension
derived projection
legacy-only field
```

---

## 3. Aprobar y formalizar DR-R2-03 — Observabilidad por sidecar

Corregir D-12.

NO agregar observabilidad dentro de:

```text
RUN_SUMMARY.json
```

porque R2 demostró que rompe contratos/tests vigentes.

Nueva decisión:

```text
RUN_SUMMARY.json
→ permanece byte/deterministic compatible con V4.3

RUN_OBSERVABILITY.json
→ sidecar aditivo, no determinista, fuera de D-01
```

`RUN_OBSERVABILITY.json` puede contener:

```text
stage_started_at
stage_finished_at
duration_ms
peak_memory_mb
input_count
output_count
cache_hit
cache_miss
provider_calls
payload_estimated_tokens
threads_alive_at_exit
```

Clasificar cada campo:

```text
required
optional
diagnostic
```

Definir que el sidecar:

- no es evidence;
- no participa en byte-equivalence;
- puede faltar sin invalidar evidence;
- no altera exit codes;
- no contiene secretos ni source content.

---

## 4. Aprobar y formalizar DR-R2-04 — EvidenceReference

Reemplazar el contrato contradictorio anterior por una unión etiquetada:

```text
ref_type
```

Tipos mínimos:

### entity

```text
{
  ref_type: "entity",
  entity_kind,
  entity_id
}
```

### source

```text
{
  ref_type: "source",
  source_id,
  line?,
  excerpt?
}
```

### source_span

Reservado para cuando exista rango real:

```text
{
  ref_type: "source_span",
  source_id,
  start_line?,
  start_column?,
  end_line?,
  end_column?
}
```

No inventar columnas para V4.3 si no existen.

### textual

```text
{
  ref_type: "textual",
  text,
  origin?
}
```

### legacy_ref

Campo opcional para preservar:

```text
CALL-
PAR-
UNRES-
```

u otra referencia legacy no única.

Reglas:

- `promotion_basis` y `provenance` usan esta unión;
- proposals deben usar `entity` refs para grounding canónico;
- legacy refs ambiguas pueden conservarse pero no cuentan como identidad única;
- una referencia rota debe detectarse explícitamente.

---

## 5. Resolver formalmente los 4 tests rojos

Aceptar la recomendación de R2:

```text
Option A
```

Decisión contractual:

1. `PROJECT_STATE.json` representa estado/historia acumulada y puede avanzar.
2. Las invariantes históricas de una fase pertenecen a artefactos congelados.
3. Las aserciones de:
   ```text
   provider_calls == 0
   real_llm_calls == 0
   ```
   deben vivir contra el baseline congelado V4-R14, no contra `PROJECT_STATE.json` vivo.
4. `test_baseline_matches_on_disk_artifact` debe normalizar también esos campos cuando compare contra el state vivo, siguiendo el patrón ya usado para otros campos legítimamente avanzados.

IMPORTANTE:

R2A NO modifica tests.

Solo fija la decisión.

La corrección física de tests debe ocurrir en una ronda posterior autorizada explícitamente.

---

## 6. Actualizar la matriz D-01…D-16

El resultado debe mostrar:

```text
D-01 ... unchanged / amended
...
D-16 ... unchanged / amended
```

Como mínimo deben aparecer corregidas:

```text
D-02
D-12
```

y ampliadas las secciones asociadas a:

```text
D-03/D-04
D-06
D-07
D-14
D-15
```

si los nuevos contratos de entidades/referencias lo requieren.

No renumerar D-01…D-16.

Registrar los cambios como:

```text
D-xx Amendment R2A
```

---

## 7. Actualizar Acceptance Criteria para R3

R3 debe poder validar que:

1. DR-R2-01…04 quedaron incorporados;
2. no quedan identidades V4.3 inventadas;
3. `PAR/CALL/UNRES` no se usan como identity key V5;
4. todos los campos de V4.3 tienen destino;
5. EvidenceReference ya no es ambiguo;
6. observabilidad quedó fuera de RUN_SUMMARY;
7. Option A de tests quedó fijada;
8. no existe conflicto restante entre D-01…D-16;
9. V5.1 puede empezar sin redefinir el normalized model.

---

# OUTPUT OBLIGATORIO

Crear únicamente:

```text
docs/V5/V5_0_R2A_CONTRACT_CORRECTIONS.md
```

Debe contener:

```text
STATUS
EXECUTIVE SUMMARY
APPROVED DECISION RECORDS
D-01..D-16 AMENDMENT MATRIX
IDENTITY CONTRACT CORRECTIONS
NORMALIZED EVIDENCE COMPLETION
OBSERVABILITY SIDECAR CONTRACT
EVIDENCE REFERENCE CONTRACT
TEST BASELINE DECISION
UPDATED ACCEPTANCE CRITERIA FOR R3
RISKS
DEFERRED ITEMS
FILES READ
FILES MODIFIED
```

---

# ESTADOS PERMITIDOS

Solo:

```text
V5_0_R2A_CONTRACT_CORRECTIONS_READY
V5_0_R2A_BLOCKED
```

---

# RESTRICCIONES

NO:

- modificar producción;
- modificar tests;
- modificar CLI;
- modificar providers;
- modificar PROJECT_STATE.json;
- implementar V5.1;
- crear evidence store;
- implementar templates;
- implementar cache;
- cambiar budgets;
- ejecutar IA real;
- ejecutar full IST;
- crear documentos auxiliares;
- iniciar R3.

---

# TESTS / COMANDOS

No repetir full IST.

No repetir suite completa.

Solo realizar lecturas o comprobaciones puntuales si hace falta confirmar una frase del contrato.

R2 ya contiene la evidencia empírica principal.

---

# NEXT STEP

Si queda:

```text
V5_0_R2A_CONTRACT_CORRECTIONS_READY
```

NO crear el prompt de R3 por cuenta propia.

Esperar revisión/aprobación humana.

---

# PRINCIPIO FINAL

```text
medir
→ descubrir conflicto
→ corregir contrato
→ validar arquitectura
→ implementar una vez
```
