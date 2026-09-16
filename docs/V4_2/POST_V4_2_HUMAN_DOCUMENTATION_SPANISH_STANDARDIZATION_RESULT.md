# Post-V4.2 — Estandarización al Español de la Documentación Humana — Resultado

## ESTADO

COMPLETO

## OBJETIVO

Traducir y estandarizar al español la documentación actual de LegacyMapper destinada principalmente a
lectores humanos, preservando el significado técnico exacto, el comportamiento actual, las rutas de
archivo, los nombres de contrato, los estados, los comandos, los identificadores, los hashes, los SHA de
commit de Git, los conteos de tests, los límites de versión y los hechos históricos. Esta es una conversión
fiel de idioma sobre contenido ya aprobado, no una reescritura desde memoria.

## REGLA_DE_IDIOMA

A partir de esta ronda, toda documentación nueva o mantenida destinada principalmente a lectores humanos
debe redactarse en español. Los identificadores técnicos, el código, los comandos, los estados legibles por
máquina, los nombres de contrato, las rutas, los nombres de protocolo y los nombres oficiales de
tecnología/producto permanecen en su forma original. La regla se registró explícitamente en
`docs/GENERATED_ARTIFACT_POLICY.md` (sección `## Idioma de la documentación para humanos`), por ser la
ubicación natural de política documental ya existente en el repositorio.

## DOCUMENTOS_ACTUALIZADOS

Traducidos íntegramente al español, preservando estructura, tablas, bloques de código, comandos, rutas y
referencias cruzadas:

- `docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md` (obligatorio)
- `docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md` (obligatorio)
- `docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md` (obligatorio)
- `docs/PROJECT_RECOVERY.md` (opcional — inspeccionado y traducido: es documentación viva y operativa,
  no un documento de cierre histórico)
- `docs/GENERATED_ARTIFACT_POLICY.md` (opcional — inspeccionado y traducido; además recibió la nueva
  sección de política de idioma, sección 12 del prompt de esta ronda)

Ningún nombre de archivo fue cambiado.

## DOCUMENTOS_NO_MODIFICADOS

- `PROJECT_STATE.json` — no traducido, según instrucción explícita (es un contrato legible por máquina).
- `AGENTS.md`, `CLAUDE.md` — no traducidos en esta ronda; ya están escritos para ser neutrales al agente de
  desarrollo y no se evidenció ninguna regla del repositorio que exija su localización a idioma humano en
  este momento.
- Todos los prompts bajo `prompts/` — no traducidos retroactivamente, según instrucción explícita.
- Todos los documentos de resultado/cierre históricos bajo `docs/V4/`, `docs/V4_1/`, `docs/V4_2/` distintos
  de los tres manuales obligatorios (por ejemplo, `V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`,
  `POST_V4_2_FINAL_APPROVAL_AND_VERSIONING_RESULT.md`, todos los documentos `V4_2_R*_RESULT.md`) — se
  preservan como evidencia histórica en el idioma en que fueron aprobados, según instrucción explícita de
  no traducir en masa documentos de resultado históricos.
- `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` — documentación V3 ya aprobada en
  español desde su origen; fuera del alcance de esta ronda (no listados como documentos a inspeccionar).

No hubo ningún caso de incertidumbre sobre si un documento era evidencia histórica o documentación viva
actual que requiriera reportarse sin modificar; la clasificación arriba fue clara en cada caso según las
reglas de la sección 4 del prompt de esta ronda.

## IDENTIFICADORES_TECNICOS_PRESERVADOS

Verificados sin traducir en los cinco documentos actualizados (muestra no exhaustiva): `RunResult`,
`StageStatus`, `StageResult`, `RunStatus`, `StageId`, `LegacyMapperPluginKnowledge`,
`CanonicalKnowledgeEntry`, `KnowledgeStatement`, `EvidenceRef`, `Provenance`, `Proposal`, `ApprovalDecision`,
`FakeLLMProvider`, `CopilotProvider`, `GeminiProvider`, `ProviderRegistry`, `LLMProvider`, `LLMRequest`,
`LLMResponse`; los literales de estado `READY`, `BLOCKED`, `SUCCESS`, `PARTIAL`, `FAILED`, `USAGE`,
`NOT_RUN`, `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, `PENDING_TECHNICAL_LEAD_REVIEW`, `READY_FOR_REVIEW`,
`NOT_IMPLEMENTED`, `APPROVED_DESIGN_ONLY`, `V5_DESIGN_PENDING`; todos los comandos de CLI
(`python main.py analyze/full/readiness`, `--allow-ai-interpretation`, `--flow-max-depth`, `--output`,
`--exclude`, `--verbose`); todas las rutas de archivo y de módulo Python; todos los nombres de campo JSON
(`ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval`, `provider_calls`,
`real_llm_calls`, etc.); todos los comandos de Git citados; los nombres de tecnología/producto (.NET
Framework, VB.NET, ASP.NET Web Forms, Oracle, GitHub Copilot, Gemini, Python).

## CONSISTENCIA_TECNICA

Verificación de consistencia documental realizada (sin ejecutar la suite completa de tests, según lo
permitido por la sección 14 del prompt de esta ronda, dado que no se modificó producción ni tests):

- Ningún identificador de código fue traducido accidentalmente.
- Ningún comando de CLI fue alterado.
- Ninguna ruta fue alterada.
- Ningún hash ni SHA de commit fue alterado (verificado por grep: el SHA histórico de cierre de V4.2
  `af7e2099039e791c5a14ff94bf5ad348e8dbb4db` aparece intacto donde el documento original lo citaba).
- Ningún valor/enum de estado fue traducido (verificado por grep en los cinco documentos: `SUCCESS`,
  `PARTIAL`, `FAILED`, `USAGE`, `READY`, `NOT_RUN`, `SKIPPED_DUE_TO_UPSTREAM_FAILURE`,
  `PENDING_TECHNICAL_LEAD_REVIEW` conservados literalmente).
- Ningún campo JSON fue traducido.
- Ningún conteo histórico fue cambiado (1809, 1810, 132, 676, 1625 preservados exactamente donde el
  original los citaba, incluyendo el contraste histórico 1809 vs. la primera ejecución en clon nuevo 1625
  en el Manual Técnico §16).
- Ninguna capacidad de V5 se describe como ya implementada; el Manual Técnico §23 y el Manual de Usuario
  §4.1 mantienen explícitamente que la agnosticidad de lenguaje/framework/base de datos/proveedor de IA es
  trabajo de V5, no implementado.
- El Runtime de Plugin se describe consistentemente como `NOT_IMPLEMENTED` en los tres manuales.
- La superficie de aprobación se describe consistentemente como `NOT_IMPLEMENTED` (solo diseño aprobado)
  en los tres manuales.

## DATOS_HISTORICOS_PRESERVADOS

Sin alterar en ningún documento traducido: `V4_CLOSED=true`, `V4_1_CLOSED=true`, `V4_2_CLOSED=true`,
`POST_V4_2_MAINTENANCE=FORMALLY_VERSIONED`, `TESTS=1810` (Manual de Usuario/Técnico no citan un conteo de
tests fijo propio distinto del histórico 1809/1625 ya presente en el contenido original — no se introdujo
ningún conteo nuevo), `TEST_FAILURES=0`, `TEST_ERRORS=0`, `EXPECTED_FRESH_CLONE_SKIPS=132`,
`ALL_SKIPS_EXPLAINED=true`, `READINESS=READY`, `PLUGIN_RUNTIME=NOT_IMPLEMENTED`, `V5_IMPLEMENTED=false`,
`NEXT=V5_DESIGN_PENDING`. Commit histórico de cierre de V4.2: `af7e2099039e791c5a14ff94bf5ad348e8dbb4db`
(preservado en `docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_VERIFICATION.md`, no
modificado por esta ronda). Commit de integración Post-V4.2: `2cadd15ad63749c81fb9c350504f56abd4c36e4d`
(no citado en el texto original de los documentos traducidos; no se introdujo).

## DEUDA_Y_LIMITACIONES_PRESERVADAS

Preservadas sin suavizar ni eliminar, en el Manual Técnico §20 y en las referencias cruzadas del Manual de
Usuario: F-05 `DEFERRED_BY_DETERMINISM_CONTRACT`, F-06 `PRESERVED_OBSERVATION`, F-07
`PRESERVED_OBSERVATION`, deuda de escala de `WEB_ENTRY_POINTS.md` (DEBT-DOC-01), deuda de escala de
`PROJECT_DEPENDENCIES.md` (DEBT-DOC-02), deuda de mantenibilidad de
`technical_documentation_renderer.py` (MAINT-01), el endurecimiento pendiente de `readiness.py` ante
`ARCHITECTURE_EVIDENCE.json` ausente/corrupto, AI-01 (`GeminiProvider` existe pero `ProviderRegistry` no lo
expone), la superficie de aprobación `NOT_IMPLEMENTED` (APPR-01), el runtime de Plugin `NOT_IMPLEMENTED`
(PLUGIN-01), y el riesgo conocido R6-01 (intermitencia no reproducible desde el cierre formal de V4.2).

## CAMBIOS_DE_POLITICA_DOCUMENTAL

Se añadió la sección `## Idioma de la documentación para humanos` al final de
`docs/GENERATED_ARTIFACT_POLICY.md`, declarando la regla permanente de que toda documentación nueva o
mantenida destinada principalmente a humanos debe escribirse en español, con las mismas excepciones de
identificadores técnicos descritas arriba, y aclarando que `PROJECT_STATE.json`, `AGENTS.md` y `CLAUDE.md`
no quedan sujetos automáticamente a la regla, y que los documentos históricos de cierre/resultado no se
traducen retroactivamente. No se creó ningún archivo de política nuevo, según la preferencia expresada en
la sección 12 del prompt de esta ronda.

## CODIGO_DE_PRODUCCION_MODIFICADO

false

## TESTS_MODIFICADOS

false

## PROVEEDOR_IA_REAL

0

## IST_REAL_ACCEDIDO

false

## ESTADO_V4_2

V4.2 permanece formalmente cerrada. Esta ronda no la reabrió.

## ESTADO_V5

No implementada. Esta ronda no comenzó V5.

## ESTADO_GIT

Sin commit. Sin push. `PROJECT_STATE.json` no fue modificado en esta ronda, según instrucción explícita.
Los cinco documentos traducidos y este documento de resultado permanecen como cambios pendientes en el
árbol de trabajo, a la espera de la revisión del Líder Técnico antes del versionado.

## DECISION

DOCUMENTACION_HUMANA_EN_ESPAÑOL_LISTA_PARA_REVISION_DEL_LIDER_TECNICO

## SIGUIENTE

REVISION_HUMANA_DOCUMENTACION_ESPAÑOL

## CORRECCION_POST_REVISION

El Líder Técnico revisó la traducción al español de la documentación humana Post-V4.2 producida por esta
ronda. La calidad de la traducción fue aprobada, pero la revisión detectó tres inconsistencias técnicas que
provenían de contenido fuente anterior a las correcciones Post-V4.2 más recientes (la corrección de
estabilidad post-commit del manifiesto histórico y la aprobación/versionado final Post-V4.2), las cuales
ocurrieron después de que el contenido original en inglés de los manuales ya existiera. Esta sección registra
la corrección aplicada como un amendment posterior, sin borrar el registro de lo que hizo la ronda original
arriba.

Se detectaron y corrigieron, en
`docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION_RESULT.md`:

1. La expectativa ACTUAL de conteo de tests para un clon nuevo, que todavía decía 1809 descubiertos en
   varios pasajes del Manual Técnico, se actualizó a 1810 descubiertos — sin alterar ninguna referencia
   HISTÓRICA legítima a 1809 (la baseline de cierre formal de V4.2 sigue citada como
   `"1809_PASS_0_FAIL_0_SKIP"`).
2. La descripción de la solución de verificación del manifiesto histórico, que todavía presentaba la
   semántica intermedia basada en HEAD/árbol de trabajo sucio-o-limpio como si fuera el comportamiento
   final, se actualizó para describir la solución definitiva: anclada al commit histórico fijo de cierre de
   V4.2 (`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`), independiente de HEAD y del estado del árbol de
   trabajo, protegida por `test_historical_manifest_integrity_survives_a_later_commit`.
3. La definición del Glosario sobre el artefacto histórico de cierre frente al documento mutable de estado
   actual, que describía los hashes de `authoritative_artifacts` como verificados contra el "último
   contenido confirmado (commit)", se corrigió para reflejar que se verifican contra el commit histórico
   fijo de cierre de V4.2, nunca contra HEAD ni contra el último commit actual del archivo.
4. Las referencias obsoletas de TESTINFRA-01/BASELINE-01 en la tabla de deuda técnica (§20), el mapa de
   auditoría (§21) y el traspaso a V5 (§23) del Manual Técnico se actualizaron: BASELINE-01 permanece
   `RESOLVED` de forma definitiva (no presentado como deuda pendiente de V5); TESTINFRA-01 permanece
   `RESOLVED` respecto a la reproducibilidad en clon nuevo, con el endurecimiento residual reformulado
   correctamente como manejo defensivo ante la eliminación/corrupción posterior de un archivo *ya
   rastreado*, no como "una dependencia de un archivo actualmente no rastreado".

Ver `docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION_RESULT.md` para el detalle
completo de esta corrección, incluyendo la validación documental exhaustiva realizada.
