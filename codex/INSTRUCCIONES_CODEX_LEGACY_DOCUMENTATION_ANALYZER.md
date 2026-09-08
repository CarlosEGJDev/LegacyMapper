# Instrucciones de Implementación — Legacy .NET Documentation Analyzer

## 1. Objetivo

Implementar una herramienta en Python para analizar un repositorio legacy desarrollado completamente sobre:

- .NET Framework 4.0.
- Visual Basic .NET.
- ASP.NET Web Forms.
- Archivos `.aspx`.
- Archivos `.ascx`.
- Archivos `.vb`.
- Archivos `.vbproj`.
- Archivos `.sln`.
- `web.config`.
- JavaScript.
- CSS.
- HTML.

El sistema objetivo puede contener aproximadamente 18.000 archivos.

La herramienta debe minimizar el uso de IA. Toda tarea que pueda resolverse de forma determinista debe realizarse con Python.

La IA, inicialmente Qwen3, debe utilizarse únicamente para interpretar y redactar documentación a partir de información previamente extraída y estructurada.

---

# 2. Principios obligatorios

Codex debe respetar las siguientes reglas durante toda la implementación.

1. No intentar enviar el repositorio completo a un modelo de IA.
2. No utilizar IA para tareas que Python pueda resolver de forma fiable.
3. No implementar una arquitectura innecesariamente compleja.
4. No utilizar LangGraph en esta solución.
5. No utilizar agentes múltiples en la V1.
6. No incorporar una base vectorial en la V1.
7. No depender de servicios cloud.
8. La herramienta debe poder ejecutarse localmente.
9. La primera versión debe priorizar rapidez, estabilidad y trazabilidad.
10. Toda información extraída debe poder rastrearse hasta su archivo fuente.
11. No inventar relaciones cuando no exista evidencia suficiente.
12. Las relaciones inferidas deben distinguirse claramente de las relaciones confirmadas.
13. Los errores de parsing no deben detener el análisis completo del repositorio.
14. Los archivos problemáticos deben registrarse para revisión posterior.
15. La herramienta debe soportar rutas Windows.
16. La herramienta debe poder procesar repositorios grandes sin cargar todos los archivos simultáneamente en memoria.
17. No modificar ningún archivo del proyecto legacy analizado.
18. Todos los resultados deben escribirse fuera del código fuente analizado.
19. No incluir credenciales, passwords ni secretos en la documentación generada.
20. Mantener el código simple, modular, mantenible y testeable.

---

# 3. Estrategia general

La solución se divide en dos versiones.

## V1 — Análisis estructural

Objetivo:

Obtener automáticamente la mayor parte de la documentación estructural del sistema sin analizar profundamente el cuerpo de los métodos.

La V1 debe descubrir:

- estructura física del repositorio;
- soluciones;
- proyectos;
- archivos por proyecto;
- namespaces;
- clases;
- interfaces;
- módulos;
- enums;
- herencia;
- interfaces implementadas;
- métodos públicos;
- funciones públicas;
- propiedades públicas;
- referencias entre proyectos;
- referencias a DLL;
- configuración de proyectos;
- configuración de ASP.NET;
- páginas Web Forms;
- controles ASCX;
- relación ASPX/ASCX con CodeBehind;
- relación ASPX/ASCX con `Inherits`;
- controles registrados mediante `Register`;
- JavaScript utilizado;
- CSS utilizado;
- configuración relevante de `web.config`.

Esta versión debe cubrir aproximadamente el 70–85 % de la necesidad documental.

No intentar resolver todavía el flujo completo:

`Web -> CodeBehind -> BL -> DAL -> Oracle`

salvo cuando una relación pueda establecerse de forma completamente determinista.

---

## V2 — Análisis funcional profundo

La V2 se implementará después de validar la V1.

Objetivo:

Completar las relaciones funcionales que no pueden resolverse solamente desde la estructura.

Debe permitir analizar progresivamente:

- llamadas entre clases;
- instanciaciones;
- tipos utilizados;
- imports;
- llamadas entre proyectos;
- interfaces y sus implementaciones;
- factories;
- posibles patrones de acceso a datos;
- llamadas a DAL;
- comandos SQL;
- stored procedures;
- parámetros Oracle;
- flujo Web -> BL -> DAL;
- dependencias funcionales;
- reglas de negocio;
- módulos funcionales.

Qwen3 podrá utilizar esta información para explicar el comportamiento funcional del sistema.

La V2 no debe implementarse antes de completar y validar la V1.

---

# 4. Arquitectura propuesta

Usar una arquitectura sencilla.

```text
legacy_documenter/
│
├── main.py
├── config.py
│
├── scanner/
│   ├── __init__.py
│   ├── repository_scanner.py
│   └── file_classifier.py
│
├── extractors/
│   ├── __init__.py
│   ├── solution_extractor.py
│   ├── vbproj_extractor.py
│   ├── vbnet_extractor.py
│   ├── webforms_extractor.py
│   └── webconfig_extractor.py
│
├── analysis/
│   ├── __init__.py
│   └── dependency_resolver.py
│
├── context/
│   ├── __init__.py
│   └── context_builder.py
│
├── exporters/
│   ├── __init__.py
│   ├── json_exporter.py
│   └── markdown_exporter.py
│
├── models/
│   ├── __init__.py
│   ├── source_file.py
│   ├── project.py
│   ├── symbol.py
│   ├── webform.py
│   └── dependency.py
│
├── tests/
│   ├── fixtures/
│   └── ...
│
└── output/
```

Codex puede ajustar nombres cuando exista una razón técnica clara, pero no debe incrementar innecesariamente el número de componentes.

---

# 5. Pipeline de V1

El flujo inicial debe ser:

```text
RepositoryScanner
      |
      v
FileClassifier
      |
      v
SolutionExtractor
VBProjExtractor
VBNetExtractor
WebFormsExtractor
WebConfigExtractor
      |
      v
DependencyResolver
      |
      v
JSON indexes
      |
      v
ContextBuilder
      |
      v
MarkdownExporter
```

La integración con Qwen3 debe quedar desacoplada del análisis determinista.

---

# 6. RepositoryScanner

Responsabilidad:

Recorrer recursivamente el repositorio.

Debe registrar como mínimo:

- ruta relativa;
- extensión;
- tamaño;
- carpeta;
- nombre;
- tipo clasificado.

Debe ignorar por defecto carpetas como:

```text
.git
.vs
bin
obj
packages
node_modules
TestResults
```

Debe ser posible configurar exclusiones adicionales.

No leer el contenido de todos los archivos durante la primera pasada.

---

# 7. FileClassifier

Clasificar archivos como mínimo en:

```text
solution
vb_project
vb_source
aspx
ascx
master
web_config
app_config
javascript
css
html
xml
resource
assembly
other
```

Debe producir estadísticas globales.

Ejemplo:

```json
{
  "total_files": 18347,
  "vb_files": 6214,
  "aspx": 412,
  "ascx": 687,
  "javascript": 923,
  "css": 184
}
```

---

# 8. SolutionExtractor

Analizar archivos `.sln`.

Extraer:

- nombre de solución;
- proyectos declarados;
- rutas;
- GUID si corresponde;
- tipo de proyecto cuando sea identificable.

Debe relacionar:

```text
Solution -> Project
```

---

# 9. VBProjExtractor

Analizar `.vbproj` utilizando XML siempre que sea posible.

Extraer como mínimo:

- `ProjectName`;
- `AssemblyName`;
- `RootNamespace`;
- `TargetFrameworkVersion`;
- `OutputType`;
- `ProjectReference`;
- `Reference`;
- `HintPath`;
- `Compile Include`;
- `Content Include`;
- configuraciones relevantes.

Debe generar relaciones:

```text
Project -> ProjectReference
Project -> AssemblyReference
Project -> SourceFile
```

No asumir que todos los `.vbproj` tienen el mismo esquema XML.

---

# 10. VBNetExtractor

Objetivo V1:

Extraer estructura, no interpretar completamente el cuerpo de los métodos.

Extraer:

- Namespace;
- Class;
- Interface;
- Module;
- Structure si existe;
- Enum;
- Inherits;
- Implements;
- métodos públicos;
- funciones públicas;
- propiedades públicas.

Cuando sea razonablemente sencillo, registrar también:

- Friend/Public/Private/Protected;
- Shared;
- MustInherit;
- NotInheritable;
- Partial.

No es obligatorio construir un parser completo de VB.NET en la V1.

Puede utilizarse una combinación controlada de:

- tokenización;
- expresiones regulares;
- análisis por líneas;
- estructuras de estado.

Las regex deben ser defensivas.

Debe manejar:

- comentarios;
- continuaciones con `_`;
- atributos;
- clases Partial;
- namespaces anidados;
- bloques multilinea.

Un error en un archivo no debe detener el procesamiento del resto.

---

# 11. WebFormsExtractor

Analizar:

```text
.aspx
.ascx
.master
```

Extraer las directivas iniciales.

Como mínimo:

- `Language`;
- `CodeBehind`;
- `CodeFile`;
- `Inherits`;
- `MasterPageFile`;
- `Src`;
- `Namespace`;
- `Assembly`.

Procesar directivas:

```asp
<%@ Page ... %>
<%@ Control ... %>
<%@ Register ... %>
```

Detectar controles registrados mediante:

```text
TagPrefix
TagName
Src
Namespace
Assembly
```

Detectar referencias a JavaScript y CSS cuando sea razonablemente posible.

Construir relaciones como:

```text
ASPX -> CodeBehind
ASCX -> CodeBehind
ASPX -> MasterPage
ASPX -> ASCX
ASCX -> ASCX
WebForm -> JavaScript
WebForm -> CSS
```

Cuando `Inherits` pueda relacionarse con una clase VB encontrada, registrar:

```text
WebForm -> VBClass
```

---

# 12. WebConfigExtractor

Analizar `web.config` como XML siempre que sea posible.

Extraer:

- `appSettings`;
- nombres de `connectionStrings`;
- provider;
- authentication;
- authorization;
- compilation;
- assemblies;
- httpHandlers;
- httpModules;
- sessionState;
- customErrors;
- pages;
- controls;
- impersonation cuando exista;
- runtime/assemblyBinding cuando exista.

No almacenar contraseñas.

Connection strings deben sanitizarse.

Ejemplo:

```text
Password=********
Pwd=********
User ID=********
```

Puede conservarse el nombre lógico de la conexión.

---

# 13. DependencyResolver V1

Construir únicamente relaciones basadas en evidencia estructural.

Ejemplos:

```text
Solution -> Project
Project -> Project
Project -> DLL
Project -> SourceFile
Namespace -> Class
Class -> BaseClass
Class -> Interface
ASPX -> CodeBehind
ASCX -> CodeBehind
ASPX -> ASCX
ASCX -> ASCX
WebForm -> JavaScript
WebForm -> CSS
```

Cada dependencia debe incluir:

- origen;
- destino;
- tipo;
- archivo fuente;
- evidencia;
- nivel de confianza.

Para V1 utilizar preferentemente:

```text
confirmed
unresolved
```

Evitar inferencias especulativas.

---

# 14. Índices JSON

La V1 debe producir como mínimo:

```text
output/
├── index/
│   ├── repository.json
│   ├── files.json
│   ├── solutions.json
│   ├── projects.json
│   ├── symbols.json
│   ├── webforms.json
│   ├── configuration.json
│   ├── dependencies.json
│   └── errors.json
```

Estos archivos son la fuente estructurada para etapas posteriores.

---

# 15. ContextBuilder

Debe construir paquetes pequeños de contexto destinados a Qwen3.

No enviar código completo salvo que posteriormente sea necesario.

Ejemplo:

```json
{
  "project": "CobMorosidad",
  "technology": "ASP.NET Web Forms",
  "language": "VB.NET",
  "target_framework": "v4.0",
  "classes": 83,
  "aspx": 6,
  "ascx": 14,
  "namespaces": [
    "Sonda.Gestion.Nssmut.Web.CobMorosidad"
  ],
  "dependencies": [
    "CobMorosidad.Web -> CobMorosidad.BL"
  ]
}
```

Los contextos deben poder generarse por:

- solución;
- proyecto;
- namespace;
- carpeta;
- módulo Web Forms.

---

# 16. MarkdownExporter

Sin utilizar IA debe poder producir documentación básica.

Como mínimo:

```text
output/
└── documentation/
    ├── PROJECT_OVERVIEW.md
    ├── SOLUTION_STRUCTURE.md
    ├── PROJECT_DEPENDENCIES.md
    ├── WEBFORMS_MAP.md
    ├── CONFIGURATION_SUMMARY.md
    └── ANALYSIS_WARNINGS.md
```

Esta documentación será inicialmente factual.

Posteriormente Qwen3 podrá enriquecerla.

---

# 17. Integración con Qwen3

No implementar hasta que el pipeline determinista funcione correctamente.

La integración debe ser desacoplada.

Propuesta posterior:

```text
llm/
├── client.py
├── prompts.py
└── documentation_service.py
```

Qwen3 debe recibir información estructurada.

No debe recibir los 18.000 archivos directamente.

Sus responsabilidades serán principalmente:

- resumir módulos;
- describir arquitectura;
- interpretar responsabilidades;
- redactar documentación funcional;
- detectar posibles patrones;
- transformar evidencia técnica en lenguaje comprensible.

Toda conclusión no confirmada debe marcarse como interpretación.

---

# 18. CLI

La herramienta debe tener una interfaz sencilla.

Ejemplo mínimo:

```powershell
python main.py "C:\ruta\repositorio"
```

Debe permitir especificar directorio de salida:

```powershell
python main.py "C:\ruta\repositorio" --output "C:\resultado"
```

Opciones futuras:

```text
--scan-only
--project
--document
--include
--exclude
--verbose
```

No implementar flags innecesarios antes de necesitarlos.

---

# 19. Logging

Registrar:

- inicio;
- fin;
- duración;
- cantidad de archivos;
- archivos ignorados;
- errores de parsing;
- warnings;
- estadísticas.

No generar logs excesivamente verbosos por defecto.

---

# 20. Manejo de errores

Errores individuales no deben detener el proceso completo.

Ejemplo:

```json
{
  "file": "ruta/al/archivo.vb",
  "extractor": "VBNetExtractor",
  "error": "Unexpected block structure"
}
```

Todos los errores deben almacenarse en:

```text
output/index/errors.json
```

---

# 21. Rendimiento

El sistema debe estar preparado para aproximadamente 18.000 archivos.

Evitar:

- cargar todos los contenidos simultáneamente;
- análisis repetido de un mismo archivo;
- llamadas IA archivo por archivo;
- serializaciones innecesarias.

La V1 debe procesar archivos secuencialmente o mediante concurrencia controlada.

Primero priorizar simplicidad.

No optimizar prematuramente.

---

# 22. Seguridad

No imprimir ni persistir:

- passwords;
- tokens;
- secrets;
- credenciales;
- connection strings completas cuando contengan información sensible.

Sanitizar siempre antes de exportar.

---

# 23. Pruebas

Codex debe crear pruebas automatizadas para cada extractor.

Usar fixtures pequeños representativos del sistema legacy.

Debe existir al menos una prueba para:

### RepositoryScanner

- descubre archivos;
- respeta exclusiones.

### SolutionExtractor

- detecta proyectos de una solución.

### VBProjExtractor

- ProjectReference;
- Reference;
- Compile;
- Content;
- TargetFrameworkVersion.

### VBNetExtractor

- Namespace;
- Class;
- Interface;
- Module;
- Enum;
- Inherits;
- Implements;
- Sub;
- Function;
- Property;
- Partial Class.

### WebFormsExtractor

- Page;
- Control;
- CodeBehind;
- Inherits;
- Register Src;
- Register Namespace/Assembly.

### WebConfigExtractor

- appSettings;
- connectionStrings;
- sanitización;
- assemblies.

### DependencyResolver

- ProjectReference;
- CodeBehind;
- Inherits;
- Register.

---

# 24. Fixtures

No utilizar el repositorio real para todas las pruebas unitarias.

Crear fixtures mínimos como:

```text
tests/fixtures/
├── sample_solution/
├── vb/
├── webforms/
└── config/
```

Cada fixture debe probar un caso concreto.

Posteriormente se realizará una prueba de integración con el repositorio real.

---

# 25. Estrategia de implementación para Codex

Codex no debe implementar toda la V1 de golpe.

Realizar el trabajo incrementalmente.

Orden recomendado:

## Fase A

Crear:

- estructura;
- models;
- RepositoryScanner;
- FileClassifier;
- pruebas.

## Fase B

Crear:

- SolutionExtractor;
- VBProjExtractor;
- pruebas.

## Fase C

Crear:

- VBNetExtractor;
- pruebas.

## Fase D

Crear:

- WebFormsExtractor;
- WebConfigExtractor;
- pruebas.

## Fase E

Crear:

- DependencyResolver;
- índices JSON;
- pruebas.

## Fase F

Crear:

- ContextBuilder;
- MarkdownExporter;
- CLI;
- prueba de integración.

Después de cada fase ejecutar las pruebas existentes.

No continuar si existen regresiones importantes sin documentarlas.

---

# 26. Criterios de aceptación V1

La V1 estará terminada cuando:

1. Puede escanear el repositorio completo sin modificarlo.
2. Puede procesar aproximadamente 18.000 archivos sin detenerse ante errores individuales.
3. Identifica soluciones.
4. Identifica proyectos.
5. Identifica referencias entre proyectos.
6. Identifica DLL referenciadas.
7. Extrae estructura básica de VB.NET.
8. Identifica ASPX y ASCX.
9. Relaciona Web Forms con CodeBehind.
10. Extrae `Inherits`.
11. Extrae controles registrados.
12. Analiza configuración principal.
13. Sanitiza secretos.
14. Produce índices JSON.
15. Produce documentación Markdown básica.
16. Produce reporte de errores.
17. Todas las pruebas unitarias están aprobadas.
18. Existe una prueba de integración sobre una muestra representativa.
19. Puede ejecutarse desde línea de comandos.
20. La V1 no depende de Qwen3 para completar el análisis.

---

# 27. Condición para iniciar V2

No implementar V2 automáticamente.

Al finalizar V1, Codex debe producir:

```text
result_codex/
└── V1_ANALYSIS_REPORT.md
```

El informe debe contener:

- funcionalidades implementadas;
- archivos creados/modificados;
- pruebas realizadas;
- pruebas aprobadas;
- errores pendientes;
- limitaciones;
- cobertura lograda;
- relaciones que V1 todavía no puede detectar;
- propuesta específica para V2.

La V2 solamente debe comenzar después de revisar este informe.

---

# 28. Alcance inicial de V2

Una vez aprobada V1, priorizar:

1. llamadas entre clases;
2. instanciaciones;
3. interfaces -> implementación;
4. dependencias Web -> BL;
5. dependencias BL -> DAL;
6. acceso a Oracle;
7. stored procedures;
8. flujos funcionales completos.

No intentar resolver reflexión dinámica o patrones extremadamente complejos hasta comprobar que realmente son relevantes en el repositorio.

---

# 29. Filosofía de análisis

La herramienta debe separar claramente:

```text
HECHO
```

Información directamente observada en archivos.

```text
RELACIÓN CONFIRMADA
```

Relación demostrable mediante referencia explícita.

```text
INFERENCIA
```

Interpretación razonable, pero no garantizada.

```text
INTERPRETACIÓN IA
```

Explicación realizada por Qwen3.

Nunca mezclar estas categorías.

---

# 30. Regla principal

Python descubre.

Qwen3 interpreta.

La documentación final debe poder demostrar de dónde proviene cada hecho relevante.

La prioridad es construir primero un analizador determinista pequeño, confiable y reusable antes de incorporar inteligencia artificial avanzada.
