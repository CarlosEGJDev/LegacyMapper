# LegacyMapper V4.3 — Instrucciones de piloto externo real

Entregable obligatorio de `prompts/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE.md`. Este documento es para quien
**ejecuta** el piloto externo real (contra un repositorio legacy real, fuera de este repositorio de
desarrollo), no para quien desarrolla LegacyMapper. Ver
`docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md` para la verificación interna que precede a este piloto.

## 0. Regla que gobierna todo este documento

**Ningún dato real, ninguna salida generada a partir de un repositorio legacy real, y ningún script del
entorno del piloto (`C:\PruebasLegacyMapper` u otro) se incorpora jamás a este repositorio de desarrollo de
LegacyMapper.** Solo los *hallazgos* de un piloto (defectos, mejoras, requisitos) se convierten en requisitos
o criterios de aceptación para una ronda futura (`V4_3_R8_EXTERNAL_PILOT_CORRECTIONS.md`, si aplica) — nunca
los datos ni las salidas del sistema analizado. Esta regla ya está declarada en `README.md` de este
repositorio y se repite aquí para quien solo lee este documento.

## 1. Qué es LegacyMapper en este punto (V4.3, tras R7)

Analiza estáticamente un repositorio de código VB.NET/ASP.NET (Web Forms) y produce, de forma determinista
(sin IA por defecto):

- índices exhaustivos (`index/*.json`) y contexto compacto (`ai_context/*.json`);
- documentación técnica determinista en `documentation/`, **en español por defecto** (corrección de esta misma
  ronda, BLOQUEO 2 — ver `docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md`): `PROJECT_OVERVIEW.md`,
  `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`, `WEB_ENTRY_POINTS.md`,
  `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`, `CONFIGURATION_SUMMARY.md`,
  `ANALYSIS_WARNINGS.md` y `README.md` son todos prosa/encabezados en español; identificadores, paths,
  comandos, nombres de tipos, campos JSON y valores de status (p. ej. `confirmed`/`unresolved`) nunca se
  traducen. Junto a esto, **documentación humana en español** por flujo
  (`documentation/HUMAN_DOCUMENTATION.md` + `documentation/flujos_humanos/`, V4.3-R3/R4/R7);
- `RUN_SUMMARY.md` en español por defecto (misma corrección, BLOQUEO 2 — sección 4 abajo); `RUN_SUMMARY.json`,
  el contrato machine-readable equivalente, sin cambios;
- una proyección de consumidor estable y particionada (`consumer_projection/`, V4.3-R6);
- opcionalmente (solo con `--allow-ai-interpretation`), una interpretación de IA acotada por presupuesto real
  sobre esa misma evidencia, nunca sustituyendo hechos deterministas, y propuestas
  `PENDING_TECHNICAL_LEAD_REVIEW` (nunca aprobadas automáticamente).

`Plugin Runtime` no está implementado. `consumer_projection` es una proyección JSON estable pensada para un
futuro consumidor, no un mecanismo de plugin en ejecución.

## 2. Requisitos del entorno del piloto

- Python 3.10+ (sin dependencias de terceros para el análisis determinista: solo librería estándar).
- Acceso de solo lectura al repositorio legacy real a analizar. **LegacyMapper nunca escribe, renombra ni
  elimina nada en el repositorio fuente** (`AGENTS.md`, "Legacy Source Repository": "Legacy source is
  READ-ONLY").
- Espacio en disco suficiente para el `--output`: para un repositorio grande (miles de flujos), el árbol de
  salida puede alcanzar cientos de MB — nada de esto se incorpora nunca a este repositorio de desarrollo.
- Si se va a usar `--allow-ai-interpretation` con un proveedor real: credenciales/configuración de ese
  proveedor ya disponibles en el entorno del piloto (nunca en este repositorio de desarrollo, y nunca en
  ningún artefacto que se comparta de vuelta).

## 3. Obtener una copia limpia de LegacyMapper (sin docs/prompts/tests/histórico)

Desde un clon de este repositorio de desarrollo (o desde el propio checkout que ya tiene el Líder Técnico),
generar una distribución limpia, runtime-only:

```
python -m tools.v4_3_r7_build_pilot_distribution <destino>
```

`<destino>` debe estar vacío o no existir todavía. Esto copia únicamente `main.py` y el paquete
`legacy_documenter/` — nada de `docs/`, `prompts/`, `tests/`, `codex/`, `output/`, `result_codex/`, `tools/`,
`README.md`, `AGENTS.md`, `CLAUDE.md`, ni `PROJECT_STATE.json`. Verificado (V4.3-R7): `legacy_documenter/` no
tiene ninguna dependencia de terceros para el análisis determinista (solo librería estándar; el único paquete
opcional, `copilot`, se importa perezosamente solo si de verdad se llama a un proveedor Copilot real).

Esta copia es la que se traslada al entorno del piloto — nunca el repositorio de desarrollo completo.

## 4. Ejecutar el análisis determinista (sin IA)

Desde dentro de la copia limpia:

```
cd <destino>
python main.py full "<ruta al repositorio legacy real>" --output "<directorio de salida>" --verbose
```

- `full` ejecuta las nueve etapas deterministas (`SCAN` → … → `CONTEXT` → `DOCUMENTATION`) siempre, sin
  necesidad de ningún flag adicional.
- Nunca contacta ningún proveedor de IA a menos que se pase `--allow-ai-interpretation` explícitamente
  (sección 6).
- Código de salida: `0` = `SUCCESS`, `1` = `PARTIAL`, `2` = uso incorrecto de la CLI, `4` = `FAILED` — el
  mismo contrato ya vigente desde V4.2-R5.1, sin cambios en V4.3.

### 4.1 Qué esperar bajo `<directorio de salida>`

| Ruta | Contenido | Cuándo aparece |
|---|---|---|
| `index/*.json` | Evidencia exhaustiva, machine-readable | `EXPORT` exitoso |
| `documentation/*.md` (README, WEB_ENTRY_POINTS, FUNCTIONAL_FLOWS, DATABASE_ACCESS, UNRESOLVED_FINDINGS, PROJECT_DEPENDENCIES, WEBFORMS_MAP, CONFIGURATION_SUMMARY, ANALYSIS_WARNINGS) | Documentación técnica determinista, **en español por defecto** (corrección de esta ronda, BLOQUEO 2), particionada a escala; identificadores/paths/campos JSON/valores de status nunca traducidos | `EXPORT`/`DOCUMENTATION` exitosos |
| `documentation/HUMAN_DOCUMENTATION.md` + `documentation/flujos_humanos/*.md` | Documentación humana en español, por flujo, particionada por WebForm/módulo (V4.3-R3/R4/R7) | `DOCUMENTATION` exitoso |
| `ai_context/*.json` | Contexto compacto para consumo por IA (uso interno, opt-in) | `CONTEXT` exitoso |
| `consumer_projection/CONSUMER_PROJECTION.json` | Manifest estable, pequeño: qué particiones existen, sus ids/hashes, estadísticas globales | `CONTEXT` exitoso |
| `consumer_projection/parts/part-NNNNNN.json` | Evidencia hidratada completa, particionada, autocontenida (ninguna partición depende de otra) | `CONTEXT` exitoso |
| `RUN_SUMMARY.json` | Resumen de la corrida, machine-readable: estado de cada etapa, `output_locations`, próxima acción. Contrato sin cambios | Siempre, al final |
| `RUN_SUMMARY.md` | El mismo resumen, human-readable, **en español por defecto** (corrección de esta ronda, BLOQUEO 2): prosa/encabezados en español; `StageId`/nombres de stage, statuses (`SUCCESS`/`PARTIAL`/`FAILED`/etc.), códigos/mensajes de error, paths y nombres de archivo nunca traducidos | Siempre, al final |

Para verificar exactamente qué se produjo, con tamaño y hash de cada archivo (útil para entregar evidencia de
la corrida sin reenviar el árbol completo, o para detectar una modificación posterior):

```
python main.py output-manifest "<directorio de salida>"
```

`output-manifest` es un subcomando de `legacy_documenter.cli` (no un script de `tools/`): vive dentro del
paquete `legacy_documenter/` que la distribución limpia del paso 3 ya copió, así que está disponible **desde
esa misma copia limpia**, sin volver nunca al repositorio de desarrollo ni depender de `tools/` (que la
distribución limpia excluye deliberadamente — ver sección 3). Esto corrige una inconsistencia detectada durante
la aceptación interna de esta ronda: una versión anterior de este documento instruía ejecutar
`python -m tools.v4_3_r7_build_output_manifest`, un script que en efecto no está disponible dentro de la
distribución limpia porque `tools/` nunca se copia — ver
`docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md` BLOQUEO 1 para el detalle de la corrección.
`tools/v4_3_r7_build_output_manifest.py` sigue existiendo, sin cambios, como una conveniencia equivalente para
quien trabaja directamente dentro del repositorio de desarrollo (no dentro de una distribución limpia) — ambas
vías llaman a la misma lógica determinista
(`legacy_documenter.cli.output_manifest.build_output_manifest`), nunca duplicada.

Esto escribe `<directorio de salida>/OUTPUT_MANIFEST.json`. **Este archivo, y todo lo demás bajo
`<directorio de salida>`, es evidencia local del piloto — no se sube a este repositorio de desarrollo** (regla
0).

## 5. Verificar el resultado antes de continuar

- `RUN_SUMMARY.json.status` debe ser `SUCCESS` (ideal) o `PARTIAL` (aceptable: algún hallazgo/etapa incompleta,
  ver `RUN_SUMMARY.md` para el detalle) — `FAILED` significa que ni siquiera se produjo un paquete de análisis
  mínimamente útil; en ese caso, revisar `RUN_SUMMARY.md`/consola antes de continuar.
- `documentation/HUMAN_DOCUMENTATION.md` debe listar al menos un grupo de flujos si el repositorio real tiene
  al menos un flujo funcional resuelto (WebForm → evento → lógica → dato). Si el repositorio real no produce
  ningún flujo (`0 flujo(s) hidratado(s)`), esto es en sí mismo un hallazgo a reportar (sección 7), no un
  fallo esperado a asumir sin más.
- `consumer_projection/CONSUMER_PROJECTION.json.statistics.completeness` debe ser siempre `"COMPLETE"` —
  nunca `"TRUNCATED"` ni `"BUDGET_INSUFFICIENT"` (esa superficie nunca omite evidencia; si ese campo no dice
  `COMPLETE`, es un defecto a reportar, no un límite esperado).
- Con miles de flujos reales, `consumer_projection/parts/` puede contener docenas de archivos — esto es
  particionado determinista funcionando como se diseñó (V4.3-R6), no un error.

## 6. Interpretación de IA (opcional, opt-in explícito)

Por defecto, `full` **nunca** contacta ningún proveedor de IA. Para habilitarlo:

```
python main.py full "<repositorio>" --output "<salida>" --allow-ai-interpretation
```

- Esto solo se ejecuta si `CONTEXT` tuvo éxito, y solo genera hallazgos (`AI_INTERPRETATION`) y propuestas
  (`PROPOSAL_GENERATION`) — nunca modifica ni sustituye la documentación determinista ya escrita, y un fallo
  aquí (`AI_INTERPRETATION: FAILED`) nunca invalida `documentation/`, `consumer_projection/`, ni ningún otro
  artefacto determinista (verificado conductualmente en V4.3-R6/R7).
- Toda propuesta generada queda en `proposals/AI_PROPOSALS.json` con estado
  `PENDING_TECHNICAL_LEAD_REVIEW` — **nunca aprobada automáticamente**. Solo una decisión humana explícita del
  Líder Técnico (fuera del alcance de este documento) puede aprobar, rechazar o corregir una propuesta.
- Este flag requiere que el proveedor real (credenciales, configuración) ya esté disponible en el entorno del
  piloto — nunca en este repositorio de desarrollo.
- **No usar `python main.py full ... --allow-ai-interpretation` para verificar que el camino de IA "funciona"
  sin haber configurado deliberadamente un proveedor real primero**: si ningún proveedor está inyectado, esa
  invocación intentará resolver uno real a través de `ProviderRegistry`, tal como debe hacerlo en uso de
  producción autorizado — esto solo es relevante si el operador del piloto no pretendía todavía hacer una
  llamada real a un proveedor de IA en ese momento.

## 7. Reportar hallazgos de vuelta al desarrollo

Un hallazgo del piloto (un defecto, una limitación de escala, un caso no cubierto) se documenta como
**hallazgo**, nunca acompañado de los datos ni las salidas reales que lo revelaron:

- describir el síntoma (ej. "`HUMAN_DOCUMENTATION.md` reporta 0 grupos aunque `FUNCTIONAL_FLOWS.md` lista
  120 flujos");
- si es posible, reproducirlo con datos sintéticos equivalentes (nunca con el fragmento real) para que pueda
  convertirse en un test comprometible al repositorio;
- referenciar el `RUN_SUMMARY.json`/`OUTPUT_MANIFEST.json` de esa corrida como evidencia local del piloto, sin
  adjuntarlos al reporte que sí se incorpora a este repositorio.

Estos hallazgos son la entrada a una eventual `V4_3_R8_EXTERNAL_PILOT_CORRECTIONS.md`, si el Líder Técnico
decide que se necesita esa ronda.

## 8. Qué NO hacer

- No copiar ningún archivo bajo `<directorio de salida>` a este repositorio de desarrollo (ni a `output/`, ni
  a `docs/`, ni a ningún otro lugar) — es evidencia local del piloto, no un artefacto de desarrollo.
- No modificar el repositorio legacy real bajo ningún concepto (LegacyMapper nunca lo necesita: es
  exclusivamente de lectura).
- No comprometer credenciales, cadenas de conexión, ni ningún valor sensible descubierto durante el análisis:
  el sanitizador centralizado de LegacyMapper (`legacy_documenter.utils.sanitize_data`/`sanitize_text`) ya
  protege los artefactos que el propio LegacyMapper escribe, pero esta regla sigue aplicando a cualquier nota
  u observación que el operador del piloto redacte a mano.
- No asumir que un `full` exitoso implica que las propuestas de IA (si se generaron) ya están aprobadas — no
  lo están, nunca automáticamente.
