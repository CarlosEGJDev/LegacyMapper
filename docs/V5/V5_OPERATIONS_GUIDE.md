# LegacyMapper V5 — Guía operativa mínima

Esta guía describe solo comandos y comportamientos verificados en V5 Closure R1 (`python main.py --help`, subcomandos y la suite). No hay CLI para los consumers: se usan como API Python.

## 0. Cuatro cosas que nunca se mezclan

```text
Evidence determinista  → lo produce Python (analyze / full). Es la verdad observada.
Propuesta de IA        → opt-in; siempre «pendiente de revisión»; nunca verdad.
Decisión humana        → APPROVE / REJECT / CORRECT / DEFER, con revisor explícito.
Conocimiento canónico  → solo nace de APPROVE o CORRECT humanos; nunca automático.
```

## 1. Analizar un repositorio

```text
python main.py analyze <repo> --output <dir>          # análisis determinista (index/, evidence/, ai_context/…)
python main.py full    <repo> --output <dir>          # lo anterior + documentación + RUN_SUMMARY (recomendado)
python main.py <repo> --output <dir>                   # atajo heredado de `analyze`
```

Opciones comunes: `--exclude <carpeta>` (repetible, por nombre de carpeta), `--flow-max-depth N` (12 por defecto), `--verbose`, `--repository-id <nombre>`. `full` añade `--long-paths` (Windows, rutas > 260), `--cache-mode {auto,off,refresh}`, `--cache-dir`, `--verify-cache`, `--trust-mtime` (inseguro, opt-in), `--incremental-max-changed-ratio`.

- **IST / VB.NET WebForms-Oracle:** el comportamiento por defecto (adapter `vbnet-webforms-oracle` 1.0, seleccionado por los tipos de archivo observados). Sin `--repository-id`, los ids son los de V5.1.
- **Python:** el adapter `python-generic` 1.0 se selecciona solo cuando el repositorio contiene archivos `.py` y ningún tipo VB/WebForms. Un repositorio mixto (VB + Python) falla con «ambiguo»; use `--exclude` para separar (p. ej. carpetas de fixtures).
- **`--repository-id`:** nombre lógico (no una ruta; solo `[A-Za-z0-9._:-]`, hasta 128 caracteres). Si lo declara, los `SourceArtifact` quedan namespaced por ese nombre y dos repositorios con las mismas rutas relativas nunca comparten ids. **Recomendado siempre que compare o junte evidencia de repositorios distintos.** Es opcional; sin declarar, el espacio es el heredado V5.1.
- El análisis es estático: **no** ejecuta, importa ni compila el código analizado, no usa red y no escribe en el repositorio fuente.

## 2. Documentación humana

`full` genera `<output>/documentation_v52/` (perfiles `general/` = `human-functional` y `developer/` = `human-technical`) y `<output>/ai_context/`. Los mismos templates y renderer sirven a toda tecnología; el vocabulario por tecnología es un overlay de datos. `<output>/documentation/` es el árbol histórico (V3/V4). Un template cambia la presentación, nunca la evidencia.

## 3. Incremental / cache

Por defecto `--cache-mode auto`: la cache vive en `<output>/_cache_v53`; si la corrida anterior es compatible reutiliza la extracción de los archivos sin cambios (una segunda corrida sin cambios produce exactamente la misma salida; un cambio de un archivo re-extrae solo ese). Se invalida sola ante cambios del código del analizador (fingerprint), de opciones de análisis o del contrato. `--cache-mode off` ignora la cache; `refresh` la reconstruye. Todas las etapas posteriores a la extracción se recalculan siempre (el scope incremental informa y puede decir `mode=full` para cambios de código: es conservador, no un error). Use un `--output` por repositorio.

## 4. IA: cómo activarla con seguridad

Por defecto **no hay llamadas a IA ni a providers**. `--allow-ai-interpretation` (solo con `full`) añade un paso de interpretación sobre la evidencia de esa corrida y puede contactar al provider configurado (hoy Copilot local). Las propuestas se escriben en `<output>/proposals/` con estado `READY_FOR_REVIEW` y envelope `PENDING_TECHNICAL_LEAD_REVIEW`; nada se aprueba ni se vuelve canónico. Para probar el camino con IA sin riesgo, use `python -m tools.manual_verify_full_pipeline <repo> --output <dir> --allow-ai-interpretation`, que inyecta un provider Fake y no puede alcanzar uno real. Un flujo demasiado grande para la ventana del provider se segmenta (cada segmento es `partial=true` con `parent_flow_id`, `segment_id`, `included_paths`, `omitted_paths`, `evidence_refs`); si ni un segmento cabe, falla con error explícito, nunca se trunca en silencio.

## 5. Revisión y conocimiento canónico

```text
python main.py review list      --output <dir>
python main.py review prepare   --output <dir> --reviewer "<persona>" [--proposal PRP-…]
python main.py review decide    --output <dir> --proposal PRP-… --action {APPROVE,REJECT,CORRECT,DEFER} --reviewer "<persona>" [--rationale …] [--correction-file x.json] [--expected-evidence-fingerprint …]
python main.py review canonical --output <dir> [--id CAN-… [--chain] | --proposal PRP-… | --evidence-ref …]
```

- `prepare` fija el **baseline** (huella de la propuesta + huella de la evidencia que cita); es obligatorio antes de la primera decisión. El baseline demuestra estabilidad **entre `prepare` y la decisión**; las propuestas no llevan evidencia de generación, así que no se afirma inmutabilidad desde que la IA las generó.
- Si la evidencia cambia después de `prepare`, la decisión falla con `PROPOSAL_STALE` y no se escribe nada. Una propuesta alterada falla `PROPOSAL_TAMPERED`.
- `--reviewer` es obligatorio, sin valor por defecto; rechaza nombres automáticos (`AUTO`, `system`, `ai`, `llm`, el provider o modelo de la propuesta).
- APPROVE/CORRECT crean un registro canónico (`knowledge/canonical/CAN-*.json`) con cadena de auditoría (canónico → decisión → snapshot de la propuesta → baseline → evidencia); REJECT y DEFER nunca crean canónico. Un `full` posterior no borra `knowledge/`.

## 6. Cómo leen los consumidores

La facade `legacy_documenter.consumers.facade.ConsumerFacade(<output>, registry=None).handle(<request dict>)` (Python; **no hay comando de CLI**) es de solo lectura y devuelve un `ConsumerResult` versionado (contrato 1.0). Capabilities: `READ_EVIDENCE`, `READ_FLOW`, `READ_PARTIAL_FLOW`, `READ_AI_CONTEXT`, `READ_CANONICAL`, `READ_REVIEW_HISTORY`, `RENDER_HUMAN_DOC` (`human-functional` / `human-technical`), `EXPORT_JSON`. La salida es determinista (mismo request + mismos artifacts → mismos bytes); los errores son códigos contractuales (`ENTITY_NOT_FOUND`, `PARTIAL_NOT_SUPPORTED`, `READ_ONLY_VIOLATION`…). Las capabilities de escritura no existen.

## 7. Qué significa el Plugin Contract

`Plugin Contract ≠ Plugin Runtime`. Hoy solo existe un **manifest declarativo** (`legacy_documenter.plugins.validation.validate_manifest`) que se valida contra el contrato de consumidores (compatibilidad de versión mayor, capabilities conocidas, solo lectura) y se convierte en un descriptor. Nada se carga, importa, instala ni ejecuta; `entrypoint_metadata` es texto inerte.

## 8. Qué NO está implementado

Plugin Runtime (descubrimiento, carga, instalación, sandbox, firma, hot reload, registry remoto); capabilities de escritura para consumidores; UI de revisión, RBAC, firmas, quórum o aprobación masiva; interpretación de IA integrada en la documentación humana; inferencia de tipos rica, `argparse`/console scripts, drivers de base de datos y decoradores en Python; validación de una segunda tecnología sobre un producto externo independiente (el piloto Python es **circular**: analiza una copia congelada de LegacyMapper); tercera tecnología; V6.

## 9. Comandos auxiliares

`python main.py readiness` (valida los prerrequisitos de conocimiento del propio proyecto); `python main.py output-manifest <dir>` (escribe `OUTPUT_MANIFEST.json` con ruta/tamaño/SHA-256 de una corrida terminada); pruebas: `python -X utf8 -m unittest discover -s tests`.
