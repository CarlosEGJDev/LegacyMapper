# V5.2 R3 — Validación técnica y revisión humana

## 1. Estado técnico

V5_2_R3_TECHNICALLY_READY_HUMAN_REVIEW_REQUIRED

La implementación de R2 cumple el contrato R1 sin regresiones. No se modificó código, Evidence Core, V5.1, roadmap ni `PROJECT_STATE.json`; no hay commits ni push. Se encontró un hallazgo de exactitud del contenido (sección 4) que el Technical Lead debe decidir; no es un defecto del contrato del motor.

## 2. Qué se verificó

Contra código y salida real (no solo tests), sobre la corrida IST de R2 (`v5_2_r2_real_run_c`):

- Regeneración desde `evidence/` en dos pasadas: idéntica entre sí y byte a byte a la salida del pipeline (838 `.md` + manifiesto).
- 2640 enlaces relativos: 0 rotos. Búsqueda automática de ids internos, hashes y marcas del motor: 0 (el único acierto textual fue «Extensions» en nombres de bibliotecas .NET).
- Separación de capas Evidence → Transformación → Profile → Template → Renderer: se mantiene; el renderer no importa profile, política, evidencia ni templates (test existente + lectura de `engine.py`).
- Lectura física de General Overview y de 6 módulos.

Salida de validación: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_validation\`.

## 3. Pendientes R2

**P-1 — `RUN_SUMMARY`.** Confirmado: `output_locations` lista `documentation`, `index`, `ai_context`, `consumer_projection` y los `RUN_SUMMARY`, pero no `documentation_v52` ni `evidence`. Impacto en lenguaje simple: quien lea el resumen de la corrida no se entera de que existe la documentación nueva; los archivos sí se generan bien. Es la misma clase de omisión que V4.3-R7 ya corrigió para `consumer_projection`. Decisión: **B, deuda aceptable para R4**, pero debe corregirse (una línea y un test en `compute_output_locations`) antes de cerrar V5.2.

**P-2 — flujo → ubicación de código.** Cada flujo muestra pantalla, evento y manejador (`Page_Load`, `hypBuscar_Click`); un desarrollador puede buscar el manejador con esos dos datos, pero no salta directo al archivo:línea (el acceso a datos sí lo tiene). Es una incomodidad real, no una contradicción del perfil Developer Technical. **No bloquea R4; mejora posterior.**

**P-3 — ruido residual.** Medido en los 514 documentos de módulo (cuerpos, sin detalle): `Me.X.DataBind()` 83 apariciones, `Me.` 319; `InitializeComponent`, `Commit`, `MsgBox` 0. El sistema de política funciona: lo que la política cubre desapareció del cuerpo y queda declarado con conteo y categoría. Lo residual es llamadas a controles de interfaz que el set por defecto no clasifica; se resuelve **solo con configuración** (un patrón `ui_messaging`/nueva categoría en un JSON custom), sin tocar código. No bloquea.

## 4. General Overview

Se leyeron los 5 documentos. Una persona no desarrolladora puede responder: qué se analizó (113 soluciones, 259 proyectos), partes principales (12 módulos con más actividad), sistemas/bibliotecas externas, datos (paquetes de base de datos) y qué no se determinó. No penalizado: falta de propósito de negocio.

Problemas de lectura observados (sin corregir):

1. **Hallazgo de exactitud.** El titular «12642 flujos, de los cuales 2370 llegan a un acceso a datos confirmado» (18,7 %) se apoya en `has_confirmed_terminal` de V4. De esos 2370, **1698 (72 %) terminan solo en una operación transaccional** (`BeginTrans`/`Commit`), que la propia política de ruido oculta en otras partes; solo **672 (5,3 % del total) alcanzan una operación de datos real**. Los módulos muestran `(transaction)` como «destino confirmado». Es una semántica heredada, presentada literalmente; el lector la entenderá como «llegan a datos» de forma más optimista de lo que la evidencia sostiene. Requiere decisión del Technical Lead (¿contar solo destinos reales?).
2. Jerga: «flujos», «destino confirmado», «evidencia estática», «INTERPRETED» (README raíz) y «LegacyMapper» exigen conocer el producto.
3. Nombres de módulo técnicos (`sysPENResoluciones`); «Tipo de salida: Library» aparece también en proyectos web.
4. `modules.md` es una tabla de 6 columnas; legible pero densa.

## 5. Developer Technical

Un desarrollador encuentra: módulo/proyecto (README → tabla o índice de 260), pantallas y eventos, flujos, objetivos de datos con `archivo:línea`, dependencias y bibliotecas, información no resuelta con conteos, y detalle bajo enlace. Deficiencias: sin `archivo:línea` del manejador (P-2), `(transaction)` como destino (sección 4), columnas con valores crudos (`stored_procedure`, `web_lifecycle`, `web_event`). Módulos con sufijo `-2`/`-3` (copias `Backup`/nombres repetidos) son difíciles de distinguir sin abrir el documento.

## 6. Progressive disclosure

Cumple. Raíz 702 B; README general 0,7 KB; README developer ~2 KB; documento de módulo 0,6–7,3 KB (el mayor, `blPENResoluciones`); detalle en partes; el cuerpo enlaza «Se muestran 15 de N: ver todos». Archivo máximo 49 131 B con los defaults. Ningún archivo humano gigante.

## 7. Templates / custom

Probado con directorios custom reales (`C:\PruebasLegacyMapper\Resultados\v5_2_r3_validation\c_*`; se conservan los directorios custom de entrada, las salidas temporales se borraron):

| Caso | Resultado |
|---|---|
| Override parcial válido (título y viñetas propios, catálogo propio) | Solo cambia `general/limitations.md` (+ manifiesto); el resto idéntico al default |
| Fallback (los otros 12 templates no existen en custom) | Usa default |
| Bloque de tipo `script` | Warning visible + fallback; visible en README raíz |
| JSON malformado | Warning + fallback |
| Condición con código (`__import__('os')…`) | Rechazada («condición desconocida»); no se ejecutó nada, no se creó `pwned.txt` |
| Parámetros internos (`__class__.__mro__`, `evidence_id`) | Rechazados |
| Clave de idioma inexistente | Warning + fallback |
| Ruta de salida `../../escape.md` y absoluta `C:/…` | Rechazadas; ningún archivo fuera del output |
| `strict_templates=True` (API) | `ConfigError` legible en bloque inválido, JSON malformado y ruta fuera del árbol |

Aislamiento confirmado: el archivo centinela fuera del output quedó intacto. El modo estricto sigue sin CLI.

## 8. Particionado

Defaults (300 filas / 65 536 B) sin cambios de código: no se repitieron las mediciones de R2. Verificado además:

- Por cantidad: con 5 filas/parte ninguna tabla superó 5 filas.
- Elemento individual oversize (nombre de 200 KB inyectado en un registro): se escribe solo (200 606 B), con warning, sin truncar y determinista entre dos corridas. El documento principal del módulo que lo muestra también supera el límite (204 570 B) y lo avisa. Caso patológico; comportamiento correcto.
- Observación: con límites artificialmente pequeños (5 filas) el documento de índice de partes (`unassigned/detail.md`, 85 KB) no se particiona y supera el límite con warning. Con los defaults el mayor es 49 KB. Se anota como deuda menor.
- Nombres y enlaces: 0 rotos; 0 colisiones sin distinguir mayúsculas.

## 9. Ruido técnico

Ver P-3. El cuerpo ya no está dominado por infraestructura. Persisten `Me.X.DataBind()` y `(transaction)` (este último como destino de flujo, sección 4). La declaración «Se omiten N elementos de infraestructura» es clara y con categoría.

## 10. INTERNAL_ONLY

Por defecto no aparecen ids (`FLOW-`, `DAO-`, `PATH-`, `EP-`, `UNRES-`), hashes de 40–64 hex, metadata del motor, `schema_version` ni marcas del resolver en ninguno de los 838 `.md` (búsqueda automática + revisión visual de los documentos leídos). El manifiesto sí contiene hashes, pero es un artefacto técnico, no documentación humana.

## 11. Integración / independencia

- AI = OFF: la corrida real fue sin IA; la regeneración importa el paquete sin cargar ningún módulo con `provider`/`openai`/`anthropic`/`llm`/`copilot`; documenta completo sin contenido INTERPRETED.
- Runtime: la regeneración usa solo `evidence/` (sin `docs/`, `prompts/`, `tools/`).
- Integración productiva: `full` genera `documentation_v52/` en la etapa DOCUMENTATION; una falla es visible como fallo de esa etapa (probado por test de R2).

## 12. Compatibilidad legacy

`documentation/` no se modificó (el motor no la lee ni escribe; test de R2). Los 876 archivos de la corrida R2 eran idénticos por SHA-256 al run V5.1 previo (medición de R2, no repetida: el código de la etapa no cambió). No se retiró.

## 13. Suite

`python -m unittest discover -s tests`: **2322 tests, 0 fallas, 0 errores, 132 skips** (los esperados de checkout limpio).

## 14. Muestra humana preparada

Copias exactas (comparadas con `cmp`, sin edición) de la salida real: General Overview completo, `BLInterfazSAP` (simple), `WebMEDPabellon` (medio), `blPENResoluciones` (complejo), `sysPENResoluciones` (acceso a datos), `WebSUBCalculoPagoSubsidios` (no resuelto), más `developer/README.md`. 26 archivos, 359 KB. Índice único `README.md` en lenguaje simple, sin análisis de Claude. Los enlaces a módulos fuera de la muestra no abren.

## 15. Ruta exacta de la muestra

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_validation\human_review_sample\README.md`

Documentación completa regenerada: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_validation\regen_a\documentation_v52\`.

## 16. Qué debe revisar el Technical Lead

1. Leer `general/` sin ayuda: ¿se entiende qué se está mirando? ¿molesta la jerga?
2. Decidir el hallazgo de la sección 4 (destino «(transaction)» y titular 18,7 %): corregir en R4, reformular el texto o aceptar.
3. En un módulo con datos y otro con no resuelto: ¿el documento principal alcanza y el detalle queda aparte?
4. Decidir P-1 (recomendado: corregir antes de cerrar V5.2), P-2 y P-3 (configuración) como mejoras de R4 o posteriores.
5. Aprobar la muestra, pedir ajustes o bloquear R4.

## 17. Deuda restante

1. P-1 `documentation_v52`/`evidence` fuera de `output_locations`.
2. P-2 flujo → archivo:línea.
3. P-3 ruido de controles de interfaz (solo datos).
4. Destino `(transaction)` en flujos y titular de porcentaje (sección 4).
5. Valores crudos en columnas Tipo y jerga en textos del catálogo `es`.
6. Índice de partes no particionable bajo límites extremos.
7. Defaults JSON sin declarar como package data; modo estricto sin CLI; INTERPRETED sin cargador desde el pipeline.
8. Particionado medido solo en IST; renderer HTML y retiro de `documentation/` fuera de alcance.

## 18. Conclusión técnica

El motor V5.2 es estable, determinista, aislado y fiel al contrato R1; las pruebas custom reales confirman el aislamiento y los avisos. La calidad humana no puede darse por aprobada: hay un hallazgo de exactitud en el titular de flujos y jerga residual. Ninguno rompe el contrato técnico; el juicio de comprensibilidad corresponde al Technical Lead.

## 19. HUMAN_REVIEW_REQUIRED

HUMAN_REVIEW_REQUIRED

Claude no aprueba en nombre del Technical Lead. R4 no puede comenzar hasta aprobación humana explícita.
