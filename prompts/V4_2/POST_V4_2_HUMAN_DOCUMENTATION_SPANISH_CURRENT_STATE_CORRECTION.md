# LegacyMapper — Corrección de Estado Actual de la Documentación Humana en Español

## MODO

POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION

## MODELO

Claude Opus 4.6

## AUTORIDAD

La traducción al español de la documentación humana Post-V4.2 fue revisada
por el Líder Técnico.

La calidad de traducción fue aprobada, pero se detectaron tres inconsistencias
técnicas provenientes de contenido anterior a las últimas correcciones
Post-V4.2.

Esta ronda es exclusivamente documental.

NO reabre V4.2.

NO implementa V5.

NO modifica producción.

NO modifica tests.

NO modifica manifests/baselines históricos.

NO hace commit ni push.

---

# 1. FUENTE DE VERDAD ACTUAL

Leer obligatoriamente antes de modificar documentación:

PROJECT_STATE.json

docs/V4_2/POST_V4_2_FINAL_APPROVAL_AND_VERSIONING_RESULT.md

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_VERIFICATION.md

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION_RESULT.md

La fuente actual autoritativa es el estado Post-V4.2 FINAL ya versionado.

---

# 2. HECHOS ACTUALES QUE DEBEN QUEDAR REFLEJADOS

Estado final:

TESTS=1810

TEST_FAILURES=0

TEST_ERRORS=0

EXPECTED_FRESH_CLONE_SKIPS=132

ALL_SKIPS_EXPLAINED=true

READINESS=READY

POST_COMMIT_STABILITY=PASS

HISTORICAL_MANIFEST_INTEGRITY=PASS

V4_2_CLOSED=true

V5_IMPLEMENTED=false

NEXT=V5_DESIGN_PENDING

Commit histórico fijo de cierre V4.2:

af7e2099039e791c5a14ff94bf5ad348e8dbb4db

Commit de integración Post-V4.2:

2cadd15ad63749c81fb9c350504f56abd4c36e4d

---

# 3. CORRECCIÓN 1 — CONTEO ACTUAL DE TESTS

En:

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

existen secciones que todavía presentan:

1809 tests descubiertos

como expectativa ACTUAL para un clon nuevo.

Eso ya no es correcto.

1809 corresponde al estado anterior a la incorporación del nuevo test:

test_historical_manifest_integrity_survives_a_later_commit

El estado actual es:

1810 tests descubiertos
0 fallos
0 errores
132 omisiones esperadas cuando los fixtures reales históricos no están presentes.

Actualizar todas las afirmaciones de estado ACTUAL.

IMPORTANTE:

No cambiar referencias HISTÓRICAS legítimas a 1809.

Debe distinguirse claramente:

HISTÓRICO V4.2:
1809 PASS / 0 FAIL / 0 SKIP

CORRECCIÓN INTERMEDIA POST-V4.2:
1809 discovered / 132 skips

ESTADO ACTUAL FINAL:
1810 discovered / 0 failures / 0 errors / 132 expected skips

No reemplazar globalmente "1809" por "1810".

Corregir según contexto.

---

# 4. CORRECCIÓN 2 — BASELINE-01 / MANIFEST HISTÓRICO

El Manual Técnico todavía contiene texto de una solución intermedia descartada
que describe aproximadamente:

- comparar contra HEAD cuando el working tree está dirty;
- comparar contra disco cuando está clean;
- usar `git show HEAD:<path>`.

Esa solución YA NO ES el comportamiento final.

La solución definitiva:

- resuelve el commit histórico fijo de cierre V4.2 desde
  `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`;
- referencia:

  af7e2099039e791c5a14ff94bf5ad348e8dbb4db

- verifica `authoritative_artifacts` contra el contenido de ESE commit
  histórico;
- no depende de HEAD;
- no depende de si el working tree está dirty o clean;
- contempla las representaciones LF/CRLF históricas necesarias;
- está protegida por el test
  `test_historical_manifest_integrity_survives_a_later_commit`.

Actualizar:

- fila BASELINE-01;
- mapa de auditoría;
- deuda/continuidad;
- sección V5 handover si contiene todavía la solución anterior;
- cualquier otra referencia obsoleta.

BASELINE-01 debe permanecer RESOLVED.

No presentar esta corrección como deuda pendiente de V5.

---

# 5. CORRECCIÓN 3 — GLOSARIO

En:

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

la definición:

"Artefacto histórico de cierre frente a documento mutable de estado actual"

dice aproximadamente que los hashes de `authoritative_artifacts` se verifican
contra el "último contenido confirmado (commit)".

Corregirlo.

La semántica exacta debe ser:

los hashes históricos se verifican contra el contenido correspondiente al
commit histórico fijo de cierre V4.2 registrado en la documentación de cierre,
no contra HEAD ni contra el último commit actual del archivo.

Explicar en español natural.

Preservar nombres técnicos.

---

# 6. TESTINFRA-01

TESTINFRA-01 está RESOLVED respecto a fresh-clone reproducibility porque:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

está ahora rastreado como excepción estrecha.

Pero existe deuda residual distinta:

si ese archivo rastreado es eliminado o corrompido manualmente,
`readiness.py` puede todavía lanzar una excepción no controlada en vez de
degradar a BLOCKED.

No describir TESTINFRA-01 como:

"dependencia de archivo no rastreado actualmente existente".

Eso es obsoleto.

Puede describirse como:

RESOLVED, con hardening residual separado.

Actualizar cualquier texto obsoleto del mapa de auditoría / handover.

---

# 7. DOCUMENTO DE RESULTADO DE LA TRADUCCIÓN

Actualizar:

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION_RESULT.md

Añadir una sección:

## CORRECCION_POST_REVISION

Explicar que la revisión humana detectó y corrigió:

1. expectativa actual 1809 -> 1810;
2. semántica intermedia HEAD-based -> commit histórico fijo V4.2;
3. definición del glosario sobre manifest histórico;
4. referencias obsoletas de TESTINFRA-01/BASELINE-01.

No borrar el registro de lo que hizo la ronda original.

Registrar la corrección como amendment posterior.

---

# 8. MANUAL DE USUARIO

Revisar:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

Solo modificarlo si contiene alguna de las inconsistencias anteriores.

No hacer una reescritura general.

Actualmente su descripción de readiness y ARCHITECTURE_EVIDENCE parece
correcta; preservar ese contenido salvo contradicción comprobada.

---

# 9. REGLA DE IDIOMA

Mantener vigente:

Toda documentación destinada principalmente a humanos debe estar escrita en
español.

Preservar sin traducir:

- nombres de clases;
- funciones;
- enums;
- contratos;
- rutas;
- comandos;
- flags;
- estados machine-readable;
- campos JSON;
- hashes;
- SHAs;
- nombres oficiales de tecnologías.

---

# 10. ARCHIVOS PERMITIDOS

Esperado:

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md
docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md
docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_STANDARDIZATION_RESULT.md

Opcional solamente si se encuentra inconsistencia real:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

No modificar:

legacy_documenter/**
tests/**
PROJECT_STATE.json
output/v4_2_r8/**
output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

---

# 11. VALIDACIÓN

Buscar explícitamente en los tres documentos:

"1809"
"1810"
"HEAD"
"git show HEAD"
"TESTINFRA-01"
"BASELINE-01"
"último contenido"
"commit histórico"
"ARCHITECTURE_EVIDENCE"

Clasificar cada ocurrencia como:

HISTORICA_CORRECTA
ACTUAL_CORRECTA
OBSOLETA_CORREGIDA

No reemplazar números o términos globalmente.

---

# 12. TESTS

No es necesario ejecutar la suite completa.

Producción y tests no cambian.

Realizar validación documental únicamente.

PRODUCTION_CODE_CHANGED=false
TESTS_CHANGED=false
REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

---

# 13. NUEVO RESULTADO

Crear:

docs/V4_2/POST_V4_2_HUMAN_DOCUMENTATION_SPANISH_CURRENT_STATE_CORRECTION_RESULT.md

Todo en español.

Secciones:

## ESTADO
## PROBLEMAS_DETECTADOS
## CONTEO_DE_TESTS_CORREGIDO
## MANIFEST_HISTORICO_CORREGIDO
## TESTINFRA_01
## BASELINE_01
## GLOSARIO_CORREGIDO
## MANUAL_DE_USUARIO
## MANUAL_TECNICO
## RESULTADO_DE_ESTANDARIZACION_ACTUALIZADO
## IDENTIFICADORES_PRESERVADOS
## VALIDACION_DOCUMENTAL
## CODIGO_DE_PRODUCCION_MODIFICADO
## TESTS_MODIFICADOS
## PROVEEDOR_IA_REAL
## IST_REAL_ACCEDIDO
## ESTADO_V4_2
## ESTADO_V5
## ESTADO_GIT
## DECISION
## SIGUIENTE

Esperado:

ESTADO=COMPLETO

CURRENT_TEST_DISCOVERY_DOCUMENTED=1810

HISTORICAL_V4_2_TESTS_PRESERVED=1809

POST_COMMIT_STABILITY_DOCUMENTED=PASS

HISTORICAL_MANIFEST_REFERENCE=af7e2099039e791c5a14ff94bf5ad348e8dbb4db

CODIGO_DE_PRODUCCION_MODIFICADO=false

TESTS_MODIFICADOS=false

PROVEEDOR_IA_REAL=0

IST_REAL_ACCEDIDO=false

V4_2_REABIERTO=false

V5_IMPLEMENTADO=false

DECISION=DOCUMENTACION_HUMANA_EN_ESPAÑOL_Y_ESTADO_ACTUAL_LISTA_PARA_REVISION

SIGUIENTE=REVISION_FINAL_DOCUMENTACION_ESPAÑOL

---

# 14. GIT

No commit.

No push.

No modificar PROJECT_STATE.json.

Detenerse para revisión humana.