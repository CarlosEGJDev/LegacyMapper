# V4.3 — Pre-Closure Distribution Dependency Follow-Up — Resultado

## 1. Hallazgo

`docs/V4_3/V4_3_PRE_CLOSURE_COPILOT_PROVIDER_CORRECTION_RESULT.md` dejó al repositorio en estado
`V4_3_READY_FOR_FINAL_AI_PILOT`, con `requirements-copilot.txt` (raíz del repositorio) declarando
correctamente la dependencia opcional del provider COPILOT (`github-copilot-sdk>=1.0.14`).

Sin embargo, el piloto externo real no se ejecuta contra el repositorio de desarrollo: se ejecuta
contra una distribución limpia construida por `tools/v4_3_r7_build_pilot_distribution.py`
(`RUNTIME_ROOT_ENTRIES`), que hasta este follow-up copiaba únicamente:

```text
main.py
legacy_documenter/
```

Verificación manual que originó este hallazgo:

```bat
findstr /N /I "requirements requirements-copilot" tools\v4_3_r7_build_pilot_distribution.py
```

```text
<sin resultados>
```

Consecuencia: la distribución limpia usada por el operador del piloto no transportaba
`requirements-copilot.txt`, de modo que el piloto podía depender accidentalmente de que el SDK ya
estuviera instalado en el Python global del equipo, en vez de instalarse explícitamente desde la
distribución que realmente se va a usar.

## 2. Archivo modificado

* `tools/v4_3_r7_build_pilot_distribution.py` — se agregó `"requirements-copilot.txt"` a
  `RUNTIME_ROOT_ENTRIES` (mismo mecanismo de allowlist ya existente; `build_distribution` ya sabía
  copiar tanto directorios como archivos sueltos de la raíz del repositorio). Se actualizó también
  el docstring del módulo para reflejar el nuevo contenido de la distribución.
* `tests/test_v4_3_r7_internal_acceptance.py` — ajustada/ampliada la cobertura de
  `PilotDistributionTests` (ver sección 4).

No se modificó `legacy_documenter/llm/providers/copilot.py`, `consumer_projection`, hidratación,
selección, documentación humana, confianza de flows, resolución de terminales, la lógica de
presentación de R8, `ProviderRegistry`, `PROJECT_STATE.json`, V5 ni el Plugin Runtime.
`requirements-copilot.txt` en sí no se modificó: sigue conteniendo exactamente
`github-copilot-sdk>=1.0.14`.

## 3. Motivo

El builder de distribución usa deliberadamente un allowlist fijo (`RUNTIME_ROOT_ENTRIES`), no un
blocklist, precisamente para que ningún archivo nuevo de la raíz del repositorio se filtre a una
distribución de piloto sin una decisión explícita de incluirlo (ver comentario original del
módulo). `requirements-copilot.txt` es exactamente ese caso: un archivo nuevo en la raíz,
introducido por la corrección pre-cierre anterior, que necesitaba una decisión explícita para
sumarse al allowlist. No se creó un sistema de distribución nuevo; no se instala nada desde el
builder; no se ejecuta `pip`; no se autentica GitHub; no se descarga el runtime del SDK desde el
builder. El builder solamente transporta la declaración de dependencia opcional, igual que ya
transportaba `main.py` y `legacy_documenter/`.

## 4. Tests

Se ajustó/amplió `tests/test_v4_3_r7_internal_acceptance.py::PilotDistributionTests`:

1. `test_distribution_contains_only_main_py_legacy_documenter_and_requirements_copilot` (renombrado
   desde `test_distribution_contains_only_main_py_and_legacy_documenter`) — el nivel superior de la
   distribución es ahora exactamente `["legacy_documenter", "main.py", "requirements-copilot.txt"]`.
2. `test_distribution_carries_requirements_copilot_with_the_optional_dependency` (nuevo) — el
   `requirements-copilot.txt` copiado contiene literalmente `github-copilot-sdk>=1.0.14`.
3. `test_build_distribution_return_value_lists_every_copied_file` (ampliado) — el valor de retorno
   de `build_distribution` incluye `"requirements-copilot.txt"`.
4. `test_distribution_excludes_dev_only_root_files` (nuevo) — `PROJECT_STATE.json`, `README.md`,
   `AGENTS.md`, `CLAUDE.md` siguen ausentes de la distribución.
5. `test_distribution_excludes_dev_only_directories` (preexistente, sin cambios) — `docs/`,
   `prompts/`, `tests/`, `codex/`, `output/`, `result_codex/`, `tools/` siguen ausentes.
6. `test_refuses_to_copy_into_a_non_empty_destination` (preexistente, sin cambios) — el builder
   sigue rechazando un destino no vacío.
7. `test_clean_distribution_runs_full_standalone_against_a_fixture` y
   `test_clean_distribution_builds_output_manifest_via_its_own_cli_subcommand` (preexistentes, sin
   cambios) — el comportamiento previo (ejecutar `full` y `output-manifest` desde la distribución
   copiada, sin acceso al repositorio de desarrollo) se conserva intacto.

Ningún test usa Copilot real; todos operan sobre directorios temporales
(`tempfile.TemporaryDirectory`), nunca sobre el directorio de salida del piloto final del usuario.

### Resultado de tests

```text
Comando: python -m unittest tests.test_v4_3_r7_internal_acceptance
Ran 35 tests -- OK

Comando: python -m unittest discover -s tests
total:    2098
passed:   1966
failed:   0
errors:   0
skipped:  132
```

`0 failures`, `0 errors` (criterio obligatorio cumplido). El total creció de 2096 a 2098 por los 2
tests nuevos agregados en este follow-up.

## 5. Comprobación de distribución (verificación manual)

Se construyó una distribución de prueba en un directorio temporal (no en el directorio del piloto
final del usuario) mediante `tools.v4_3_r7_build_pilot_distribution.build_distribution`:

```text
root: ['legacy_documenter', 'main.py', 'requirements-copilot.txt']
requirements-copilot.txt present: True
content (última línea no vacía): github-copilot-sdk>=1.0.14
docs absent: True
prompts absent: True
governance absent: True
results absent: True
tests absent: True
PROJECT_STATE.json absent: True
```

## 6. Runtime Independence

`requirements-copilot.txt` es una declaración de dependencia para `pip`, no código Python; el
runtime (`legacy_documenter/`, `main.py`) no lo importa ni lo lee en ningún punto. Su presencia en
la raíz de la distribución es válida per las instrucciones de este follow-up: es una dependencia
runtime *opcional*, no una dependencia hacia documentación o artefactos de desarrollo. La
distribución construida sigue sin contener `docs/`, `prompts/`, `governance/`, `results/`,
`PROJECT_STATE` ni `tests/`. Verificado: PASS.

## 7. Restricciones verificadas

* No se modificó `legacy_documenter/llm/providers/copilot.py`. PASS.
* No se modificó `consumer_projection`, hidratación, selección, documentación humana, confianza de
  flows, resolución de terminales, ni la lógica de presentación de R8. PASS.
* No se modificó `ProviderRegistry`. PASS.
* No se modificó `PROJECT_STATE.json`. PASS.
* No se inició trabajo de V5 ni Plugin Runtime. PASS.
* No se modificó `requirements-copilot.txt` (sigue exactamente igual). PASS.
* `github-copilot-sdk` sigue siendo una dependencia opcional, no obligatoria del runtime
  determinista. PASS.
* No se incorporó Copilot real a ningún test. PASS.
* No se ejecutó R9. PASS.
* No se ejecutó el piloto final real. PASS.
* V4.3 no se declaró cerrada. PASS.

## 8. Estado final

```text
V4_3_READY_FOR_FINAL_AI_PILOT
```
