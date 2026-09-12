# Validación Real LegacyMapper V2-R1

## Resumen Ejecutivo

Se revisó la ejecución real ubicada en `output/v2_r1_full/`, especialmente:

- `output/v2_r1_full/index/calls.json`
- `output/v2_r1_full/index/functional_dependencies.json`
- `output/v2_r1_full/index/errors.json`
- cruces con `projects.json`, `symbols.json`, `dependencies.json`, `webforms.json` y `repository.json`

Resultado: V2-R1 produce información útil, especialmente en llamadas `confirmed` Web/BL/SYS donde el destino existe en `symbols.json`. Sin embargo, todavía no es suficientemente confiable para construir V2-R2 encima sin correcciones. El principal problema no está en errores de ejecución, sino en calidad: exceso de `inferred` falsos o débiles, detección de accesos a colecciones como llamadas funcionales, duplicación alta en `functional_dependencies.json`, y evidencia parcial para varios `confirmed`.

Decisión final: **B) V2-R1_REQUIERE_CORRECCIONES**

---

## 1. Estadísticas Generales

Repositorio analizado:

- root: `E:\IAProyectos\revision\revision-main`
- total archivos: 14.355
- `.vb`: 4.328
- `.vbproj`: 260
- `.sln`: 113
- WebForms: 3.346 aproximados (`aspx`: 177, `ascx`: 3.165, `master`: 4)
- errores: 0

Call graph:

| Métrica | Valor |
|---|---:|
| total calls | 453.574 |
| confirmed | 10.909 |
| inferred | 210.786 |
| unresolved | 231.879 |
| confirmed % | 2,41 % |
| inferred % | 46,47 % |
| unresolved % | 51,12 % |
| instanciaciones | 40.279 |
| instanciaciones confirmed | 1.833 |
| instanciaciones unresolved | 38.446 |
| llamadas con receiver | 237.424 |
| llamadas internas sin receiver | 216.150 |
| llamadas `Me.*` | 6.024 |
| llamadas `MyBase.*` | 2.441 |
| llamadas Shared/estáticas detectables por receiver con mayúscula inicial | 64.840 |
| llamadas cross-project confirmed | 7.841 |
| clases con llamadas salientes | 2.959 |
| métodos con llamadas salientes | 40.204 |
| targets resueltos únicos | 32.611 |
| llamadas con múltiples candidatos | 8.808 |

Observación: el volumen total de llamadas es alto, pero más del 97 % no queda `confirmed`. El sistema ya captura mucha actividad, pero todavía mezcla llamadas funcionales con accesos a colecciones, built-ins VB y expresiones en strings.

---

## 2. Functional Dependencies

`functional_dependencies.json` contiene 532.200 relaciones.

Distribución por tipo:

| Tipo | Cantidad | % |
|---|---:|---:|
| Method -> Method | 453.574 | 85,23 % |
| Method -> InstantiatesClass | 40.279 | 7,57 % |
| Class -> UsesClass | 38.347 | 7,21 % |

Distribución por confianza:

| Confianza | Cantidad | % |
|---|---:|---:|
| confirmed | 14.488 | 2,72 % |
| inferred | 210.786 | 39,61 % |
| unresolved | 306.926 | 57,67 % |

Cross-project:

- confirmed cross-project: 7.841
- ejemplos frecuentes de origen/destino:
  - `WebADHAdmCalculoDs67.vbproj -> bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj`
  - `WebADHAdmCalculoDs67.vbproj -> bl\blParGenerales\blParGenerales.vbproj`
  - `WebPENCalculoPensionIndem.vbproj -> bl\blPENResoluciones\blPENResoluciones.vbproj`
  - `bl\blCobMorosidad\blCobMorosidad.vbproj -> sys\sysCOBMorosidad\sysCOBMorosidad.vbproj`

Duplicación:

- 36.251 claves duplicadas.
- 85.692 filas extra por duplicación.
- ejemplos:
  - 563 veces: `BLResoluciones -> SondaExceptionManager`, `Class -> UsesClass`, `Dim sm As New SondaExceptionManager(e, False)`, `unresolved`
  - 285 veces: `BLResoluciones -> OraConn`, `Class -> UsesClass`, `dbc = New OraConn`, `unresolved`
  - 272 veces: `BLResoluciones -> OraConn`, `Class -> UsesClass`, `dbc = New OraConn()`, `unresolved`

Conclusión: no se observa un crecimiento infinito, pero sí hay crecimiento artificial relevante por relaciones repetidas de instanciación/uso a nivel clase. Esto debe corregirse antes de usar el grafo como base de flujos.

---

## 3. Errores

`errors.json`:

- total errores: 0
- extractores afectados: ninguno
- tipos de error: ninguno

Esto es positivo: la ejecución es robusta operacionalmente. Los problemas detectados son de precisión del modelo, no de estabilidad.

---

## 4. Muestreo de Calls Confirmed

Se revisaron 24 llamadas `confirmed`, cruzando contra `symbols.json`, `projects.json` y código fuente puntual cuando fue necesario.

| # | Evidencia | Resolución | Clasificación |
|---:|---|---|---|
| 1 | `bl\blPistCargaArchSisesat.vb:223`, `ParRuta.txtraer` | `Sonda.Gestion.Nssmut.Bl.ParametrosGenerales.ParRuta.txtraer` | CORRECT |
| 2 | `webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:61`, `blADHds67.txtraerPereva` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | CORRECT |
| 3 | `webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:124`, `blADHds67.txTraerDatosRut` | método existe en `blADHds67` | CORRECT |
| 4 | `webADHAdmCalculoDs67\ucADHActualizaTasasRecal.ascx.vb:80`, `blADHds67.txtraerPereva` | método destino único | CORRECT |
| 5 | `webADHAdmCalculoDs67\ucADHAnexoDEU.ascx.vb:58`, `blUtil.CargaCamposFormulario` | método destino único | CORRECT |
| 6 | `webADHAdmCalculoDs67\ucADHAnexoNOM.ascx.vb:61`, `blUtil.CargaCamposFormulario` | método destino único | CORRECT |
| 7 | `webADHAdmCalculoDs67\ucADHAnexoPAT.ascx.vb:282`, `blUtil.CargaCamposFormulario` | método destino único | CORRECT |
| 8 | `webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:90`, `ParRuta.txtraer` | cross-project Web -> BL ParGenerales | CORRECT |
| 9 | `ucADHActualizaTasas.ascx.vb:61`, `blADHds67.txtraerPereva` | source project no resuelto, target existe | SUSPICIOUS |
| 10 | `ucADHActualizaTasas.ascx.vb:124`, `blADHds67.txTraerDatosRut` | source project no resuelto, target existe | SUSPICIOUS |
| 11 | `ucADHActualizaTasasRecal.ascx.vb:80`, `blADHds67.txtraerPereva` | source project no resuelto, target existe | SUSPICIOUS |
| 12 | `ucADHAnexoDEU.ascx.vb:57`, `blUtil.CargaCamposFormulario` | source project no resuelto, target existe | SUSPICIOUS |
| 13 | `ucADHAnexoNOM.ascx.vb:60`, `blUtil.CargaCamposFormulario` | source project no resuelto, target existe | SUSPICIOUS |
| 14 | `ucADHCalPruImpresion.ascx.vb:62`, `ParRuta.txtraer` | source project no resuelto, target existe | SUSPICIOUS |
| 15 | `ucADHCalPruImpresion.ascx.vb:89`, `ParNum.txLlenarDropDownList` | source project no resuelto, target existe | SUSPICIOUS |
| 16 | `ucADHCargaRecupero.ascx.vb:66`, `ParNum.txLlenarDropDownList` | source project no resuelto, target existe | SUSPICIOUS |
| 17 | `bl\blPistCargaArchSisesat.vb:103`, `DescomprimirArchivo()` | método local existe | CORRECT |
| 18 | `webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:74`, `Mostrar_Campos()` | método local existe | CORRECT |
| 19 | `webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:102`, `Grabar_Lote()` | método local existe | CORRECT |
| 20 | `webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:142`, `Mostrar_Campos()` | método local existe | CORRECT |
| 21 | `webADHAdmCalculoDs67\ucADHGenArcServicePDF.ascx.vb:149`, `Mostrar_Campos()` | método local existe | CORRECT |
| 22 | `webADHAdmCalculoDs67\ucADHCartasDefine.ascx.vb:350`, `blADHds67.txLeeUltSecCalRut` | método destino existe | CORRECT |
| 23 | `webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:276`, `blPadhD67Rut.txCargarAdhTasas` | método destino existe | CORRECT |
| 24 | `webADHAdmCalculoDs67\ucADHCargaTasaHistorica.ascx.vb:331`, `blPadhD67Rut.txReversarAdhTasas` | método destino existe | CORRECT |

Resultado del muestreo confirmed:

- confirmed_sample_correct: 16
- confirmed_sample_suspicious: 8
- confirmed_sample_incorrect: 0
- confirmed_observed_precision: 16 / 24 = 66,7 %

Esta es una estimación por muestreo, no una precisión global demostrada. La precisión sube si se consideran aceptables los casos con target confirmado pero source project no resuelto, pero para V2-R2 eso todavía es una debilidad importante.

Hallazgo adicional: en código real se observó `Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(2)`, pero el extractor registra la llamada como receiver `blADHds67` y pierde el qualifier anterior en el modelo de llamada. El target final puede ser correcto, pero la evidencia estructurada queda incompleta.

---

## 5. Muestreo de Inferred

Se revisaron 25 llamadas `inferred`.

Ejemplos:

- `CabeceraGrande.ascx.vb:14`, `InitializeComponent()` -> `CabeceraGrande.initializecomponent`
- `PREComite.vb:13`, `values()` -> `PREComite.values`
- `PREComite.vb:22`, `IsNothing(dbc)` -> `PREComite.isnothing`
- `PREComite.vb:25`, `IsNothing(dbc)` -> `PREComite.isnothing`
- `ucADHActualizaTasas.ascx.vb:47`, `OnClickWindowOpen(...)` dentro de string JavaScript -> `ucADHActualizaTasas.onclickwindowopen`
- `ucADHActualizaTasas.ascx.vb:48`, `onGuardarOff(...)` dentro de string JavaScript -> `ucADHActualizaTasas.onguardaroff`
- `ucADHActualizaTasas.ascx.vb:57`, `Format(Now.Month, "00")` -> `ucADHActualizaTasas.format`
- `ucADHActualizaTasas.ascx.vb:77`, `Parametros_Ok()` -> `ucADHActualizaTasas.parametros_ok`

Evaluación:

- inferred_sample_reasonable: 4
- inferred_sample_should_confirm: 3
- inferred_sample_should_unresolve: 6
- inferred_sample_incorrect: 12

Problema cuantificado:

- `inferred` sospechosos por built-ins VB o identificadores equivalentes: 111.980.
- `inferred` originados en strings JavaScript detectables: 2.771.

Conclusión: el nivel `inferred` actual no es confiable como base para flujos. Debe dejar de fabricar targets tipo `Clase.isnothing`, `Clase.cstr`, `Clase.values`, `Clase.format` y similares.

---

## 6. Muestreo de Unresolved

Muestras observadas:

- `funcGral.vb:7`, `ddl.Items(i)`, receiver `ddl`, unresolved.
- `PREComite.vb:11`, `dbc.BeginTrans()`, receiver `dbc`, unresolved.
- `PREComite.vb:14`, `dbc.ExecProc(...)`, receiver `dbc`, unresolved.
- `PREComite.vb:20`, `dbc.Commit()`, receiver `dbc`, unresolved.
- `PREComite.vb:22`, `dbc.Rollback()`, receiver `dbc`, unresolved.
- `PREComite.vb:25`, `dbc.Close()`, receiver `dbc`, unresolved.
- `ucADHActualizaTasas.ascx.vb:47`, `hypBusEmp.Attributes("href")`, receiver `hypBusEmp`, unresolved.
- `ucADHActualizaTasas.ascx.vb:48`, `btnSimular.Attributes("onClick")`, receiver `btnSimular`, unresolved.
- `ucADHActualizaTasas.ascx.vb:50`, `btnContinuar.Attributes("onClick")`, receiver `btnContinuar`, unresolved.

Causas principales estimadas:

| Causa | Cantidad |
|---|---:|
| framework_or_data_receiver_untyped | 109.901 |
| receiver_without_resolved_type | 106.217 |
| multiple_candidates | 8.808 |
| internal_or_unknown_without_symbol | 5.998 |
| vb_builtin_function | 920 |
| javascript_string_or_ui_expression | 35 |

Observación: muchos unresolved son esperables y sanos: `dbc.ExecProc`, `DataSet.Tables`, `Rows`, `Items`, controles WebForms y objetos framework. Para V2-R3, `dbc.ExecProc(...)` será valioso como acceso a datos, pero en V2-R1 está correctamente no resuelto como llamada de método propia del sistema.

---

## 7. Falsos Positivos

Patrones problemáticos encontrados:

1. Built-ins VB inferidos como métodos locales:
   - `PREComite.vb:22`, `IsNothing(dbc)` -> `PREComite.isnothing`
   - `ucADHActualizaTasas.ascx.vb:57`, `Format(Now.Month, "00")` -> `ucADHActualizaTasas.format`
   - otros nombres frecuentes: `CStr`, `CInt`, `CDate`, `IIf`, `CDbl`.

2. Array/identificadores tratados como llamada:
   - `PREComite.vb:13`, `Dim values() As Object = {...}` registrado como `values()`.

3. JavaScript dentro de strings tratado como llamada VB:
   - `ucADHActualizaTasas.ascx.vb:47`, string `javascript:OnClickWindowOpen(...)` registrado como llamada inferred.
   - `ucADHActualizaTasas.ascx.vb:48`, string `javascript:onGuardarOff(...)` registrado como llamada inferred.

4. Accesos a colecciones tratados como llamadas funcionales:
   - `ds.Tables(0)`
   - `Rows(0)`
   - `Item("...")`
   - `Attributes("href")`

5. Duplicaciones funcionales:
   - `Class -> UsesClass` para `OraConn` y `SondaExceptionManager` se repite cientos de veces por clase/archivo.

No se detectó evidencia de comentarios activos confundidos de forma masiva, pero sí strings con JavaScript y accesos indexados confundidos como llamadas.

---

## 8. Falsos Negativos

Riesgos observados o altamente probables:

- llamadas sin paréntesis no quedan cubiertas suficientemente;
- llamadas multilinea con `_` se capturan parcialmente, pero pueden perder receiver o argumentos;
- expresiones `Call Metodo(...)` pueden detectarse si queda `Metodo(...)`, pero el prefijo `Call` no se modela;
- cadenas fully-qualified pierden prefijos: `Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(...)` queda estructurado como receiver `blADHds67`;
- `With ... End With` no queda modelado;
- variables declaradas fuera del método no se usan para resolver receiver;
- propiedades que devuelven servicios o factories no se resuelven;
- llamadas sobre interfaces no se resuelven en esta salida real;
- métodos privados/locales pueden quedar `inferred` porque V1 no siempre los incluye como miembros resolubles.

Ejemplos concretos:

- `PREComite.vb` declara `Dim dbc As OraConn`, luego `dbc.ExecProc(...)`; el receiver se conoce por declaración, pero queda unresolved porque V2-R1 no resuelve tipos externos/DLL.
- `webADHAdmCalculoDs67\ucADHActualizaTasas.ascx.vb:61` contiene llamada fully-qualified a `Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(2)`; el target final es plausible, pero el qualifier completo no queda preservado en campos separados.
- `ucADHActualizaTasas.ascx.vb:77`, `Parametros_Ok()` aparece inferred aunque el método existe como `Private Function`; esto sugiere que la extracción de miembros V1 limita resolución de llamadas internas privadas.

---

## 9. Cross-Project

Se revisaron más de 10 relaciones cross-project. Ejemplos:

| Origen | Destino | Evidencia | Evaluación |
|---|---|---|---|
| `WebADHAdmCalculoDs67.vbproj` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | `ucADHActualizaTasas.ascx.vb:61`, `blADHds67.txtraerPereva` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | `ucADHActualizaTasas.ascx.vb:124`, `txTraerDatosRut` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | `ucADHAnexoDEU.ascx.vb:58`, `blUtil.CargaCamposFormulario` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blParGenerales\blParGenerales.vbproj` | `ucADHCargaTasaHistorica.ascx.vb:90`, `ParRuta.txtraer` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blParGenerales\blParGenerales.vbproj` | `ucADHCartasDefine.ascx.vb:111`, `ParNum.txLlenarDropDownList` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | `ucADHCargaTasaHistorica.ascx.vb:276`, `txCargarAdhTasas` | razonable |
| `WebADHAdmCalculoDs67.vbproj` | `bl\blADHAdmCalculoDs67\blADHAdmCalculoDs67.vbproj` | `ucADHCargaTasaHistorica.ascx.vb:331`, `txReversarAdhTasas` | razonable |
| `bl\BlCargaSISESAT.vbproj` | `bl\blParGenerales\blParGenerales.vbproj` | `blPistCargaArchSisesat.vb:223`, `ParRuta.txtraer` | razonable |
| `WebPENCalculoPensionIndem.vbproj` | `bl\blPENResoluciones\blPENResoluciones.vbproj` | concentración top source/target | requiere muestreo adicional |
| `bl\blCobMorosidad\blCobMorosidad.vbproj` | `sys\sysCOBMorosidad\sysCOBMorosidad.vbproj` | concentración top source/target | útil para V2-R3/R4, validar después |

Conclusión cross-project: la señal es prometedora. LegacyMapper sí está encontrando relaciones Web -> BL y BL -> SYS. Pero no debe avanzar a flujos todavía porque la resolución depende demasiado de coincidencias de receiver/clase y no siempre demuestra el tipo del receiver.

---

## 10. Sanity Check Global

Anomalías detectadas:

- targets inferred artificiales frecuentes:
  - `PrePrevencion.isnothing`
  - `BLResoluciones.isnothing`
  - `FiscalizacionRemota.cstr`
  - `ccTransacciones.iif`
  - `sysPREPrevencion.values`
- métodos más detectados globalmente incluyen muchos no funcionales:
  - `tables`: 41.874
  - `item`: 34.585
  - `cstr`: 32.425
  - `isnothing`: 22.461
  - `cint`: 21.889
  - `iif`: 20.309
- top unresolved receivers:
  - `dbc`: 51.202
  - `_row`: 28.234
  - `ds`: 18.485
  - `Columns`: 5.987
  - `Items`: 3.397
- duplicación alta en functional dependencies: 85.692 filas extra.

No se observó que un único método `confirmed` absorba miles de llamadas. Los targets `confirmed` más repetidos son plausibles, por ejemplo:

- `ParNum.txLlenarDropDownList`: 540
- `ParAlfNum.txLlenarDropDownList`: 387
- `ParUga.txtraer`: 132
- `Fechas.txahora`: 124

Esto sugiere que el subconjunto `confirmed` tiene valor real, aunque todavía requiere endurecimiento.

---

## 11. Métricas de Calidad del Muestreo

Confirmed:

- confirmed_sample_correct: 16
- confirmed_sample_suspicious: 8
- confirmed_sample_incorrect: 0
- confirmed_observed_precision: 66,7 %

Inferred:

- inferred_sample_reasonable: 4
- inferred_sample_should_confirm: 3
- inferred_sample_should_unresolve: 6
- inferred_sample_incorrect: 12

Aclaración: estas métricas son estimaciones por muestreo dirigido, no una medición global estadísticamente demostrada.

---

## 12. Correcciones Requeridas

### CRITICAL

1. Filtrar built-ins y funciones intrínsecas VB antes de crear llamadas funcionales o targets inferred:
   - `IsNothing`, `CStr`, `CInt`, `CDate`, `CDbl`, `CDec`, `IIf`, `Format`, `DateAdd`, `CType`, `DirectCast`, `TryCast`, `GetType`.

2. Evitar inferir target local cuando no existe método en `symbols.json`.
   - `Clase.isnothing` y `Clase.values` no deben producirse.
   - Si no hay miembro confirmado, dejar `unresolved` o clasificar como `external/builtin` cuando aplique.

3. No parsear llamadas dentro de literales string.
   - Casos `javascript:OnClickWindowOpen(...)`, `onGuardarOff(...)`, `onMensajeOff(...)` deben excluirse del call graph VB.

### HIGH

4. Distinguir llamadas funcionales de accesos indexados/default properties:
   - `Tables(0)`, `Rows(0)`, `Item("...")`, `Attributes("href")`, `Session("...")`.

5. Deduplicar `functional_dependencies.json`.
   - Especialmente `Class -> UsesClass` repetidas por cada instanciación idéntica.

6. Preservar qualifiers completos en llamadas fully-qualified.
   - Ejemplo: `Bl.ADHAdmCalculoDs67.blADHds67.txtraerPereva(...)` debe conservar receiver completo o una cadena de qualifier.

### MEDIUM

7. Mejorar resolución de variables declaradas sin `New`:
   - `Dim dbc As OraConn` debería registrar tipo del receiver aunque no sea clase del sistema.

8. Incorporar miembros privados de forma estructural para resolver llamadas internas:
   - Ejemplo: `Parametros_Ok()` debería poder confirmarse si existe `Private Function Parametros_Ok`.

9. Separar llamadas a framework/DLL de llamadas unresolved internas.
   - `OraConn.ExecProc`, `DataSet.Tables`, `Response.Redirect`, `Request.QueryString`.

### LOW

10. Mejorar normalización de casing en `resolved_target` sin perder casing original del método.

11. Agregar métricas directas al output:
   - total calls por confidence;
   - top unresolved receivers;
   - duplicados;
   - cross-project confirmed;
   - candidates múltiples.

---

## 13. Decisión

**B) V2-R1_REQUIERE_CORRECCIONES**

Motivo: V2-R1 ya descubre llamadas reales y cross-project valiosas, pero el call graph todavía mezcla demasiados falsos positivos e inferencias débiles. Autorizar V2-R2 encima de esta base arriesgaría construir entry points y flujos WebForms sobre relaciones ruidosas.

V2-R2 NO debe iniciarse hasta corregir al menos los puntos CRITICAL y HIGH.
