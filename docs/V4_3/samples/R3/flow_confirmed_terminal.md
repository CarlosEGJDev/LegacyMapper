# Flujo FLOW-B01: cobCargaArcIntRea.ascx → Click

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `cobCargaArcIntRea.ascx`
- Proyectos/capas del sistema involucrados: DAL, WEB
- Confianza general del flujo: confirmado

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Click`, manejado por `btnCargar_Click`.

## 3. Qué hace, según evidencia

- Camino confirmado: `CobDAO.CargarArchivo` termina en procedimiento almacenado `PKG_COB.PRC_CARGAR`.

## 4. Servicios/capas

- `CobDAO.CargarArchivo`

## 5. Datos/SP/SQL

### Procedimientos almacenados
- `PKG_COB.PRC_CARGAR` (paquete `PKG_COB`, procedimiento `PRC_CARGAR`)

### Parámetros disponibles por invocador alcanzado
- `CobDAO.CargarArchivo`: `pArchivoId`, `pFecha`

## 6. Qué queda no resuelto

No quedan caminos ni límites sin resolver para este flujo, según la evidencia disponible.

## 7. Evidencia/trazabilidad

- `PATH` `PATH-B01-1`, `PATH-B01-2` — evidencia: `EVR-B01-1`, `EVR-B01-2`
  - `PATH-B01-1` → `index/functional_paths.json#PATH-B01-1`
  - `PATH-B01-2` → `index/functional_paths.json#PATH-B01-2`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-B01`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 2 camino(s) determinista(s) original(es), 1 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 1 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 5) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.
