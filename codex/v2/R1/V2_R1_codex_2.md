Revisa la ejecución real de LegacyMapper V2-R1 ubicada en:

output/v2_r1_full/

NO implementes V2-R2.
NO modifiques el código de LegacyMapper.
Esta tarea es exclusivamente de análisis y validación de los resultados reales de V2-R1.

Debes analizar como mínimo:

output/v2_r1_full/index/calls.json
output/v2_r1_full/index/functional_dependencies.json
output/v2_r1_full/index/errors.json

Y, cuando sea necesario para validar resoluciones, cruza información con:

output/v2_r1_full/index/projects.json
output/v2_r1_full/index/symbols.json
output/v2_r1_full/index/logical_symbols.json
output/v2_r1_full/index/dependencies.json
output/v2_r1_full/index/webforms.json
output/v2_r1_full/index/repository.json

OBJETIVO

Determinar si el Call Graph producido por V2-R1 es suficientemente confiable para autorizar V2-R2.

No basta con entregar cantidades. Debes evaluar calidad, precisión aparente, ambigüedad y posibles falsos positivos/falsos negativos.

1. ESTADÍSTICAS GENERALES

Calcula:

- total de calls;
- confirmed;
- inferred;
- unresolved;
- porcentaje de cada categoría;
- total de instanciaciones si están disponibles;
- llamadas con receiver;
- llamadas internas;
- llamadas Me.*;
- llamadas MyBase.*;
- llamadas Shared/estáticas detectables;
- llamadas entre proyectos;
- clases con llamadas salientes;
- métodos con llamadas salientes;
- cantidad de targets únicos;
- cantidad de llamadas con múltiples candidatos.

2. FUNCTIONAL DEPENDENCIES

Analiza functional_dependencies.json e informa:

- total de relaciones;
- distribución por dependency_type/relation;
- distribución por confidence;
- relaciones Method -> Method;
- Method -> InstantiatesClass;
- Class -> UsesClass;
- relaciones cross-project;
- cualquier otra relación generada.

Comprueba que no existan duplicaciones masivas o crecimiento artificial evidente.

3. ERRORES

Analiza errors.json.

Indica:

- cantidad total;
- extractores/fases afectados;
- tipos de error;
- si alguno compromete la confiabilidad del Call Graph.

4. MUESTREO DE CALLS CONFIRMED

Selecciona al menos 20 calls `confirmed`, procurando variedad:

- llamadas internas;
- llamadas por instancia;
- Shared;
- cross-project;
- diferentes proyectos/módulos.

Para cada muestra comprueba usando los índices V1 y, cuando sea necesario, el código fuente local:

- que la clase destino exista;
- que el método destino exista cuando pueda comprobarse;
- que el proyecto destino sea coherente;
- que receiver/tipo/evidencia sean coherentes;
- que la clasificación `confirmed` esté justificada.

Clasifica cada muestra:

CORRECT
SUSPICIOUS
INCORRECT

Explica brevemente los casos SUSPICIOUS/INCORRECT.

5. MUESTREO DE INFERRED

Selecciona al menos 15 calls `inferred`.

Determina si:

- la inferencia es razonable;
- debería ser confirmed;
- debería ser unresolved;
- parece falso positivo.

6. MUESTREO DE UNRESOLVED

Selecciona al menos 20 calls `unresolved`.

Agrupa las causas principales, por ejemplo:

- receiver sin tipo;
- método sin paréntesis;
- múltiples candidatos;
- Imports ambiguos;
- variable no resuelta;
- llamada externa/DLL;
- sintaxis multilinea;
- late binding;
- factory;
- reflexión;
- parser insuficiente;
- otra.

El objetivo es descubrir qué mejoras darían mayor cobertura en futuras rondas.

7. FALSOS POSITIVOS

Busca activamente patrones sospechosos.

Especial atención a:

Metodo()

detectado dentro de expresiones donde en realidad no represente una llamada funcional válida.

Busca también:

- keywords interpretadas como métodos;
- constructores confundidos con llamadas;
- declaraciones confundidas con llamadas;
- llamadas duplicadas;
- nombres de propiedades confundidos con métodos;
- llamadas pertenecientes a comentarios o strings;
- llamadas dentro de código comentado.

Entrega ejemplos concretos si existen.

8. FALSOS NEGATIVOS

Realiza un muestreo del código VB.NET real buscando llamadas que el extractor probablemente no haya registrado.

Especial atención a:

- llamadas sin paréntesis;
- llamadas multilinea;
- With ... End With;
- Call Metodo(...);
- expresiones encadenadas;
- invocaciones sobre propiedades;
- Default properties;
- llamadas mediante interfaces;
- llamadas mediante variables declaradas fuera del método.

Entrega ejemplos concretos.

9. CROSS-PROJECT

Esta validación es especialmente importante.

Selecciona al menos 10 relaciones cross-project.

Comprueba:

origen -> proyecto origen -> referencia de proyecto/DLL -> destino

Determina si LegacyMapper está resolviendo relaciones entre Web, BL, SYS u otros proyectos de forma razonable.

No asumas que prefijos Web/bl/sys prueban la arquitectura; utilízalos sólo como evidencia auxiliar.

10. SANITY CHECK GLOBAL

Busca anomalías como:

- un único método apareciendo como destino de miles de llamadas;
- clases con cantidades absurdas de relaciones;
- targets inexistentes;
- project_path inexistentes;
- métodos resueltos únicamente por nombre global;
- relaciones confirmed con evidencia insuficiente;
- fuerte concentración artificial en determinados nombres comunes.

11. MÉTRICAS DE CALIDAD DEL MUESTREO

Entrega:

confirmed_sample_correct
confirmed_sample_suspicious
confirmed_sample_incorrect

inferred_sample_reasonable
inferred_sample_should_confirm
inferred_sample_should_unresolve
inferred_sample_incorrect

Además calcula una precisión observada del muestreo confirmed:

confirmed_observed_precision =
CORRECT / total_confirmed_sampled

Aclara explícitamente que es una estimación por muestreo y no una precisión global demostrada.

12. DECISIÓN

Finaliza obligatoriamente con UNA de estas decisiones:

A) V2-R1_APROBADA_PARA_R2

B) V2-R1_REQUIERE_CORRECCIONES

C) V2-R1_NO_CONFIABLE

Si eliges B o C, enumera las correcciones concretas necesarias y ordénalas:

CRITICAL
HIGH
MEDIUM
LOW

No implementes las correcciones.

13. INFORME

Genera únicamente:

codex/V2/V2_R1_VALIDACION_REAL.md

No generes ZIP.
No copies los JSON grandes.
No generes otros informes.

El informe debe ser autocontenido y suficientemente detallado para que un revisor externo pueda decidir si V2-R2 puede comenzar sin necesitar calls.json ni functional_dependencies.json completos.

IMPORTANTE:

- No modificar código.
- No iniciar V2-R2.
- No convertir inferencias en hechos.
- Citar rutas/identificadores/evidencia concreta dentro del informe.
- Si necesitas inspeccionar código fuente para verificar una muestra, puedes hacerlo en modo lectura.
- Prioriza precisión sobre cobertura.