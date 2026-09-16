# LegacyMapper — Política de artefactos generados

## Propósito

Define cómo se clasifica la salida generada a efectos de versionado en Git. Complementa
`docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md` (qué debe permanecer versionado) y `.gitignore` (la
aplicación mecánica). Clasificación completa por ruta:
`output/v4_r1_1/V4_REPOSITORY_INVENTORY.json` y `output/v4_r1_1/V4_LARGE_ARTIFACT_ANALYSIS.json`.

El significado y la recuperabilidad deciden la disposición, no el tamaño del archivo por sí solo.

## Artefactos pequeños canónicos — versionados

Evidencia pequeña, significativa, no reproducible por azar, de que una ronda ocurrió y qué concluyó.
Ejemplos presentes en este repositorio:

* `output/v3_final/V3_FINAL_BASELINE.json` — la baseline de V3.
* `output/v3_r9/*` — salidas de la puerta de preparación de conocimiento, referenciadas por hash desde la
  baseline.
* `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` — referenciado por hash desde la baseline.
* `output/v3_r10/`, `output/v3_r7_2/`, `output/v3_r8_2/`, `output/v3_r8_3/` — artefactos de evidencia
  pequeños (cada uno muy por debajo de 1 MiB) que respaldan la narrativa de cierre de V3.
* `output/v4_bootstrap/`, `output/v4_r1/`, `output/v4_r1_1/` — resultados de ronda de V4.
* `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` — documentación APROBADA.

Regla: si un documento en cualquier otro lugar del repositorio (una baseline, un registro de cierre, un
resultado de ronda) apunta al artefacto por ruta o hash, este es canónico y se versiona sin importar que
haya sido generado.

## Artefactos pesados regenerables — no versionados

Salida determinista de escanear el repositorio fuente legado, reproducible a demanda y no referenciada por
ninguna baseline canónica ni registro de cierre:

* `output/v1_r1_full/`, `output/v2_r4_full/`, `output/v2_r4_1_full/`, `output/v2_r4_1_repro_a/`,
  `output/v2_r4_1_repro_b/`, `output/v2_r5_full/`, `output/v2_r5_1_full/`, `output/v2_r5_1_repro/`,
  `output/v3_r8_1/` — volcados de escaneo de repositorio completo y de verificación de reproducibilidad,
  en conjunto ~8.2 GiB.

Procedimiento de regeneración (requiere acceso de lectura a la fuente legada, según `AGENTS.md`):

```text
python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "<directorio-destino>" --verbose
```

Cada uno de estos artefactos debe tener, cuando existe en disco: origen documentado (qué ronda lo produjo),
un comando de regeneración, y — solo donde un documento posterior dependa de su contenido exacto — un hash
esperado. Ninguno de los nueve directorios anteriores tiene una dependencia por hash desde ningún documento
retenido, por lo que no se registra ningún hash para ellos.

**Excepción estrecha y rastreada — `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`.** A pesar de que
`output/v3_r8_1/` se clasifica arriba como un volcado pesado regenerable, este único archivo de ~1.8 KiB
dentro de él está deliberadamente rastreado (una excepción en `.gitignore`: `/output/v3_r8_1/*` más
`!/output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`), porque la verificación `architecture_integrity` de
`legacy_documenter/knowledge/readiness.py`'s lo requiere de forma estricta y, sin él, `python main.py
readiness` no puede tener éxito en un clon nuevo. Contiene solo cuatro conteos agregados estructurales de
`DETERMINISTIC_INDICATORS` y una conclusión de arquitectura fija — sin código fuente, rutas fuente,
credenciales, ni PII — reproducido textualmente del ya rastreado y aprobado por humanos
`codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`. **No** es independientemente regenerable a partir de
este repositorio solo (sus valores originales dependieron de un escaneo real del repositorio legado) y
**no** es un precedente para rastrear ningún otro archivo bajo `output/v3_r8_1/` ni ningún otro volcado de
escaneo completo histórico (`output/v2_r5_1_full/` incluido) — el resto de cada uno de esos directorios
permanece completamente excluido. Ver
`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md` para la justificación completa.

También en esta categoría: pequeñas salidas sobrantes de smoke-test run no vinculadas a ningún resultado de
ronda — `output/context/`, `output/documentation/`, `output/index/`, `output/v1_r1_internal/`,
`output/v2_r4_1_internal/`. Estas son regenerables reejecutando la herramienta contra cualquier fuente de
muestra y no llevan información única.

## Salida operacional de sistema real

Los resultados generados al ejecutar LegacyMapper contra un sistema legado real concreto (un piloto, un
análisis ad-hoc, un compromiso con un cliente) son salida operacional, no fuente del proyecto. Deben
permanecer locales y nunca deben confirmarse (commit), sin importar el tamaño:

* `output/v4_2_r7_ist_operacional/` — la ejecución del piloto real de IST de V4.2-R7. Excluida mediante una
  regla de ruta explícita en `.gitignore`. Sus hallazgos destilados (lo que importó para la historia del
  proyecto) están capturados en documentos de resultado rastreados y en el fixture sintético
  `tests/test_v4_2_r7_synthetic_full_fixture.py`, no en la salida operacional cruda misma.

Convención para futuras ejecuciones de sistema real:

* preferir la convención de nomenclatura de salida local existente, `output/_local_<nombre-descriptivo>/`,
  ya cubierta por la regla genérica de `.gitignore` `/output/_local_*/` — no se necesita editar
  `.gitignore`;
* si en su lugar se requiere un directorio con nombre formal, añadir la regla de ruta explícita
  correspondiente en `.gitignore` en el mismo cambio que crea el directorio;
* nunca resolver esto ignorando globalmente `output/` — este directorio también contiene contratos,
  baselines y manifiestos rastreados (ver "Artefactos pequeños canónicos" arriba);
* todo lo que de una ejecución de sistema real importe para la historia del proyecto debe destilarse en
  documentación pequeña rastreada, tests o fixtures sintéticos antes de descartar la salida operacional
  cruda.

## Artefactos pesados no regenerables

Actualmente ninguno existe en este repositorio. Si una ronda futura produce datos pesados que no puedan
regenerarse deterministamente (por ejemplo, un corpus suministrado por un humano una sola vez, una
exportación de un sistema externo), debe clasificarse aquí antes de excluirse de Git, y debe elegirse y
documentarse uno de los siguientes mecanismos:

* archivo externo (una ubicación fuera de Git, referenciada por ruta/URL en el documento de resultado de la
  ronda correspondiente);
* activo de GitHub Release;
* Git LFS;
* almacenamiento seguro, si el contenido es sensible.

Esta ronda no sube nada externamente y no configura Git LFS. Si esta categoría alguna vez deja de estar
vacía, el versionado del repositorio no debe avanzar hacia `DECISION=REPOSITORY_READY_FOR_GIT_VERSIONING`
hasta que el Líder Técnico elija un mecanismo.

## Cachés de Python / herramientas

`__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `*.pyc` — siempre regenerados por el
intérprete/las herramientas en la siguiente ejecución. Nunca versionados, nunca archivados.

## Directorios vacíos esperados en tiempo de ejecución

`context/` es creado y poblado en tiempo de ejecución por `context/context_builder.py` y está vacío en un
checkout limpio. Se mantiene presente mediante `context/.gitkeep`; su contenido generado nunca se versiona.

## Idioma de la documentación para humanos

A partir de la ronda `POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION`, toda la documentación nueva o
mantenida destinada principalmente a lectores humanos debe redactarse en español. Esto incluye, como
mínimo, manuales de usuario, manuales técnicos, glosarios, documentos de arquitectura y de roadmap
destinados a revisión humana, guías operativas, guías de recuperación, documentos de resultado/revisión de
cara al humano, y documentos de gobernanza/capacitación.

Los identificadores técnicos, el código, los comandos, los estados legibles por máquina, los nombres de
contrato, las rutas, los nombres de protocolo y los nombres oficiales de tecnología/producto permanecen en
su forma original — nunca se traducen. El texto explicativo que los rodea debe estar en español.

`PROJECT_STATE.json`, `AGENTS.md` y `CLAUDE.md` no están sujetos automáticamente a esta regla; su idioma se
decide caso por caso según su propia naturaleza (contrato legible por máquina, o gobernanza neutral al
agente que ya funciona correctamente en inglés). Los documentos históricos de cierre/resultado no se
traducen retroactivamente — permanecen como evidencia histórica en el idioma en que fueron aprobados.
