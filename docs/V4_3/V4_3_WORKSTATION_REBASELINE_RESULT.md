# V4.3 — Workstation Rebaseline & Test Reconstruction — Resultado

## Estado de esta ronda

`V4_3_WORKSTATION_REBASELINE_READY`. Ronda exclusivamente de reconstrucción/reproducción/validación de
entorno. No se ejecutó `V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`. No se ejecutó R9. V4.3 no se
declara cerrada. No se invocó ningún provider real ni red en ningún momento de esta ronda
(`--allow-ai-interpretation` nunca se pasó).

## 1. Rutas vigentes

```text
LegacyMapper:        C:\dev\LegacyMapper
Legacy real (usado):  C:\inetpub\wwwroot\2010\IST\Operacional  (19075 archivos, verificado con find)
Legacy real (AGENTS.md, alterna): C:\Users\cgalianj\source\IST_40\operacional (también presente en este
  equipo; no fue necesario usarla porque la ruta indicada en el prompt de esta tarea existe y es legible)
Output reconstruido: C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline (nueva, no existía antes de esta
  tarea)
```

## 2. Commit / branch / status

```text
Branch:  main (up to date with origin/main)
HEAD:    e9e3d6063243073e65a93cbece97d6050184a0c6
         ("Record final commit/push verification in Spanish documentation approval result", 2026-09-16)
```

`git status` al inicio de la tarea mostraba 18 archivos modificados y ~28 archivos/directorios sin trackear
bajo `legacy_documenter/`, `tests/`, `tools/`, `prompts/V4_3/`, `docs/V4_3/` (trabajo V4.3 R0-R8 ya presente
en el working tree de este equipo, no generado por esta tarea). Verificado al final de esta tarea: esta
ronda **no modificó ningún archivo bajo `legacy_documenter/`, `tests/`, `tools/`, `PROJECT_STATE.json`** —
solo generó los archivos listados en la sección 13.

## 3. Versión Python / pip / herramientas

```text
Python:  3.14.7
pip:     26.2.1 (C:\Users\cgalianj\AppData\Local\Programs\Python\Python314\Lib\site-packages\pip)
where python: C:\Users\cgalianj\AppData\Local\Programs\Python\Python314\python.exe (+ WindowsApps shim)
where git:    C:\Program Files\Git\mingw64\bin\git.exe (+ cmd shim)
where gh:     no encontrado en PATH (no fue necesario: no se usó ninguna funcionalidad de `gh` en esta
              tarea)
```

`requirements-copilot.txt` existe (untracked). Contenido: declara `github-copilot-sdk>=1.0.14` como
dependencia opcional únicamente para el provider COPILOT real (`--allow-ai-interpretation` con COPILOT
configurado). No se instaló nada — no fue necesario para ningún test ni para el análisis determinista de
esta tarea.

## 4. `core.autocrlf`

```text
core.autocrlf = true
```

No se modificó durante esta tarea (restricción explícita de la sección 2 del prompt).

## 5. Inventario de artefactos

```text
output/            -- versionado: v3_final, v3_r7_2..v3_r10_1, v4_bootstrap, v4_r1..v4_r14,
                       v4_1_r0..v4_1_r10, v4_2_r8. NINGÚN output/v4_3_* versionado en el repo:
                       confirma que los outputs V4.3 (índices reales de 12642 flows, paquetes AI,
                       propuestas) siempre vivieron fuera del repositorio (política ya documentada en
                       V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md sección 8) y por tanto se perdieron
                       al cambiar de equipo -- exactamente el motivo de esta tarea.
docs/V4_3/          -- 19 documentos de resultado + prompt (R0-R8, correcciones, diagnóstico R3), + samples/
prompts/V4_3/       -- 17 archivos, incluyendo R0-R9, correcciones, y este mismo prompt de rebaseline.
tests/              -- 75 archivos de test, 11 de ellos V4.3-específicos (ver sección 7).
tools/              -- v4_3_ai_selection_diagnostic.py presente y funcional; también
                       v4_3_r7_build_output_manifest.py, v4_3_r7_build_pilot_distribution.py.
PROJECT_STATE.json  -- presente. current_version="V4.2", v4_2_closed=true (V4.3 aún no registrada como
                       cerrada ni en progreso en este archivo -- consistente con "no declarar V4.3
                       cerrada").
```

Confirmado específicamente:

- `tools/v4_3_ai_selection_diagnostic.py`: presente, funcional (usado en sección 10).
- `tests/test_v4_3_final_ai_pilot_r3_proposal_diversity_diagnostic.py`: presente, 12/12 OK.
- `prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`: presente, **no ejecutado** (congelado
  por restricción explícita de esta tarea).

## 6. Baseline de tests — primera ejecución completa

```text
python -m unittest discover -s tests
Ran 2148 tests in 116.315s
OK (skipped=132)
```

**0 failed, 0 errors, 0 fallos de hash/EOL** en esta ejecución. Los 132 skips están explicados: 80 requieren
`output/v2_r5_1_full/` y 52 requieren `output/v3_r8_1/` (dumps del repositorio real, no versionados,
regenerables solo desde el repositorio legacy real — ver `docs/PROJECT_RECOVERY.md`), consistente con
`PROJECT_STATE.json.all_skips_explained=true`.

Esto contrasta con la ronda anterior (`V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md`
sección 12), que reportó `failures=7, errors=3` — los 10 fallos de hash de bytes crudos contra
`output/v4_r12/`, `output/v4_r13/`, `output/v4_1_r4/` causados por representación CRLF de worktree vs. blob
LF grabado. **En este equipo, esos 10 fallos no se reprodujeron.**

## 7. Diagnóstico EOL/hash

No hubo fallos de hash que diagnosticar en este equipo (sección 6). Verificación igualmente realizada por
completitud, sobre los mismos archivos que fallaban en la ronda anterior:

```text
git ls-files --eol output/v3_final/V3_FINAL_BASELINE.json output/v4_2_r8/V4_2_FINAL_BASELINE.json \
  output/v4_2_r8/V4_2_FINAL_MANIFEST.json
-> i/lf  w/lf  attr/   (los tres: index LF, worktree LF -- sin normalización CRLF activa sobre estos
   archivos en este checkout, pese a core.autocrlf=true)
```

`git status --short` no reporta estos paths como sucios. Conclusión: en este equipo/checkout concreto no
hay discrepancia representación-vs-blob detectable en los archivos de baseline V4/V4.1 que causaron el
problema en el equipo anterior; por tanto **no fue necesario clasificar ningún FAIL como
`producto` vs. `worktree/autocrlf`** porque no hubo FAILs. No se tocó `core.autocrlf` ni ningún artefacto de
baseline. Si en una ejecución futura reaparecieran fallos de hash CRLF, la opción seria (documentada, no
aplicada) sería reconstruir el worktree con `git -c core.autocrlf=false checkout -- <paths>` sobre los
archivos de baseline únicamente, verificando primero que el blob Git ya sea LF (`git ls-files --eol`) para
no alterar contenido lógico versionado.

## 8. Tests V4.3 específicos

Ejecutados por separado los 11 módulos de test V4.3 (R2 hydration, R3 human documentation, R4 scaling, R5 AI
context budgeting, R6 AI/consumer projection, R7 internal acceptance, R8 external pilot corrections, Copilot
provider correction, proposal quality correction, R2 context budget correction, R3 proposal diversity
diagnostic):

```text
Ran 338 tests in 23.513s
OK -- 0 failed, 0 errors, 0 skipped
```

V4.3 queda **0 failed / 0 errors** en este equipo, cumpliendo el criterio de la sección 6 del prompt.

## 9. Output determinista reconstruido

```text
Comando: python main.py full "C:\inetpub\wwwroot\2010\IST\Operacional" \
  --output "C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline" --verbose
  (sin --allow-ai-interpretation)

status: SUCCESS
AI requested: False / AI invoked: False (ningún provider real contactado -- consistente con la restricción)
flow_count: 12642   (idéntico al histórico de referencia 12642)
path_count: 170020

Stages: SCAN..DOCUMENTATION todos SUCCESS; AI_INTERPRETATION/PROPOSAL_GENERATION: NOT_RUN (no solicitado);
  FINAL_SUMMARY: SUCCESS.

Output locations: documentation/, index/, ai_context/, consumer_projection/, RUN_SUMMARY.json,
  RUN_SUMMARY.md

output-manifest: 933 archivo(s), 1,701,890,708 bytes (~1.70 GB / 1.6 GiB) totales.
```

## 10. Validación de índices reconstruidos

```text
index/               22 archivos (functional_flows.json, functional_paths.json, data_access.json,
                      stored_procedures.json, sql_operations.json, entry_points.json, etc.) -- legibles.
ai_context/           5 archivos (SYSTEM_CONTEXT.json/.md, FUNCTIONAL_FLOWS.json, ARCHITECTURE_GRAPH.json,
                      TRACEABILITY.json) + AI_SELECTION_DIAGNOSTIC.json emitido por esta tarea (sección 11).
documentation/       18 archivos Markdown.
consumer_projection/ CONSUMER_PROJECTION.json + parts/.
```

`flow_count=12642` coincide exactamente con la referencia histórica -- no se detectó diferencia que
investigar; el árbol `C:\inetpub\wwwroot\2010\IST\Operacional` de este equipo produce el mismo conteo que el
repositorio usado en la ronda anterior. No se compararon hashes contra outputs externos perdidos (esos ya
no existen); solo se comparó esta métrica estructural conocida.

## 11. Diagnóstico R3 reproducido

```text
python -m tools.v4_3_ai_selection_diagnostic "C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline" \
  --emit-artifact

{
  "final_attempt_profile": "SMALL",
  "final_fits": true,
  "candidate_count": 80,
  "final_request_included_count": 6,
  "rich_in_final_request_count": 0,
  "rich_excluded_count": 40,
  "historical_flow_exists": true
}
```

Idéntico en estructura al resultado histórico (`prueba_01`/`prueba_02`): 80 candidatos seleccionados, 40
ricos (bucket 0/1) de ellos, 6 records finales (todos triviales bucket 2/3), 0 records ricos en el request
final, 40/40 ricos excluidos. `completeness=TRUNCATED`, `payload_estimated_tokens` muy por debajo del límite
(el gate final nunca se activa). **`DIAGNOSIS_A_SELECTION_PACKING` se reproduce exactamente en este
equipo.** Artefacto de diagnóstico completo escrito en
`C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline\ai_context\AI_SELECTION_DIAGNOSTIC.json` (no
contractual, opt-in).

## 12. Aclaración de la contradicción 9680 vs 16000

La ronda anterior afirmó simultáneamente "candidato rico más pequeño excluido = 9680 caracteres" y "100% de
los candidatos ricos individualmente exceden el presupuesto completo de 16000". Ambas afirmaciones no pueden
ser ciertas a la vez (9680 < 16000). Con los datos frescos reconstruidos en este equipo:

```text
Candidatos ricos (bucket 0/1) totales: 40
Tamaño mínimo real:                    9680 caracteres  (FLOW-0004993422)
Tamaño máximo real:                    161040 caracteres (FLOW-0017679388)

Ricos individualmente < 16000 (el budget COMPLETO de SMALL): 5 de 40 (12.5%)
  FLOW-0004993422   9680 chars
  FLOW-0005929194  11778 chars
  FLOW-0011096966  15352 chars
  FLOW-0006182693  15659 chars
  FLOW-0020041332  15795 chars
Ricos individualmente >= 16000: 35 de 40 (87.5%)
```

**La afirmación "100% de los candidatos ricos individualmente exceden el presupuesto completo" es falsa**,
verificado con datos reales y reproducibles: 5 candidatos ricos individualmente caben, por sí solos, dentro
del presupuesto de 16000 caracteres.

**Por qué esos 5 candidatos ricos, que individualmente caben, no entran de todas formas al paquete final**
(orden exacto de evaluación reconstruido replicando `AiProjectionBuilder.package` con instrumentación de
solo lectura, sin modificar la función productiva):

```text
idx  flow_id           bucket  chars   used_antes  cabe?  restante_antes
0    FLOW-0000543312    0     160197      0        NO       15311
1    FLOW-0000051656    2       2912      0        SI       15311   <- incluido
2    FLOW-0002725421    3       1809    2912        SI       12399   <- incluido
3    FLOW-0001317330    0      39604   4722        NO       10589
4    FLOW-0000262249    2       5100   4722        SI       10589   <- incluido
5    FLOW-0002807290    3       1769   9823        SI        5488   <- incluido
6    FLOW-0001510983    0     121859  11593        NO        3718
7    FLOW-0000502417    2       4232  11593        NO        3718
8    FLOW-0003405755    3       2075  11593        SI        3718   <- incluido
9    FLOW-0001810890    0     141596  13669        NO        1642
10   FLOW-0000533981    2       2889  13669        NO        1642
11   FLOW-0003482328    3       1667  13669        NO        1642
...
24   FLOW-0004993422    0       9680  13669        NO        1642   <- el "9680" histórico
...
36   FLOW-0005929194    0      11778  15303        NO           8
39   FLOW-0006182693    0      15659  15303        NO           8
64   FLOW-0011096966    0      15352  15303        NO           8
79   FLOW-0020041332    0      15795  15303        NO           8
TOTAL incluidos: 6, used final: 15303 (+ envelope 689 = 15992; character_count final del paquete: 16099,
  incluye el `package_id` calculado después del recorte)
```

Causa raíz precisa, en dos capas, ninguna sustituye a la otra:

1. **Capa 1 (outliers reales)**: 35 de 40 candidatos ricos exceden, cada uno por sí solo, el presupuesto
   completo de 16000 caracteres (84948-161040 caracteres, flows con 75-149 paths). Para estos, ningún orden
   de evaluación los habría incluido enteros bajo este presupuesto.
2. **Capa 2 (orden de evaluación + first-fit greedy, la parte que la ronda anterior no reportó)**: los otros
   5 candidatos ricos SÍ caben individualmente, pero `AiProjectionBuilder.package` itera en un único orden
   fijo (`_bucketed_order`: round-robin entre buckets 0/1/2/3, y dentro de cada bucket ordenado por
   `confidence` y luego `flow_id` ascendente -- **nunca por tamaño**). Los primeros elementos del bucket 0
   que aparecen en ese orden son enormes (160197, 39604, 121859, 141596 caracteres) y se descartan
   (`continue`) sin consumir presupuesto, pero mientras tanto los elementos pequeños de los buckets 2/3 que
   les tocan en cada ronda del round-robin SÍ se aceptan de inmediato (first-fit greedy, sin mirar hacia
   adelante). Para cuando el candidato rico de 9680 caracteres aparece (posición 24 de 80), el presupuesto ya
   tiene solo 1642 caracteres libres -- consumidos enteramente por 6 records triviales de 1633-5100
   caracteres aceptados en rondas anteriores. Los otros 4 candidatos ricos bajo budget (11778-15795
   caracteres) aparecen aún más tarde (posiciones 36-79) con apenas 8 caracteres libres. Ninguno de los 5
   fue nunca comparado contra "¿cabe mejor que lo ya aceptado?" -- el algoritmo es estrictamente
   incremental/irrevocable, sin reordenamiento por tamaño ni revisión posterior.

Conclusión: el defecto no es únicamente "todo rico es demasiado grande" (falso, 12.5% no lo es). Es que el
presupuesto se agota con records triviales aceptados antes, en el orden fijo de evaluación, de que el
packer llegue a los candidatos ricos de tamaño razonable -- un problema de **orden de evaluación / ausencia
de look-ahead en el first-fit greedy**, adicional al problema real de outliers de tamaño. Esta ronda **no
corrige el algoritmo** (fuera de alcance, restricción explícita); solo deja esta causa raíz precisa, con
evidencia real y reproducible, documentada para la ronda de corrección.

## 13. `FLOW-0343552547`

```text
exists: true
in_selected_candidates: false   (no fue de los 80 candidatos que select_flow_ids ofrece bajo SMALL en esta
                                  corrida -- su confidence="unresolved" lo ordena después de otros flows
                                  confirmed/inferred de su mismo bucket 0)
richness_bucket: 0
flow_confidence: unresolved
serialized_record_chars: 109866   (individualmente ~6.9x el budget completo de SMALL -- para este flow
                                    específico, la explicación de "outlier de tamaño" SÍ es correcta)
path_count: 94, evidence_ref_count: 153
has_stored_procedures: true (4), has_transactions: true (3), has_confirmed_write: false
```

Idéntico byte a byte en sus métricas al reportado en la ronda anterior (`docs/V4_3/
V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` sección 4): confirma que el repositorio
legacy real usado en este equipo (`C:\inetpub\wwwroot\2010\IST\Operacional`) produce exactamente el mismo
flow con la misma evidencia hidratada que el equipo anterior. Para este flow puntual, la afirmación "excede
individualmente el presupuesto completo" es correcta (109866 >> 16000) -- el error de la ronda anterior fue
generalizar esa propiedad al 100% de los 40 candidatos ricos, cuando en realidad aplica solo al 87.5%.

## 14. Archivos creados por esta tarea

```text
docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md                  -- este documento (repositorio)
prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION_R1.md -- prompt corregido (repositorio, ver
                                                                      sección 16; NO ejecutado)
C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline\               -- output determinista completo reconstruido
  (index/, ai_context/, documentation/, consumer_projection/, RUN_SUMMARY.json/.md, OUTPUT_MANIFEST.json,
  ai_context/AI_SELECTION_DIAGNOSTIC.json), externo al repositorio, ~1.70 GB, 933 archivos + manifiesto.
```

## 15. Archivos modificados por esta tarea

```text
Ninguno. Esta tarea no modificó ningún archivo bajo legacy_documenter/, tests/, tools/, PROJECT_STATE.json,
ni ningún artefacto de baseline V4/V4.1/V4.2 versionado. Los 18 archivos "modified" y ~28 "untracked" que
git status ya mostraba al inicio de esta tarea (trabajo V4.3 R0-R8 preexistente en este working tree) no
fueron tocados por esta ronda.
```

## 16. Runtime Independence

PASS. `tools/v4_3_ai_selection_diagnostic.py` (sin modificar por esta tarea) no importa
`legacy_documenter.llm.providers.copilot`, `ProviderRegistry` ni `_resolve_provider`; no abre sockets; no lee
variables `LEGACYMAPPER_LLM_*`. El único acceso a disco de escritura de esta tarea, aparte del propio output
determinista bajo `--output`, fue el artefacto opcional `ai_context/AI_SELECTION_DIAGNOSTIC.json` bajo el
mismo `output_dir` externo (vía `--emit-artifact`), y el script de instrumentación de solo lectura de la
sección 12 (ejecutado inline, no persistido como archivo del repositorio). `python main.py full` se ejecutó
sin `--allow-ai-interpretation`; `AI_INTERPRETATION`/`PROPOSAL_GENERATION` quedaron `NOT_RUN`. Cero llamadas
a provider, cero acceso a red, en toda la tarea.

## 17. Restricciones

PASS. No se ejecutó `V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`. No se ejecutó R9. V4.3 no se declara
cerrada. No se llamó a Copilot/LLM real. No se cambiaron budgets, selector, hydration, prompts runtime de
IA, provider, ni lógica de confidence -- ningún problema de entorno reproducible que ameritara excepción fue
encontrado (sección 7: 0 fallos de hash en este equipo). No se modificaron outputs cerrados V4/V4.1 ni se
actualizaron hashes grabados. No se tocó V5 ni Plugin Runtime. No se cambió `core.autocrlf`.

## 18. Conclusión sobre el prompt R3A vigente

`prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md` (versión original, sin ejecutar):
**NEEDS_REVISION**. Su objetivo (sección 2), sus invariantes obligatorios (sección 2 items 1-4), sus
restricciones (sección 5) y su clasificación de causa raíz macro (`DIAGNOSIS_A_SELECTION_PACKING`, "0 records
ricos llegan al request final") siguen siendo **válidos y reproducidos** en este equipo. Pero su premisa
numérica de la sección 1 ("candidato rico MÁS PEQUEÑO excluido: 9680 caracteres (> 60% del budget COMPLETO
de SMALL=16000)" junto con "el 100% de los candidatos ricos individualmente exceden el presupuesto total")
es **internamente inconsistente y parcialmente falsa** (sección 12 de este documento): 5 de 40 candidatos
ricos (12.5%) individualmente caben bajo el presupuesto completo y aun así quedan excluidos, no por tamaño
individual sino por el orden fijo de evaluación (`_bucketed_order` sin ordenar por tamaño) combinado con
first-fit greedy sin look-ahead. Esto es información nueva y relevante para el diseño de la corrección: la
dirección "priorizar records ricos medianos que sí quepan individualmente" (sección 3 del R3A original, ya
sugerida como una de las direcciones a evaluar) es exactamente la que esta ronda demuestra que hace falta,
con evidencia concreta de qué candidatos (9680-15795 caracteres) se beneficiarían de ese cambio de orden. Se
crea `prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION_R1.md` como reemplazo corregido (sección
16), no ejecutado en esta tarea.
