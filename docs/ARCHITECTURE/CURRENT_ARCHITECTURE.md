# Arquitectura vigente

Estado: vigente (post-H5; `POST_V5` cerrado, `V6` no iniciado). Para historia por versión, ver `docs/V5/`
y `docs/POST_V5/` (documentos históricos/específicos de versión).

## Flujo canónico

```text
Source
→ extracción / análisis determinista
→ Evidence persistida
→ interpretación de IA (opcional)
→ conocimiento estructurado
→ proyecciones human / ai / internal
```

| Etapa | Módulos principales | Comando |
| --- | --- | --- |
| Análisis determinista + Evidence | `scanner`, `adapters`, `extractors`, `analysis`, `evidence`, `cache` | `full` / `analyze` |
| Interpretación de IA (opcional) | `llm`, `orchestration`, `knowledge`, `context` | `interpret` |
| Documentación humana | `documentation`, `documentation_v52`, `behavior`, `templates/human` | `docs` |
| Proyecciones visuales | `visuals` | `visuals` |
| Paquete final | `deliver`, `product` | `deliver` |
| Contrato para consumidores/plugins | `consumers`, `plugins` | (contrato declarativo, sin runtime) |

`docs`, `visuals` y `deliver` leen únicamente la Evidence persistida: no reescanean la fuente ni llaman a
un proveedor. `interpret` es la única etapa que puede llamar a un proveedor y falla de forma controlada
(`PROVIDER_UNAVAILABLE`) si no hay SDK/configuración.

## Principios

```text
analizar una vez / proyectar muchas
la autoridad final es humana
sin canonicalización automática
preservar lo no resuelto
existencia != uso
ausencia de evidencia de uso != obsolescencia
```

* La IA propone; todo texto de IA queda como `AI_INTERPRETATION` hasta una decisión humana explícita.
* Estados de hechos: Confirmado / Inferido / No resuelto.
* La plantilla controla presentación, nunca la verdad.

## Independencia

* El runtime del paquete no importa `tests/`, `tools/`, `docs/`, `prompts/` ni `PROJECT_STATE.json`.
* Ninguna ruta de máquina está embebida: fuente, salida y workspace son argumentos
  (ver `docs/OPERATIONS/WORKSPACE_CONTRACT.md`).
* Adapters: `vbnet-webforms-oracle` 1.0 (principal, validado en IST real) y `python-generic` 1.0 (piloto).
* Proyectos sin UI/acciones producen un paquete solo de máquina (`ai/` + `internal/`).
