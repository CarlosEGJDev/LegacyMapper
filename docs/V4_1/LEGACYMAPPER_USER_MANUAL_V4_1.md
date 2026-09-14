# LegacyMapper V4.1 — Manual de Usuario

> Este manual describe el sistema LegacyMapper **tal como está implementado en V4.1** (formalmente cerrado). No describe funcionalidad planificada para V5. Términos técnicos se explican en el [Glosario V4.1](LEGACYMAPPER_GLOSSARY_V4_1.md).

---

## 1. ¿Qué es LegacyMapper?

LegacyMapper es una herramienta que ayuda a **descubrir, organizar, interpretar, validar y documentar** el conocimiento sobre sistemas legados (aplicaciones antiguas, muchas veces mal documentadas).

El sistema se basa en una separación de responsabilidades muy clara:

- **Python descubre y resuelve hechos determinísticos.** Analiza el código fuente y extrae información objetiva y verificable (archivos, clases, métodos, llamadas, accesos a base de datos, etc.).
- **La IA interpreta cuando hace falta interpretación.** Cuando la información del código no es suficiente, o cuando hay que relacionar código con conocimiento humano, un modelo de IA puede proponer una interpretación.
- **El Technical Lead aprueba.** Ninguna interpretación de la IA se convierte en conocimiento oficial sin que una persona (el Technical Lead) la apruebe.

**Importante:** LegacyMapper nunca le da autoridad a la IA para decidir qué es correcto. La IA propone; el sistema valida estructura; una persona aprueba.

---

## 2. ¿Qué problema resuelve?

LegacyMapper existe para situaciones como estas:

- Aplicaciones legadas con documentación escasa o inexistente.
- Repositorios de código muy grandes, difíciles de recorrer manualmente.
- Dependencias desconocidas entre proyectos, clases o módulos.
- Flujos funcionales difíciles de seguir a simple vista.
- Acceso a base de datos disperso en muchos puntos del código.
- Conocimiento de negocio que existe solo en la cabeza de las personas, no en el código.
- Necesidad de generar documentación estructurada y consistente.
- Necesidad de **preservar la incertidumbre**: cuando algo no se puede determinar con certeza, el sistema lo marca como tal en lugar de inventar una respuesta.

---

## 3. Qué puede hacer LegacyMapper V4.1 actualmente

### 3.1 Análisis de código .NET / VB.NET

LegacyMapper V4.1 sabe analizar repositorios de tecnología **.NET Framework, VB.NET, ASP.NET Web Forms y Oracle**. Sobre ese tipo de repositorio puede descubrir, según el caso:

- Soluciones (`.sln`) y proyectos (`.vbproj`).
- Formularios Web Forms (`.aspx`, `.ascx`, `.master`) y su configuración (`web.config`).
- Clases y métodos del código VB.NET.
- Dependencias entre proyectos y componentes.
- Llamadas entre métodos.
- Accesos a base de datos (con foco en Oracle).
- Flujos funcionales (secuencias de pantallas/métodos que forman un caso de uso).
- Relaciones que no se pudieron resolver de forma automática.
- Un nivel de **evidencia** y **confianza** para cada hallazgo.

### 3.2 Capacidades de conocimiento (V4)

Además del análisis de código, LegacyMapper incorpora un sistema de **gestión de conocimiento**:

- Incorporación de información suministrada por personas (no solo código).
- **Procedencia** (provenance): de dónde salió cada dato.
- Clasificación del conocimiento.
- Estados temporales: **AS_IS** (cómo es hoy), **TO_BE** (cómo debería ser) e **HISTORICAL** (cómo era antes).
- Representación de **vacíos (gaps)** y **conflictos**.
- **Propuestas** de interpretación o resolución.
- **Aprobación** por parte del Technical Lead.
- **Conocimiento canónico**: una única fuente de verdad.
- **Proyección legible por humanos**: documentos Markdown generados a partir del conocimiento canónico.
- **Contrato de proyección legible por máquina** (para un futuro Plugin, todavía no implementado como runtime).

### 3.3 Qué es "capacidad implementada" vs. "CLI expuesta"

Es importante distinguir dos cosas:

1. Lo que el **motor de LegacyMapper** es capaz de hacer internamente (por ejemplo, gestionar conocimiento canónico, generar proyecciones).
2. Lo que está **expuesto como comando ejecutable** por un usuario final.

En V4.1, el comando de línea de comandos disponible y soportado para un usuario que quiere analizar un repositorio legado es el análisis de código (sección 7). Otras capacidades del sistema de conocimiento (aprobación, proyección, etc.) se ejercitan hoy principalmente a través de módulos internos y pruebas automatizadas, no a través de un CLI unificado de conocimiento para el usuario final. No existe todavía un "CLI de conocimiento V4" único que integre ingestión, aprobación y proyección en un solo comando de usuario.

---

## 4. Qué NO hace LegacyMapper actualmente

Para evitar expectativas incorrectas, es importante ser explícito:

- **El runtime de Plugin no está implementado.** Existe un contrato de proyección (`LegacyMapperPluginKnowledge`, versión 1.0) pensado para que un futuro Plugin consuma el conocimiento, pero **no hay ningún Plugin ejecutándose hoy**.
- **V5 no está implementado.** Todo lo relacionado con agnosticismo de lenguaje, framework, base de datos o proveedor de IA es una meta futura, no una capacidad actual.
- **LegacyMapper todavía no es agnóstico de lenguaje/framework/base de datos.** Hoy está enfocado en .NET Framework, VB.NET, ASP.NET Web Forms y Oracle.
- **La IA no puede aprobar conocimiento.** Solo el Technical Lead tiene esa autoridad.
- **LegacyMapper no modifica el código fuente legado que analiza.** El acceso al repositorio analizado es de solo lectura.
- **LegacyMapper no desarrolla el proyecto destino de forma autónoma.** No escribe código nuevo para el sistema legado ni para el sistema de reemplazo.
- **No existe un CLI único de conocimiento V4** que unifique ingestión, clasificación, propuestas, aprobación y proyección en un solo comando para el usuario final (ver sección 3.3).

---

## 5. Modos de información soportados

LegacyMapper puede trabajar con distintos niveles de información disponible:

### CODE_ONLY (solo código)

- **Información disponible:** únicamente el código fuente del sistema legado.
- **Qué puede hacer:** extraer hechos determinísticos (clases, métodos, llamadas, accesos a datos) y construir evidencia a partir del código.
- **Limitaciones esperadas:** no puede explicar el "por qué" de una decisión de negocio; las relaciones que dependan de contexto humano quedarán como no resueltas.
- **Ejemplo:** se analiza un módulo VB.NET sin ninguna documentación adicional; el sistema identifica sus métodos y llamadas, pero no puede decir si una regla de validación responde a un requerimiento legal.

### CODE_AND_HUMAN_INFORMATION (código + información humana)

- **Información disponible:** código fuente más documentos o explicaciones aportadas por personas.
- **Qué puede hacer:** combinar hechos determinísticos del código con conocimiento humano, generar interpretaciones con mayor contexto y detectar gaps o conflictos entre lo que dice el código y lo que dice la persona.
- **Limitaciones esperadas:** la calidad depende de la calidad de la información humana aportada.
- **Ejemplo:** además del código, un analista aporta un documento que explica el proceso de negocio; LegacyMapper puede relacionar el flujo de código con ese proceso.

### HUMAN_INFORMATION_ONLY (solo información humana)

- **Información disponible:** no hay acceso al código, solo documentos o relatos humanos.
- **Qué puede hacer:** incorporar ese conocimiento como material de entrada, con su propia procedencia, y usarlo en el sistema de conocimiento.
- **Limitaciones esperadas:** no hay hechos determinísticos de código con los que contrastar; todo depende de la fiabilidad de la fuente humana.
- **Ejemplo:** se documenta un sistema que ya no existe, a partir de entrevistas con quienes lo operaban.

### PARTIAL_INFORMATION (información parcial)

- **Información disponible:** una combinación incompleta de código y/o información humana (por ejemplo, solo una parte del repositorio, o documentación parcial).
- **Qué puede hacer:** analizar lo disponible y marcar explícitamente qué queda sin resolver.
- **Limitaciones esperadas:** habrá relaciones y flujos incompletos; el sistema los deja como `UNRESOLVED` en lugar de completarlos con suposiciones.
- **Ejemplo:** se analiza solo un subconjunto de proyectos de una solución grande; las dependencias hacia proyectos no incluidos quedan marcadas como no resueltas.

---

## 6. Flujo conceptual principal

```
MATERIAL DE ENTRADA
        │
        ▼
INGESTIÓN / NORMALIZACIÓN
        │
        ▼
EVIDENCIA / CONTEXTO
        │
        ▼
ANÁLISIS / CLASIFICACIÓN / RELACIÓN
        │
        ▼
PROPUESTAS
        │
        ▼
APROBACIÓN DEL TECHNICAL LEAD
        │
        ▼
FUENTE DE CONOCIMIENTO CANÓNICO
        │
   ┌────┴─────┐
   ▼          ▼
Documentos   Proyección
humanos      para máquina
```

En palabras simples:

1. Se recibe **material de entrada** (código, documentos, explicaciones humanas).
2. Ese material se **ingiere y normaliza** en un formato interno consistente.
3. A partir del material se genera **evidencia** con contexto.
4. Sobre la evidencia se hace **análisis, clasificación y detección de relaciones** (incluyendo gaps y conflictos).
5. Cuando hace falta interpretar, se generan **propuestas** (humanas, por regla determinística, o por IA).
6. Toda propuesta pasa por **aprobación del Technical Lead**.
7. Lo aprobado se convierte en **conocimiento canónico**, la única fuente de verdad.
8. Desde el conocimiento canónico se generan **documentos legibles por humanos** y una **proyección legible por máquina** para un futuro Plugin.

---

## 7. Flujo de análisis de código fuente

Para analizar un repositorio legado, el comando soportado es:

```
python main.py <repositorio> [--output <salida>] [--exclude <carpeta>] [--verbose] [--flow-max-depth <N>]
```

Parámetros:

- `<repositorio>` (obligatorio): ruta a la carpeta raíz del sistema legado a analizar.
- `--output <salida>` (opcional, por defecto `output`): carpeta donde se generan los resultados.
- `--exclude <carpeta>` (opcional, puede repetirse): carpetas a excluir del análisis.
- `--verbose` (opcional): muestra más detalle durante la ejecución.
- `--flow-max-depth <N>` (opcional, por defecto `12`): profundidad máxima al resolver flujos funcionales.

### Ejemplo en Windows

```
python main.py "C:\Legacy\Sistema" --output "C:\LegacyMapperResults" --verbose
```

Esto analiza el sistema ubicado en `C:\Legacy\Sistema` y escribe los resultados en `C:\LegacyMapperResults`.

> El acceso al repositorio analizado es siempre de **solo lectura**. LegacyMapper nunca modifica el código del sistema legado.

---

## 8. Cómo entender los resultados generados

Al analizar un repositorio, LegacyMapper distingue varios tipos de información:

- **Hechos determinísticos:** datos extraídos directamente del código, sin interpretación (por ejemplo, "el método X llama al método Y").
- **Información inferida:** conclusiones que requirieron algún tipo de interpretación.
- **Información no resuelta:** casos donde no se pudo determinar la respuesta con la evidencia disponible.
- **Confianza:** qué tan seguro está el sistema de un hallazgo.
- **Evidencia:** en qué parte del código o documento se basa un hallazgo.
- **Procedencia (provenance):** el origen y el camino que siguió un dato hasta convertirse en conocimiento.
- **Propuestas:** interpretaciones sugeridas, pendientes de aprobación.
- **Conocimiento aprobado:** lo que el Technical Lead ya validó.
- **Documentos generados:** la proyección legible en Markdown del conocimiento canónico.

**Que algo quede "no resuelto" no es un fracaso.** LegacyMapper prefiere marcar explícitamente lo que no puede determinar con certeza, en lugar de adivinar. Esto es una decisión de diseño: es mejor saber que algo es incierto que tener una respuesta incorrecta presentada como si fuera un hecho.

---

## 9. Aprobación humana

- El **Technical Lead** es la autoridad final de aprobación.
- La **IA** puede proponer una interpretación, pero no puede aprobarla.
- El **sistema** puede validar que una propuesta tenga una estructura correcta (por ejemplo, que tenga la evidencia mínima requerida), pero eso no es lo mismo que aprobarla como conocimiento válido.
- Solo una persona con autoridad de Technical Lead puede:
  - **Aprobar** una propuesta (se incorpora al conocimiento canónico).
  - **Rechazar** una propuesta (no se incorpora).
  - **Corregir** una propuesta (se solicita una versión ajustada antes de aprobar).

---

## 10. Fuente de Conocimiento Canónico

LegacyMapper mantiene **una única fuente de conocimiento canónico**. Esto evita que existan varias "verdades" distintas y contradictorias sobre el mismo sistema.

```
   Conocimiento Canónico
           │
   ┌───────┴───────┐
   ▼               ▼
Documentos      Proyección
humanos         para máquina
(Markdown)      (Plugin)
```

Los documentos Markdown que LegacyMapper genera son **vistas** del conocimiento canónico, no fuentes de verdad independientes. Si un documento Markdown y el conocimiento canónico llegaran a no coincidir, el conocimiento canónico es lo autoritativo.

---

## 11. Documentación generada

LegacyMapper puede generar una **proyección legible por humanos** del conocimiento canónico (conocida internamente como "R11"). Esta proyección organiza el contenido en una familia cerrada de documentos, agrupados en carpetas numeradas (por ejemplo `00-el-area/`, `01-...` hasta `09-capacitacion/`), cada una dedicada a un tema específico del sistema documentado.

Cada dato dentro de esos documentos puede rastrearse hasta su origen mediante un identificador de conocimiento (`knowledge_id`), lo que permite saber exactamente de qué pieza de conocimiento canónico proviene cada afirmación.

Cuando un dato de conocimiento no encaja en ninguna regla de proyección definida, se marca como **`UNMAPPED`** en lugar de forzarlo dentro de un documento donde no corresponde.

---

## 12. AS_IS, TO_BE e HISTORICAL

LegacyMapper distingue tres estados temporales del conocimiento:

- **AS_IS:** cómo funciona el sistema hoy.
- **TO_BE:** cómo debería funcionar según un requerimiento u objetivo.
- **HISTORICAL:** cómo funcionaba antes (ya no vigente).

> **Importante:** que `AS_IS` sea distinto de `TO_BE` **no significa automáticamente que haya una contradicción**. Puede representar simplemente un **GAP** (una diferencia pendiente de resolver), no un error.

---

## 13. GAP vs. CONFLICTO

> Los siguientes son **ejemplos ilustrativos**, no datos reales de ningún proyecto.

**Ejemplo de GAP** (diferencia entre estado actual y estado deseado, sin contradicción entre fuentes):

- AS_IS: La aplicación autentica usuarios de forma local.
- TO_BE: La aplicación debe usar el SSO corporativo.

Esto no es un conflicto: ambas afirmaciones pueden ser ciertas al mismo tiempo (una describe el presente, la otra el objetivo).

**Ejemplo de CONFLICTO** (dos fuentes afirman cosas incompatibles sobre el mismo momento):

- Fuente A: La base de datos X es la autoritativa.
- Fuente B: La base de datos Y es la autoritativa.

Aquí sí hay una contradicción real que debe resolverse (por ejemplo, mediante una propuesta de reconciliación aprobada por el Technical Lead).

---

## 14. Seguridad

- El código fuente del sistema legado se accede en **modo solo lectura**; LegacyMapper nunca lo modifica.
- La **incertidumbre se preserva**: si algo no se puede determinar, se marca como tal en vez de completarlo con una suposición.
- **No hay aprobación oculta**: toda incorporación al conocimiento canónico pasa por una decisión explícita del Technical Lead.
- La **procedencia se conserva** siempre, para poder rastrear el origen de cualquier dato.
- **No se deben colocar secretos** (contraseñas, claves, cadenas de conexión reales, etc.) en la documentación generada ni en el material de entrada.
- Los artefactos generados deben seguir la política del repositorio (ver `docs/GENERATED_ARTIFACT_POLICY.md`).

---

## 15. Problemas comunes

| Problema | Qué significa | Qué hacer |
|---|---|---|
| `READINESS` distinto de `READY` | El sistema detectó que no están dadas las condiciones para considerar el ciclo listo (por ejemplo, falta algún artefacto esperado). | Revisar el detalle de `checks` que reporta el comando de readiness y corregir lo que falte antes de continuar. |
| Repositorio faltante | La ruta pasada como `<repositorio>` no existe o no es accesible. | Verificar que la ruta sea correcta y que se tenga permiso de lectura. |
| Ruta de salida inválida | La ruta pasada en `--output` no se puede crear o escribir. | Verificar permisos y que la ruta sea válida en el sistema operativo. |
| Análisis parcial | El análisis se completó, pero con partes del repositorio sin poder procesarse (por ejemplo, por exclusiones o archivos no soportados). | Revisar qué quedó fuera y, si corresponde, ajustar `--exclude` o el alcance del análisis. |
| Relaciones no resueltas | El sistema no pudo determinar con certeza una relación entre elementos. | Esto es esperado en información parcial; revisar la evidencia disponible o aportar más contexto humano. |
| Evidencia faltante | Una afirmación no cuenta con evidencia suficiente. | No forzar su aprobación; aportar más material o marcarla como no resuelta. |
| Propuesta pendiente de aprobación | Existe una propuesta de interpretación que todavía no fue revisada por el Technical Lead. | El Technical Lead debe aprobar, rechazar o corregir la propuesta. |
| Entrada canónica `UNMAPPED` | Un dato de conocimiento canónico no encaja en ninguna regla de proyección de documentos. | Es un estado válido, no un error; puede requerir revisar las reglas de proyección si se espera que ese dato sí aparezca en algún documento. |
| Pruebas fallando | La suite de pruebas automatizadas no pasa en su totalidad. | No se debe considerar el sistema estable hasta que las pruebas vuelvan a pasar en su totalidad; esto es responsabilidad de mantenimiento, no de un usuario final. |
| Repositorio de LegacyMapper "sucio" durante mantenimiento controlado | Hay cambios sin confirmar (commitear) mientras se realiza una tarea de mantenimiento sobre el propio LegacyMapper. | Revisar y confirmar o descartar los cambios pendientes antes de continuar con tareas de mantenimiento. |

> No se documentan códigos de error específicos porque el sistema actual no expone una tabla formal de códigos de error para el usuario final.

---

## 16. Ejemplo práctico de uso

> **EJEMPLO ILUSTRATIVO — NO REPRESENTA DATOS REALES.**

1. **Repositorio legado:** un analista tiene acceso a un sistema ASP.NET Web Forms con VB.NET y base de datos Oracle, con documentación escasa.
2. **Análisis:** ejecuta `python main.py "C:\Legacy\SistemaFacturacion" --output "C:\LegacyMapperResults\Facturacion" --verbose`.
3. **Evidencia:** LegacyMapper identifica un formulario `FacturaDetalle.aspx` que llama a un método `GuardarFactura`, el cual accede a una tabla Oracle `FACTURAS`.
4. **Interpretación:** no queda claro en el código por qué existe una validación de "monto máximo"; un analista aporta un documento de negocio que explica que responde a una política interna de control de fraude.
5. **Propuesta:** el sistema (o una persona) genera una propuesta de interpretación relacionando esa validación con la política de negocio.
6. **Aprobación:** el Technical Lead revisa la propuesta, la encuentra correcta y la **aprueba**.
7. **Conocimiento canónico:** la interpretación aprobada se incorpora como una entrada de conocimiento canónico, con su `knowledge_id` correspondiente.
8. **Documentación legible por humanos:** esa entrada aparece proyectada en el documento correspondiente dentro de la familia de documentos generados, trazable mediante su `knowledge_id`.

---

## 17. Estado de versión actual

- **V4** = FORMALMENTE CERRADO.
- **V4.1** = FORMALMENTE CERRADO.
- **Pruebas automatizadas (baseline actual):** `1566 PASS, 0 FAIL, 0 SKIP`.
- **READINESS:** `READY`.
- **Runtime de Plugin:** `NOT_IMPLEMENTED` (no implementado).
- **V5:** `false` (no implementado).

---

Para definiciones de términos usados en este manual, ver el [Glosario V4.1](LEGACYMAPPER_GLOSSARY_V4_1.md).
Para detalles técnicos de implementación, ver el [Manual Técnico V4.1](LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md).
