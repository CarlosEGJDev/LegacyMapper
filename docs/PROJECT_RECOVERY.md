# LegacyMapper — Recuperación del proyecto

## Propósito

Este documento permite a un desarrollador o agente de IA en una máquina completamente nueva, sin historial
de conversación ni de sesión previa, clonar este repositorio y volverse plenamente productivo. El
repositorio es autoritativo; este documento no duplica el conocimiento del proyecto, señala dónde vive ese
conocimiento.

## Requisitos previos

* Python 3.x, solo biblioteca estándar. LegacyMapper tiene **cero dependencias de terceros** — no existe
  `requirements.txt`/`pyproject.toml` porque ninguno es necesario. No se requiere `pip install` para
  ejecutar los tests ni la herramienta.
* No se requieren herramientas externas, bases de datos ni servicios.
* Windows o cualquier SO con Python; el proyecto se ha desarrollado en Windows pero no contiene supuestos
  de tiempo de ejecución específicos del SO en su propia fuente.

## Clonación

```text
git clone https://github.com/CarlosEGJDev/LegacyMapper.git
cd LegacyMapper
```

## Configuración local

No se requiere ningún archivo de configuración local para ejecutar la suite de tests ni el comando
`readiness`. Nada en este repositorio requiere un archivo `.env` ni credenciales para el desarrollo normal.

La única ruta específica de la máquina es la ubicación del repositorio fuente legado (ver abajo); se pasa
como argumento de la CLI, nunca se almacena en un archivo confirmado (commit).

Nunca coloque credenciales, tokens ni cadenas de conexión en ningún archivo confirmado. `.gitignore` excluye
los archivos `.env*` como red de seguridad, pero ninguno existe actualmente ni se espera que exista.

## Fuente legada

El repositorio fuente legado (`C:\Users\cgalianj\source\IST_40\operacional` en la máquina del operador
actual) es:

* **opcional** para el desarrollo ordinario de V4 — el modo de ingesta de conocimiento
  `HUMAN_INFORMATION_ONLY` de V4 no lo requiere, y la suite completa de 676 tests se ejecuta enteramente
  contra fixtures y no lo toca;
* **requerido** solo para regenerar las salidas específicas de escaneo de repositorio completo históricas
  de V1/V2/V3 listadas abajo, o para ejecutar un escaneo nuevo de repositorio completo de esa aplicación
  legada en particular.

Si no tiene acceso a ese repositorio legado, aun así puede: ejecutar todos los tests, leer cada decisión y
resultado de V1–V4, y continuar el desarrollo desde `PROJECT_STATE.json` en adelante.

## Artefactos históricos pesados (excluidos de Git)

Los siguientes directorios están intencionalmente sin versionar (ver `.gitignore` y
`docs/GENERATED_ARTIFACT_POLICY.md`) porque son grandes (~8.2 GiB en conjunto), deterministas y
reproducibles:

| Artefacto | ¿Requerido para el desarrollo ordinario? | ¿Requerido para regenerar resultados antiguos? | Fuente | Comando |
|---|---|---|---|---|
| `output/v1_r1_full/` | No | Sí, para reproducir la ejecución completa de V1-R1 | repo fuente legado | `python main.py "<repo_legado>" --output "output/v1_r1_full" --verbose` |
| `output/v2_r4_full/`, `v2_r4_1_full/`, `v2_r4_1_repro_a/`, `v2_r4_1_repro_b/` | No | Sí, para reproducir las ejecuciones completas y de reproducibilidad de V2-R4/R4.1 | repo fuente legado | mismo patrón, sustituyendo `--output` |
| `output/v2_r5_full/`, `v2_r5_1_full/`, `v2_r5_1_repro/` | No | Sí, para reproducir las ejecuciones completas y de reproducibilidad de V2-R5/R5.1 | repo fuente legado | mismo patrón |
| `output/v3_r8_1/` | No | Sí, para reproducir el volcado crudo de análisis profundo de V3-R8.1 | repo fuente legado | mismo patrón; ver `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_ENGINE.md` para las instrucciones exactas de la ronda |
| `output/context/`, `output/documentation/`, `output/index/`, `output/v1_r1_internal/`, `output/v2_r4_1_internal/` | No | No — ejecuciones sobrantes de smoke-test, no referenciadas por ningún resultado canónico | cualquier fuente de muestra | `python main.py "<cualquier_fuente>" --output "<dir>"` |

Ninguno de estos directorios fue eliminado del disco por esta ronda; están excluidos únicamente de Git. Si
está recuperándose en una máquina que nunca los tuvo, un checkout limpio simplemente no los incluirá, y el
repositorio permanece totalmente funcional sin ellos.

Si el propio repositorio fuente legado no está disponible, estas salidas históricas específicas no pueden
regenerarse, pero nada en el desarrollo actual (V4) depende de eso.

**Excepción dentro de `output/v3_r8_1/`**: un archivo, `ARCHITECTURE_EVIDENCE.json` (~1.8 KiB), está
deliberadamente rastreado a pesar de la fila anterior — `legacy_documenter/knowledge/readiness.py` lo
requiere para la verificación `architecture_integrity`, y sin él `python main.py readiness` no puede tener
éxito en un clon nuevo. Contiene solo evidencia agregada pequeña de indicador estructural reproducida
textualmente del ya rastreado `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md` — no un volcado crudo
restaurado, y no regenerable por sí solo a partir de este repositorio. El resto de `output/v3_r8_1/`
permanece excluido según la tabla anterior; esto no es un precedente para rastrear ningún otro archivo en
ese directorio ni en `output/v2_r5_1_full/`. Ver
`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`.

## Verificación

Tras clonar, ejecute, en orden:

```text
python -m unittest discover -s tests
```

Esperado: **OK, 0 fallos, 0 errores** (baseline V5: 3100 tests, 132 skips explicados en un clon nuevo; ver `PROJECT_STATE.json` para el conteo autoritativo actual).

```text
python -m legacy_documenter.knowledge.readiness
```

Esperado: `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`,
`provider_calls=0`, `real_llm_calls=0`.

Si alguna de las dos verificaciones falla en un clon limpio, deténgase y repórtelo — no continúe con nuevo
desarrollo hasta que ambas pasen, según las reglas de control de fases de `AGENTS.md`.

## Estado actual (V5 CLOSED)

Empiece la recuperación por, en este orden:

1. `PROJECT_STATE.json` — autoridad operativa legible por máquina (estado, última ronda, `next`).
2. `docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md` — auditoría final, invariantes, baselines y deuda.
3. `docs/V5/V5_FINAL_BASELINE.json` — baseline de release (analyzer v3, fingerprint, IST, piloto Python).
4. `docs/V5/V5_OPERATIONS_GUIDE.md` — guía operativa mínima.
5. `docs/V5/V5_FINAL_CLOSURE.md` — recibo de cierre: commit final, verificación remota, tag `v5`.
6. `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md` y `LEGACYMAPPER_LESSONS_LEARNED.md` — historia, visión, lecciones.
7. `docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md` — iniciativa post-V5 (H1–H5, planificada).

Qué permite reconstruir:

* **Estado V5 y commit final:** `PROJECT_STATE.json` → `v5_final_production_commit`; recibo en `docs/V5/V5_FINAL_CLOSURE.json`.
* **Invariantes y contratos:** `docs/V5/V5_FINAL_INVARIANT_MATRIX.json`, `docs/V5/V5_FINAL_CONTRACT_MATRIX.json`.
* **Baselines:** IST (47523 archivos de salida, 0 diferencias) y piloto Python circular (`SELF_HOSTED_CIRCULAR`, sin claim de independencia externa) en `V5_FINAL_BASELINE.json`.
* **Deuda y trabajos post-V5:** `docs/V5/V5_FINAL_DEBT_LEDGER.json` (BLOCKING = 0) y `docs/V5/V5_FINAL_MAINTAINABILITY_INVENTORY.json`. Siguiente paso: `POST_V5_PLANNING`; no hay V6 iniciada.
* **Roadmap e historia:** `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`, `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`.

Histórico (V4/V3, conservado para compatibilidad y trazabilidad, no es el estado vigente):
`docs/V4/V4_AI_HANDOVER.md`, `docs/V4/V4_PROPOSED_ROADMAP.md`, `output/v3_final/V3_FINAL_BASELINE.json`.

## Descubrimiento del siguiente paso

Un nuevo agente de desarrollo lee, en orden:

1. `AGENTS.md` — reglas operativas, límite de permisos, control de fases.
2. `CLAUDE.md` — punto de entrada y orden de lectura.
3. `PROJECT_STATE.json` — estado y tarea declarada como `next`.
4. Los documentos V5 listados arriba.
5. El prompt activo bajo `prompts/V5/` (o `prompts/V4/` para historia V4), si existe; en caso contrario, la siguiente ronda se delimita con un nuevo prompt antes de implementar (`Do not automatically start the next round`).

No inicie trabajo post-V5 (incluida cualquier V6) sin un prompt explícito.
