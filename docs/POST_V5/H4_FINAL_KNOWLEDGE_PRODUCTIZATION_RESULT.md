# H4 — Final Knowledge Productization: resultado

Estado: **`H4_FINAL_KNOWLEDGE_PRODUCTIZATION = READY_FOR_HUMAN_APPROVAL`**. **H4 = HUMAN_APPROVAL_PENDING** (no cerrado). **H5 = NOT_STARTED**. Sin commit, push ni tag.

## 1. Estructura final de salida
Nuevo paquete `legacy_documenter/product/` (3 módulos: `__init__`, `domain`, `package`), sin cambios en Evidence, analizador, adapters, proveedor ni validadores. Comando (sin análisis, sin proveedor):

```text
python -m legacy_documenter.product.package <baseline> --output <dir> [--ai-run <dir con ai_raw_responses.json>]
        [--project P] [--solution S] [--domain-knowledge terms.json]
```

```text
<dir>\
    KNOWLEDGE_PACKAGE.json
    human\   index.html (punto de entrada único) · LegacyMapper.pdf · executive.pdf
             guide\ (HTML funcional+técnico + assets) · executive\index.html · diagrams\index.html
    ai\      knowledge.json (modelo autoritativo) · architecture.json · views.json · flows.json · data.json · unresolved.json · provenance.json
    internal\ behavioral\ (explanations, validation_report, AI manifest, ai_raw_responses, ui/style/wireframe reports, template manifest)
              baseline_reference.json
```
Las carpetas `human_default`, `human_executive`, `docs`, `visuals`, `behavioral`, `package` no aparecen en la estructura pública. Una sola semántica (`BehavioralDocument` + vistas explicadas) se proyecta a `human/` y `ai/`; los índices de `ai/` solo guardan ids que referencian a `knowledge.json`. Audiencias: ejecutivo (`executive/`, PDF) y guía funcional+técnica (`guide/`, con tablas de rutas con símbolos reales, datos y relaciones); no se duplica contenido entre ellas (misma proyección, distinta plantilla).

## 2. Cambios de prompt / estilo de IA (`behavior/ai.py`)
* `SYSTEM`/`INSTRUCTION`/instrucción de proyecto: explicar para una persona; preferir nombres y relaciones a conteos; sin estadísticas del análisis ni identificadores de Evidence en la prosa; 1–3 frases; incertidumbre solo breve y cuando cambie la comprensión; ruta técnica con símbolos reales (vista → evento → manejador → negocio → entre proyectos → datos → procedimiento/SQL → frontera).
* Contexto: se retiraron `counts`, `totals_for_reference_only`, el hecho «Cobertura» y los conteos de uso/invocaciones (ahora nombres: acciones, quiénes la abren, vistas por estado de uso).
* Contexto con `human_confirmed_domain_knowledge` (solo si una persona lo suministra), etiquetado como confirmado por una persona y no como evidencia.

## 3. Proveedor real
`copilot-local` / `gpt-6-luna` (Copilot CLI ya instalado vía `COPILOT_CLI_PATH`, solo para el proceso). **6 solicitudes reales, 6 correctas** (5 vistas + proyecto; 120 354 caracteres de entrada, 96 252 de salida). 91 afirmaciones de IA aceptadas, 2 rechazadas por el validador (se conservan en el informe interno); solo 2 de 91 contienen algún número (antes: recuentos como «121 vistas», «26 sitios», «7 con uso observable, 52…»). Detalle por solicitud en `internal\behavioral\AI_INTERPRETATION_MANIFEST.json`. No hubo más llamadas (el paquete final re-valida las respuestas guardadas).

## 4. Cero reanálisis
Baseline persistido de la corrida real (`C:\PruebasLegacyMapper\runs\manual_validation\baseline`) sin modificar; no se ejecutó escáner, analizador ni reconstrucción de Evidence y no se leyó el código fuente (`package.py` solo lee el baseline; verificado con pruebas que parchean `run_full_pipeline` y el registro de proveedores). El manifiesto `KNOWLEDGE_PACKAGE.json` registra `portable_evidence_sha256` = `d83e5711…` idéntico al baseline de la validación manual.

## 5. Conocimiento de dominio confirmado por humanos
Contrato `LegacyMapperDomainKnowledge 1.0` (`product/domain.py`), archivo `{"terms": [{term, meaning, status: "CANONICAL", source: "human"}]}`; se rechaza todo estado distinto de `CANONICAL`, fuente distinta de `human`, términos vacíos o duplicados. Se reutiliza el estado existente `CANONICAL` (no hay un sistema de verdad paralelo) y cada entrada lleva `origin = HUMAN_CONFIRMED`. Uso: tabla visible y diferenciada «Terminología confirmada por una persona» (con «Aparece en» por coincidencia de nombre, solo orientativo), sección propia `domain_knowledge` en `ai/knowledge.json` y mención en `provenance.json` / `KNOWLEDGE_PACKAGE.json`, y contexto de futuras interpretaciones de IA. **No se pre-pobló ningún término** (COB, WebCob, Mantencion, Morosidad quedan a la espera de que el propietario los suministre con `--domain-knowledge`). En la corrida real de esta ronda no se suministró ninguno.

## 6. Contenido de los paquetes
* **Humano:** guía HTML/PDF (por defecto) y resumen ejecutivo HTML/PDF, página de diagramas, landing única `human\index.html`.
* **IA:** `knowledge.json` (solución, proyectos, 121 vistas con acciones, rutas, datos, relaciones, narrativa de IA con estado `AI_INTERPRETATION`, conocimiento humano), más proyecciones `architecture/views/flows/data/unresolved/provenance`. Se preservan identidades, estados (CONFIRMED / INFERRED / UNRESOLVED / AI_INTERPRETATION / CANONICAL), relaciones, símbolos, referencias de fuente y procedencia; cada ruta termina en datos o en una frontera explícita `UNRESOLVED`.
* **Interno:** artefactos de soporte copiados y referencia a la línea base (no se copia; ~47 k archivos).

## 7. Compatibilidad
Los comandos y rutas anteriores (`analyze`, `interpret`, `docs`, `visuals`, `deliver`, `behavior.prototype` y sus carpetas) no se modificaron y siguen funcionando; la capa nueva es de proyección y no los reemplaza. `behavior.prototype` gana `--domain-knowledge`. `BehavioralDocument` gana el campo `domain_knowledge` (vacío por defecto).

## 8. Pruebas
Nuevas: `tests/test_post_v5_h4_knowledge_productization.py` (14): estructura human/ai/internal y punto de entrada único, manifiesto (entradas existentes, hashes, sin marcas de tiempo), internos separados, `ai/` modelo + proyecciones, misma verdad en humano e IA (vistas y rutas), conocimiento humano distinguible de Evidence, carga/rechazo de términos y sin pre-poblado, contrato de prompt (sin métricas, nombres, Evidence, ruta técnica), contextos sin conteos, términos humanos en el contexto de IA, sin proveedor ni reanálisis, salida no vacía rechazada. Proveedor siempre doble (nunca real en pruebas). Actualizado el conteo de módulos del inventario (330 → 333) y su snapshot vivo.

## 9. Suite completa
`python -X utf8 -m unittest discover -s tests`, ejecutada **una vez** con todos los cambios estables: **3481 tests, 0 failures, 0 errors, 132 skips, 824 s, exit code 0**. (Antes de la corrida final se regeneró la clave `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` y se actualizó el conteo de módulos por el nuevo paquete `product`.)

## 10. Rutas de revisión humana
`C:\PruebasLegacyMapper\Resultados\h4_final_knowledge_productization\package\` — abrir `human\index.html`, `human\LegacyMapper.pdf`, `human\executive.pdf`, `ai\knowledge.json`, `KNOWLEDGE_PACKAGE.json` (+ `REVIEW_GUIDE.md`). Corrida real de IA conservada en `...\ai_run\`.

## 11. Estado
`H4_FINAL_KNOWLEDGE_PRODUCTIZATION = READY_FOR_HUMAN_APPROVAL` · `H4 = HUMAN_APPROVAL_PENDING` · `H5 = NOT_STARTED`. El cierre de H4 requiere aprobación explícita del propietario.
