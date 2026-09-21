# Documentación humana de flujos — webCobMorosidad

*Esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R4`. [Volver al índice](../HUMAN_DOCUMENTATION.md).*

3 flujo(s) en este grupo.

# Flujo FLOW-D: webCobMorosidad\CobConsultaTransferencia.ascx → Load

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `webCobMorosidad\CobConsultaTransferencia.ascx`
- Proyectos/capas del sistema involucrados: WEB
- Confianza general del flujo: no resuelto

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Load`, manejado por `Page_Load`.

## 3. Qué hace, según evidencia

- Camino no resuelto: (sin pasos intermedios evidenciados) termina en límite no resuelto sin nombre resuelto (`unknown`).

## 4. Servicios/capas

No se identificaron servicios/clases de acceso a datos en la cadena de este flujo.

## 5. Datos/SP/SQL

No se confirmó acceso a procedimientos almacenados ni operaciones SQL para este flujo.


## 6. Qué queda no resuelto

- Límite no resuelto: `unknown` — no se pudo confirmar su destino real.

Caminos con incertidumbre (`path_id`): `PATH-D1`.

Ninguna de estas ausencias se completa con una suposición: se declaran explícitamente como no resueltas.

## 7. Evidencia/trazabilidad

- `PATH` `PATH-D1` — evidencia: (sin referencias de evidencia)
  - `PATH-D1` → `index/functional_paths.json#PATH-D1`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-D`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 1 camino(s) determinista(s) original(es), 0 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 1 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 5) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.

---

# Flujo FLOW-B: webCobMorosidad\cobCargaArcIntRea.ascx → Click

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `webCobMorosidad\cobCargaArcIntRea.ascx`
- Proyectos/capas del sistema involucrados: DAL, WEB
- Confianza general del flujo: confirmado

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Click`, manejado por `btnCargar_Click`.

## 3. Qué hace, según evidencia

- Camino confirmado: `CobDAO.Actualizar` termina en procedimiento almacenado `spActualizarSaldo`.

## 4. Servicios/capas

- `CobDAO.Actualizar`

## 5. Datos/SP/SQL

### Procedimientos almacenados
- `spActualizarSaldo` (paquete `PKG_COB`, procedimiento `PR_SALDO`)


## 6. Qué queda no resuelto

No quedan caminos ni límites sin resolver para este flujo, según la evidencia disponible.

## 7. Evidencia/trazabilidad

- `PATH` `PATH-B1` — evidencia: `EVR-B1`
  - `PATH-B1` → `index/functional_paths.json#PATH-B1`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-B`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 1 camino(s) determinista(s) original(es), 0 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 1 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 5) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.

---

# Flujo FLOW-C: webCobMorosidad\cobChqInsRen.ascx → Click

*Documento generado de forma determinista (sin IA), esquema `HUMAN_DOCUMENTATION_PROJECTION 1.0`, modelo `V4.3-R3`.*

## 1. Qué es y dónde está

- Formulario web: `webCobMorosidad\cobChqInsRen.ascx`
- Proyectos/capas del sistema involucrados: DAL
- Confianza general del flujo: confirmado

## 2. Evento/entrada inicial

El flujo se inicia con el evento `Click`, manejado por `HypGuardar_Click`.

## 3. Qué hace, según evidencia

- Camino confirmado: `CobChequesDAO.InsertarRenovacion` (evidencia transaccional confirmada (`BeginTrans`)) termina en procedimiento almacenado `spInsertarRenovacionCheque`.

## 4. Servicios/capas

- `CobChequesDAO.InsertarRenovacion`

## 5. Datos/SP/SQL

### Procedimientos almacenados
- `spInsertarRenovacionCheque` (paquete `PKG_COB`, procedimiento `PR_RENOVACION`)

### Evidencia transaccional
- `DAO-2`: evidencia transaccional confirmada (`BeginTrans`)


## 6. Qué queda no resuelto

No quedan caminos ni límites sin resolver para este flujo, según la evidencia disponible.

## 7. Evidencia/trazabilidad

- `PATH` `PATH-C1` — evidencia: `EVR-C1`
  - `PATH-C1` → `index/functional_paths.json#PATH-C1`

Puntero de origen del flujo: `index/functional_flows.json#FLOW-C`
Índices exhaustivos de origen: `index/functional_flows.json`, `index/functional_paths.json`, `index/entry_points.json`, `index/data_access.json`, `index/stored_procedures.json`, `index/sql_operations.json`, `index/data_parameters.json`

## Límites de esta documentación

- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se invoca ningún proveedor de IA para producir el contenido anterior.
- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres resueltos cuando existen.
- De 1 camino(s) determinista(s) original(es), 0 fueron cadenas equivalentes fusionadas (sin pérdida de `path_id` ni evidencia); este documento describe los 1 camino(s) resultantes.
- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.
- La evidencia transaccional y el tipo de operación de datos (sección 5) solo se muestran cuando el índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado como 'escritura' a partir de su nombre.
- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección separada, etiquetada `INTERPRETED`, al final.

