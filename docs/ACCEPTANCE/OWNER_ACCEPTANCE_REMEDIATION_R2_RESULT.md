# Remediación R2 de la aceptación del propietario — normalización de la proyección humana

Documento de ronda (histórico). Estado vigente: `PROJECT_STATE.json`.

```text
H5 = CLOSED    POST_V5 = CLOSED    V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_OWNER_MANUAL_REVIEW   (la revisión manual del propietario sigue pendiente; no se declara PASS)
llamadas reales al proveedor durante la remediación = 0     análisis IST nuevos = 0     commit / push / tag = NO
```

## BD-1: causa raíz

El proveedor real escribe dentro del texto de la afirmación el mismo estado que ya entrega en el campo estructurado `status`
(`CONFIRMED: …`, `INFERRED: …`, `UNRESOLVED: …`, a veces con guion largo: `CONFIRMED — …`, y en afirmaciones mixtas
`CONFIRMED: a. INFERRED: b.`). `validate_semantic` no tocaba la prosa y los renderizadores humanos la imprimían tal cual, junto a la
etiqueta humana («Confirmado — CONFIRMED: …»). El validador de producto rechazó con razón el vocabulario: 191 páginas
(datos 81, flujos 64, proyectos 17, soluciones 16, vistas 12, no resueltos 1). La corrida con STUB no podía mostrarlo porque
el proveedor sintético no escribe prefijos.

## Frontera de normalización elegida

`provider response → parse → validate_semantic (normaliza la prosa) → registro persistido → proyección (normaliza de nuevo, idempotente) → renderizador`.

| Capa | Qué hace | Por qué |
| --- | --- | --- |
| A. `models.validate_semantic` | Los registros **nuevos** guardan la prosa ya normalizada (`claim_id` se sigue derivando del texto crudo) | Los padres reciben hechos limpios y el modelo semántico persistido nace limpio |
| C. `product.normalize_assessment` | En la proyección, cada registro resuelto se sustituye por una **copia** normalizada, después de `assess` | La identidad de solicitud de SOLUCIÓN/SISTEMA depende del hash del `semantic` almacenado de sus hijos: reescribir los 597 registros reales invalidaría identidades y obligaría a llamar al proveedor. Los archivos persistidos no se reescriben |

La opción B (migrar los registros persistidos) se descartó por esa dependencia. Una prueba de regresión lo ancla: registros guardados con
prefijos se reproducen con 0 llamadas y proyectan limpio, y sus bytes en disco no cambian.

`normalize_claim_text` (determinista, idempotente, sin regex global ciega):
1. Un marcador al **inicio** de la afirmación (`MARCA:` o `MARCA —`, con o sin negritas) se elimina; el estado estructurado ya lo expresa.
2. Un marcador que **abre una oración posterior** de una afirmación mixta se reescribe con el vocabulario humano (`Inferido: …`), de modo que la distinción sobrevive.
3. Una palabra de estado en inglés suelta en la prosa (p. ej. «esa atribución es INFERRED») se **traduce** al vocabulario humano, nunca se borra. Cadenas que solo contienen esas letras (`UNCONFIRMEDX`) no se tocan.

Una afirmación que queda vacía tras quitar el marcador se rechaza (`EMPTY_TEXT`). Nunca cambia `status`, `refs`, `claim_id` ni procedencia.

## Pruebas

`tests/test_owner_acc01_r2_human_projection.py` (15 pruebas): casos unitarios del normalizador (inicio, guion, mixtas, palabra suelta, texto ajeno
intacto, idempotencia); los seis niveles `SYSTEM/SOLUTION/PROJECT/VIEW/FLOW/DATA` con las tres marcas conservan estado, `refs` e identidad
de afirmación; sin promoción ni degradación por el prefijo; extremo a extremo con prefijos (dos estilos) sin fugas ni doble etiqueta y con
proveniencia de máquina intacta; registros persistidos con prefijos reproducibles con 0 llamadas; afirmación mixta; proyecto solo-no-resuelto
(deriva de cobertura); afirmaciones sin `subject`.

También se regeneró el campo `inventory` de `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json` (cambian las líneas de `models.py` y
`product.py`; no hay módulos de producción nuevos, el total sigue en 348).



## Deriva de cobertura 184/9 → 183/10

```text
proyecto            WebAmbiente
id estable          PRJ-013b43d015f3884427d97cb2170938a9757d7c4724eda8ea06f821982e5a0592
ruta                WebAmbiente/WebAmbiente.vbproj
solución            SOL-ebd66cf8127ba553ce0acb46794f341632a077dd7a91b6bc045e9385148086a5 (WebAmbiente)
categoría STUB      HUMAN_AND_MACHINE_DOCUMENTED
categoría REAL      MACHINE_ONLY_DOCUMENTED (motivo NO_CONFIRMED_OR_INFERRED_CLAIMS)
causa               resultado semántico de la IA + regla determinista de aplicabilidad
CATEGORY_DRIFT_EXPLAINED = YES
```

Los hechos del proyecto son una biblioteca con una vista cuyos eventos son «no resueltos» y una llamada saliente sin destino. La IA real
respondió correctamente **solo** con afirmaciones `UNRESOLVED` en las siete secciones (7 afirmaciones aceptadas, 0 rechazadas); el STUB
siempre emite al menos una afirmación `CONFIRMED`. La regla `_project_state` clasifica «sin afirmaciones confirmadas ni inferidas» como
solo de máquina. No es un defecto del producto: el proyecto conserva su página humana, su paquete de máquina y sus afirmaciones no
resueltas. No se forzó la igualdad con el STUB.

## Campos `subject` vacíos

606 de 7 347 afirmaciones persistidas (8,2 %); afecta a DATA 112, FLOW 15, PROJECT 384, SOLUTION 95; VIEW y SYSTEM: 0.
Clasificación: **VALID_OPTIONAL** (el esquema marca `subject` como opcional). Impacto humano: la fila se muestra sin prefijo «sujeto:» y
la prosa sigue siendo autosuficiente; verificado con prueba. Impacto de máquina: `subject` se emite como cadena vacía, `claim_id` y
`fact_ids` no dependen de él. No se infiere ningún significado de negocio.

## Telemetría de tokens

`TOKEN_USAGE_TELEMETRY = NOT_AVAILABLE_FROM_ADAPTER` (`usage` vacío en las 597 respuestas reales). No se inventan cifras; no bloquea.

## Inspección de la interpretación SYSTEM real (sin llamadas)

Respuesta válida, 22 afirmaciones aceptadas, 4 degradadas a «Inferido» por el validador (nunca promovidas), 0 rechazadas. El resumen dice que el
sistema «parece ser un conjunto de soluciones con responsabilidades distintas, no una aplicación única con un propósito global establecido»;
las tres afirmaciones `unresolved` declaran que no se puede determinar un propósito único, las reglas ni las fuentes de datos comunes. Sin
inferencia de obsolescencia ni de actores. Observación para la revisión manual: los grupos «Soluciones ADH/COT/MED/PEN/SUB» son agrupaciones
por prefijo de nombre, respaldadas por hechos citados de cada solución, pero conviene confirmar que la lectura es útil.
Además, los hechos persistidos del SYSTEM contienen texto de hijos con marcadores (`[Confirmado] CONFIRMED: …`); es entrada interna de
procedencia, no llega a prosa humana, y en corridas nuevas ya nacen limpios.

## Reproyección con cero proveedor (wheel candidata)

Wheel candidata construida del árbol de trabajo (sin commit): `legacymapper-5.9.0-py3-none-any.whl`, 947 530 bytes,
SHA-256 `5baee7d9418da732e74ad651fe91b997c7bffac5736e100a4c749a9a9d9909ba`, instalada no editable en `venv_r2`. No se usó para IA nueva.

- `interpret-system` (reproducción sobre `work/real_ai_state`): **0 solicitudes al proveedor, 597 reproducidas**, cobertura 183/10/35, 0 pendientes.
- `project-system` → `output/real_ai_product_r2`: 0 llamadas, `source_scanned` falso, escáner 0, analizador 0, lecturas de fuente 0; estado SUCCESS.
- Validación: enlaces rotos 0, activos faltantes 0, JSON inválido 0, ids colgantes 0, ids duplicados 0, fugas de procedencia 0, estados humanos inválidos 0,
  omisiones silenciosas 0, PDF válido, 602 páginas; prefijos ingleses en texto humano 0; marcadores iniciales en texto de máquina 0.
- Comparación antes/después: 597/597 registros persistidos idénticos byte a byte; identidad, hash de entrada y hash de respuesta cruda sin
  cambios; 7 347 afirmaciones con estado, hechos y `subject` idénticos; inventario de cobertura idéntico (228 proyectos). El único archivo del
  estado que cambia al reproducir es `FULL_SYSTEM_COVERAGE.json` (bitácora de corridas).
- El `real_ai_product` original (defectuoso) se conserva sin cambios.

## Resultados

```text
pruebas dirigidas R2 + R1 = 51 PASS
suite completa, primera ejecución = 3626 pruebas, 1 fallo: la evidencia en disco del inventario de mantenibilidad quedó desactualizada
   (cambiaron las líneas de models.py y product.py); se regeneró el campo `inventory` con la herramienta del propio repositorio
suite completa, segunda ejecución (python -X utf8 -m unittest discover -s tests) = 3626 pruebas, 0 fallos, 0 errores, 135 omitidas
tras editar PROJECT_STATE.json se repitieron las pruebas que lo leen (173 PASS)
```

## Pendiente

Revisión manual del propietario (no se declara PASS en su nombre). Muestra sugerida: resumen del sistema, ejecutivo, 5 soluciones, un proyecto
UI grande y uno pequeño, un proyecto sin UI, un flujo entre proyectos, un proyecto intensivo en datos, un proyecto no resuelto (p. ej. WebAmbiente) y vistas.
