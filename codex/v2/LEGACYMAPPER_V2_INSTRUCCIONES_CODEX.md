# LegacyMapper — V2 Functional System Mapping
## Instrucciones maestras para Codex

## 1. Autoridad y objetivo

Este documento autoriza el inicio de **LegacyMapper V2**.

V1 queda considerada suficientemente validada sobre el repositorio legacy real como base estructural. V2 debe construirse **encima de V1**, preservando compatibilidad y evitando convertir LegacyMapper en un analizador basado principalmente en heurísticas o LLM.

V2 es la fase central del proyecto.

Su objetivo es transformar el mapa estructural de V1 en un **modelo funcional y trazable del sistema**, capaz de responder no sólo:

> ¿Qué archivos, proyectos, clases y vistas existen?

sino también:

> ¿Qué hace el sistema, qué componentes participan en cada operación y cómo fluye una acción desde la interfaz hasta las capas de negocio y persistencia?

El resultado debe ser reutilizable por:

- desarrolladores;
- mantenedores del legacy;
- arquitectos;
- herramientas automáticas;
- modelos de IA;
- generadores de documentación;
- generadores de diagramas.

---

# 2. Principio rector

Mantener estrictamente:

```text
Código fuente
    ↓
extracción determinista
    ↓
hechos comprobables
    ↓
resolución de relaciones
    ↓
grafo funcional
    ↓
modelo intermedio del sistema
    ↓
contexto para IA/documentación/diagramas
```

## Regla fundamental

> Python descubre y relaciona hechos. La IA interpreta esos hechos.

V2 NO debe utilizar un LLM para sustituir relaciones que puedan obtenerse determinísticamente.

Cuando una relación no pueda comprobarse:

```text
confirmed
inferred
unresolved
```

o el sistema de confianza equivalente existente.

Nunca convertir una inferencia en un hecho confirmado.

---

# 3. Base V1 que debe preservarse

La última ejecución real validada de V1-R1 produjo aproximadamente:

- 14.355 archivos analizados;
- 113 soluciones;
- 260 proyectos;
- 4.328 fuentes VB.NET;
- 6.513 símbolos;
- 3.346 Web Forms;
- 3.146 Web Forms con CodeBehind identificado;
- 26.941 relaciones estructurales;
- 0 errores.

V1 ya proporciona, entre otras relaciones:

```text
Solution -> Project
Project -> Project
Project -> DLL
Project -> SourceFile
Namespace -> Class
Class -> BaseClass
Class -> Interface
WebForm -> CodeBehind
WebForm -> VBClass
WebForm -> RegisteredNamespace
WebForm -> JavaScript
WebForm -> CSS
ASPX -> MasterPage
```

V2 debe reutilizar estos índices y modelos.

No duplicar innecesariamente lógica existente.

---

# 4. Alcance de V2

V2 debe incorporar análisis funcional profundo pero continuar siendo una fase principalmente determinista.

Debe analizar como mínimo:

1. Imports VB.NET.
2. instanciaciones de clases;
3. referencias a tipos;
4. llamadas a métodos;
5. llamadas entre clases;
6. llamadas entre proyectos;
7. implementación y uso de interfaces;
8. herencia relevante para resolución;
9. eventos Web Forms;
10. handlers de eventos;
11. flujo WebForm -> CodeBehind -> método;
12. llamadas CodeBehind -> BL;
13. llamadas BL -> SYS/DAL u otras capas;
14. acceso a Oracle;
15. SQL embebido;
16. stored procedures;
17. comandos Oracle;
18. parámetros Oracle;
19. connection strings/configuración relacionada;
20. servicios externos cuando puedan detectarse;
21. flujos funcionales reconstruibles;
22. trazabilidad completa de cada relación.

---

# 5. Lo que V2 NO debe hacer todavía

No implementar:

- modificación del código legacy;
- refactor automático;
- migración tecnológica;
- generación de código nuevo para el sistema legacy;
- ejecución de SQL;
- conexión real a Oracle;
- ejecución de stored procedures;
- modificación de configuraciones;
- vector database;
- embeddings;
- LangGraph;
- arquitectura multiagente;
- dependencia obligatoria de servicios cloud;
- inferencia funcional presentada como hecho;
- análisis semántico mediante LLM dentro del pipeline determinista.

La integración interpretativa con Qwen3 debe diseñarse como una capa posterior y desacoplada.

---

# 6. Arquitectura V2

Extender la arquitectura existente de LegacyMapper.

Estructura conceptual sugerida:

```text
legacy_documenter/
│
├── extractors/
│   ├── vbnet_extractor.py
│   ├── webforms_extractor.py
│   ├── webconfig_extractor.py
│   ├── call_extractor.py
│   ├── database_extractor.py
│   └── external_service_extractor.py
│
├── analysis/
│   ├── dependency_resolver.py
│   ├── symbol_resolver.py
│   ├── call_resolver.py
│   ├── database_resolver.py
│   ├── functional_flow_resolver.py
│   └── system_model_builder.py
│
├── models/
│   ├── call.py
│   ├── database_operation.py
│   ├── functional_flow.py
│   ├── evidence.py
│   └── ...
│
├── context/
│   ├── context_builder.py
│   └── ai_context_builder.py
│
└── exporters/
    ├── json_exporter.py
    ├── markdown_exporter.py
    └── graph_exporter.py
```

No es obligatorio utilizar exactamente estos nombres si la arquitectura actual permite una solución más coherente.

Evitar archivos monolíticos.

---

# 7. V2-A — Modelo de evidencia

Antes de ampliar el análisis, formalizar cómo se representa evidencia.

Cada relación funcional importante debe poder indicar como mínimo:

```json
{
  "source": "...",
  "target": "...",
  "relation": "...",
  "confidence": "confirmed",
  "evidence": {
    "file": "...",
    "line": 123,
    "expression": "..."
  }
}
```

Cuando sea posible agregar:

```text
project
class
method
namespace
```

La línea es recomendable cuando pueda calcularse de manera confiable.

No es necesario almacenar bloques completos de código.

Evitar duplicar grandes cantidades de fuente en JSON.

---

# 8. V2-B — Extracción de Imports y referencias de tipos

Extraer:

```vb
Imports Namespace
Imports Alias = Namespace.Tipo
```

Relacionarlos con:

```text
File -> ImportedNamespace
File -> ImportedType
```

cuando corresponda.

Registrar aliases.

Los Imports deben utilizarse posteriormente como evidencia para resolver tipos, pero un `Imports` por sí solo NO implica que una clase sea utilizada.

---

# 9. V2-C — Instanciaciones

Detectar patrones VB.NET como:

```vb
Dim servicio As New Servicio()
Dim servicio As Servicio = New Servicio()
New Servicio()
```

y variantes razonables.

Generar relaciones:

```text
Method -> InstantiatesClass
Class -> UsesClass
```

La relación `Class -> UsesClass` puede derivarse de instanciaciones confirmadas dentro de sus métodos.

Registrar:

- archivo;
- clase contenedora;
- método contenedor;
- tipo textual;
- tipo resuelto cuando sea posible;
- proyecto origen;
- proyecto destino;
- evidencia;
- confianza.

---

# 10. V2-D — Extracción de llamadas

Detectar llamadas como:

```vb
obj.Metodo()
Clase.Metodo()
Metodo()
Me.Metodo()
MyBase.Metodo()
```

y otras formas comunes del código real.

Distinguir:

```text
call expression
receiver
method name
arguments count
containing class
containing method
```

No es obligatorio comprender semánticamente cada argumento en la primera implementación.

---

# 11. V2-E — Resolución de llamadas

Esta es una de las piezas más importantes de V2.

Construir un `CallResolver` o equivalente capaz de intentar resolver:

```text
llamada textual
    ↓
variable/receptor
    ↓
tipo
    ↓
clase
    ↓
método
    ↓
proyecto
```

Usar evidencia disponible:

1. clase/método actual;
2. variables declaradas;
3. tipos explícitos;
4. instanciaciones;
5. Imports;
6. namespace declarado/efectivo;
7. proyecto;
8. referencias de proyecto;
9. interfaces;
10. herencia;
11. miembros Shared;
12. símbolos de V1.

Clasificar resolución:

### Confirmed

Existe evidencia determinista suficiente para identificar destino único.

### Inferred

Existe un candidato de alta probabilidad, pero no puede probarse de forma única.

### Unresolved

No existe evidencia suficiente.

No resolver únicamente por coincidencia global del nombre de método.

---

# 12. V2-F — Interfaces e implementaciones

V1 detecta interfaces y `Implements`.

V2 debe construir:

```text
Interface -> ImplementingClass
Class -> ImplementsInterface
```

y utilizar esta información al resolver llamadas.

Ejemplo:

```vb
Dim repo As IRepositorio
repo.Guardar()
```

Si existe una única implementación compatible y evidencia estructural suficiente, puede marcarse según el nivel de confianza correspondiente.

Si existen varias implementaciones posibles:

```text
unresolved / candidate set
```

No elegir arbitrariamente una.

---

# 13. V2-G — Web Forms y eventos

Reconstruir eventos de UI cuando sea determinísticamente posible.

Ejemplos:

```vb
Protected Sub btnProcesar_Click(...) Handles btnProcesar.Click
```

o wiring equivalente detectable.

Generar:

```text
WebForm
    -> Control/Event
    -> Handler
    -> Method
```

Ejemplo:

```text
ucCobConsulta.ascx
    ↓
btnBuscar.Click
    ↓
btnBuscar_Click
```

Desde ahí el grafo de llamadas debe permitir continuar hacia BL/SYS/DAL.

---

# 14. V2-H — Acceso a datos Oracle

Detectar patrones de acceso a Oracle utilizados realmente por el repositorio.

Considerar al menos APIs legacy comunes:

```text
OracleConnection
OracleCommand
OracleDataAdapter
OracleParameter
CommandType.StoredProcedure
CommandText
ExecuteNonQuery
ExecuteReader
ExecuteScalar
Fill
```

y namespaces/proveedores observados como:

```text
Oracle.DataAccess
System.Data.OracleClient
```

No asumir que son los únicos proveedores.

El extractor debe ser extensible.

---

# 15. V2-I — Stored procedures

Detectar asignaciones como:

```vb
cmd.CommandType = CommandType.StoredProcedure
cmd.CommandText = "PKG_PROCESO.PROCEDIMIENTO"
```

y variantes.

Generar:

```text
Method -> StoredProcedure
Class -> StoredProcedure
Project -> StoredProcedure
```

Registrar:

```text
procedure_name
package_name si puede separarse
source_file
containing_class
containing_method
command_variable
confidence
evidence
```

No ejecutar el procedimiento.

---

# 16. V2-J — SQL embebido

Detectar SQL razonablemente identificable:

```text
SELECT
INSERT
UPDATE
DELETE
MERGE
```

incluyendo strings concatenados cuando pueda reconstruirse parcialmente.

No es necesario implementar un parser SQL completo inicialmente.

Registrar:

```text
operation
statement_preview
tables_detected
containing_method
containing_class
project
confidence
evidence
```

No almacenar secretos ni valores sensibles.

Si el SQL se construye dinámicamente y no puede reconstruirse:

```text
dynamic_sql = true
```

y conservar sólo los hechos comprobables.

---

# 17. V2-K — Parámetros Oracle

Cuando pueda relacionarse un comando con sus parámetros, extraer:

```text
parameter_name
direction
oracle_type / db_type
source_expression
```

Ejemplo conceptual:

```json
{
  "procedure": "PKG_COBRANZA.BUSCAR_DEUDA",
  "parameters": [
    {
      "name": "P_RUT",
      "direction": "Input",
      "type": "Varchar2"
    }
  ]
}
```

No evaluar valores reales.

No exponer secretos.

---

# 18. V2-L — Configuración y conexiones

Relacionar acceso a datos con configuración cuando sea posible:

```text
Method/Class
    -> ConnectionName
    -> web.config/app.config
```

Sanitizar siempre:

```text
password
pwd
user id cuando sea sensible
tokens
secret
keys
```

El contexto final puede indicar:

```text
connection_name = "..."
provider = "..."
```

sin publicar credenciales.

---

# 19. V2-M — Servicios externos

Detectar cuando sea posible:

- Web References;
- Service References;
- SOAP;
- URLs configuradas;
- clases proxy;
- llamadas HTTP legacy;
- componentes externos identificables.

Generar relaciones:

```text
Project -> ExternalService
Class -> ExternalService
Method -> ExternalServiceOperation
```

Sólo cuando exista evidencia.

---

# 20. V2-N — Grafo funcional

Crear un nuevo índice:

```text
output/index/functional_dependencies.json
```

Debe complementar, no reemplazar:

```text
dependencies.json
```

Tipos de relación previstos:

```text
Method -> Method
Method -> Class
Method -> StoredProcedure
Method -> SQL
Method -> ExternalService
Method -> InstantiatesClass
Class -> UsesClass
Interface -> ImplementingClass
WebForm -> Event
Event -> Handler
Handler -> Method
Project -> StoredProcedure
Project -> ExternalService
```

Cada relación debe conservar evidencia y confianza.

---

# 21. V2-O — Flujos funcionales

Crear:

```text
output/index/functional_flows.json
```

Un flujo representa una cadena trazable.

Ejemplo:

```text
WebForm
  -> btnBuscar.Click
  -> btnBuscar_Click
  -> blCobMorosidad.BuscarDeuda
  -> sysCobMorosidad.Consultar
  -> PKG_COBRANZA.BUSCAR_DEUDA
```

Modelo conceptual:

```json
{
  "id": "FLOW-0001",
  "entry_point": {
    "type": "web_event",
    "source": "..."
  },
  "steps": [
    {
      "type": "method",
      "target": "...",
      "confidence": "confirmed"
    }
  ],
  "endpoints": [
    {
      "type": "stored_procedure",
      "target": "..."
    }
  ],
  "overall_confidence": "confirmed"
}
```

## Regla crítica

No fabricar un flujo continuo cuando existe una interrupción no resoluble.

Ejemplo:

```text
A -> B -> ? -> Oracle
```

debe conservar el `?`.

No presentar:

```text
A -> B -> Oracle
```

como si estuviera demostrado.

---

# 22. V2-P — Entry points

Identificar puntos de entrada funcionales como:

```text
WebForm event
Page_Load
UserControl event
public service method
scheduled/batch entry point si es detectable
```

Estos entry points son la base para reconstruir flujos.

No todos los métodos públicos son necesariamente entry points.

---

# 23. V2-Q — Detección de capas

LegacyMapper puede observar patrones como nombres de proyectos:

```text
Web*
bl*
sys*
```

pero NO debe convertir el nombre en verdad arquitectónica absoluta.

Crear clasificación separada:

```text
declared_layer
inferred_layer
layer_evidence
layer_confidence
```

Ejemplo:

```text
nombre de proyecto = blCobMorosidad
```

puede ser evidencia para:

```text
inferred_layer = business
```

pero no necesariamente `confirmed`.

Las dependencias reales deben reforzar o contradecir esa inferencia.

---

# 24. Modelo intermedio del sistema

Este es uno de los entregables más importantes de V2.

Crear:

```text
output/ai_context/
```

con al menos:

```text
SYSTEM_CONTEXT.json
SYSTEM_CONTEXT.md
ARCHITECTURE_GRAPH.json
FUNCTIONAL_FLOWS.json
TRACEABILITY.json
```

---

# 25. SYSTEM_CONTEXT.json

Debe proporcionar una representación estructurada y autocontenida del sistema.

Debe incluir como mínimo:

```text
repository
solutions
projects
layers
web_applications
webforms
classes
interfaces
project_dependencies
class_dependencies
method_calls
database_access
stored_procedures
sql_operations
external_services
functional_flows
configuration
unresolved_relations
statistics
```

No copiar simplemente todos los índices existentes.

Debe ser un **modelo integrado**.

Evitar duplicación masiva.

Utilizar identificadores estables/referencias cuando sea conveniente.

---

# 26. SYSTEM_CONTEXT.md

Crear una versión diseñada específicamente para consumo por IA y humanos.

Estructura mínima:

```markdown
# LegacyMapper System Context

## 1. Repository Summary
## 2. Solutions
## 3. Projects
## 4. Detected / Inferred Layers
## 5. Web Applications
## 6. Structural Architecture
## 7. Project Dependencies
## 8. Important Classes
## 9. Interfaces and Implementations
## 10. Functional Entry Points
## 11. Functional Flows
## 12. Database Access
## 13. Stored Procedures
## 14. SQL Operations
## 15. External Services
## 16. Shared Components
## 17. Configuration
## 18. Unresolved Relations
## 19. Confidence Model
## 20. Statistics
```

## Objetivo

Este archivo debe permitir que otra IA reciba:

```text
SYSTEM_CONTEXT.md
```

junto con los JSON especializados cuando necesite detalle, y pueda generar documentación técnica sin releer el repositorio completo.

---

# 27. ARCHITECTURE_GRAPH.json

Crear un grafo normalizado.

Modelo conceptual:

```json
{
  "nodes": [],
  "edges": []
}
```

Nodos posibles:

```text
solution
project
webform
class
interface
method
stored_procedure
database
external_service
```

Edges posibles:

```text
contains
references
inherits
implements
calls
uses
handles
executes
depends_on
```

Cada edge debe tener:

```text
confidence
evidence/reference
```

cuando corresponda.

El formato debe ser suficientemente genérico para generar posteriormente:

- Mermaid;
- PlantUML;
- C4;
- Graphviz;
- diagramas de dependencias;
- diagramas de secuencia.

---

# 28. FUNCTIONAL_FLOWS.json

Debe contener una versión orientada a documentación/diagramación de:

```text
functional_flows.json
```

Puede referenciar IDs del grafo para evitar duplicación.

Debe permitir que otra herramienta produzca diagramas de secuencia como:

```text
Usuario
 -> WebForm
 -> CodeBehind
 -> BL
 -> SYS
 -> Oracle
```

sin volver a analizar código fuente.

---

# 29. TRACEABILITY.json

Debe permitir responder:

> ¿De dónde obtuvo LegacyMapper esta afirmación?

Ejemplo conceptual:

```json
{
  "relation_id": "REL-123",
  "claim": "A calls B",
  "confidence": "confirmed",
  "evidence": [
    {
      "file": "...",
      "line": 100,
      "expression": "..."
    }
  ]
}
```

La trazabilidad es obligatoria para evitar documentación inventada por una IA posterior.

---

# 30. Preparación para documentación por IA

V2 NO necesita generar todavía toda la documentación final del sistema.

Debe producir un contexto que permita prompts como:

```text
Usa SYSTEM_CONTEXT.md y ARCHITECTURE_GRAPH.json como fuente factual.

Genera una descripción de la arquitectura.

No conviertas relaciones inferred o unresolved en hechos confirmados.

Genera un diagrama Mermaid de los proyectos principales.
```

o:

```text
Usa FUNCTIONAL_FLOWS.json.

Documenta el flujo de CobMorosidad desde la interfaz hasta Oracle.

Distingue hechos confirmados de inferencias.
```

El modelo intermedio debe ser independiente del proveedor de IA.

Debe poder utilizarse con:

- Qwen;
- GPT;
- Claude;
- Gemini;
- otros modelos.

---

# 31. Chunking del contexto para IA

El sistema completo puede exceder el contexto práctico de un LLM.

No asumir que `SYSTEM_CONTEXT.md` completo siempre será enviado.

Diseñar adicionalmente una estrategia para contextos por ámbito.

Ejemplos:

```text
output/ai_context/modules/
    ADHContratos/
    CobMorosidad/
    TransmisionMan/
```

Cada módulo puede disponer posteriormente de:

```text
MODULE_CONTEXT.json
MODULE_CONTEXT.md
```

No es obligatorio materializar todos los módulos en la primera iteración V2 si esto aumenta demasiado el alcance.

Pero `SYSTEM_CONTEXT` debe diseñarse de forma que permita generar estos subconjuntos sin reanalizar el repositorio.

---

# 32. Diagramación

No es necesario que V2 produzca diagramas visuales perfectos.

La prioridad es generar datos correctos para diagramarlos.

Sin embargo, implementar exportación Mermaid básica es aceptable si resulta simple.

Ejemplos futuros:

```text
PROJECT_DEPENDENCIES.mmd
MODULE_ARCHITECTURE.mmd
FUNCTIONAL_FLOW_<id>.mmd
```

La fuente de verdad debe seguir siendo JSON/modelos estructurados.

---

# 33. Rendimiento

El repositorio real contiene más de 14.000 archivos.

V2 no debe realizar búsquedas globales ingenuas O(N²) sobre todos los símbolos/llamadas cuando pueda utilizar índices.

Construir índices como:

```text
symbol_by_name
symbol_by_effective_namespace
methods_by_class
methods_by_name
projects_by_path
interfaces_by_name
implementations_by_interface
```

y otros necesarios.

Procesar archivos incrementalmente cuando sea razonable.

No cargar innecesariamente todo el contenido fuente simultáneamente.

---

# 34. Robustez

Un archivo problemático no debe detener el análisis completo.

Mantener:

```text
output/index/errors.json
```

Extender errores con fase/extractor cuando corresponda.

Ejemplo:

```json
{
  "file": "...",
  "extractor": "CallExtractor",
  "error": "..."
}
```

---

# 35. Tests V2

Crear fixtures representativos VB.NET/Web Forms.

La suite debe cubrir como mínimo:

### T01 — instanciación

```vb
Dim servicio As New Servicio()
```

### T02 — llamada por instancia

```vb
servicio.Procesar()
```

### T03 — llamada Shared

```vb
Servicio.Procesar()
```

### T04 — llamada interna

```vb
Procesar()
```

### T05 — interfaz

```vb
Dim repo As IRepositorio
repo.Guardar()
```

### T06 — WebForm event

```vb
Handles btnBuscar.Click
```

### T07 — Oracle StoredProcedure

```vb
CommandType.StoredProcedure
CommandText = "PKG_TEST.PROCESAR"
```

### T08 — Oracle parameters

```vb
OracleParameter(...)
```

### T09 — SQL SELECT

### T10 — SQL INSERT/UPDATE/DELETE

### T11 — llamada entre proyectos

### T12 — llamada ambigua

Debe quedar unresolved/inferred, nunca confirmada arbitrariamente.

### T13 — flujo completo controlado

Fixture:

```text
ASCX
 -> CodeBehind
 -> BL
 -> SYS
 -> StoredProcedure
```

Debe generar un `functional_flow` completo.

### T14 — flujo incompleto

Debe conservar el salto unresolved.

### T15 — sanitización de connection string/secrets.

---

# 36. Estrategia de implementación obligatoria

V2 es grande.

NO intentar implementar todo en una única modificación gigante.

Dividir en iteraciones controladas.

## V2-R1 — Call Graph Foundation

Implementar:

- modelo de evidencia;
- Imports;
- variables/tipos básicos;
- instanciaciones;
- extracción de llamadas;
- resolución inicial de llamadas;
- Class -> UsesClass;
- Method -> Method;
- tests correspondientes.

Resultado:

```text
codex/V2_R1_RESULTADO.md
```

Detenerse para revisión.

---

## V2-R2 — Web Functional Entry Points

Después de aprobación de R1:

- eventos Web Forms;
- handlers;
- entry points;
- integración WebForm -> Event -> Handler -> Method;
- interfaces/implementaciones necesarias para resolución;
- tests.

Resultado:

```text
codex/V2_R2_RESULTADO.md
```

Detenerse para revisión.

---

## V2-R3 — Data Access Mapping

Después de aprobación de R2:

- Oracle;
- commands;
- stored procedures;
- parameters;
- SQL;
- connection/config relationships;
- tests.

Resultado:

```text
codex/V2_R3_RESULTADO.md
```

Detenerse para revisión.

---

## V2-R4 — Functional Flow Resolver

Después de aprobación de R3:

- reconstrucción de cadenas;
- entry point -> llamadas -> persistencia/servicio;
- confidence propagation;
- interrupciones unresolved;
- functional_dependencies.json;
- functional_flows.json;
- tests.

Resultado:

```text
codex/V2_R4_RESULTADO.md
```

Detenerse para revisión.

---

## V2-R5 — System Intermediate Model

Después de aprobación de R4:

Generar:

```text
output/ai_context/SYSTEM_CONTEXT.json
output/ai_context/SYSTEM_CONTEXT.md
output/ai_context/ARCHITECTURE_GRAPH.json
output/ai_context/FUNCTIONAL_FLOWS.json
output/ai_context/TRACEABILITY.json
```

Agregar tests de consistencia/referencias.

Resultado:

```text
codex/V2_R5_RESULTADO.md
```

Detenerse para revisión final V2.

---

# 37. Regla de ejecución de Codex

En esta primera ejecución de este documento:

## Implementar ÚNICAMENTE V2-R1.

NO avanzar automáticamente a V2-R2.

Aunque V2-R1 quede en PASS, detenerse.

Esto permite revisar el call graph contra código legacy real antes de construir las siguientes capas sobre él.

---

# 38. Validación de V2-R1

Después de implementar V2-R1:

1. ejecutar toda la suite V1 + V2;
2. ejecutar LegacyMapper sobre fixtures internos;
3. comprobar compatibilidad V1;
4. generar nuevos índices V2-R1;
5. no ejecutar automáticamente el repositorio legacy completo si no está disponible;
6. proporcionar el comando para que el usuario lo ejecute.

La salida V1 debe continuar disponible.

Agregar el índice inicial que resulte apropiado, por ejemplo:

```text
output/index/calls.json
```

y/o:

```text
output/index/functional_dependencies.json
```

según la arquitectura elegida.

---

# 39. Informe obligatorio V2-R1

Crear:

```text
codex/V2_R1_RESULTADO.md
```

Debe contener:

## Estado

```text
PASS
PARTIAL
FAIL
```

## Archivos modificados

Lista exacta.

## Modelo implementado

Explicar:

- Call;
- Evidence;
- TypeReference;
- resolución;
- confidence.

## Extracción

Cantidad de patrones soportados.

## Resolución

Explicar reglas exactas utilizadas para:

```text
confirmed
inferred
unresolved
```

## Tests

- comando;
- total;
- resultado;
- nuevos tests.

## Compatibilidad V1

Confirmar explícitamente.

## Limitaciones

Muy importante.

Registrar casos VB.NET que todavía no puedan resolverse.

## Riesgos

Registrar falsos positivos/falsos negativos conocidos.

## Ejecución real recomendada

Entregar comando exacto.

## Próximo paso

Finalizar con:

```text
V2-R1 lista para validación sobre repositorio legacy real.
V2-R2 NO iniciada.
```

---

# 40. Archivos Codex

Mantener la convención del proyecto:

```text
codex/
```

para instrucciones e informes `.md` relacionados con trabajo Codex.

No dispersar informes en la raíz.

---

# 41. Criterio de aceptación V2-R1

V2-R1 sólo puede aprobarse si:

- V1 continúa funcionando;
- todos los tests existentes pasan;
- se detectan instanciaciones;
- se detectan llamadas;
- se identifica correctamente el método contenedor;
- existe resolución determinista de una parte de las llamadas;
- las llamadas ambiguas no se marcan como confirmed;
- las relaciones tienen evidencia;
- las relaciones tienen confianza;
- no se introduce dependencia de LLM;
- errores individuales no detienen el análisis;
- la salida puede analizarse estadísticamente.

No se exige 100% de resolución de llamadas.

Es preferible:

```text
60% confirmed
20% inferred
20% unresolved
```

con evidencia correcta,

que:

```text
95% confirmed
```

basado en heurísticas inseguras.

Los porcentajes anteriores son sólo ilustrativos, no objetivos obligatorios.

---

# 42. Validación real después de V2-R1

Después de que Codex entregue V2-R1, el usuario ejecutará LegacyMapper sobre:

```text
E:\IAProyectos\revision\revision-main
```

usando una carpeta de salida nueva, por ejemplo:

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r1_full" --verbose
```

No sobrescribir:

```text
output\v1_r1_full
```

Luego revisar como mínimo:

```text
repository.json
projects.json
symbols.json
logical_symbols.json
webforms.json
dependencies.json
errors.json
calls.json
functional_dependencies.json
```

si estos dos últimos existen según el diseño final.

La revisión debe medir:

```text
total calls
confirmed calls
inferred calls
unresolved calls
instantiations
cross-project calls
classes with outgoing calls
methods with outgoing calls
ambiguities
errors
```

Además se seleccionarán manualmente varios flujos conocidos para contrastarlos contra el código fuente.

---

# 43. Condición para avanzar a V2-R2

NO avanzar únicamente porque los tests unitarios pasen.

V2-R1 debe probarse sobre el repositorio legacy real.

Se autorizará V2-R2 sólo después de comprobar que el call graph:

- encuentra llamadas reales;
- no genera falsos enlaces masivos;
- mantiene ambigüedad cuando corresponde;
- resuelve razonablemente llamadas entre proyectos;
- conserva trazabilidad.

---

# 44. Objetivo final de V2

Al cerrar V2, LegacyMapper debe poder transformar:

```text
Repositorio legacy
```

en:

```text
Modelo estructural
+
Modelo funcional
+
Grafo de arquitectura
+
Flujos funcionales
+
Trazabilidad
+
Contexto portable para IA
```

de modo que un modelo externo pueda recibir el resultado y generar:

- documentación técnica;
- documentación funcional;
- arquitectura;
- diagramas de componentes;
- diagramas de dependencias;
- diagramas de secuencia;
- descripción de módulos;
- análisis de impacto;
- material de onboarding;

sin necesitar releer los más de 14.000 archivos originales.

---

# 45. Principio final de LegacyMapper V2

LegacyMapper no debe intentar parecer inteligente inventando relaciones.

Debe ser útil porque puede demostrar de dónde obtuvo cada relación.

```text
Descubrir
    ↓
Resolver
    ↓
Trazar
    ↓
Modelar
    ↓
Interpretar después
```

La calidad de V2 se medirá principalmente por:

**precisión + trazabilidad + reutilización del modelo resultante.**
