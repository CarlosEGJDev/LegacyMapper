# LegacyMapper — Post-V4.2 GitHub Repository Inventory and Cleanup Plan

## MODE

POST_V4_2_REPOSITORY_AUDIT_ONLY

## MODEL

Claude Opus 4.6

## CONTEXT

LegacyMapper V4.2 está formalmente cerrado.

Estado autorizado:

STATUS=V4_2_FORMALLY_CLOSED
V4_2_CLOSED=true
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
LATEST_COMPLETED_ROUND=V4.2-R8
LATEST_APPROVED_ROUND=V4.2-R8
TESTS=1809_PASS_0_FAIL_0_SKIP
READINESS=READY
V5_IMPLEMENTED=false
NEXT=V5_DESIGN_PENDING

Baseline final V4.2 aprobado:

output/v4_2_r8/V4_2_FINAL_BASELINE.json

SHA256:

4e80b2ac757227204178d46c3eddb0fdebd166ee40c6453bbbae2c45e184d5ed

Manifest final V4.2 aprobado:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

SHA256:

1ed09ad06daaa698ed3bf0b7d119fffdea41a610b6cc230d79bfedebb8cef7e0

V4, V4.1 y V4.2 NO deben reabrirse.

Esta tarea NO implementa V5.

Esta tarea NO modifica producción.

Esta tarea NO elimina archivos.

Esta tarea NO mueve archivos.

Esta tarea NO modifica .gitignore.

Esta tarea NO realiza commit ni push.

El objetivo es exclusivamente inspeccionar el repositorio y producir un plan de limpieza seguro antes de comenzar V5.

---

# 1. OBJETIVO

Determinar qué archivos y directorios necesita conservar LegacyMapper en GitHub para:

1. continuar el desarrollo de V5 desde un clon limpio;
2. conservar el código fuente completo;
3. conservar los tests necesarios;
4. conservar contratos, configuración y herramientas necesarias;
5. conservar documentación técnica y de usuario relevante;
6. conservar prompts y evidencia histórica útil de V1, V2, V3, V4, V4.1 y V4.2;
7. mantener continuidad agent-neutral;
8. permitir auditoría histórica del proyecto;
9. permitir comprender por qué se tomaron decisiones importantes;
10. mantener reproducibilidad razonable de las versiones cerradas;
11. evitar subir resultados generados por análisis de sistemas legacy;
12. evitar subir temporales, caches, logs, artefactos locales y archivos regenerables innecesarios;
13. mantener el repositorio GitHub en un tamaño razonable.

Objetivo orientativo:

Preferir un repositorio claramente inferior a 100 MB si es razonablemente posible.

Se acepta hasta aproximadamente 200 MB únicamente si existe una justificación técnica o histórica clara.

NO utilizar el límite de tamaño como autorización para eliminar evidencia necesaria.

---

# 2. PRINCIPIO FUNDAMENTAL

Distinguir explícitamente:

SOURCE / CONTRACT / TEST / GOVERNANCE / HISTORY

de:

GENERATED ANALYSIS OUTPUT / CACHE / TEMPORARY / LOCAL ARTIFACT / REGENERABLE OUTPUT

Los resultados producidos al analizar sistemas legacy NO forman parte del repositorio fuente de LegacyMapper.

Especialmente:

output/v4_2_r7_ist_operacional/

es evidencia local del piloto real y NO debe incorporarse a Git.

No asumir, sin embargo, que todo directorio llamado output/ puede eliminarse.

Existen artefactos de baseline, manifest, fixtures o evidencia de cierre que pueden ser necesarios para reproducibilidad o continuidad histórica.

Analizar cada caso.

---

# 3. REGLA DE SEGURIDAD

Esta ronda es READ-ONLY respecto de la estructura del repositorio.

PROHIBIDO:

- eliminar archivos;
- mover archivos;
- renombrar archivos;
- modificar archivos de producción;
- modificar tests;
- modificar documentación histórica;
- modificar prompts históricos;
- modificar PROJECT_STATE.json;
- modificar AGENTS.md;
- modificar CLAUDE.md;
- modificar .gitignore;
- ejecutar limpieza automática;
- ejecutar git rm;
- ejecutar commit;
- ejecutar push;
- implementar V5;
- acceder al repositorio real IST/Operacional;
- realizar llamadas reales a proveedores de IA.

Si se encuentra algo problemático, solamente documentarlo.

---

# 4. INVENTARIO DEL REPOSITORIO

Inspeccionar el repositorio completo.

Generar métricas como mínimo de:

- número total de archivos;
- tamaño total del working tree;
- tamaño aproximado de archivos actualmente tracked por Git;
- número y tamaño por directorio principal;
- número y tamaño por extensión;
- archivos individuales de mayor tamaño;
- directorios individuales de mayor tamaño;
- archivos tracked;
- archivos untracked relevantes;
- archivos ignorados relevantes;
- artefactos generados detectados.

Cuando sea útil, diferenciar:

- tamaño del working tree;
- tamaño de contenido actualmente versionado;
- tamaño de .git.

No confundir el tamaño de .git/history con el tamaño del snapshot actual.

Si .git es grande, reportarlo separadamente.

---

# 5. CLASIFICACIÓN

Clasificar archivos/directorios usando exactamente:

KEEP
EXCLUDE
REVIEW

## KEEP

Usar cuando el contenido deba permanecer disponible en GitHub.

Ejemplos conceptuales:

- código fuente;
- tests;
- fixtures sintéticos necesarios;
- configuración necesaria;
- AGENTS.md;
- CLAUDE.md;
- PROJECT_STATE.json;
- contratos;
- schemas;
- herramientas necesarias;
- documentación vigente;
- manuales;
- glosarios;
- roadmap;
- prompts necesarios;
- resultados de cierre/versionado que forman parte de la evidencia histórica;
- evidencia histórica necesaria para comprender decisiones o contratos;
- baselines/manifests cuya conservación sea necesaria para verificar cierres históricos.

## EXCLUDE

Usar únicamente cuando sea seguro mantener el contenido fuera de Git.

Ejemplos conceptuales:

- resultados completos de análisis de repositorios legacy;
- outputs reales del IST;
- caches;
- __pycache__;
- .pytest_cache;
- logs locales;
- archivos temporales;
- artefactos del IDE;
- entornos virtuales;
- resultados regenerables que no forman parte de contratos ni evidencia histórica;
- outputs manuales locales;
- archivos accidentales.

## REVIEW

Usar cuando exista duda razonable.

Ejemplos:

- evidencia histórica grande;
- artefactos aparentemente duplicados;
- outputs que podrían participar en tests;
- archivos antiguos que podrían ser necesarios para trazabilidad;
- baselines antiguos cuyo papel no esté claro;
- documentos reemplazados pero potencialmente necesarios para auditoría.

Ante duda:

REVIEW > EXCLUDE.

Nunca clasificar como EXCLUDE solamente porque un archivo sea antiguo.

---

# 6. EVIDENCIA HISTÓRICA

LegacyMapper debe conservar suficiente evidencia para que otro desarrollador o agente pueda comprender la evolución:

V1
V2
V3
V4
V4.1
V4.2

Revisar especialmente:

codex/
docs/
prompts/
output/

No renombrar ni reorganizar evidencia histórica en esta ronda.

Los nombres históricos como codex/V1, codex/V2 y codex/V3 deben preservarse.

Determinar qué contenido constituye:

- evidencia histórica necesaria;
- resultado generado innecesario;
- duplicado;
- snapshot;
- baseline;
- manifest;
- cierre;
- prompt;
- resultado de ronda;
- artefacto reproducible;
- artefacto local.

No eliminar la historia documental solamente para reducir tamaño.

---

# 7. CONTINUIDAD HACIA V5

Realizar una revisión específica:

"¿Podría un programador o un nuevo agente clonar este repositorio y comenzar V5 correctamente utilizando solamente los archivos clasificados KEEP?"

Verificar que KEEP cubra al menos:

- bootstrap del agente;
- estado actual;
- arquitectura;
- contratos;
- código;
- tests;
- fixtures;
- herramientas;
- documentación;
- decisiones;
- deuda conocida;
- V4.2 final;
- requisitos pendientes para V5.

Identificar cualquier archivo actualmente local/untracked que debería estar versionado para que esa respuesta sea YES.

No añadirlo todavía.

Solo reportarlo.

---

# 8. RESULTADOS DE ANÁLISIS LEGACY

Crear una política clara para outputs de ejecuciones futuras.

La política debe distinguir:

A. OUTPUT OPERACIONAL

Resultados generados al analizar un sistema legacy concreto.

Por defecto:

NO GIT.

Ejemplos:

- indexes generados;
- documentación generada para un sistema analizado;
- contexto;
- ai_context;
- proposals;
- registros de análisis;
- resultados del piloto real.

B. OUTPUT DE DESARROLLO / CONTRATO

Artefactos pequeños necesarios para:

- tests;
- fixtures;
- baselines;
- manifests;
- verificación de contratos;
- evidencia formal de una versión cerrada.

Pueden ser KEEP cuando exista justificación.

No crear una regla global que ignore indiscriminadamente todo output/.

---

# 9. .GITIGNORE

Revisar el .gitignore actual.

NO modificarlo.

Proponer en el informe qué reglas deberían:

- mantenerse;
- añadirse;
- corregirse;
- hacerse más específicas.

Especial atención a evitar que una regla amplia sobre output/ o docs/ o prompts/ o fixtures elimine artefactos históricos necesarios.

Preparar una propuesta de .gitignore, pero NO aplicarla todavía.

---

# 10. TAMAÑO

Calcular:

CURRENT_WORKING_TREE_SIZE
CURRENT_TRACKED_CONTENT_SIZE
CURRENT_GIT_DIRECTORY_SIZE

y estimar:

PROPOSED_KEEP_SIZE

PROPOSED_EXCLUDED_SIZE

EXPECTED_REPOSITORY_SNAPSHOT_SIZE_AFTER_CLEANUP

Indicar claramente si:

TARGET_UNDER_100_MB=YES/NO

y:

TARGET_UNDER_200_MB=YES/NO

Si el tamaño supera 100 MB, explicar exactamente qué categorías lo provocan.

Si supera 200 MB, marcarlo como problema que requiere decisión del Technical Lead.

---

# 11. ARCHIVOS GRANDES

Enumerar archivos relevantes de gran tamaño.

Como mínimo revisar:

> 1 MB
> 5 MB
> 10 MB
> 25 MB
> 50 MB

Para cada archivo grande indicar:

PATH
SIZE
TRACKED
CLASSIFICATION
PURPOSE
CAN_REGENERATE
NEEDED_FOR_V5
NEEDED_FOR_HISTORY
RECOMMENDATION

---

# 12. GIT HISTORY

Inspeccionar de manera no destructiva si existen objetos/blob históricos especialmente grandes.

NO ejecutar reescritura de historia.

NO utilizar git filter-repo.

NO utilizar BFG.

NO ejecutar gc destructivo.

Solamente informar si el historial Git contiene archivos grandes que expliquen un tamaño elevado de .git.

Distinguir:

CURRENT SNAPSHOT CLEANUP

de:

GIT HISTORY CLEANUP

Una eventual limpieza de historia deberá ser una decisión separada del Technical Lead.

---

# 13. SALIDA PRINCIPAL

Crear:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN_RESULT.md

Debe contener como mínimo:

## STATUS

## EXECUTIVE_SUMMARY

## REPOSITORY_SIZE

## DIRECTORY_SIZE_BREAKDOWN

## FILE_TYPE_BREAKDOWN

## LARGEST_FILES

## GIT_HISTORY_SIZE

## KEEP

## EXCLUDE

## REVIEW

## GENERATED_ANALYSIS_OUTPUT_POLICY

## HISTORICAL_EVIDENCE_POLICY

## V5_CONTINUITY_CHECK

## GITIGNORE_RECOMMENDATIONS

## PROPOSED_CLEANUP

## EXPECTED_SIZE_AFTER_CLEANUP

## RISKS

## TECHNICAL_LEAD_DECISIONS_REQUIRED

## NEXT

---

# 14. INVENTARIO MACHINE-READABLE

Crear además:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_FILE_INVENTORY.csv

Una fila por archivo relevante o por archivo inspeccionado cuando sea razonablemente viable.

Columnas mínimas:

path
size_bytes
git_status
classification
category
needed_for_v5
needed_for_history
regenerable
recommendation
reason

El CSV debe ser determinista:

- ordenado por path;
- sin timestamps;
- sin UUID;
- sin rutas absolutas del analista;
- sin secretos.

---

# 15. PLAN DE LIMPIEZA

El informe debe proponer un plan posterior, pero NO ejecutarlo.

Separar claramente:

SAFE_EXCLUSIONS

REQUIRES_TECHNICAL_LEAD_REVIEW

MUST_KEEP

OPTIONAL_GIT_HISTORY_OPTIMIZATION

Para cada exclusión propuesta indicar cómo sabemos que V5 podrá continuar sin ella.

---

# 16. VALIDACIÓN

No es obligatorio ejecutar toda la suite de 1809 tests porque esta ronda no modifica código.

Sí verificar:

- repository inspection completed;
- no production files changed;
- no tests changed;
- no historical files changed;
- no files deleted;
- no files moved;
- no .gitignore changes;
- no real IST access;
- no real provider calls;
- no commit;
- no push.

Comprobar git status antes y después.

El único contenido nuevo permitido es:

prompts/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN.md

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN_RESULT.md

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_FILE_INVENTORY.csv

Si el prompt ya existe porque fue creado por el Technical Lead antes de ejecutar Claude, tratarlo como entrada autorizada.

---

# 17. STOP CONDITIONS

STOP y reportar sin modificar nada si:

- se detecta riesgo de perder evidencia necesaria;
- no puede determinarse si un artefacto es necesario para tests/contratos;
- se detectan secretos potenciales en contenido que actualmente está tracked;
- se detecta contenido real IST tracked accidentalmente;
- se detecta un archivo individual incompatible con GitHub por tamaño;
- la continuidad V5 depende de archivos locales no versionados que podrían perderse;
- cualquier limpieza requeriría reescribir historia Git.

Estos hallazgos NO son fallos de la auditoría.

Son decisiones para el Technical Lead.

---

# 18. DECISIÓN ESPERADA

La tarea debe terminar con uno de:

READY_FOR_TECHNICAL_LEAD_CLEANUP_REVIEW

o

BLOCKED_REQUIRES_TECHNICAL_LEAD_DECISION

No ejecutar la limpieza.

No iniciar V5.

No actualizar todavía los manuales post-V4.2.

Detenerse después de generar el informe y el CSV.