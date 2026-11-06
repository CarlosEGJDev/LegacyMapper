# LegacyMapper — Aprobación y Versionado de Documentación Humana en Español

## MODO

POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_APPROVAL_AND_VERSIONING

## MODELO

Claude Opus 4.6

## AUTORIDAD

El Líder Técnico ha revisado y aprobado:

- la traducción al español de la documentación humana actual;
- la corrección posterior de consistencia con el estado final Post-V4.2.

Esta ronda debe únicamente:

1. verificar el estado documental aprobado;
2. versionar los cambios;
3. actualizar continuidad si corresponde;
4. dejar el repositorio limpio;
5. detenerse antes de V5.

No reabrir V4.2.

No iniciar V5.

---

# 1. DOCUMENTOS APROBADOS

Versionar los cambios pendientes aprobados asociados a:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/PROJECT_RECOVERY.md

docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION_RESULT.md

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION_RESULT.md

prompts/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION.md

prompts/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION.md

y cualquier archivo estrictamente necesario de esta propia ronda.

El git diff/status real es autoritativo.

No inventar archivos ausentes.

---

# 2. REGLA DOCUMENTAL PERMANENTE

Confirmar que:

docs/GENERATED_ARTIFACT_POLICY.md

contiene la regla permanente:

Toda documentación nueva o mantenida destinada principalmente a humanos debe
estar redactada en español.

Preservar en idioma original:

- identificadores técnicos;
- clases;
- funciones;
- enums;
- contratos;
- nombres de archivo/ruta;
- comandos;
- opciones CLI;
- estados machine-readable;
- campos JSON;
- hashes;
- SHA de Git;
- nombres oficiales de tecnologías/productos.

Los documentos históricos de cierre/resultado no se traducen retroactivamente.

---

# 3. ESTADO TÉCNICO QUE DEBE PRESERVARSE

Mantener documentado:

CURRENT_TEST_DISCOVERY=1810

CURRENT_TEST_FAILURES=0

CURRENT_TEST_ERRORS=0

EXPECTED_FRESH_CLONE_SKIPS=132

ALL_SKIPS_EXPLAINED=true

READINESS=READY

POST_COMMIT_STABILITY=PASS

HISTORICAL_MANIFEST_INTEGRITY=PASS

V4_2_CLOSED=true

V5_IMPLEMENTED=false

NEXT=V5_DESIGN_PENDING

Commit histórico de cierre V4.2:

af7e2099039e791c5a14ff94bf5ad348e8dbb4db

Commit Post-V4.2 anterior:

2cadd15ad63749c81fb9c350504f56abd4c36e4d

No modificar esos hechos.

---

# 4. VALIDACIÓN PRE-COMMIT

Verificar documentalmente:

- Manual de Usuario en español;
- Manual Técnico en español;
- Glosario en español;
- PROJECT_RECOVERY en español;
- GENERATED_ARTIFACT_POLICY en español;
- regla documental permanente presente;
- ninguna ruta/comando/identificador técnico traducido por error;
- Manual Técnico distingue correctamente 1809 histórico / 1809 intermedio / 1810 actual;
- BASELINE-01 usa commit histórico fijo, no HEAD;
- TESTINFRA-01 no se describe como dependencia actualmente no rastreada;
- Glosario usa commit histórico fijo;
- V5 sigue NOT_IMPLEMENTED.

No modificar producción ni tests.

---

# 5. PROJECT_STATE

Actualizar PROJECT_STATE.json solo si es necesario para continuidad.

No cambiar:

current_version_status = V4_2_FORMALLY_CLOSED

No inventar V4.3.

No marcar V5 como implementado.

Registrar, usando la estructura existente si es apropiado:

human_documentation_language = ES

human_documentation_spanish_standardization = COMPLETE

human_documentation_spanish_current_state_correction = COMPLETE

latest_result_path =
docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_APPROVAL_AND_VERSIONING_RESULT.md

next = V5_DESIGN_PENDING

Si introducir nuevos campos rompe el estilo/contrato actual de PROJECT_STATE,
usar el mecanismo existente equivalente en lugar de inventar una estructura
paralela.

---

# 6. TESTS

Producción y tests no fueron modificados en estas rondas documentales.

No es obligatorio ejecutar la suite completa antes del commit.

Sin embargo, ejecutar al menos:

python main.py readiness

Esperado:

READINESS=READY
EXIT_CODE=0
provider_calls=0
real_llm_calls=0

Opcionalmente ejecutar una validación ligera de JSON/paths/documentación.

No acceder a IST real.

No invocar proveedor de IA real.

---

# 7. RESULTADO

Crear:

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_APPROVAL_AND_VERSIONING_RESULT.md

Todo el documento debe estar en español.

Secciones obligatorias:

## ESTADO
## APROBACION_DEL_LIDER_TECNICO
## DOCUMENTOS_VERSIONADOS
## REGLA_DE_IDIOMA
## VALIDACION_DOCUMENTAL
## ESTADO_TECNICO_PRESERVADO
## PROJECT_STATE
## READINESS
## CODIGO_DE_PRODUCCION_MODIFICADO
## TESTS_MODIFICADOS
## PROVEEDOR_IA_REAL
## IST_REAL_ACCEDIDO
## GIT_COMMIT
## GIT_PUSH
## GIT_STATUS_FINAL
## ESTADO_V4_2
## ESTADO_V5
## DECISION
## SIGUIENTE

---

# 8. GIT

Antes de commit:

git status --short
git diff --stat
git diff
git diff --cached

Stage únicamente los archivos aprobados de esta ronda documental y los
archivos de continuidad estrictamente necesarios.

No incluir salidas operacionales reales.

No incluir archivos generados no relacionados.

Commit sugerido:

Post-V4.2: estandarizar documentación humana en español

Registrar SHA exacto.

Push al upstream existente.

Verificar:

git rev-parse HEAD
git rev-parse origin/main

Deben coincidir.

---

# 9. POST-COMMIT

Después del commit/push:

python main.py readiness

Debe continuar:

READY
exit 0
provider_calls=0
real_llm_calls=0

git status --short

debe quedar limpio.

---

# 10. LÍMITES

PRODUCTION_CODE_CHANGED=false

TESTS_CHANGED=false

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

V4_2_REOPENED=false

V5_IMPLEMENTED=false

No modificar:

legacy_documenter/**
tests/**
output/v4_2_r8/**
output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

---

# 11. ÉXITO

Solo si todo pasa:

ESTADO=COMPLETO

DOCUMENTACION_HUMANA_IDIOMA=ES

DOCUMENTACION_HUMANA_ESPAÑOL=APROBADA_Y_VERSIONADA

READINESS=READY

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

PRODUCTION_CODE_CHANGED=false

TESTS_CHANGED=false

V4_2_CLOSED=true

V5_IMPLEMENTED=false

GIT_PUSH=PASS

HEAD_EQUALS_ORIGIN_MAIN=true

GIT_STATUS=CLEAN

DECISION=DOCUMENTACION_HUMANA_EN_ESPAÑOL_FORMALMENTE_VERSIONADA

SIGUIENTE=V5_DESIGN_PENDING

Detenerse.

No iniciar V5 en esta misma tarea.