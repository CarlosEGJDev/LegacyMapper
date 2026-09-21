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
