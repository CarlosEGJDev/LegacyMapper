# H5 — Validación real en IST y cierre: resultado

```text
H5 = CLOSED (Git pendiente de autorización del propietario)
POST_V5 = CLOSED
BLOCKING_DEBT = 0
V6 = NOT_STARTED
```

## Alcance IST
113 soluciones, 260 proyectos (77 con vistas, 183 sin vistas), una sola tecnología (VB.NET WebForms/Oracle). 194 proyectos resuelven una solución; 66 no figuran en ningún `.sln` resoluble (referencias obsoletas o copias en Backup) y se conservan como no resueltos. 32 nombres de proyecto están duplicados.

## Línea base única
Un único análisis determinista completo: 15 170 archivos fuente, 48 114 archivos / 3,70 GB de baseline, 576 s, analyzer v4 (huella `0f288039…`), Evidence 1.0 / UI 1.1 / cross-project 1.0. Las particiones son idénticas a las del baseline de H4. Después: scanner 0, analyzer 0, aperturas del árbol de fuentes 0 (auditadas con un hook en las cohortes y en el barrido).

## IA real (acotada)
15 solicitudes reales a `copilot-local` / `gpt-6-luna`, 15 correctas, en tres cohortes (grande 110 vistas, pequeña 2 vistas, con llamadas entre proyectos 98 vistas). El resto se regeneró desde respuestas guardadas o sin IA. Todo texto de IA queda como `AI_INTERPRETATION`; ningún término canónico sin una persona; 0 palabras de obsolescencia.

## Matriz representativa
Grande, pequeño, entre proyectos, reutilización H4 (WebPREPrevencion), datos/negocio sin UI (`blADHAdmCalculoDs67`) y disperso (`IstFunciones`): los 6 válidos. Los proyectos sin UI producen un paquete solo de máquina (`ai/` + `internal/`, con `human_documentation.applicable=false` y la razón); no se fuerza un modelo de pantallas.

## Escala (260 proyectos)
192 paquetes válidos (63 con documentación humana, 129 solo máquina), 66 sin solución resoluble, 2 con error controlado. 252 HTML, 126 PDF, 1 963 SVG, 1 473 JSON de IA (2 247 vistas, 6 229 flujos, 9 729 datos, 2 677 no resueltos). Enlaces rotos 0, activos faltantes 0, JSON inválido 0, IDs colgantes 0, procedencia cruda en `human/` 0, estados fuera de Confirmado/Inferido/No resuelto 0, texto fuera del marco 0.

## Runtime
Wheel aislada (sha256 `fb22a155…`) en una ruta con espacios y acentos, sin PYTHONPATH, desde un directorio ajeno: el paquete resultó idéntico byte a byte al de desarrollo. Sin el SDK del proveedor, las rutas deterministas funcionan y `interpret` falla de forma controlada (`PROVIDER_UNAVAILABLE`, sin escanear).

## Defectos hallados y corregidos en H5
1. La pertenencia proyecto→solución usaba subcadenas: 76 proyectos aparecían sin solución; con ruta exacta relativa al `.sln` son 66.
2. Proyectos sin vistas (o sin acciones) fallaban con `TemplateError`; ahora generan paquete solo de máquina.
3. `knowledge.json` listaba nombres de datos en vez de ids (referencias colgantes).
4. Dos wireframes dibujaban controles fuera del marco de 760 px.
5. La frase de propósito de la solución sugería un área de negocio a partir del nombre.

Cada uno tiene test de regresión (`tests/test_post_v5_h5_real_ist_scale.py`).

## Suite completa
`python -X utf8 -m unittest discover -s tests`: 3 562 tests, 0 fallos, 0 errores, 132 omitidos (explicados). Solo se regeneró la clave `inventory` de `PRE_H5_GATE_C_FINAL_HARDENING_EVIDENCE.json`, que fija el inventario de módulos.

## Deuda
BLOCKING 0. OBSERVATION: 66 proyectos sin solución resoluble; 32 nombres duplicados (2 proyectos fallan con error controlado y pista); un único adapter en IST. FUTURE_CAPABILITY: seleccionar proyecto por ruta.

## Git
Sin commit, push ni tag; requiere autorización explícita. Artefactos fuera del repo en `C:\PruebasLegacyMapper\H5_Validation\`.
