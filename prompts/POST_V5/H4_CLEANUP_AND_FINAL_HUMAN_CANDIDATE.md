# LegacyMapper Post-V5 — H4 Cleanup and Final Human Candidate

## Objetivo

Ejecutar dos fases, en este orden:

1. **Limpiar resultados obsoletos** sin perder baseline ni respuestas IA persistidas.
2. **Generar el único candidato final de H4** corrigiendo lo último de documentación humana y reconstrucciones de vistas.

No iniciar H5. No cerrar H4 automáticamente. No llamar al provider. No ejecutar scanner/analyzer. No reconstruir Evidence. No releer fuente.

## Autoridad

Autorizado:

```text
eliminar carpetas de resultados obsoletos = SÍ
migrar/copiar estado reutilizable requerido = SÍ
editar presentación = SÍ
tests = SÍ
commit = NO
push = NO
tag = NO
```

---

# FASE A — LIMPIEZA SEGURA

## 1. Inventariar antes de borrar

Revisar:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\
C:\PruebasLegacyMapper\Resultados\
```

Crear:

```text
C:\PruebasLegacyMapper\FinalValidation\CLEANUP_INVENTORY_BEFORE.md
```

Por cada carpeta candidata registrar:

```text
ruta
ronda/propósito
última modificación
contiene baseline
contiene respuestas IA persistidas
contiene package
es referenciada por scripts actuales
decisión: KEEP / DELETE / MIGRATE_REQUIRED_ARTIFACTS
motivo
```

No asumir nombres: descubrir las carpetas reales.

## 2. Preservación obligatoria

No borrar:

```text
venv\
scripts\
README_RUN_ME.md
RUN_LEGACYMAPPER.cmd
wheel/runtime actual
baseline determinista reutilizable
respuestas IA persistidas
manifiestos necesarios para replay
```

Si baseline o respuestas IA viven dentro de una corrida vieja, migrarlos primero a:

```text
C:\PruebasLegacyMapper\FinalValidation\state\
    baseline\
    ai\
```

Actualizar scripts auxiliares para que no dependan de una corrida obsoleta.

Verificar byte-identidad cuando corresponda.

Si no es posible asegurar la preservación:

```text
STOP
reportar bloqueo
NO ejecutar análisis ni provider automáticamente
```

## 3. Borrar resultados obsoletos

Después del gate de preservación, eliminar únicamente outputs generados de rondas anteriores.

Objetivo conceptual final:

```text
C:\PruebasLegacyMapper\FinalValidation\
    venv\
    scripts\
    state\
        baseline\
        ai\
    runs\
        final_h4_review\
    README_RUN_ME.md
    RUN_LEGACYMAPPER.cmd
    CURRENT_RUN.txt
```

No tocar `C:\dev\LegacyMapper\` salvo los cambios de código/tests/docs de la Fase B.

Crear:

```text
C:\PruebasLegacyMapper\FinalValidation\CLEANUP_REPORT.md
```

con carpetas borradas, retenidas, artefactos migrados y prueba de que no se perdió estado reutilizable.

---

# FASE B — CANDIDATO FINAL H4

## 4. Congelar lo ya aprobado

No rediseñar:

```text
RUN_ALL.cmd
estructura human / ai / internal
diagramas de flujo
diagramas de dependencias
diagramas de datos
diagramas de invocaciones
system/project maps
```

El propietario los considera aprobados.

Corregir solo:

```text
A. reconstrucciones de vistas
B. separación human vs evidence
C. wording/estados humanos
```

## 5. HUMAN debe contener interpretación, no auditoría

Eliminar de `human\index.html`, `LegacyMapper.pdf` y `executive.pdf`:

```text
EP-*
FLOW-*
CALL-*
DAO-*
src:...
paths de archivos fuente
números de línea
(línea N)
Base de las afirmaciones
Respaldo de la interpretación
Evidencia técnica
Referencias y controles
razonamiento/provenance crudo
columnas "Dónde (archivo:línea)"
columnas "Línea" usadas solo como provenance
provider/modelo
fingerprints
```

Toda esa trazabilidad debe seguir existiendo en:

```text
ai\
internal\
```

No destruirla.

## 6. Portada humana

No mostrar:

```text
copilot-local
gpt-6-luna
provider call count
baseline fingerprint
```

Mostrar una sola nota:

```text
Interpretación asistida por IA

Este documento presenta una interpretación generada a partir del análisis de IST.
Las afirmaciones se distinguen como Confirmadas, Inferidas o No resueltas.
```

## 7. Solo tres estados humanos

En la documentación humana:

```text
AZUL     Confirmado
NARANJA  Inferido
ROJO     No resuelto
```

No mostrar en la leyenda humana:

```text
AI_INTERPRETATION
CANONICAL
```

Esos estados permanecen en machine/governance.

## 8. No repetir badge IA

Una sola nota introductoria IA.

No poner cuadro morado `IA` antes de cada explicación.

## 9. Lenguaje documental

Evitar repetición de:

```text
La evidencia muestra...
La evidencia confirma...
La evidencia no precisa...
según la evidencia...
Evidencia de uso
```

Preferir:

```text
La vista muestra...
El análisis confirma...
No se pudo determinar...
La ruta observable...
Uso observable
```

Sin reemplazos mecánicos que alteren significado.

---

# 10. Reconstrucciones de vistas — regla general

La reconstrucción es documental, no pixel-perfect.

Puede:

```text
rebalancear columnas
agrupar controles
fusionar celdas estructurales vacías
mover labels auxiliares
normalizar espacios
dar ancho mínimo a palabras humanas
```

Debe preservar:

```text
controles visibles
agrupación funcional
relaciones
acciones conocidas
semántica
```

Ninguna palabra humana puede renderizarse carácter por carácter en vertical.

## 11. `ucBusSuc`

Corregir `Criterio`.

Debe verse:

```text
Criterio
```

horizontal y legible.

Nunca:

```text
C
r
i
t
e
r
i
o
```

Regla general:

```text
ancho mínimo de celda >= ancho renderizado de la palabra + padding
```

## 12. `ucPreConActxProd`

Corregir rango de fechas.

Debe verse:

```text
[fec_ini]   Hasta   [fec_fin]
```

No inventar `Desde` si no está respaldado.

`Hasta` jamás vertical.

## 13. `ucPreMantJerarquia2`

La zona central debe dejar de usar flechas sueltas y celdas angostas.

Preferido, solo si la dirección está respaldada:

```text
[Asignar →]
[← Desasociar]
```

Si no:

```text
[Asignar]
[Desasociar]
```

Requisitos:

```text
sin < o > sueltos
sin símbolos apilados
sin clipping
sin overlap
columna central suficientemente ancha
lblMensaje1/lblMensaje2 no deben romper la composición
```

Los labels de mensajes pueden reubicarse debajo de acciones si mejora la documentación y no altera semántica.

## 14. Patrones comunes

Implementar reglas deterministas para:

```text
label + control
control + separador + control
dos listas con acciones de transferencia
rango de fechas
columnas de botones
labels/mensajes auxiliares
tablas legacy usadas solo para spacing
```

Aplicar ancho mínimo humano a palabras como:

```text
Criterio
Hasta
Buscar
Asignar
Desasociar
Clasificación
Profesional
Unidad
Fecha
```

---

# 15. Validación visual real

Inspeccionar render/raster real de:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

Comprobar explícitamente:

```text
Criterio horizontal
Hasta horizontal
Asignar/Desasociar coherentes
sin flechas sueltas
sin palabras verticales
sin overlap
sin clipping
sin controles fuera del marco
```

No basta con `SVG dentro de viewBox`.

Requerido:

```text
structural PASS
visual human-readable PASS
```

---

# 16. Única corrida final

Crear solo:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\
```

Con:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

No crear otra corrida iterativa si el proceso termina correctamente.

## 17. CURRENT_RUN

Crear:

```text
C:\PruebasLegacyMapper\FinalValidation\CURRENT_RUN.txt
```

con:

```text
CURRENT_REVIEW_RUN=C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review

STATUS=H4 HUMAN_APPROVAL_PENDING
H5=NOT_STARTED

REVIEW_FILES:
package\human\index.html
package\human\LegacyMapper.pdf
package\human\executive.pdf

DO_NOT_REVIEW_OLDER_RUNS=YES
```

Actualizar `README_RUN_ME.md` indicando que siempre debe revisarse `CURRENT_RUN.txt`.

---

# 18. Reutilización obligatoria

Para toda esta tarea:

```text
provider calls = 0
scanner = 0
analyzer = 0
Evidence rebuild = 0
source reads = 0
```

Reutilizar únicamente baseline y respuestas IA persistidas.

No ejecutar:

```text
01_ANALYZE_ONCE
02_INTERPRET_WITH_AI
```

---

# 19. Tests

Durante desarrollo:

```text
targeted tests only
```

Cubrir:

```text
no provenance IDs en human HTML/PDF
no source paths/números de línea en human
no Base de las afirmaciones
no Respaldo de la interpretación
no Evidencia técnica
no IA repetida
solo 3 estados humanos
provider/model ausentes de portada humana
provenance intacta en ai/internal
Criterio horizontal
Hasta horizontal
transfer controls legibles
sin flechas sueltas
sin palabras humanas verticales
diagramas aprobados sin cambio semántico
```

Al final, una sola suite completa:

```text
python -X utf8 -m unittest discover -s tests
```

Requerido:

```text
0 failures
0 errors
```

---

# 20. Reporte final

Crear:

```text
docs/POST_V5/H4_CLEANUP_AND_FINAL_HUMAN_CANDIDATE_RESULT.md
```

Incluir:

```text
resumen de limpieza
carpetas eliminadas
artefactos retenidos/migrados
ruta final del baseline
ruta final de respuestas IA
limpieza human/evidence
correcciones de reconstrucciones
páginas/renders inspeccionados
prueba de diagramas congelados
provider/scanner/analyzer/source-read counts
targeted tests
suite completa
ruta final de revisión
```

Estado esperado:

```text
H4_CLEANUP_AND_FINAL_HUMAN_CANDIDATE = READY_FOR_OWNER_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

No cerrar H4 automáticamente.

El propietario revisará únicamente:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\index.html
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\LegacyMapper.pdf
C:\PruebasLegacyMapper\FinalValidation\runs\final_h4_review\package\human\executive.pdf
```

Si los aprueba, el siguiente paso es el cierre formal de H4.

---

# Principios finales

> **Una sola corrida actual, un solo objetivo de revisión.**

> **Eliminar outputs obsoletos, nunca estado reutilizable necesario.**

> **Humans recibe interpretación; AI/internal conserva la prueba.**

> **Los diagramas aprobados quedan congelados.**

> **La deuda visual final está en la reconstrucción de pantallas legacy.**
