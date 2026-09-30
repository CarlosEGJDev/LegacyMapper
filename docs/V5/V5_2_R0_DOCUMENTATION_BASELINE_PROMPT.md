# V5.2 R0 — Documentation & Output Profiles Baseline

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

Esta ronda inicia V5.2:

Template-Driven Documentation & Output Profiles.

V5.1 está cerrada.

NO modificar V5.1.
NO implementar todavía templates ni output profiles.
NO modificar código productivo en esta ronda.

El objetivo es estudiar cómo se genera y consume actualmente la documentación y definir una baseline real antes del diseño de V5.2.

---

# 1. Principio central de V5.2

La documentación humana NO debe ser una representación directa del Evidence Core.

La arquitectura objetivo es:

Evidence
    ↓
Audience Transformation
    ↓
Output Profile
    ↓
Template
    ↓
Renderer
    ↓
Human Documentation

Separaciones obligatorias:

Template != AI
Profile != AI
Renderer != AI
Evidence != Human Documentation

La IA no debe ser necesaria para generar documentación determinista.

---

# 2. Objetivo humano prioritario

La documentación debe ser comprensible para personas con distintos niveles técnicos.

V5.2 debe contemplar como mínimo dos necesidades.

## A. Vista general

Dirigida a:

- administradores;
- analistas;
- usuarios técnicos no desarrolladores;
- personas que necesitan entender un sistema sin leer código.

Debe permitir responder fácilmente:

- ¿Qué hace este sistema?
- ¿Qué módulos principales tiene?
- ¿Cómo se relacionan?
- ¿Qué procesos principales existen?
- ¿Con qué sistemas externos se comunica?
- ¿Qué datos utiliza a grandes rasgos?

Debe evitar:

- IDs internos;
- estructuras JSON;
- listas gigantes de métodos;
- detalles irrelevantes del parser;
- terminología interna del motor;
- evidencia cruda salvo que se solicite.

---

## B. Vista desarrollador

Dirigida a una persona que debe mantener o modificar el sistema.

Debe permitir responder:

- ¿Cómo está organizado el sistema?
- ¿Qué proyectos o módulos existen?
- ¿Qué responsabilidad tiene cada módulo?
- ¿Cuáles son los puntos de entrada principales?
- ¿Cómo fluye una operación importante?
- ¿Qué componentes llama?
- ¿Dónde accede a datos?
- ¿Qué stored procedures / SQL / servicios externos utiliza?
- ¿Dónde está el código relacionado?
- ¿Qué dependencias importantes existen?

Debe ser técnica pero legible.

No debe convertirse en un dump completo de Evidence Core.

Los detalles profundos deben poder consultarse progresivamente cuando sean necesarios.

---

# 3. Regla de documentación progresiva

Evaluar la documentación actual usando este principio:

Nivel 1 — Qué es
Nivel 2 — Cómo funciona
Nivel 3 — Cómo está construido
Nivel 4 — Evidencia técnica detallada

Una persona no debería necesitar leer Nivel 4 para entender Nivel 1.

Investigar si la documentación actual mezcla estos niveles y dónde ocurre.

---

# 4. Revisar implementación actual

Inspeccionar cómo LegacyMapper genera actualmente:

- documentation/
- index/
- ai_context/
- consumer_projection/

Identificar:

- renderers;
- exporters;
- templates existentes si los hay;
- generación Markdown;
- generación HTML si existe;
- estructura de archivos;
- datos usados como entrada;
- acoplamientos entre documentación y estructuras legacy.

No asumir arquitectura por los documentos anteriores: revisar el código real.

---

# 5. Baseline real

Usar una salida real reciente de IST.

Preferir, si sigue disponible y corresponde al código actual:

C:\PruebasLegacyMapper\Resultados\v5_1_r3_2_run_a

o una salida equivalente reciente.

NO ejecutar un análisis completo de IST nuevamente salvo que sea necesario.

Revisar documentación real producida.

---

# 6. Seleccionar muestras representativas

No intentar revisar manualmente cientos de documentos.

Seleccionar una muestra pequeña pero representativa, incluyendo cuando sea posible:

- un módulo relativamente sencillo;
- uno mediano;
- uno complejo;
- un flujo con acceso a base de datos;
- un flujo con dependencias externas;
- algún caso con información incompleta/unresolved.

Documentar cómo se eligió la muestra.

---

# 7. Evaluar comprensión humana

Para cada tipo de documento actual, analizar:

## Comprensibilidad

¿Una persona que no conoce LegacyMapper podría entender qué está viendo?

## Utilidad

¿Ayuda realmente a comprender el sistema?

## Exceso técnico

¿Presenta información interna que el lector probablemente no necesita?

## Falta de contexto

¿Muestra datos correctos pero no explica qué significan?

## Navegabilidad

¿Permite ir de información general a detalles técnicos?

## Escalabilidad

¿Sigue siendo usable en un sistema grande como IST?

---

# 8. Clasificación de contenido

Clasificar la información actual en cuatro grupos:

### KEEP_SIMPLE

Información que debería aparecer directamente en documentación general.

### KEEP_TECHNICAL

Información útil para desarrolladores.

### DETAIL_ON_DEMAND

Información útil, pero solo cuando el lector necesita profundizar.

### INTERNAL_ONLY

Información que sirve al motor, validación o trazabilidad pero no debería mostrarse normalmente a humanos.

No eliminar datos del Evidence Core.

Esta clasificación afecta únicamente a presentación/documentación.

---

# 9. Output Profiles

NO diseñar todavía el formato final.

Determinar qué perfiles parecen necesarios según evidencia real.

Como mínimo estudiar:

- General Overview
- Developer Technical

Puede proponer perfiles adicionales solo si existe una necesidad real demostrable.

No crear docenas de perfiles especulativos.

---

# 10. Templates

NO implementar Template Engine.

Revisar qué partes de la documentación actual deberían ser controlables por templates.

Ejemplos conceptuales:

- títulos;
- secciones;
- orden;
- tablas;
- bloques;
- inclusión/exclusión de secciones.

Determinar qué debe pertenecer al template y qué NO.

---

# 11. Separación Profile / Template / Renderer

Evaluar y preparar el diseño futuro respetando:

Profile
    = qué información necesita una audiencia

Template
    = cómo se estructura/presenta esa información

Renderer
    = cómo se convierte a Markdown/HTML/etc.

No mezclar estas responsabilidades.

---

# 12. Documentación por defecto

Analizar qué debería ocurrir si el usuario NO entrega templates propios.

V5.2 debe poder ofrecer defaults razonables.

Determinar necesidades, no implementarlas aún.

La experiencia por defecto debe priorizar simplicidad.

---

# 13. Personalización futura

Analizar cómo un usuario podría posteriormente:

- elegir perfil;
- elegir template;
- proporcionar template propio;
- seleccionar formato;
- modificar presentación sin tocar código.

No diseñar todavía CLI final si falta evidencia.

No implementar.

---

# 14. Relación con IA

La documentación base debe poder generarse sin IA.

La IA futura podrá:

- interpretar;
- resumir;
- enriquecer;
- adaptar lenguaje;

pero NO debe ser necesaria para que templates/profiles/renderers funcionen.

V5.5 sigue siendo responsable de Generic AI Provider.

---

# 15. Problemas actuales

Crear una lista corta y priorizada de problemas reales encontrados.

No generar una lista enorme.

Clasificar únicamente:

- BLOCKING_FOR_V5_2
- IMPORTANT
- MINOR

Explicar cada problema en lenguaje claro.

---

# 16. Decisiones que necesitará R1

Identificar solo las decisiones arquitectónicas que realmente necesitemos tomar antes de implementar V5.2.

No decidirlas automáticamente si requieren decisión del Technical Lead.

Separar:

- decisiones ya respaldadas por V5.0/V5.1;
- decisiones nuevas que necesitan aprobación.

---

# 17. No hacer

NO:

- modificar producción;
- implementar templates;
- implementar profiles;
- implementar renderer nuevo;
- implementar IA;
- modificar Evidence Core;
- implementar D-5;
- implementar cache;
- implementar adapters;
- implementar V5.3–V5.9;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentos auxiliares;
- crear FIX_NOTES.md;
- crear PATCH_RESULT.md;
- crear DIAGNOSTICO_EXTRA.md;
- crear TODO_FIX.md;
- crear prompts adicionales.

---

# 18. Documento de resultado

Crear EXACTAMENTE:

docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md

Debe ser entendible también para una persona que no sea experta en LegacyMapper.

Estructura recomendada:

1. Estado.
2. Cómo funciona hoy la documentación.
3. Qué problema tiene para lectores humanos.
4. Qué funciona bien y debe conservarse.
5. Vista general necesaria.
6. Vista desarrollador necesaria.
7. Clasificación KEEP_SIMPLE / KEEP_TECHNICAL / DETAIL_ON_DEMAND / INTERNAL_ONLY.
8. Perfiles de salida que parecen necesarios.
9. Qué debería controlar un template.
10. Qué debería controlar un profile.
11. Qué debería controlar un renderer.
12. Defaults necesarios.
13. Relación con IA.
14. Problemas encontrados.
15. Decisiones necesarias para R1.
16. Evidencia real utilizada.
17. Conclusión.

Evitar llenar el resultado con IDs internos, conteos masivos o detalles de implementación salvo que sean necesarios para justificar una decisión.

---

# 19. Estados permitidos

Terminar exactamente con uno:

V5_2_R0_BASELINE_READY

V5_2_R0_BLOCKED

V5_2_R0_CONFLICT

V5_2_R0_OPEN_DECISION

---

# 20. Regla final

Al terminar:

- crear únicamente `docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md`;
- no crear el prompt R1;
- no modificar roadmap;
- no modificar PROJECT_STATE;
- esperar revisión externa.