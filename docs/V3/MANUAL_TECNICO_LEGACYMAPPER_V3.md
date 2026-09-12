# Manual técnico de LegacyMapper V3

## 1. Propósito técnico

Este manual permite mantener LegacyMapper sin romper determinismo, trazabilidad, contratos de proveedor, decisiones humanas ni evidencia canónica.

## 2. Arquitectura de LegacyMapper

Es un pipeline Python modular: scanner → extractors → resolvers → context → LLM/documentation → human review → knowledge readiness → exporters.

## 3. Dos arquitecturas distintas

La arquitectura de **LegacyMapper** es su organización Python. La arquitectura del **sistema analizado** es un resultado sujeto a evidencia. V3 soporta evidencia WebForms, pero no confirma MVC ni una arquitectura formal única del legado.

## 4. Estructura de directorios

`analysis/` resuelve relaciones; `extractors/` obtiene hechos; `models/` define registros; `context/` compone paquetes; `llm/` aísla proveedores; `documentation/` crea y valida documentos; `knowledge/` aplica readiness; `exporters/` serializa; `utils/` contiene sanitización; `quality/` audita mantenibilidad.

## 5. Módulos principales

`legacy_documenter.main` orquesta discovery. `context.resolver` y `context.composer` preparan contexto. `documentation.*` controla assessment, síntesis y revisión. `knowledge.readiness` valida la frontera final V3.

## 6. Clases principales

`RepositoryScanner`, extractores especializados, `CallResolver`, `DatabaseResolver`, `FunctionalFlowResolver`, `ContextResolver`, `ContextComposer`, `LLMProvider`, adaptadores de proveedor y `KnowledgeReadinessService`.

## 7. Flujo runtime

`analyze_repository()` escanea, clasifica, extrae, consolida símbolos, resuelve llamadas/entradas/datos/flujos/dependencias y exporta índices y contextos.

## 8. Pipeline V1

V1 obtiene la estructura base y exporta inventarios sin requerir interpretación LLM.

## 9. Pipeline V2

V2 amplía relaciones, llamadas, flujos y evidencia canónica. Sus outputs son entradas inmutables de V3.

## 10. Pipeline V3

V3 resuelve y presupuesta contexto, aplica perfiles, valida respuestas, sintetiza documentos, incorpora revisiones humanas y proyecta readiness.

## 11. Discovery determinista

Los extractores leen archivos y los resolvers calculan relaciones. No se debe delegar al LLM identidad, conteos, ids, enlaces o estados factuales.

## 12. Context Resolver

`ContextResolver` lee `ai_context`, resuelve tipos de paquete y produce ids `CTX-*` a partir de JSON canónico.

## 13. Composición de contexto

`ContextComposer.compose()` prioriza P0..P4, aplica perfiles y presupuestos, deduplica y expone truncamiento/continuaciones.

## 14. Perfiles documentales

`documentation.interpretation` mantiene perfiles funcional y técnico, secciones permitidas y contratos de interpretación.

## 15. Abstracción LLMProvider

`LLMProvider` define `generate`, `capabilities` y `model_info`. `LLMRequest`/`LLMResponse` conservan identidad, propósito, uso, validación y errores.

## 16. Adaptador Copilot

`CopilotProvider` deshabilita herramientas, cambios de archivos, instrucciones dinámicas y sesiones persistentes. Solicita JSON estricto y convierte fallos en respuestas de dominio.

## 17. Adaptador Gemini

`GeminiProvider` permanece como adaptador HTTP compatible. Obtiene la credencial desde la variable indicada por `credential_source`; no la serializa. El registro actual crea FAKE y COPILOT; Gemini debe conectarse explícitamente antes de uso mediante un cambio probado.

## 18. Contratos de assessment

Los schemas cierran campos, estados, secciones e ids de evidencia permitidos. Python valida la salida antes de persistirla.

## 19. Modelo de evidencia

Cada evidencia conserva id canónico, categoría, lineage y snapshot. Los consumidores no deben usar descripciones como sustituto del id.

## 20. Modelo de claim

Un claim incluye statement, status, source type, evidence refs, sección y procedencia. Estados semánticos publicados: `CONFIRMED`, `INTERPRETED`, `UNRESOLVED`.

## 21. AllowedEvidenceCatalog

`evidence_catalog.py` expone claves locales `E*` al proveedor y las resuelve de vuelta a ids canónicos. Una clave desconocida causa error, nunca reparación.

## 22. Revisión humana

`human_review.py` prepara la primera revisión. `second_review.py` prepara las 20 disposiciones de R8.4. Los Markdown de autoridad son entradas humanas, no decisiones inventadas por runtime.

## 23. Deep source analysis

`analysis.deep_source` produce evidencia dirigida y sanitizada sin reabrir discovery completo.

## 24. Deep interpretation

`analysis.deep_interpretation` limita la interpretación a objetivos y contexto autorizados; la salida debe seguir evidencia y schema.

## 25. Knowledge readiness

`KnowledgeReadinessService.validate()` verifica approvals, disposiciones, claims, cierre de evidencia, métricas, arquitectura, seguridad y outputs.

## 26. Knowledge projection

`build_projection()` clasifica cada registro como fact, interpretation, partial, unresolved limitation o ineligible. No reescribe statements.

## 27. Knowledge boundary

`build_boundary()` separa conocido, interpretado, parcial, desconocido aceptado y assertions prohibidas consumibles por una fase posterior.

## 28. Modelo de seguridad

Fuente read-only, sanitizer centralizado, contexto acotado, herramientas del proveedor deshabilitadas y detección de valores con forma de secreto en la proyección.

## 29. Garantías de inmutabilidad

Cada ronda posterior trata evidencia y decisiones aprobadas como entrada. Pruebas y hashes verifican que ejecutar R9 solo modifica `output/v3_r9/`.

## 30. Manejo de errores

Violaciones de catálogo o schema levantan errores explícitos. Adaptadores externos convierten timeouts/configuración/fallos en `LLMResponse` seguro sin filtrar payloads.

## 31. Pruebas

La suite `unittest` contiene fixtures, contratos V1/V2/V3, providers, reproducibilidad, revisiones e inmutabilidad.

## 32. Cómo ejecutar pruebas

```text
python -m unittest discover -s tests
python -m unittest tests.test_v3_r9
```

## 33. Cómo agregar un módulo

Elija una responsabilidad, ubíquelo en el paquete correspondiente, añada docstring de módulo, tipos en límites públicos y pruebas antes de integrarlo al pipeline.

## 34. Cómo agregar una clase

Use una clase cuando exista estado o comportamiento cohesivo. Evite envolver una función simple sin beneficio. Documente efectos y dependencias.

## 35. Convenciones de nombres

Clases `PascalCase`; módulos, funciones y variables `snake_case`; constantes canónicas `UPPER_SNAKE_CASE`.

## 36. PascalCase y snake_case

`KnowledgeReadinessService` vive conceptualmente en `knowledge_readiness_service.py`; el wrapper histórico `knowledge/readiness.py` puede conservarse por compatibilidad. Python importa módulos en snake_case aunque la clase sea familiar para C#.

## 37. Type hints

Tipar APIs, servicios y transformaciones importantes. Prefiera `Path`, unions modernas y colecciones concretas. No introduzca genéricos complejos si ocultan el contrato.

## 38. Docstrings y comentarios

Explique propósito, resultado, efectos de escritura y razones de seguridad/determinismo. No repita el identificador de la función.

## 39. Cómo agregar un proveedor

Implemente `LLMProvider`, declare capabilities reales, produzca `LLMResponse`, proteja credenciales, deshabilite herramientas no requeridas, añada tests falsos y registre el tipo explícitamente en `ProviderRegistry`.

## 40. Cómo cambiar context budgeting

Modifique perfiles o reglas en `context/composer.py`, preserve prioridades y unresolved reserve, y pruebe COMPLETE/TRUNCATED/BUDGET_INSUFFICIENT, ids deterministas y reanudación.

## 41. Cómo extender tipos de evidencia

Actualice modelos/extractores, lineage, catálogos y schemas. Toda referencia publicada debe resolver de manera canónica y conservar snapshot.

## 42. Cómo extender revisión humana

Agregue decisiones permitidas al propietario canónico, valide igualdad exacta y mantenga separado recommendation de decisión humana explícita.

## 43. Cómo depurar validación fallida

Revise el status y checks del JSON de etapa. En R9 consulte `READINESS_TRACEABILITY.json`; ids en `unresolved_aliases` señalan la namespace rota.

## 44. Cómo inspeccionar artefactos

Use lectores JSON/Markdown; no edite para forzar PASS. Compare hashes antes/después y siga document → claim → evidence → package → snapshot.

## 45. Compatibilidad

No elimine entry points existentes. Si mueve código, deje un import o wrapper pequeño y pruebe ambos caminos.

## 46. Limitaciones conocidas

No hay CLI unificado para todas las rondas V3. La cobertura semántica no es total. Parte del código histórico tiene estilo compacto y documentación/tipos desiguales.

## 47. Deuda técnica preservada

Se conservan módulos compactos de R7/R8, broad exception boundaries de adaptadores y helpers potencialmente duplicados porque una limpieza masiva elevaría el riesgo antes de V4.

## 48. Guías para V4/V5

Aplicar el estándar Python permanente, extraer servicios solo con beneficio, centralizar valores canónicos gradualmente y conservar wrappers durante migraciones.

## 49. Checklist de modificación segura

Definir contrato; identificar inputs canónicos; evitar fuente; mantener sanitizer; tipar/documentar API; añadir pruebas; ejecutar suite; revalidar readiness; verificar hashes; documentar compatibilidad.

## 50. Checklist de regresión

Todos los tests PASS; R9 READY; allowed true; generated false; cero provider calls no autorizadas; evidencia/decisiones/proyección sin cambios; ningún secreto; ninguna escritura en legado.

