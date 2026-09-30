# LegacyMapper — Lecciones aprendidas para proyectos futuros

## 1. Propósito

Este documento resume aprendizajes técnicos y de proceso obtenidos durante el desarrollo de LegacyMapper.

No es solo un registro histórico.

Debe utilizarse como checklist para evitar repetir errores en:

- LegacyMapper V5/V6;
- Software Factory;
- herramientas de análisis;
- sistemas gobernados por IA;
- proyectos grandes con Claude Code u otros agentes.

---

# 2. Principio principal

La regla que más valor produjo fue:

> **Python descubre y valida; la IA interpreta.**

Todo aquello que pueda decidirse de forma reproducible debe permanecer determinista.

Ejemplos:

```text
buscar archivos
calcular hashes
resolver paths
ordenar
filtrar
presupuestar
validar schemas
ejecutar tests
crear manifests
medir tamaños
```

La IA debe concentrarse en:

```text
interpretar
explicar
diseñar
proponer
clasificar significado cuando no es determinista
```

Esto reduce:

- tokens;
- alucinaciones;
- variabilidad;
- tiempo;
- dependencia del modelo.

---

# 3. Medir antes de diseñar

Uno de los principales problemas de V4.3 fue diseñar bajo supuestos que parecían razonables pero no reflejaban completamente los datos reales.

Ejemplo:

Se asumió inicialmente que todos los flows ricos eran demasiado grandes.

La medición real mostró:

```text
35/40 >= 16000 caracteres
5/40  < 16000 caracteres
```

Esos cinco sí cabían individualmente, pero quedaban fuera por orden y first-fit greedy.

Lección:

> Toda afirmación cuantitativa usada para justificar arquitectura debe estar respaldada por una medición reproducible.

No usar:

```text
"todos son grandes"
```

Usar:

```text
n = 40
35 >= límite
5 < límite
min = ...
max = ...
```

---

# 4. Baseline real antes de implementar

Fixtures sintéticos son útiles, pero no suficientes.

Antes de diseñar una feature dependiente de escala:

1. ejecutar el sistema actual;
2. medir comportamiento real;
3. capturar distribución de datos;
4. identificar outliers;
5. diseñar con esos resultados.

IST debe seguir siendo baseline real para LegacyMapper.

---

# 5. No implementar antes de comprender la causa raíz

En V4.3 fue necesario distinguir entre:

```text
selector
packing
budget interno
budget final
provider
prompt
modelo
```

Un resultado de mala calidad podía parecer problema del LLM y ser realmente un problema determinista anterior.

Lección:

```text
observar síntoma
→ localizar etapa exacta
→ reproducir
→ medir
→ corregir
```

No modificar varias etapas simultáneamente.

---

# 6. Una responsabilidad por ronda

Las rondas que mejor funcionaron fueron las que tenían una sola misión.

Ejemplos:

```text
diagnosticar
```

o:

```text
corregir packing
```

o:

```text
cerrar versión
```

No combinar:

```text
diagnóstico
+ refactor
+ nueva feature
+ cambios de provider
+ cierre
```

Una ronda pequeña produce:

- revisión más fácil;
- menos riesgo;
- menos tokens;
- rollback claro.

---

# 7. Diseñar contrato antes de código

Especialmente importante para:

- normalized evidence;
- templates;
- segmentation;
- canonical knowledge;
- adapters;
- plugin contracts.

Antes del código definir:

```text
inputs
outputs
schema
invariantes
errores
compatibilidad
traceability
casos límite
```

Una ronda de arquitectura debe responder:

```text
¿Qué preservamos?
¿Qué cambia?
¿Qué rompemos?
¿Cómo se prueba?
¿Cómo se revierte?
¿Qué datos reales justifican el cambio?
```

---

# 8. Determinismo como contrato

El determinismo no es una optimización.

Es una característica funcional.

Para una misma entrada y versión:

```text
mismo input
→ mismo output
→ mismo orden
→ mismos IDs
```

Cuando un cambio exige romper determinismo, debe documentarse expresamente.

---

# 9. No mezclar evidence con presentation

Un hallazgo importante de V4.3:

```text
technical_noise
```

puede ocultarse o separarse en documentación, pero no eliminarse de la evidencia si sigue siendo útil para trazabilidad.

Separar:

```text
evidence
```

de:

```text
presentation
```

Permite cambiar documentación sin alterar conocimiento.

---

# 10. No mezclar deterministic confidence con UX

`confidence`, `terminal_type`, `evidence_refs` y otros campos forman parte del significado técnico.

La presentación puede mostrar esos conceptos de forma más humana, pero no cambiar su semántica.

---

# 11. Preserve unresolved

Un unresolved no es un fracaso que deba ocultarse.

Representa el límite de la evidencia.

Regla:

```text
si no sabemos
→ unresolved
```

No:

```text
si no sabemos
→ inferir algo plausible
```

Esto es especialmente importante en sistemas legacy.

---

# 12. IA nunca debe canonicalizar sola

Arquitectura permanente:

```text
Evidence
    ↓
AI Proposal
    ↓
Human Review
    ↓
Canonical Knowledge
```

No:

```text
AI Proposal
    ↓
Canonical Knowledge automáticamente
```

---

# 13. Tests + piloto real

La secuencia correcta es:

```text
unit tests
→ integration tests
→ synthetic fixtures
→ real repository
```

Una suite verde no demuestra por sí sola que una feature funcione bien a escala.

El piloto real de IST fue esencial para descubrir:

- documentos gigantes;
- problemas de partitioning;
- selection bias;
- packing bias;
- errores de provider;
- comportamiento real de Luna.

---

# 14. No reanalizar innecesariamente

El análisis completo de IST es costoso.

Esto demostró que:

- cache;
- incremental analysis;
- scope analysis;
- persisted indexes

deben diseñarse desde temprano.

No dejar rendimiento para el final cuando el dominio es grande.

---

# 15. Analizar una vez, proyectar muchas veces

Un mismo conocimiento debería alimentar:

```text
human docs
AI context
client docs
architect docs
migration docs
graphs
plugins
queries
```

Sin volver a escanear el repositorio.

Esto motiva:

```text
repository
→ normalized knowledge index
→ projections
```

---

# 16. Templates no deben modificar verdad

Los templates pueden controlar:

- orden;
- títulos;
- audiencia;
- idioma;
- campos visibles;
- formato.

No pueden cambiar:

- confidence;
- relations;
- terminals;
- evidence refs;
- confirmed/unresolved.

---

# 17. Runtime debe ser independiente del proceso de desarrollo

No mezclar runtime con:

```text
docs
prompts
tests
PROJECT_STATE
governance
resultados
```

Una distribución limpia permite:

- probar lo que realmente recibe el usuario;
- detectar dependencias accidentales;
- reducir superficie del producto.

---

# 18. Mantener outputs grandes fuera de Git

Versionar:

- source;
- tests;
- contracts;
- prompts;
- docs;
- baselines pequeños;
- handovers.

No versionar automáticamente:

- outputs de 1+ GB;
- caches;
- logs;
- dumps completos;
- artifacts temporales.

---

# 19. Cuidado con line endings en Windows

Git + Windows + hashes de bytes crudos puede producir diferencias inesperadas.

Antes de concluir que un baseline está roto:

```bat
git status
git config --get core.autocrlf
git ls-files --eol <archivo>
```

Distinguir:

```text
contenido lógico
```

de:

```text
representación CRLF/LF del worktree
```

No actualizar hashes cerrados solo para ocultar un problema ambiental.

---

# 20. Rebaseline después de cambiar de máquina

Al cambiar de PC:

1. revisar Git;
2. revisar Python;
3. revisar dependencias;
4. ejecutar suite completa;
5. regenerar outputs externos necesarios;
6. comparar métricas estructurales;
7. no asumir que outputs antiguos siguen disponibles.

El rebaseline de V4.3 evitó diseñar sobre artefactos perdidos.

---

# 21. Distinguir repo de desarrollo y distribución

Mantener:

```text
C:\dev\LegacyMapper
```

separado de algo como:

```text
C:\Tools\LegacyMapper
```

y de:

```text
C:\LegacyMapperResults
```

Esto reduce errores y hace más claro qué pertenece a producto, desarrollo o resultados.

---

# 22. No tocar varias capas para resolver un solo síntoma

Ejemplo de capas:

```text
selection
hydration
packing
budget
provider
prompt
adapter
renderer
```

Si el problema está en packing, no cambiar:

```text
prompt
provider
confidence
budget
```

sin evidencia.

---

# 23. Conservar backward compatibility deliberadamente

Cuando una versión anterior está cerrada:

- caracterizar outputs;
- congelar contratos;
- agregar cambios aditivos cuando sea posible;
- justificar cualquier breaking change.

Nunca romper compatibilidad accidentalmente durante un refactor.

---

# 24. Deuda técnica debe clasificarse

Toda deuda descubierta debe quedar como:

```text
BLOCKING
CURRENT_PHASE
NEXT_PHASE
POST_VERSION
OBSERVATION
```

No intentar arreglar cada deuda inmediatamente.

Eso evita scope creep.

---

# 25. Evitar rondas infinitas

Patrón recomendado:

```text
R0 baseline
R1 contract
R2 implementation
R3 verification
R4 closure
```

Si aparecen muchas revisiones:

```text
R5
R6
R7
...
```

detenerse.

Probablemente exista:

- causa raíz incorrecta;
- scope incorrecto;
- contrato incompleto;
- modelo no adecuado.

---

# 26. Regla de modelo

Experiencia del proyecto:

Sonnet 5 medium fue suficiente para V3/V4.

No usar automáticamente el modelo más caro.

Regla:

```text
Sonnet medium por defecto
Opus para arquitectura crítica
```

Si después de aproximadamente tres intentos el modelo sigue fallando:

```text
cambiar de modelo
```

antes de seguir consumiendo tokens.

---

# 27. Prompts autocontenidos

Un buen prompt para Claude debe incluir:

- objetivo;
- rutas;
- estado actual;
- archivos relevantes;
- restricciones;
- tests;
- output esperado;
- estados finales permitidos;
- qué NO hacer.

No depender de que Claude recuerde una conversación anterior.

---

# 28. Prompts con rutas exactas

Preferir:

```text
docs/V5/...
prompts/V5/...
legacy_documenter/context/...
```

No:

```text
"modifica el archivo correspondiente"
```

Esto reduce exploración innecesaria y tokens.

---

# 29. Handover documental

Cada fase importante debe producir un resultado que permita retomar trabajo posteriormente.

Un handover útil debe incluir:

```text
estado
decisiones
archivos modificados
tests
deudas
next step
```

---

# 30. No confiar ciegamente en outputs de IA

Una IA puede:

- resumir demasiado;
- elegir findings triviales;
- generalizar;
- interpretar mal confidence.

Siempre conservar:

```text
evidence_refs
```

para auditar cada afirmación.

---

# 31. Calidad de contexto antes que cantidad

Más contexto no siempre produce mejor IA.

El objetivo es:

```text
evidencia relevante
+ diversidad
+ trazabilidad
```

no:

```text
payload gigantesco
```

---

# 32. Outliers necesitan estrategia propia

Un flow de 100K caracteres no debe tratarse igual que uno de 2K.

Diseñar explícitamente:

- segmentation;
- summary;
- partial contract;
- lazy details.

No esperar que un único budget resuelva todas las escalas.

---

# 33. Validar dependencias opcionales de verdad

Copilot debe ser opcional no solo conceptualmente.

Debe poder:

```text
importar runtime
ejecutar deterministic full
correr tests
```

sin instalar SDK real.

---

# 34. Seguridad

Nunca persistir:

- tokens;
- API keys;
- bearer tokens;
- credenciales.

Los documentos de resultados pueden registrar:

```text
provider
model
status
```

pero no secretos.

---

# 35. Checklist para futuros proyectos

Antes de implementar una feature grande:

- [ ] ¿Tenemos baseline real?
- [ ] ¿Tenemos mediciones?
- [ ] ¿Está claro el contrato?
- [ ] ¿Está claro qué NO cambia?
- [ ] ¿Hay tests de regresión?
- [ ] ¿Existe un caso real?
- [ ] ¿Sabemos cómo validar a escala?
- [ ] ¿El runtime queda independiente?
- [ ] ¿La IA es realmente necesaria?
- [ ] ¿Puede hacerlo Python?
- [ ] ¿Hay rollback claro?
- [ ] ¿La deuda nueva está clasificada?


---

# 36. Lecciones añadidas tras V5.1 y V5.2 (29-09-2026)

Estas lecciones se añaden a las anteriores sin alterar los hechos históricos de V4.3. V5.1 está cerrada; V5.2 R3.4.1 está lista para **revisión y aprobación humana**, pero V5.2 no tiene cierre formal R4 todavía.

## 36.1 Identidad no es semejanza de nombres

Un `.sln` es Solution; un `.vbproj`/`.csproj` es Project; una clase/formulario es Component; un archivo es SourceArtifact. `BLInterfazSAP.vbproj` es un proyecto real y `BLInterfazSAP.vb` su archivo homónimo, no otro proyecto. Nunca inferir entidad ni ownership a partir de `BL`/`Web`/`sys`, una carpeta o el mero uso durante un flujo. Un recurso como `img\aceptar.gif` puede ser declarado por varios proyectos: informar pertenencia compartida/ambigua, no seleccionar un dueño arbitrario.

## 36.2 Documentación humana = salida completa; muestra humana = instrumento de QA

`documentation_v52/` contiene las proyecciones completas General Overview y Developer Technical. Los ZIP `human_review_sample` son subconjuntos para revisión. La muestra debe contener los destinos necesarios para recorridos elegidos e identificar enlaces a archivos fuera de la selección; no debe presentarse como el resultado íntegro.

## 36.3 Verificar semántica, no solo enlaces ni tests

Las primeras vistas humanas confundían flujos que llegan a una operación real de datos con flujos puramente transaccionales, propiedad de pantallas con flujos entrantes, y direcciones de dependencias. En IST: 12.642 recorridos; 672 llegan a operación de datos real, otros 1.698 solo a control transaccional. Mantener acceso directo e indirecto separados. Una suite verde no reemplaza leer físicamente la documentación generada.

## 36.4 Navegación progresiva y profundidad honesta

Solution→Project→Archivo→Component→Método→Detalle permite una vista principal pequeña con enlaces a información ya recopilada. «Bajo demanda» significa abrir archivos de detalle ya generados, **no** volver a ejecutar extracción ni llamar a IA al hacer clic. Si una relación solo existe a nivel proyecto, no adjudicarla a un método. Sin firma/identidad canónica de sobrecarga no distinguir falsamente dos métodos homónimos.

## 36.5 Las llamadas no resueltas deben conservar la expresión original

Mostrar únicamente `(no resuelto)` desperdicia `call.expression` disponible. La expresión, estado y `archivo:línea` ayudan a investigar; no convertir la expresión en destino confirmado. Ruido conocido de framework/UI se controla en el perfil/política de presentación, nunca borrando evidence/provenance.

## 36.6 Transacciones no equivalen a acceso real a datos

Una operación de control transaccional (Begin/Commit/Rollback) no demuestra por sí sola consulta SQL/SP. Separar visualmente ambos apartados y conservar la misma semántica en índices, tests, medidas y documentación.

## 36.7 Escala: medir antes/después sin fijar reducciones arbitrarias

R3.4 generó 47.375 Markdown, con 22.215 páginas individuales de método. R3.4.1 generó 46.567, con 21.407 páginas de método; los 33.610 métodos permanecen en sus índices. El filtro eliminó 808 páginas de bajo valor, no cientos de relaciones útiles. No perseguir un porcentaje de reducción si elimina evidencia válida. Especificar el denominador y cuándo una métrica es solapada o proviene de muestreo; 0 links rotos en 5.514 enlaces revisados de 3.000 documentos **no es prueba exhaustiva** de los 46.567.

## 36.8 IA interpretativa y verdad son capas distintas

Una documentación determinista navegable no es una explicación funcional generada por IA. V5.2 no integra dicha interpretación ni ejecuta IA al abrir una página de detalle; la corrida real tuvo etapas IA `NOT_RUN`. V5.5–V5.7 prevén provider/contexto, segmentación y revisión/canonicalización. Mantener `Evidence → AI Proposal → Human Review → Canonical Knowledge`; jamás confundir el piloto IA grounded de V4.3 con integración ya entregada por V5.2.

## 36.9 No cerrar una fase por inferencia

`READY_FOR_HUMAN_REVIEW` y pruebas correctas no equivalen a `CLOSED`. Si el usuario quiere revisar otro aspecto, mantener R4 pendiente hasta aprobación expresa. No fabricar prompt siguiente antes de revisar el resultado y obtener autorización. Un resultado de ronda único bajo `docs/V5/`, prompt bajo `prompts/V5/`, rutas exactas y sin commits/push salvo autorización del usuario.

## 36.10 Procesos largos y monitores

En las corridas R3.3/R3.4 se observaron esperas repetidas por monitores de procesos en segundo plano. Comprobar proceso, log y exit code directamente; no declarar éxito de un test sin resumen final; evitar lanzar suites completas concurrentes o repetir extracción IST cuando ya existe evidencia persistida válida. Analizar una vez y regenerar proyecciones tantas veces como se necesite; ejecutar el pipeline real nuevamente cuando haga falta validar integración.

## 36.11 Cierre V5.2: lecciones generales

- **Baseline histórico frente a otra copia del mismo sistema:** dos rutas con el mismo nombre no son el mismo input. Comparar rama, `HEAD` y hashes de archivos relevantes antes de equiparlas; declarar por escrito cuál es el baseline oficial.
- **No cerrar una versión con el estado oficial desactualizado:** `PROJECT_STATE.json` debe actualizarse en la ronda de cierre. Al hacerlo, comprobar los tests históricos que parsean sus campos (los de rondas V4 exigían una etiqueta `V4…-R<N>`; se generalizaron para aceptar `V5.x-R<N>`).
- **Cubrir con tests las correcciones de robustez:** un reintento de escritura (`_replace_with_retry`) documentado pero sin prueba directa era una deuda evitable; se cubrió en R4.2 simulando `os.replace` y `time.sleep`.
- **Versionar antes de una nueva fase importante:** cerrar con commit + tag + push (con aprobación humana del push) para no arrastrar semanas de trabajo sin historial.
