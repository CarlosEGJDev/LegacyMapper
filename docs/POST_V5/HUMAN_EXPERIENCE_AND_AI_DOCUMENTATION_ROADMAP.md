# Post-V5 — Human Experience & AI Documentation (roadmap H1–H5)

Estado: H1 implementado (`python main.py interpret`, ver `docs/POST_V5/H1_AI_ONLY_INTEGRATED_DELIVERY_RESULT.md`); H2 implementado (`python main.py docs`, ver `docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md`; corrección funcional H2-R2 incluida); H3 implementado (`python main.py visuals`, ver `docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md`; corrección de legibilidad H3-R2 incluida); H4 **CERRADO** tras aprobación manual del propietario (ver `docs/POST_V5/H4_CLOSURE.md` y `docs/POST_V5/H4_FORMAL_CLOSURE_RESULT.md`); H1–H4 cerrados; H5 `NOT_STARTED` (siguiente: `H5_REAL_IST_VALIDATION_AND_CLOSURE`); V6 `NOT_STARTED`. Esto **no es V6**. Autoridad de estado: `PROJECT_STATE.json` (`active_initiative`, `initiative_status`).

Convención de este documento: *[hecho]* verificado y vigente · *[limitación]* aceptada · *[capacidad futura]* no existe · *[candidato de diseño]* no decidido.

## 1. Propósito
Que una persona entienda cómo funciona un sistema legado **sin abrir el código**, según su nivel, y que la IA pueda interpretar ese sistema a partir de conocimiento determinista ya persistido, sin reanalizar.

## 2. Por qué existe esta fase
V5 cerró el motor determinista (Evidence, cache, adapters, proveedor de IA, revisión humana, contratos de consumers). La corrección técnica está probada; la **comprensión humana** no. La documentación actual es correcta pero demasiado técnica y poco visual para audiencias amplias.

## 3. Qué ya provee V5 *[hecho]*
Evidence normalizada y persistida; `documentation_v52/` (perfiles `general/` y `developer/`); `ai_context/` y `consumer_projection/`; propuestas de IA con revisión humana y conocimiento canónico (nunca automáticos); segmentación de flujos; Consumer API de solo lectura; adapters VB.NET WebForms/Oracle y Python (piloto circular). Baseline: tag `v5` → `e831a2f84d2749b4452e06860521b3171093c7b9`; analyzer v3 `f05b2de4…`.

## 4. Brecha principal (histórica al abrir la iniciativa; estado actual)
Brechas identificadas al abrir post-V5 y su estado vigente:
* **HX-01** documentación humana demasiado técnica / poco visual → **resuelta por H2 + H3 + H4**, pendiente de la aceptación humana de H5.
* **HX-02** HTML/PDF visual no productizado → **resuelta por H4** (`python main.py deliver`).
* **HX-03** proyección visual estructurada → **resuelta por H3** (`python main.py visuals`; casos de uso fuera de alcance por falta de evidencia).
Detalle método/clase **no** es el objetivo primario de esta fase; se conserva como evidencia profunda, no como narrativa principal.

## 5. Requisito: reutilizar el output determinista para IA (AI-only)
Modos: **A** determinista (`full` sin IA) *[hecho]*; **B** `full --allow-ai-interpretation` (analiza + interpreta en una corrida) *[hecho]*; **C** AI-only (`python main.py interpret`) *[hecho, H1]*:

```text
output determinista existente → validar baseline → reutilizar Evidence / AI context / manifests
→ interpretación IA → propuestas / documentación humana
```
Objetivo: **analizar una vez, interpretar muchas veces** (esencial en repositorios grandes como IST). **Implementado en H1:** `python main.py interpret <output-existente>` (UX-02 resuelto; el contrato de arriba es el implementado; el nombre quedó fijado como `interpret`).
Puerta obligatoria antes de invocar un provider: output existe; Evidence manifest existe y valida; schema soportado; analyzer fingerprint conocido; AI context existe; provenance válida; identidad de fuente/repositorio disponible; baseline no corrupto ni obsoleto. Si falla → estado `AI_ONLY_INPUT_INVALID`, **sin llamada al provider** *[hecho, H1]*. El comando se fijó como `interpret` (alternativas descartadas: `ai-only`, `interpret-existing`).

## 6. Roadmap H1–H5
**H1 — AI-only desde conocimiento determinista persistido.** Output válido existente → interpretación IA, sin reescanear la fuente. Preserva: sin provider ante baseline inválido; provenance; validación de schema/fingerprint; proposal ≠ canonical; autoridad de revisión humana.

**H2 — Documentación humana por nivel de audiencia** *(implementado: `python main.py docs`; perfiles `executive`, `functional`, `technical_overview`)*. Tres perfiles: `executive`, `functional`, `technical-overview`. Contenido primario: sistema, módulos/áreas funcionales, proyectos, capas, vistas/pantallas, dependencias principales, flujos de negocio, interacciones de datos, integraciones externas, áreas no resueltas. Sin método/clase como narrativa por defecto.

**H3 — Proyecciones visuales estructuradas** *(implementado: `python main.py visuals`)*. La IA no inventa diagramas libremente: `Evidence → interpretación IA estructurada → modelo de diagrama validado → renderer determinista → SVG/PNG/HTML/PDF`. Tipos posibles: mapa del sistema, de módulos, proyecto/capa, dependencias, flujo de negocio, casos de uso, interacción de datos, integraciones externas. Cada relación importante conserva trazabilidad a evidencia o se marca como interpretación/inferencia de IA.

**H4 — Entregables humanos finales** *(implementado: `python main.py deliver`)*. `SYSTEM_OVERVIEW`, `MODULE_MAP`, `FUNCTIONAL_AREAS`, `USE_CASES`, `BUSINESS_FLOWS`, `ARCHITECTURE_OVERVIEW`, `PROJECT_LAYER_MAP`, `DATA_INTERACTIONS`, `EXTERNAL_INTEGRATIONS`, `KNOWN_UNRESOLVED_AREAS`. Formato primario: HTML navegable; secundario: PDF; artefactos de render: SVG/PNG. No prometer interactividad rica hasta implementarla y validarla.

**H5 — Validación real en IST y cierre.** Primero un slice representativo de IST. Éxito: una persona no técnica entiende qué hace el sistema/módulo; una funcional entiende flujos y casos de uso; una técnica entiende proyectos, capas y dependencias, todo sin abrir el código. Además: afirmaciones importantes trazan a evidencia; la interpretación de IA se distingue visiblemente de hechos confirmados; lo no resuelto sigue no resuelto; sin canonicalización automática.

Solo tras H1–H5 se vuelve a la expansión técnica amplia.

## 7. No-objetivos (de esta fase)
Tercera tecnología; Plugin Runtime; inferencia de tipos más rica en Python; ampliación del adapter de BD de Python; refactors grandes; capacidades de escritura para consumers; proliferación de providers; documentación profunda de método/clase; rediseño V6.

## 8. Criterios de éxito
Los de H5, más: existe un camino AI-only que rechaza baselines inválidos antes de tocar un provider; los entregables H4 se generan desde evidencia con trazabilidad; los invariantes de la sección 9 siguen verdes (suite completa + regresión IST 0/0/0).

## 9. Invariantes permanentes
Python descubre, estructura, selecciona y valida; la IA interpreta. Nunca inventar relaciones. Preservar confirmed / inferred / unresolved. Provenance es parte del producto. Proposal ≠ canonical; la canonicalización requiere autoridad humana explícita. La IA nunca muta la verdad determinista. Runtime independiente de archivos de desarrollo (verificado en clean-room). Ningún provider real se invoca por accidente. Detalle: `LEGACYMAPPER_PRODUCT_PRINCIPLES.md`.

## 10. Backlog diferido y deuda post-V5
Clasificación `POST_V5` (no bloquean el cierre de V5; V5 no se marca incompleta):

| Id | Descripción | Tipo |
|---|---|---|
| UX-01 | `full` sobre un repositorio inexistente devuelve SUCCESS con análisis vacío | **resuelto en pre-H5 Gate A** (exit 4 + `PATH_CONTRACT_VIOLATION`, antes de escáner/analizador/proveedor) |
| UX-02 | No había comando público AI-only para reutilizar un output determinista | **resuelto en H1** (`python main.py interpret`) |
| UX-03 | No hay CLI de consumers (solo API Python) | limitación aceptada / capacidad futura |
| HX-01 | Docs humanas demasiado técnicas / poco visuales | **resuelto por H2 + H3 + H4**, pendiente de la aceptación humana de H5 |
| HX-02 | HTML/PDF visual no productizado | **resuelto en H4** (`python main.py deliver`: HTML navegable primario + PDF secundario) |
| HX-03 | Proyección visual estructurada | **resuelto en H3** (`python main.py visuals`; casos de uso fuera de alcance: sin evidencia que los sustente) |

Más el backlog de la sección 7 y el ledger de V5 intacto (`docs/V5/V5_FINAL_DEBT_LEDGER.json`: BLOCKING 0 / FUTURE_PHASE 14 / OBSERVATION 15 / HISTORICAL_COMPATIBILITY 5).

## 11. Siguiente ronda recomendada
**H5 — Real IST validation and closure** (H1, H2, H3 y H4 cerrados; H4 cerrado el 2026-10-30 con el paquete aprobado `C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\`). H5 es la dueña de la validación final y del cierre y solo empieza con un prompt explícito. Regla de ejecución: un hito en un prompt cuando sea razonable; máximo 3 rondas de revisión/corrección por defecto (ver `LEGACYMAPPER_LESSONS_LEARNED.md` §37.1).

## 12. H4-R4 — Prototipo de documentación conductual (ronda excepcional)
La revisión humana del paquete H4 halló un desajuste de producto: los entregables reorganizan documentación técnica en lugar de explicar cómo funciona el software. Estado: empaquetado H4 = técnicamente validado; **concepto de documentación humana de H4 = reabierto**; prototipo conductual = `H4_BEHAVIORAL_PROTOTYPE_READY_FOR_HUMAN_REVIEW` (`docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md`). Modelo: Solución → Proyecto → (Módulo solo con evidencia; en `WebPREPrevencion`: `NO_SAFE_MODULE_STRUCTURE`) → Vista → acciones → ruta técnica → datos → invocaciones → no resuelto, con explicación estructurada, validación determinista y wireframe documental. Sin IA real en el prototipo. **H5 = NOT_STARTED**; la revisión humana decide si este modelo sustituye al paquete H4 actual. No es V6 ni cierre de post-V5.

### H4-R5 — Corrección final conductual con IA real
`H4_BEHAVIORAL_AI_READY_FOR_HUMAN_REVIEW`: interpretación de IA real (proveedor existente) sobre contexto conductual acotado, validada de forma determinista y rotulada `AI_INTERPRETATION`; clasificación de uso observable (existir ≠ usar; ausencia de evidencia ≠ obsolescencia); catálogo relegado al apéndice. H4 **no** está cerrado (espera la decisión humana); H5 = NOT_STARTED. Detalle: `docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md`.

### Productización de la plantilla humana
`H4_HUMAN_TEMPLATE_READY_FOR_HUMAN_REVIEW`: sistema de plantillas humanas (`legacy_documenter/templates/human/default`, contrato `LegacyMapperHumanTemplate 1.0`), aviso de IA único con marcador «IA», jerarquía
tipográfica, índice HTML/PDF, diagrama simple de cajas por vista y reconstrucción visual sensible a estilos con capacidad `STRUCTURE_ONLY | STYLE_PARTIAL | STYLE_HIGH_CONFIDENCE`.
Deuda abierta: persistir UI/navegación en Evidence (hoy sidecar versionado) y resolver llamadas BL entre proyectos. H4 no se cierra hasta la aprobación humana; **H5 = NOT_STARTED**.
Detalle: `docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md`.

### Pulido final de la plantilla humana
`H4_HUMAN_TEMPLATE_READY_FOR_FINAL_HUMAN_APPROVAL`: título y subtítulos centrados, párrafos justificados, diagramas SVG con texto contenido y cajas adaptativas, aviso de IA único con marcador
por capítulo, portada con procedencia exacta de la IA y consistencia HTML/PDF, todo en `legacy_documenter/templates/human/default` y el renderizador. Pendiente: aprobación humana final. **H5 = NOT_STARTED.**

## 13. Pre-H5 Gate A — Portabilidad e independencia del runtime
`PRE_H5_GATE_A_PORTABILITY = PASS`. Resuelve DT-01 (portabilidad), DT-02/UX-01 (validación estricta de rutas), DT-05 (IA opcional) y DT-06 (contrato global de rutas/recursos):
las plantillas humanas integradas viajan dentro del paquete, `full`/`analyze` rechazan fuente/salida inválidas con exit 4 antes de escanear, la IA nunca es requerida por los comandos deterministas
y `interpret` sin proveedor falla de forma controlada. Detalle y evidencia: `docs/POST_V5/PRE_H5_GATE_A_PORTABILITY_RESULT.md`.
**Pendiente antes de H5:** Gate B (DT-03 UI/navegación/estilos → Evidence Core) y Gate C (DT-04 resolución BL entre proyectos, DT-07 segunda plantilla humana, DT-08 deuda menor seleccionada).
**H5 = NOT_STARTED.**

## 14. Pre-H5 Gate A.1 — Cierre de distribución
`PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS` (Gate A sigue `PASS`). Instalación real desde wheel en un venv aislado (`legacymapper` / `python -m legacy_documenter`), prototipo conductual sin defaults de IST
(selección determinista o explícita) y `output-manifest` con falla controlada. Detalle: `docs/POST_V5/PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE_RESULT.md`.
**Pendiente antes de H5:** Gate B (DT-03 → Evidence Core + proyección física vs lógica de la procedencia de la fuente) y Gate C (DT-04, DT-07, DT-08, decisión UX-03). **H5 = NOT_STARTED.**

## 15. Pre-H5 Gate B — UI/navegación/estilos en Evidence Core
`PRE_H5_GATE_B_EVIDENCE_CORE = PASS` (Gates A y A.1 siguen `PASS`). Los hechos de UI, navegación, mensajes, parámetros, estilos y activos son Evidence persistida y versionada (`evidence/ui_*.json`);
la documentación conductual, el contexto de IA y las plantillas no vuelven a leer la fuente (validado en IST con 0 aperturas, scanner 0, analyzer 0). El sidecar es proyección derivada. Detalle: `docs/POST_V5/PRE_H5_GATE_B_EVIDENCE_CORE_RESULT.md`.
**Pendiente antes de H5:** solo Gate C (DT-04, DT-07, DT-08, decisión UX-03). **H5 = NOT_STARTED.**

## 16. Pre-H5 Gate B.1 — Cierre del Evidence Core
`PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS` (Gates A, A.1 y B siguen `PASS`). Activos `~/`, navegación menú/config, identidad lógica/portable, semántica honesta de `source_snapshot_sha256`,
UI Evidence −38 % y capa `behavior/` acíclica; deriva de uso del paquete H4 diagnosticada (paquete incorrecto, superseded). Detalle: `docs/POST_V5/PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE_RESULT.md`.
**Pendiente antes de H5:** solo Gate C (DT-04, DT-07, DT-08, UX-03). **H5 = NOT_STARTED.**

## 17. Pre-H5 Gate C — Endurecimiento técnico final
`PRE_H5_GATE_C_FINAL_HARDENING = PASS`, `PRE_H5_BLOCKING_DEBT = 0`. Resolución de llamadas entre proyectos con base determinista persistida, segunda plantilla humana (`human/executive`) que prueba independencia de presentación,
UX-03 diferido como `FUTURE_CAPABILITY` y deuda DT-08 cerrada. Detalle: `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_RESULT.md`.
**Siguiente (tras revisión humana explícita): `H5_REAL_IST_VALIDATION_AND_CLOSURE`. H5 = NOT_STARTED.**

## 18. Estado de hitos y cierre de H4
```text
H1 = CLOSED
H2 = CLOSED
H3 = CLOSED
H4 = CLOSED
H5 = NOT_STARTED
V6 = NOT_STARTED
```
`POST_V5_H4_FINAL_HUMAN_DELIVERABLES = CLOSED`, `H4_OWNER_APPROVAL = APPROVED`, `H4_BLOCKING_DEBT = 0`. H1–H5 no se renombran como V6. Las secciones 12 en adelante que describen H4 como pendiente o reabierto son historia previa al cierre. Detalle: `docs/POST_V5/H4_CLOSURE.md`.
