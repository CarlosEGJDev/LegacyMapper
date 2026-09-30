# V5.2 R3.1 — Correcciones de claridad semántica de documentación humana

## 1. Estado

V5_2_R3_1_READY_FOR_HUMAN_REVIEW

No se modificó Evidence Core, V5.1, roadmap ni `PROJECT_STATE.json`. Sin commits ni push. Sin aprobación humana todavía.

## 2. Problemas humanos corregidos

| Hallazgo R3 | Corrección |
|---|---|
| Un proyecto «tenía» pantallas de otros proyectos (`blPENResoluciones`: 15 pantallas ajenas) | Propiedad separada de participación (sección 4) |
| Acceso a datos directo/indirecto parecía contradictorio | Secciones distintas (sección 5) |
| Titular «2370 flujos llegan a datos» incluía transacciones | Métrica recalculada: 672 reales (sección 6) |
| Bibliotecas mezcladas bajo «externas» | Tres clases (sección 7) |
| Jerga y valores crudos | Sección 8 |
| Copias `Backup` con sufijo `-2` | Nombre visible con ruta |
| Vista General = inventario | Explica estructura (sección 3) |

## 3. Jerarquía Solution/Project

Vista General: «Qué se analizó», «Cómo está organizado» (solución = .sln; proyecto = .vbproj/.csproj; «módulo» significa explícitamente «proyecto .NET»), «Cómo se comunican los proyectos», «Recorridos observados», «Acceso a datos», «Dependencias externas», «Qué no pudo determinarse». Además `modules.md` lista las soluciones con más proyectos y los proyectos más activos. No se inventan agrupaciones de negocio.

## 4. Propiedad vs participación en flujo

Un proyecto es dueño solo de las pantallas cuyo punto de entrada lo nombra como proyecto. Antes se usaba el primer proyecto de la secuencia del flujo, lo que atribuía pantallas web a proyectos de negocio. Ahora:

- «Flujos originados aquí» y «Flujos que llegan aquí» (con proyecto de origen y pantalla) son secciones separadas.
- Si el proyecto de la pantalla no está en la evidencia, el origen se muestra como «(origen no identificado)»; nunca se asigna al primer proyecto de la secuencia.
- IST: 1860 flujos (1878 eventos) tienen pantalla sin proyecto identificado y se agrupan aparte; los proyectos de negocio los muestran como flujos que llegan, no como pantallas propias.

## 5. Acceso directo vs indirecto

- «Acceso directo a datos»: operaciones declaradas en el propio proyecto («Acceso directo a datos: ninguno.» cuando no hay).
- «Datos alcanzados indirectamente»: datos reales que alcanzan los flujos originados en el proyecto pero declarados en otro. Ejemplo IST: `WebPENCalculoPensionIndem` → sin acceso directo, 11 procedimientos alcanzados indirectamente.

## 6. Métrica corregida

Derivada de la evidencia existente, con la política de ruido (`counts_as_data_access: false` en `transaction_control`, datos, no código). IST: 12 642 flujos; **672 (5,3 %) llegan a una operación real de datos**; 1698 solo a control transaccional (ya no se cuentan ni se muestran como «(transaction)»). Coincide con la medición de R3.

## 7. Dependencias

Clasificadas solo cuando hay evidencia: biblioteca interna del repositorio (coincide con un proyecto), de plataforma (política) o «Dependencia no clasificada» (IST: 97 / 35 / 60). No se afirma que algo sea de terceros ni se inventan servicios externos (declarado como límite).

## 8. Terminología

Catálogo `es`: sin «LegacyMapper», «evidencia estática», «INTERPRETED» ni «destino confirmado» en los documentos (solo aparecen en `MANIFEST.json`, artefacto técnico). «Recorrido» se define en la Vista General; «Resultado identificado», «Procedimiento almacenado», «Evento web», etc. reemplazan valores crudos (`translate: kind`).

## 9. Ruido técnico

Solo datos: nueva categoría `ui_control_calls` (`DataBind`). IST: `DataBind` en cuerpos de proyecto pasó de 83 a 0; sigue en el detalle.

## 10. RUN_SUMMARY

`documentation_v52` figura en `output_locations` cuando la etapa DOCUMENTATION tiene éxito (`run_summary_presenter.py`); test agregado y verificado en la corrida IST.

## 11. GAPs / deuda restante

1. Pantalla → proyecto no está en la evidencia para 1860 flujos (un enlace por archivo de código-behind resolvió solo ~12 %, con ambigüedad); requiere mejora futura de Evidence, no hecha aquí.
2. P-2 flujo → archivo:línea del manejador: requiere nueva extracción; no implementado.
3. Ruido residual de controles distinto de `DataBind`: no se abrió limpieza adicional.
4. Nombres de archivo `-2`/`-3` se conservan solo como nombre de archivo.
5. Índice de partes no particionable bajo límites extremos; modo estricto sin CLI (heredado).
6. `transform.py` pasó a riesgo HIGH en el inventario (test ajustado).

## 12. Prueba IST

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_1_validation\run` (R2/R3 intactos). `full` SUCCESS, 866 archivos, 0 advertencias, `documentation_v52` en `RUN_SUMMARY`. Tiempo ~33 min.

## 13. Suite

`python -m unittest discover -s tests`: 2351 tests, 0 fallas, 0 errores, 132 skips (esperados). Nuevos: 29 en `tests/test_v5_2_r3_1_human_semantic_corrections.py`; se actualizaron aserciones de textos en R2 y contadores del inventario V4.1.

## 14. Nueva muestra humana

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_1_validation\human_review_sample\README.md` (copias sin editar: Vista General completa, `BLInterfazSAP` simple, `WebMEDPabellon` medio, `blPENResoluciones` complejo, `sysPENResoluciones` directo, `WebPENCalculoPensionIndem` indirecto, `WebSUBCalculoPagoSubsidios` no resuelto, `WebADHTraspaso`/`-2` duplicados).

## 15. Qué debe revisar el Technical Lead

1. ¿Se entiende solución vs proyecto y el uso de «módulo»?
2. ¿Las pantallas pertenecen al proyecto correcto y «Flujos que llegan aquí» es claro? ¿Molesta «(origen no identificado)» en proyectos de negocio?
3. ¿Directo vs indirecto se lee sin contradicción?
4. ¿La cifra 672 (5,3 %) es honesta y bien explicada?
5. ¿Clasificación de dependencias y término «recorrido» en Vista General?
6. ¿Aprobar, pedir ajustes o resolver la deuda 1 antes de R4?

## 16. Conclusión

Las correcciones semánticas viven en Transformation, política de ruido, catálogo y templates; el renderer no cambió. Quedan limitaciones honestas de evidencia (origen de pantallas). La revisión humana es obligatoria.

V5_2_R3_1_READY_FOR_HUMAN_REVIEW
