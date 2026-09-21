# Flujo FLOW-C01: cobChqInsRen.ascx → Click

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `cobChqInsRen.ascx`
- Proyectos/capas del sistema involucrados: DAL, WEB
- Confianza general del flujo: confirmado

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Click`, manejado por `HypGuardar_Click`.

## 3. Qué hace, según evidencia

- Camino confirmado: `CobDAO.GuardarCheque` (evidencia transaccional confirmada (`BeginTrans`)) → `CobDAO.InsertarDetalleCheque` (operación de datos confirmada: `INSERT`) termina en procedimiento almacenado `spInsertarRenovacionCheque`.
- Camino no resuelto: `CobDAO.InitializeComponent` termina en límite no resuelto sin nombre resuelto (`UnknownHelper.Execute`). *(coincide con un patrón de código técnico/generado, no confirmado como lógica de negocio)*

## 4. Servicios/capas

- `CobDAO.GuardarCheque`
- `CobDAO.InsertarDetalleCheque`

### Elementos técnicos/auxiliares (no lógica de negocio)

*Coinciden con un patrón de código técnico/generado (p. ej. métodos del diseñador de WebForms). Se conservan como evidencia, con su confianza y trazabilidad intactas; no deben interpretarse como servicios de negocio.*

- `CobDAO.InitializeComponent`

## 5. Datos/SP/SQL

### Procedimientos almacenados
- `spInsertarRenovacionCheque` (paquete `PKG_COB`, procedimiento `PRC_INS_RENOVACION`)

### Evidencia transaccional
- `DAO-C01-TX`: evidencia transaccional confirmada (`BeginTrans`)

### Operaciones de datos confirmadas
- `DAO-C01-INS`: operación de datos confirmada `INSERT`

### Parámetros disponibles por invocador alcanzado
- `CobDAO.GuardarCheque`: `pChequeId`

## 6. Qué queda no resuelto

- Límite no resuelto: `UnknownHelper.Execute` — no se pudo confirmar su destino real.

Caminos con incertidumbre (`path_id`): `PATH-C01-2`.

Ninguna de estas ausencias se completa con una suposición: se declaran explícitamente como no resueltas.

## 7. Evidencia/trazabilidad

- `PATH` `PATH-C01-1` — evidencia: `EVR-C01-1`
  - `PATH-C01-1` → `index/functional_paths.json#PATH-C01-1`
- `PATH` `PATH-C01-2` — evidencia: `EVR-C01-2`
  - `PATH-C01-2` → `index/functional_paths.json#PATH-C01-2`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-C01`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 2 camino(s) determinista(s) original(es), 0 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 2 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 5) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.
