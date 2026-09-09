# LegacyMapper — Correcciones V1-R1 y validación posterior

## 1. Objetivo

Realizar una revisión correctiva y acotada de **LegacyMapper V1**, utilizando como evidencia la primera ejecución real sobre el repositorio legacy completo.

Esta revisión **NO autoriza comenzar V2**.

El objetivo es mejorar la precisión del análisis estructural existente sin incorporar todavía análisis funcional profundo, resolución de llamadas entre clases, trazabilidad Web → BL → DAL → Oracle ni interpretación con Qwen3.

---

## 2. Evidencia de la ejecución real

La primera ejecución de LegacyMapper sobre el repositorio completo procesó:

- 14.580 archivos.
- 4.394 archivos `.vb`.
- 3.165 archivos `.ascx`.
- 177 archivos `.aspx`.
- 4 archivos `.master`.
- 261 proyectos `.vbproj`.
- 113 soluciones `.sln`.
- 61 `web.config`.
- 120 archivos CSS.
- 907 archivos JavaScript.
- 24.699 dependencias estructurales generadas.
- 2 errores de parsing registrados.

También se confirmó que:

- `symbols.json` contiene miles de símbolos VB.NET.
- `webforms.json` contiene miles de Web Forms.
- `dependencies.json` reconstruye relaciones entre soluciones, proyectos, archivos fuente, DLLs, clases, Web Forms, code-behind, namespaces, CSS y JavaScript.
- La arquitectura física del sistema es no trivial: soluciones ubicadas en `proyectos/` referencian proyectos y fuentes ubicados fuera de dicha carpeta.

LegacyMapper V1 ya demuestra capacidad útil sobre el repositorio real. Esta revisión debe ser **quirúrgica**, no un rediseño.

---

# 3. Alcance obligatorio de V1-R1

Implementar únicamente las siguientes correcciones y mejoras.

---

## R1-01 — Normalizar atributos Web Forms sin distinguir mayúsculas/minúsculas

### Problema detectado

Existen directivas ASP.NET con variantes de capitalización como:

```text
CodeBehind
Codebehind
codebehind
CODEBEHIND
```

Actualmente el parser conserva el nombre original del atributo, pero la extracción posterior no siempre lo resuelve correctamente.

Ejemplo observado:

```json
{
  "attributes": {
    "Codebehind": "AdminFormatoImpresion.ascx.vb"
  },
  "codebehind": null
}
```

Mientras que con:

```json
{
  "attributes": {
    "CodeBehind": "Cabecera.ascx.vb"
  },
  "codebehind": "Cabecera.ascx.vb"
}
```

sí funciona.

### Corrección requerida

La resolución de atributos de directivas ASP.NET debe ser **case-insensitive**.

Debe aplicar como mínimo a:

- `CodeBehind`
- `CodeFile`
- `Inherits`
- `MasterPageFile`
- `Src`
- `Namespace`
- `Assembly`
- `TagPrefix`
- `TagName`

No modificar el contenido original del archivo.

Se puede:

- preservar el diccionario original para evidencia;
- utilizar una vista normalizada interna para resolver atributos.

### Requisito

Las diferentes variantes de capitalización deben producir exactamente el mismo resultado estructural.

---

## R1-02 — Ignorar metadatos `_vti_*` no pertenecientes al código real

### Problema detectado

Los únicos errores registrados en la ejecución completa fueron:

```text
bl\blCobMorosidad\_vti_cnf\blCobMorosidad.vbproj
bl\blCobMorosidad\_vti_cnf\Web.config
```

Ambos fallaron al intentar parsearse como XML.

Las carpetas `_vti_*` corresponden normalmente a metadatos legacy y pueden contener archivos con nombres equivalentes a archivos reales, pero cuyo contenido no corresponde al formato esperado.

### Corrección requerida

El scanner debe excluir por defecto carpetas de metadatos `_vti_*`.

Como mínimo considerar:

```text
_vti_cnf
_vti_pvt
_vti_log
_vti_txt
```

Preferiblemente implementar la regla de forma general:

```text
nombre de carpeta empieza por "_vti_"
```

### Requisito

La exclusión debe:

- evitar falsos errores de parsing;
- quedar registrada en el inventario de elementos ignorados;
- no excluir archivos reales fuera de carpetas `_vti_*`.

---

## R1-03 — Reconstruir el namespace efectivo de VB.NET cuando corresponda

### Problema detectado

Una cantidad importante de símbolos aparece con:

```json
"namespace": null
```

Esto no implica necesariamente que la clase compilada carezca de namespace.

En VB.NET el `.vbproj` puede definir:

```xml
<RootNamespace>...</RootNamespace>
```

y dicho namespace se aplica implícitamente a los tipos que no declaran un `Namespace ... End Namespace` explícito.

### Objetivo

Distinguir entre:

1. namespace explícito declarado en el `.vb`;
2. `RootNamespace` del proyecto;
3. namespace efectivo resultante.

### Cambio de modelo recomendado

No destruir el campo existente si ello rompe compatibilidad.

Preferir una extensión como:

```json
{
  "namespace": null,
  "declared_namespace": null,
  "root_namespace": "Sonda.Gestion.X",
  "effective_namespace": "Sonda.Gestion.X"
}
```

Para un archivo con:

```vb
Namespace CobMorosidad
    Public Class Ejemplo
    End Class
End Namespace
```

dentro de un proyecto con:

```text
RootNamespace = Sonda.Gestion.Nssmut.Web
```

el resultado efectivo debe poder representar:

```text
Sonda.Gestion.Nssmut.Web.CobMorosidad
```

### Precaución importante

No asumir que todo `.vb` pertenece al proyecto más cercano por ubicación física.

El sistema legacy tiene archivos y proyectos distribuidos en distintas carpetas.

La asociación `SourceFile -> Project` debe basarse prioritariamente en evidencia del `.vbproj`, referencias de solución/proyecto u otra relación determinista existente.

Si no existe evidencia suficiente para asociar el archivo a un proyecto, no inventar `RootNamespace`.

En ese caso:

```json
"effective_namespace": null
```

o equivalente, junto con evidencia/confianza apropiada.

---

## R1-04 — Consolidar clases parciales sin perder evidencia

### Problema detectado

Existen pares como:

```text
ucEjemplo.ascx.vb
ucEjemplo.ascx.designer.vb
```

que pueden contener:

```vb
Partial Class ucEjemplo
```

LegacyMapper actualmente puede registrarlos como símbolos separados.

Esto es correcto como evidencia física, pero puede generar duplicidad lógica al documentar clases.

### Corrección requerida

Mantener dos niveles:

### A. Símbolo físico

Representa cada declaración encontrada en cada archivo.

Ejemplo:

```text
ucEjemplo.ascx.vb
ucEjemplo.ascx.designer.vb
```

### B. Símbolo lógico consolidado

Representa la clase efectiva:

```text
ucEjemplo
```

con referencias a todas sus partes.

Ejemplo conceptual:

```json
{
  "name": "ucEjemplo",
  "kind": "class",
  "partial": true,
  "parts": [
    "ucEjemplo.ascx.vb",
    "ucEjemplo.ascx.designer.vb"
  ]
}
```

### Requisitos

No eliminar información de los archivos individuales.

No fusionar automáticamente símbolos únicamente porque tengan el mismo nombre.

La consolidación debe usar tanta evidencia como esté disponible, por ejemplo:

- nombre;
- namespace efectivo;
- proyecto;
- `Partial`;
- asociación Web Form / code-behind.

Cuando exista ambigüedad, mantenerlos separados.

---

# 4. Correcciones que NO deben hacerse en V1-R1

No implementar todavía:

- análisis profundo de cuerpos de métodos;
- grafo de llamadas entre métodos;
- `Class A -> Class B` por invocaciones;
- resolución completa de variables/tipos;
- Web → BL → DAL;
- SQL;
- stored procedures;
- parámetros Oracle;
- reglas de negocio;
- análisis funcional;
- inferencia mediante LLM;
- Qwen3;
- LangGraph;
- agentes;
- vector database;
- embeddings;
- generación automática de arquitectura funcional.

Todo lo anterior corresponde a V2 o fases posteriores.

---

# 5. Tests obligatorios

Agregar o actualizar tests automatizados para cubrir las cuatro correcciones.

## Test R1-01 — atributos case-insensitive

Crear fixtures equivalentes con:

```text
CodeBehind
Codebehind
codebehind
```

Los tres deben producir el mismo `codebehind`.

Agregar pruebas equivalentes al menos para:

```text
Inherits
Src
Namespace
Assembly
```

---

## Test R1-02 — `_vti_*`

Crear una estructura de fixture como:

```text
repo/
├── Real.vbproj
└── _vti_cnf/
    └── Real.vbproj
```

El segundo archivo debe quedar ignorado y no producir error de XML.

---

## Test R1-03 — namespace efectivo

Cubrir como mínimo:

### Caso A

`.vbproj`:

```text
RootNamespace = Empresa.Modulo
```

`.vb` sin `Namespace`:

```vb
Public Class Cliente
End Class
```

Resultado esperado:

```text
effective_namespace = Empresa.Modulo
```

### Caso B

`.vbproj`:

```text
RootNamespace = Empresa.Modulo
```

`.vb`:

```vb
Namespace Cobranza
    Public Class Cliente
    End Class
End Namespace
```

Resultado esperado:

```text
effective_namespace = Empresa.Modulo.Cobranza
```

### Caso C

Archivo sin asociación determinista a proyecto.

Resultado:

```text
root_namespace = null
effective_namespace = null
```

No inferir por proximidad física si no hay evidencia suficiente.

---

## Test R1-04 — Partial Class

Fixture:

```text
Cliente.ascx.vb
Cliente.ascx.designer.vb
```

Ambos con:

```vb
Partial Class Cliente
```

El resultado debe conservar ambas declaraciones físicas y producir una representación lógica consolidada cuando exista evidencia suficiente.

---

# 6. Compatibilidad

No romper:

- formato actual de los JSON sin necesidad;
- CLI existente;
- scanner;
- análisis `.sln`;
- análisis `.vbproj`;
- extracción VB.NET existente;
- extracción Web Forms existente;
- `dependencies.json`;
- documentación Markdown existente.

Si es necesario ampliar los JSON, agregar campos compatibles en vez de eliminar información anterior.

---

# 7. Manejo de evidencia y confianza

Mantener el principio de LegacyMapper:

> Python descubre hechos; no inventa arquitectura.

Toda relación nueva debe poder clasificarse como:

```text
confirmed
inferred
unresolved
```

o la estructura equivalente ya existente.

Ejemplos:

```text
.vbproj incluye Archivo.vb
=> confirmed
```

```text
RootNamespace del proyecto + Namespace explícito del archivo
=> confirmed
```

```text
archivo físicamente cercano a un .vbproj pero no incluido en él
=> NO tratar como confirmed
```

---

# 8. Ejecución posterior obligatoria

Después de implementar V1-R1:

## Paso 1 — Ejecutar tests

Ejecutar la suite automatizada completa.

Si el proyecto sigue usando `unittest`:

```powershell
python -m unittest discover -s tests
```

No instalar dependencias externas innecesarias únicamente para cambiar el framework de tests.

Registrar:

```text
tests ejecutados
tests OK
tests fallidos
```

---

## Paso 2 — Ejecutar LegacyMapper sobre sus fixtures/proyecto interno

Confirmar que la ejecución local existente continúa funcionando.

---

## Paso 3 — NO ejecutar automáticamente el repositorio legacy completo si no está disponible dentro del entorno de Codex

La ejecución del repositorio real podrá realizarla el usuario.

Codex debe entregar el comando exacto recomendado, por ejemplo:

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v1_r1_full" --verbose
```

No modificar ni borrar resultados anteriores.

Usar una nueva carpeta de salida.

---

# 9. Archivos de resultados Codex

Todos los documentos `.md` destinados a instrucciones, revisión o resultados de Codex para LegacyMapper deben mantenerse bajo:

```text
codex/
```

Generar al terminar:

```text
codex/V1_R1_RESULTADO.md
```

El informe debe contener:

## Resumen

- estado general;
- PASS / PARTIAL / FAIL.

## Archivos modificados

Lista exacta de archivos.

## R1-01

- implementación;
- tests;
- resultado.

## R1-02

- implementación;
- tests;
- resultado.

## R1-03

- implementación;
- modelo elegido para namespaces;
- método utilizado para asociar archivo a proyecto;
- casos no resolubles.

## R1-04

- implementación;
- método utilizado para consolidar `Partial Class`;
- tratamiento de ambigüedades.

## Tests

- comando ejecutado;
- cantidad total;
- resultado.

## Compatibilidad

Confirmar que no se rompieron las salidas existentes.

## Limitaciones

Registrar limitaciones reales encontradas.

## Próximo paso

Indicar explícitamente:

```text
V1-R1 lista para prueba contra repositorio legacy real.
V2 NO iniciada.
```

---

# 10. Validación manual posterior por el usuario

Después de recibir `codex/V1_R1_RESULTADO.md`, el usuario realizará nuevamente el análisis completo.

Comando esperado:

```powershell
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v1_r1_full" --verbose
```

Luego deben revisarse como mínimo:

```text
output\v1_r1_full\index\repository.json
output\v1_r1_full\index\projects.json
output\v1_r1_full\index\symbols.json
output\v1_r1_full\index\webforms.json
output\v1_r1_full\index\dependencies.json
output\v1_r1_full\index\errors.json
```

Comparar contra la primera ejecución.

---

# 11. Criterios de aceptación V1-R1

V1-R1 puede considerarse aceptada únicamente si:

- la suite automatizada completa pasa;
- las variantes `CodeBehind` / `Codebehind` quedan resueltas correctamente;
- `_vti_*` deja de generar falsos errores;
- los namespaces efectivos se reconstruyen únicamente cuando existe asociación determinista con proyecto;
- los símbolos parciales pueden consolidarse sin perder las declaraciones físicas;
- no aparecen regresiones importantes en scanner, proyectos, soluciones, Web Forms o dependencias;
- el análisis completo del repositorio real termina sin errores nuevos significativos.

Objetivo esperado para `errors.json`:

```json
[]
```

Siempre que no existan otros archivos realmente corruptos.

---

# 12. Decisión posterior a V1-R1

Después de ejecutar V1-R1 sobre el repositorio completo, NO comenzar V2 automáticamente.

Primero revisar:

- cantidad de símbolos;
- símbolos con namespace explícito;
- símbolos con namespace efectivo;
- símbolos sin proyecto resoluble;
- cantidad de Web Forms;
- Web Forms con code-behind;
- Web Forms con `Inherits`;
- clases parciales consolidadas;
- dependencias;
- errores;
- posibles relaciones faltantes.

Con esa evidencia se decidirá si:

```text
A) V1 necesita una V1-R2
```

o:

```text
B) V1 queda cerrada y se autoriza diseño de V2
```

---

# 13. Principio final

LegacyMapper debe continuar priorizando:

```text
hechos deterministas
    ↓
relaciones comprobables
    ↓
contexto estructurado
    ↓
interpretación posterior
```

No sustituir evidencia faltante por suposiciones.

La prioridad de V1-R1 es **mejorar la fidelidad del mapa estructural existente**, no aumentar artificialmente su alcance.
