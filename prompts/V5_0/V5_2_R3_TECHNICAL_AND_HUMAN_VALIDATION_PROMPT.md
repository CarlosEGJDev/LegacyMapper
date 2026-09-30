# V5.2 R3 — Validación técnica y revisión humana

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

V5.1 está cerrada.

V5.2 R0, R1 y R2 están aprobados para validación.

Esta ronda NO debe rediseñar V5.2.
NO debe convertirse en una nueva ronda de implementación.

El objetivo es verificar técnicamente la implementación de R2 y preparar una muestra humana pequeña y comprensible para revisión del Technical Lead.

R4 NO puede comenzar hasta que exista aprobación humana explícita.

---

# 1. Documentos obligatorios

Leer como mínimo:

- docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md
- docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md
- docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md
- docs/V5/V5_1_R4_CIERRE_FINAL.md

Revisar también el código actual de `legacy_documenter/documentation_v52/`.

No asumir que R2 está correcto solo porque terminó READY_FOR_R3.

---

# 2. Pregunta central de R3

Responder dos preguntas independientes:

## Técnica

¿La implementación V5.2 cumple el contrato R1 de forma estable y sin regresiones?

## Humana

¿La documentación generada es realmente comprensible y navegable para una persona?

Ambas deben aprobarse antes de R4.

---

# 3. Validación técnica

Verificar como mínimo:

- General Overview;
- Developer Technical;
- profiles;
- templates;
- custom templates;
- fallback;
- technical noise;
- idioma;
- renderer Markdown;
- particionado;
- determinismo;
- navegación;
- integración productiva;
- AI independence;
- runtime independence;
- documentación legacy intacta.

No limitarse a leer tests: contrastar con código y salida real.

---

# 4. Pendientes de R2

Revisar especialmente:

## P-1 — RUN_SUMMARY

R2 dejó pendiente que `documentation_v52/` no aparezca en `RUN_SUMMARY.output_locations`.

Determinar si:

A. debe corregirse antes de R4;

o

B. es deuda aceptable posterior.

No modificarlo en esta ronda.

Explicar en lenguaje simple qué impacto tiene.

---

## P-2 — flujo → ubicación de código

R2 indicó que algunos flujos todavía no enlazan directamente al archivo/línea de su manejador.

Determinar si:

- dificulta realmente al desarrollador;
- contradice el objetivo del perfil Developer Technical;
- bloquea R4 o puede quedar como mejora posterior.

No corregirlo en R3.

---

## P-3 — ruido técnico residual

R2 encontró llamadas de interfaz todavía visibles.

Validar:

- si afectan realmente la lectura;
- si pueden resolverse solo mediante configuración;
- si el sistema de noise policy funciona correctamente.

No convertir R3 en una limpieza infinita de patrones.

---

# 5. Validación de arquitectura

Confirmar que sigue existiendo la separación:

Evidence
    ↓
Audience Transformation
    ↓
Profile
    ↓
Template
    ↓
Renderer
    ↓
Human Documentation

Verificar que ninguna capa haya absorbido responsabilidades de otra.

---

# 6. General Overview

Leer físicamente la documentación generada.

Evaluar si una persona no desarrolladora puede responder:

- ¿Qué estoy mirando?
- ¿Cómo está organizado el sistema?
- ¿Cuáles son sus partes principales?
- ¿Qué procesos se observan?
- ¿Con qué sistemas externos se relaciona?
- ¿Qué datos utiliza?
- ¿Qué cosas no se pudieron determinar?

No penalizar la ausencia de propósito de negocio cuando no existe `INTERPRETED`.

Sí penalizar:

- jerga innecesaria;
- IDs internos;
- listas gigantes;
- explicaciones que requieran conocer LegacyMapper;
- información correcta pero incomprensible.

---

# 7. Developer Technical

Leer físicamente varios módulos.

Evaluar si un desarrollador puede encontrar de forma rápida:

- módulo/proyecto;
- puntos de entrada;
- flujos;
- acceso a datos;
- dependencias;
- archivos relacionados;
- información no resuelta;
- detalle bajo demanda.

El documento principal debe seguir siendo breve.

El detalle exhaustivo debe estar separado.

---

# 8. Progressive disclosure

Confirmar que se cumple:

Resumen
    ↓
Detalle técnico
    ↓
Detalle exhaustivo

Verificar:

- raíz pequeña;
- índices pequeños;
- módulos legibles;
- detalle particionado;
- enlaces funcionales;
- ningún archivo humano gigante.

---

# 9. Particionado

Revalidar los defaults elegidos en R2.

No repetir todas las mediciones si el código no cambió.

Comprobar:

- límite por cantidad;
- límite por tamaño;
- determinismo;
- nombres;
- navegación;
- ningún archivo excesivamente grande;
- comportamiento ante elemento individual oversized.

---

# 10. Custom templates

Realizar una prueba real con un directorio custom.

Verificar:

- override parcial;
- fallback;
- warning;
- template inválido;
- modo estricto a nivel de API;
- aislamiento;
- no ejecución de código;
- no escritura fuera del output.

No basta solo con tests unitarios.

---

# 11. INTERNAL_ONLY

Confirmar que por defecto no aparecen en documentación humana:

- IDs internos;
- hashes;
- metadata del motor;
- marcas internas del resolver;
- detalles internos de Evidence Core.

Usar búsqueda automática y revisión visual.

---

# 12. AI independence

Ejecutar/confirmar documentación con:

AI = OFF

Debe generarse completamente.

No debe importar providers ni depender de contenido INTERPRETED.

---

# 13. Legacy compatibility

`documentation/` legacy debe permanecer intacto.

Comparar contra baseline previo cuando corresponda.

No retirar todavía la documentación legacy.

---

# 14. Suite completa

Ejecutar:

python -m unittest discover -s tests

Para pasar R3:

failures = 0
errors = 0

Reportar skips.

---

# 15. Muestra para revisión humana

Preparar una muestra pequeña a partir de la documentación V5.2 real.

NO crear un nuevo sistema de documentación.

NO reescribir manualmente los documentos.

La muestra debe ser copia exacta o referencia directa a documentos generados por el producto.

Seleccionar exactamente:

1. General Overview completo.
2. Un módulo simple.
3. Un módulo medio.
4. Un módulo complejo.
5. Un módulo/caso con acceso a datos.
6. Un módulo/caso con información no resuelta.

Evitar duplicar muestras cuando un mismo módulo cubra dos categorías, salvo que hacerlo reduzca demasiado la variedad.

---

# 16. Carpeta de muestra

Crear dentro del output de validación una carpeta claramente identificada, por ejemplo:

human_review_sample/

No crearla dentro de `docs/`.

Puede contener copias de los archivos generados necesarios para que el Technical Lead pueda revisarlos fácilmente.

Debe incluir un único índice:

README.md

que explique en lenguaje simple:

- qué archivo mirar;
- por qué fue seleccionado;
- qué debería poder entender el lector.

No incluir análisis de Claude sobre si está bien o mal dentro de los documentos copiados.

---

# 17. Reglas de la muestra

La muestra debe ser:

- pequeña;
- legible;
- representativa;
- basada exclusivamente en salida real;
- sin IDs internos agregados manualmente;
- sin modificaciones para hacerla "verse mejor".

Queremos revisar el producto real, no una versión arreglada para la demo.

---

# 18. Aprobación humana

El documento R3 debe terminar la parte humana indicando:

HUMAN_REVIEW_REQUIRED

aunque Claude considere buena la documentación.

Claude NO puede aprobar en nombre del Technical Lead.

Después de esta ronda:

- el Technical Lead revisará la muestra;
- podrá aprobarla;
- pedir ajustes;
- o bloquear R4.

---

# 19. Criterio para pasar a R4

La parte técnica puede terminar READY.

Pero el estado global de R3 debe distinguir:

## Técnica OK, pendiente humano

V5_2_R3_TECHNICALLY_READY_HUMAN_REVIEW_REQUIRED

## Problema técnico

V5_2_R3_BLOCKED

## Conflicto

V5_2_R3_CONFLICT

## Decisión necesaria

V5_2_R3_OPEN_DECISION

NO usar V5_2_R3_READY_FOR_R4 todavía.

El paso a R4 ocurre únicamente después de que el Technical Lead apruebe explícitamente la muestra humana.

---

# 20. Resultado documental

Crear EXACTAMENTE:

docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md

Debe ser conciso.

Estructura:

1. Estado técnico.
2. Qué se verificó.
3. Pendientes R2.
4. General Overview.
5. Developer Technical.
6. Progressive disclosure.
7. Templates/custom.
8. Particionado.
9. Ruido técnico.
10. INTERNAL_ONLY.
11. Integración/independencia.
12. Compatibilidad legacy.
13. Suite.
14. Muestra humana preparada.
15. Ruta exacta de la muestra.
16. Qué debe revisar el Technical Lead.
17. Deuda restante.
18. Conclusión técnica.
19. HUMAN_REVIEW_REQUIRED.

No llenar el documento con métricas innecesarias.

---

# 21. No hacer

NO:

- corregir P-1/P-2/P-3 en esta ronda;
- modificar Evidence Core;
- modificar V5.1;
- implementar HTML;
- implementar IA;
- implementar V5.3–V5.9;
- retirar documentation/ legacy;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentación auxiliar fuera del resultado y la muestra humana;
- crear prompt R4.

---

# 22. Regla final

Al terminar:

- crear únicamente `docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md`;
- crear únicamente la carpeta de muestra humana dentro del output de validación;
- no crear ningún otro documento de diagnóstico;
- no crear prompt R4;
- esperar revisión externa y aprobación humana.