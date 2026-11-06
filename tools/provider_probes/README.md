# tools/provider_probes

Sondas manuales de diagnóstico del proveedor **real** GitHub Copilot. No forman parte del runtime del paquete,
no las ejecuta ningún test y **nunca deben correrse en CI**.

> **Advertencia: proveedor real / cuota.** Cada script abre una sesión real de Copilot (`use_logged_in_user=True`)
> y puede consumir cuota. Úselos solo de forma deliberada y manual.

| Script | Propósito | Uso (desde `<REPO_ROOT>`) |
| --- | --- | --- |
| `probe_copilot_sdk.py` | Verifica que el SDK arranca y se conecta (cliente → start → stop) | `python tools/provider_probes/probe_copilot_sdk.py` |
| `probe_legacymapper_provider.py` | Verifica `CopilotProvider` de LegacyMapper con una solicitud mínima de una evidencia | `python tools/provider_probes/probe_legacymapper_provider.py` |
| `list_copilot_models.py` | Lista los modelos disponibles para el usuario autenticado | `python tools/provider_probes/list_copilot_models.py` |

Requisitos: `pip install -r requirements-copilot.txt` (SDK opcional) y sesión autenticada (`gh auth login`).

Variables de entorno (opcionales; solo `probe_legacymapper_provider.py` usa la configuración de LegacyMapper):
`LEGACYMAPPER_LLM_PROVIDER` (por defecto `COPILOT`), `LEGACYMAPPER_LLM_PROVIDER_ID`, `LEGACYMAPPER_LLM_MODEL`,
`COPILOT_CLI_PATH` (ruta explícita del ejecutable, si se necesita). Los scripts no leen rutas de máquina ni de workspace.

Retiradas del repositorio (post-H5): `probe_copilot_request.py` (duplicado de `probe_legacymapper_provider.py`),
`probe_real_flow.py` y `probe_real_flow_raw.py` (experimentos históricos con rutas de máquina y un flujo fijo; el
camino soportado es `python main.py interpret <baseline>`), y `test_flow_ai*.py` del clon antiguo (rutas del
workspace borrado; mismo motivo).
