# Documentación humana de flujos — webCobMorosidad

*Esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R4`. [Volver al índice](../HUMAN_DOCUMENTATION.md).*

1 flujo(s) en este documento.

# Flujo FLOW-BIG: webCobMorosidad\CobLiquidacionDeudaPrev.ascx → Load

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `webCobMorosidad\CobLiquidacionDeudaPrev.ascx`
- Proyectos/capas del sistema involucrados: no determinado
- Confianza general del flujo: confirmado

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Load`, manejado por `Page_Load`.

## 3. Resumen funcional determinista

- 7 camino(s) de ejecución evidenciado(s) en total.
- 2 camino(s) confirmado(s) principal(es) (detalle en la sección 4).
- 5 camino(s) con un límite no resuelto (detalle en la sección 7).
- 4 camino(s) adicional(es) corresponden a infraestructura o código técnico/generado, no a lógica de negocio.

El detalle exhaustivo de todos los caminos -- incluyendo los técnicos/de infraestructura -- está en la sección 8; esta sección resume solo lo funcionalmente relevante.

## 4. Rutas confirmadas principales

- Camino confirmado: `Planilla.obtenerGastosCobEJ` termina en procedimiento almacenado `PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ`.
- Camino confirmado: `Planilla.obtenerLiqDeudaPrev` termina en operación SQL `PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV`.

## 5. Servicios/capas

- `Planilla.obtenerGastosCobEJ`
- `Planilla.obtenerLiqDeudaPrev`

### Elementos técnicos/auxiliares (no lógica de negocio)

*Coinciden con un patrón de código técnico/generado (p. ej. métodos del diseñador de WebForms). Se conservan como evidencia, con su confianza y trazabilidad intactas; no deben interpretarse como servicios de negocio.*

- `Formulario.DesplegarError`
- `Formulario.LimpiaNullDataset`

## 6. Datos/SP/SQL

### Procedimientos almacenados
- `PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ`

### Operaciones SQL
- `PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV`

### Evidencia transaccional
- `DAO-TX-BEGIN`: evidencia transaccional confirmada (`BeginTrans`)
- `DAO-TX-COMMIT`: evidencia transaccional confirmada (`Commit`)


## 7. Qué queda no resuelto

- Límite no resuelto: `UnknownHelper.ProcesarAlgo` — no se pudo confirmar su destino real.

Caminos con incertidumbre (`path_id`): `PATH-TX-BEGIN`, `PATH-TX-COMMIT`, `PATH-NOISE-1`, `PATH-NOISE-2`, `PATH-REAL-GAP`.

Ninguna de estas ausencias se completa con una suposición: se declaran explícitamente como no resueltas.

### Límites técnicos/infraestructura (no resueltos, de naturaleza conocida)

*Corresponden a llamadas de infraestructura/ciclo de vida (p. ej. control transaccional, cierre de conexión) reconocidas por su nombre, o a un límite cuyo propio camino contiene inequívocamente una llamada técnica/de infraestructura reconocida; se conservan como límite no resuelto, con su trazabilidad intacta, pero no representan una incertidumbre funcional del negocio.*

- `dbc.BeginTrans` (`DAO-TX-BEGIN`)
- `dbc.Commit` (`DAO-TX-COMMIT`)
- `unknown_noise_1` (ruido técnico detectado en el camino vía `Formulario.DesplegarError`)
- `unknown_noise_2` (ruido técnico detectado en el camino vía `Formulario.LimpiaNullDataset`)

## 8. Evidencia técnica detallada / trazabilidad

### Todos los caminos (detalle exhaustivo)

- Camino confirmado: `Planilla.obtenerGastosCobEJ` termina en procedimiento almacenado `PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ`.
- Camino confirmado: `Planilla.obtenerLiqDeudaPrev` termina en operación SQL `PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV`.
- Camino confirmado: (sin pasos intermedios evidenciados) termina en límite no resuelto `dbc.BeginTrans` (evidencia transaccional confirmada (`BeginTrans`)).
- Camino confirmado: (sin pasos intermedios evidenciados) termina en límite no resuelto `dbc.Commit` (evidencia transaccional confirmada (`Commit`)).
- Camino no resuelto: `Formulario.DesplegarError` termina en límite no resuelto sin nombre resuelto (`unknown_noise_1`).
- Camino no resuelto: `Formulario.LimpiaNullDataset` termina en límite no resuelto sin nombre resuelto (`unknown_noise_2`).
- Camino no resuelto: (sin pasos intermedios evidenciados) termina en límite no resuelto sin nombre resuelto (`UnknownHelper.ProcesarAlgo`).

### Trazabilidad por camino

- `PATH` `PATH-BIZ-1` — evidencia: `EVR-1`
  - `PATH-BIZ-1` → `index/functional_paths.json#PATH-BIZ-1`
- `PATH` `PATH-BIZ-2` — evidencia: `EVR-2`
  - `PATH-BIZ-2` → `index/functional_paths.json#PATH-BIZ-2`
- `PATH` `PATH-TX-BEGIN` — evidencia: `EVR-5`
  - `PATH-TX-BEGIN` → `index/functional_paths.json#PATH-TX-BEGIN`
- `PATH` `PATH-TX-COMMIT` — evidencia: `EVR-6`
  - `PATH-TX-COMMIT` → `index/functional_paths.json#PATH-TX-COMMIT`
- `PATH` `PATH-NOISE-1` — evidencia: `EVR-3`
  - `PATH-NOISE-1` → `index/functional_paths.json#PATH-NOISE-1`
- `PATH` `PATH-NOISE-2` — evidencia: `EVR-4`
  - `PATH-NOISE-2` → `index/functional_paths.json#PATH-NOISE-2`
- `PATH` `PATH-REAL-GAP` — evidencia: `EVR-7`
  - `PATH-REAL-GAP` → `index/functional_paths.json#PATH-REAL-GAP`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-BIG`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 7 camino(s) determinista(s) original(es), 0 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 7 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 6) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.

