# Post-V5 — Human Experience & AI Documentation (roadmap H1–H5)

Estado: `PLANNED` (nada de H1–H5 está implementado). Esto **no es V6**. Autoridad de estado: `PROJECT_STATE.json` (`active_initiative`, `initiative_status`).

Convención de este documento: *[hecho]* verificado y vigente · *[limitación]* aceptada · *[capacidad futura]* no existe · *[candidato de diseño]* no decidido.

## 1. Propósito
Que una persona entienda cómo funciona un sistema legado **sin abrir el código**, según su nivel, y que la IA pueda interpretar ese sistema a partir de conocimiento determinista ya persistido, sin reanalizar.

## 2. Por qué existe esta fase
V5 cerró el motor determinista (Evidence, cache, adapters, proveedor de IA, revisión humana, contratos de consumers). La corrección técnica está probada; la **comprensión humana** no. La documentación actual es correcta pero demasiado técnica y poco visual para audiencias amplias.

## 3. Qué ya provee V5 *[hecho]*
Evidence normalizada y persistida; `documentation_v52/` (perfiles `general/` y `developer/`); `ai_context/` y `consumer_projection/`; propuestas de IA con revisión humana y conocimiento canónico (nunca automáticos); segmentación de flujos; Consumer API de solo lectura; adapters VB.NET WebForms/Oracle y Python (piloto circular). Baseline: tag `v5` → `e831a2f84d2749b4452e06860521b3171093c7b9`; analyzer v3 `f05b2de4…`.

## 4. Brecha principal
* **HX-01** documentación humana aún demasiado técnica / poco visual.
* **HX-02** HTML/PDF visual no productizado.
* **HX-03** proyección visual estructurada (módulos, casos de uso) no implementada.
Detalle método/clase **no** es el objetivo primario de esta fase; se conserva como evidencia profunda, no como narrativa principal.

## 5. Requisito: reutilizar el output determinista para IA (AI-only)
Modos: **A** determinista (`full` sin IA) *[hecho]*; **B** `full --allow-ai-interpretation` (analiza + interpreta en una corrida) *[hecho]*; **C** *AI-only / interpret-existing* *[capacidad futura]*:

```text
output determinista existente → validar baseline → reutilizar Evidence / AI context / manifests
→ interpretación IA → propuestas / documentación humana
```
Objetivo: **analizar una vez, interpretar muchas veces** (esencial en repositorios grandes como IST). **Hoy no existe ningún comando público para esto** (UX-02).
Puerta obligatoria antes de invocar un provider: output existe; Evidence manifest existe y valida; schema soportado; analyzer fingerprint conocido; AI context existe; provenance válida; identidad de fuente/repositorio disponible; baseline no corrupto ni obsoleto. Si falla → estado conceptual `AI_ONLY_INPUT_INVALID`, **sin llamada al provider**. Nombres candidatos del comando *[candidato de diseño, no fijado]*: `interpret`, `ai-only`, `interpret-existing`. Importa el contrato, no el nombre.

## 6. Roadmap H1–H5
**H1 — AI-only desde conocimiento determinista persistido.** Output válido existente → interpretación IA, sin reescanear la fuente. Preserva: sin provider ante baseline inválido; provenance; validación de schema/fingerprint; proposal ≠ canonical; autoridad de revisión humana.

**H2 — Documentación humana por nivel de audiencia.** Tres perfiles: `executive`, `functional`, `technical-overview`. Contenido primario: sistema, módulos/áreas funcionales, proyectos, capas, vistas/pantallas, dependencias principales, flujos de negocio, interacciones de datos, integraciones externas, áreas no resueltas. Sin método/clase como narrativa por defecto.

**H3 — Proyecciones visuales estructuradas.** La IA no inventa diagramas libremente: `Evidence → interpretación IA estructurada → modelo de diagrama validado → renderer determinista → SVG/PNG/HTML/PDF`. Tipos posibles: mapa del sistema, de módulos, proyecto/capa, dependencias, flujo de negocio, casos de uso, interacción de datos, integraciones externas. Cada relación importante conserva trazabilidad a evidencia o se marca como interpretación/inferencia de IA.

**H4 — Entregables humanos finales.** `SYSTEM_OVERVIEW`, `MODULE_MAP`, `FUNCTIONAL_AREAS`, `USE_CASES`, `BUSINESS_FLOWS`, `ARCHITECTURE_OVERVIEW`, `PROJECT_LAYER_MAP`, `DATA_INTERACTIONS`, `EXTERNAL_INTEGRATIONS`, `KNOWN_UNRESOLVED_AREAS`. Formato primario: HTML navegable; secundario: PDF; artefactos de render: SVG/PNG. No prometer interactividad rica hasta implementarla y validarla.

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
| UX-01 | `full` sobre un repositorio inexistente devuelve SUCCESS con análisis vacío | defecto candidato |
| UX-02 | No hay comando público AI-only para reutilizar un output determinista | capacidad futura |
| UX-03 | No hay CLI de consumers (solo API Python) | limitación aceptada / capacidad futura |
| HX-01 | Docs humanas demasiado técnicas / poco visuales | brecha de producto |
| HX-02 | HTML/PDF visual no productizado | brecha de producto |
| HX-03 | Proyección visual estructurada (casos de uso/módulos) no implementada | brecha de producto |

Más el backlog de la sección 7 y el ledger de V5 intacto (`docs/V5/V5_FINAL_DEBT_LEDGER.json`: BLOCKING 0 / FUTURE_PHASE 14 / OBSERVATION 15 / HISTORICAL_COMPATIBILITY 5).

## 11. Primera ronda recomendada
**H1-R1 — AI-only contract, baseline validation and UX design.** Diseño y contrato (puerta de validación, estados, relación con `full --allow-ai-interpretation`, nombre del comando), con medición sobre output real. Sin implementar H2–H5. Regla de ejecución: un hito en un prompt cuando sea razonable; máximo 3 rondas de revisión/corrección por defecto (ver `LEGACYMAPPER_LESSONS_LEARNED.md` §37.1).
