# V5.3 R2.5.1 — Higiene, coherencia y obsolescencia del repositorio

Estado final: **V5_3_R2_5_1_NEEDS_HUMAN_DECISION**

## 1. Objetivo

Auditar el repositorio tras R2.5 (documentación, prompts, código R2.1–R2.5, tests, residuales) y sanear solo lo claro. Sin funcionalidad nueva.

## 2. Alcance revisado

Git (rama, tag, worktrees, ignorados, sin versionar); `docs/V5/` (43 docs), `prompts/V5/` (10) y `prompts/V5_0/` (30); `PROJECT_STATE.json`, `AGENTS.md`, `CLAUDE.md`, `docs/continuity/`; módulos `context/hydration_view.py`, `documentation_v52/writer.py`, `utils/path_limits.py`, `versions.py`, `fingerprints/`, `cache/`; tests V5.3 y rutas a docs/output en tests; raíz del repo y `output/`. Métodos: hash de contenido, nombres repetidos, extracción automática de rutas citadas en docs/prompts V5.3 + contraste con el disco, AST de imports/funciones sin uso, `git status --ignored`.

## 3. KEEP

- Todos los docs de resultado `docs/V5/V5_3_R0…R2_5` (títulos y estados finales coherentes: R2.1–R2.5 `READY_FOR_REVIEW`; R0/R0.1/R1 sin estado final por ser informes/contrato) y los 10 prompts de `prompts/V5/` (convención vigente; nombres coinciden 1:1 con su documento de resultado).
- Módulos R2.1–R2.5 (todos referenciados y cubiertos por tests; ver §14), `tests/test_v5_3_r2_*` (5 archivos, sin duplicados por hash).
- `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/PROJECT_RECOVERY.md`, `output/` rastreado (117 archivos de baselines históricos).

## 4. UPDATE

| Archivo | Qué desactualiza | Por qué no se tocó |
|---|---|---|
| `PROJECT_STATE.json` | `current_version=V5.2`, `*_status=V5_2_CLOSED_PENDING_GIT_APPROVAL`, `git_closure_status=PENDING_GIT_APPROVAL`, `v5_3_started=false`, `tests=2449`, `latest_completed_round=V5.2-R4.3`, `next=V5.3` | El prompt prohíbe cambiarlo automáticamente; ninguna ronda R2.x lo actualizó (convención: hitos) → §8 |
| `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md` (l. 3, 209, 248) | V5.2 «pendiente de versionado Git»; V5.3 «READY_TO_START, no iniciada» | La guía de continuidad exige no editar roadmap sin autorización → §8 |
| `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md` (l. 1099, sección 37) | «pendiente solo el versionado Git» | Idem; además es narrativa histórica de R4.3 → §8 |

## 5. DELETE_CANDIDATE

| Archivo | Evidencia | Acción |
|---|---|---|
| `findstr` (raíz, 0 bytes, versionado desde `effea07`) | Vacío; artefacto de una redirección accidental de comando (`findstr …` de Windows); no lo referencia ningún código/test/doc (solo el comando aparece en un prompt/resultado V4.3 como texto) | **Eliminado** (§12) |

## 6. HISTORICAL (se conservan explícitamente)

- `docs/V5/V5_2_R4_3_CIERRE_FORMAL.md`, `V5_2_R4_4_AJUSTE_FINAL_ESTADO_Y_GIT.md` y sus prompts en `prompts/V5_0/`: citan `PENDING_GIT_APPROVAL` como estado de su momento; la resolución está en `V5_2_GIT_CLOSURE_RESULT.md` (commit `6c32c4c`, tag `v5.2`, push correcto).
- Los 30 prompts de `prompts/V5_0/` (V5.0–V5.2): no se mueven ni borran; ninguno es de V5.3.
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md` (narra la corrección de una frase `PENDING_GIT_APPROVAL`).
- `prompts/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md` §«Moverlo a»: cita `prompts/V5_0/V5_3_R0_EMPIRICAL_BASELINE.md` (ruta ya inexistente) como narración de la instrucción de mover el prompt de R0; el movimiento ya se hizo. Comprensible, se conserva.
- Raíz: `probe_copilot*.py`, `probe_legacymapper_provider.py`, `probe_real_flow*.py`, `requirements-copilot.txt`, `result_codex/`, `context/.gitkeep` → ver §8 (la clasificación definitiva es de decisión humana).

## 7. GENERATED_IGNORE

`__pycache__/` (todos los paquetes), `.claude/` (32 MB), `docs/V4_3/samples/R6/parts/`: ignorados por `.gitignore`/exclusión local, no versionados. Sin acción.

## 8. NEEDS_HUMAN_DECISION

1. **`PROJECT_STATE.json` y roadmap/historia de continuidad** contradicen la realidad (V5.2 cerrada y publicada, tag `v5.2`; V5.3 en curso R0→R2.5). ¿Se actualizan ahora (p. ej. `current_version=V5.3`, `v5_3_started=true`, ronda actual R2.5, cierre Git de V5.2 resuelto, suite 2 663) o al cierre de V5.3? Recomendación: al menos corregir ya las frases de «Git pendiente» en roadmap/estado, por ser un hecho resuelto y no un estado de ronda.
2. **Dos worktrees de agentes residuales**: `.claude/worktrees/agent-a00511fc…` (rama `worktree-agent-a00511fc63aa090e0`, `e9e3d60`) y `agent-a0c75b43…` (`worktree-agent-a0c75b43cbf073bbc`, `effea07`); ambos commits ya están en la historia de `main`. Candidatos a `git worktree remove` + borrar ramas locales; toca estructura Git, lo decide el usuario.
3. **Scripts sueltos en la raíz** (`probe_*.py` ×5, `requirements-copilot.txt`, `result_codex/V1_ANALYSIS_REPORT.md`, `context/.gitkeep`): diagnóstico del piloto Copilot V4.3 y reporte V1 citados en docs V4; ¿mover a `tools/`/archivar o conservar?
4. **Estado final de R2.5.1**: queda condicionado por 1–3.

## 9. Duplicados encontrados

- Contenido idéntico (hash) en `docs/V5/`, `prompts/V5/`, `prompts/V5_0/`: **ninguno**; en `tests/`: ninguno.
- Mismo nombre en carpetas distintas: 14 pares prompt↔resultado (`prompts/V5/` o `V5_0/` vs `docs/V5/`) → **duplicado válido** (el prompt y su informe comparten nombre por convención) + 1 caso en `docs/V4_3/samples/` (muestras de rondas distintas, histórico).
- Prompts de V5.3 en `prompts/V5_0/`: **ninguno** (la convención `prompts/V5/` se cumple).
- Lógica repetida: `atomic_write_bytes` (`utils/atomic_write.py`) vs `documentation_v52/writer._atomic_write` — ya documentado en R2.4 §20, mismo mecanismo; no se unifica en esta ronda.

## 10. Referencias rotas encontradas

Rutas de repo citadas en los docs/prompts V5.3, `CLAUDE.md`, `AGENTS.md`, `PROJECT_RECOVERY.md` y roadmap, contrastadas con disco: 2 inexistentes. (a) `prompts/V5_0/V5_3_R0_EMPIRICAL_BASELINE.md` (histórica, §6). (b) `docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md` (el entregable de esta ronda, ya creado). Rutas a docs/output en tests inexistentes: 7, todas fixtures o archivos temporales de test (`docs/x.md`, `output/v3_r9/…` generados al vuelo) — sin acción.

## 11. Referencias corregidas

Ninguna: la única rota vigente es narrativa histórica comprensible; las contradictorias de estado están bajo decisión humana (§8).

## 12. Archivos eliminados realmente

- `findstr` (raíz, 0 bytes).

## 13. Archivos actualizados realmente

- `legacy_documenter/cache/session.py`: eliminado el import muerto `MODE_COLD` (sin otro uso en código ni tests; no hay efecto en runtime ni en el fingerprint del analizador).
- `docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md`: este documento.

## 14. Código muerto / imports muertos

Análisis AST sobre los módulos R2.1–R2.5: 1 import muerto (`MODE_COLD` en `cache/session.py`, eliminado); ninguna función/clase sin referencia; `cache/extraction_store.load_shard` y `cache/file_state.normalize_relative_path` solo se usan dentro de su módulo (correcto, API interna). Ningún módulo huérfano. Los símbolos que `cache/__init__` reexporta sin consumidor externo (`render_file_state`, `parse_shard`, etc.) forman parte de la API pública del paquete y de los tests.

## 15. Temporales / residuales

- `output/_r25_*` (mediciones de R2.5): ya eliminados al cierre de R2.5; verificado que no queda ninguno (`output/` solo contiene baselines rastreados).
- Sin `*.tmp`, `*.orig`, `*.bak`, `_r2*` ni `*.log` dentro del repositorio; `.claude/worktrees` (§8.2) es lo único residual no trivial.

## 16. Coherencia Git / estado

Rama `main` = `origin/main`, HEAD `6c32c4c` («chore(v5.2): close documentation profiles phase»), tag `v5.2` anotado en HEAD (`438a159…`). V5.2 está cerrado y publicado (`V5_2_GIT_CLOSURE_RESULT.md`). V5.3 en curso: R0, R0.1, R1, R2.1, R2.2, R2.2.1, R2.3, R2.4, R2.5 completas (`READY_FOR_REVIEW`), todo **sin commit**. Persisten referencias «V5.2 pendiente de Git» en `PROJECT_STATE.json` y continuidad → §8.1; en los docs de ronda V5.2 son históricas. `PROJECT_STATE.json` no se modificó.

## 17. Tests ejecutados

Se modificó código (un import) → suite completa: `python -m unittest discover -s tests`: **2 663 tests, 0 fallas, 0 errores, 132 skips**, 283 s.

## 18. Riesgos

Quien retome desde `PROJECT_STATE.json`/roadmap leerá «V5.2 pendiente de Git» y «V5.3 no iniciada» (falso); el repositorio es la fuente autoritativa y `AGENTS.md` remite a `PROJECT_STATE.json`, de modo que la contradicción es real para un checkout nuevo. Las ~13 rondas V5.3 sin commit son un riesgo de pérdida por volumen.

## 19. Deuda técnica

| Hallazgo | Clase |
|---|---|
| Estado/roadmap desactualizados (§8.1) | NEXT_ROUND (decisión humana) |
| Worktrees/ramas de agentes residuales | NEXT_ROUND |
| Scripts `probe_*` y `result_codex/` en la raíz | OBSERVATION |
| Trabajo de V5.3 R0→R2.5 sin commit | CURRENT_PHASE |
| `atomic_write_bytes` duplicado con `writer._atomic_write` | OBSERVATION |
| BLOCKING | ninguno |

## 20. Estado Git (solo consultas)

Modificados: `cli/full_pipeline.py`, `cli/output_manifest.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `context/hydration.py`, `documentation_v52/engine.py`, `utils/atomic_write.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, `cache/session.py` (aún sin versionar como parte del paquete nuevo). Sin versionar: `legacy_documenter/cache/`, `fingerprints/`, `versions.py`, `context/hydration_view.py`, `documentation_v52/writer.py`, `utils/path_limits.py`, tests R2.1–R2.5, `docs/V5/V5_2_GIT_CLOSURE_RESULT.md` y docs V5.3 (incluido este), `prompts/V5/`. Eliminado (rastreado, sin commit): `findstr`. Ignorados relevantes: `.claude/`, `__pycache__/`. Sin commit, tag ni push; historial intacto.

## 21. Recomendación para R2.6

Antes de R2.6: (1) decidir §8.1 (actualizar `PROJECT_STATE.json`/roadmap) y (2) preferiblemente que el usuario versione el trabajo V5.3 hecho (R0→R2.5) en un commit propio; (3) decidir §8.2–8.3 si se quiere limpiar. Ninguno bloquea técnicamente R2.6; el código y los tests están consistentes.

## 22. Estado final

Auditoría completada, un residual eliminado y un import muerto retirado, nada dudoso borrado, históricos preservados. Quedan decisiones humanas sobre estado/continuidad, worktrees y scripts de raíz.

**V5_3_R2_5_1_NEEDS_HUMAN_DECISION**
