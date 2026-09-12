# Manual de usuario de LegacyMapper V3

## 1. Qué es LegacyMapper V3

LegacyMapper analiza de forma reproducible aplicaciones .NET heredadas y produce inventarios, trazabilidad y documentación asistida por IA, manteniendo separados los hechos, las interpretaciones y lo no resuelto.

## 2. Objetivo

Ayudar a comprender un sistema grande sin convertir suposiciones en hechos y entregar levantamientos funcionales y técnicos revisables por personas.

## 3. Qué analiza

Soluciones y proyectos, Visual Basic .NET, WebForms, configuraciones, llamadas, dependencias, accesos a datos, procedimientos almacenados, puntos de entrada y flujos funcionales.

## 4. Qué no hace

No modifica el sistema legado, no garantiza comprensión semántica completa, no deduce arquitectura formal por nombres y no genera conocimiento final por el solo hecho de ejecutar V3-R9.

## 5. Requisitos

Python compatible con el proyecto, acceso de lectura al repositorio legado y permisos de escritura en una carpeta de salida separada. Los pilotos reales requieren además un proveedor configurado; el análisis determinista y R9 no.

## 6. Preparación del entorno

Abra una terminal en la raíz de LegacyMapper. Use el entorno Python ya preparado por el proyecto. No instale dependencias ni cambie el sistema operativo sin autorización del responsable.

## 7. Configuración

Los tipos de archivo y exclusiones base están en `legacy_documenter/config.py`. Las credenciales de proveedores, cuando correspondan, deben venir de mecanismos externos; nunca se escriben en documentación ni outputs.

## 8. Configuración del repositorio legado

Pase su ruta como argumento. La fuente es de solo lectura y la salida debe quedar fuera de ella.

## 9. Ejecución

El entry point unificado disponible para discovery es:

```text
python -m legacy_documenter.main "RUTA_REPOSITORIO" --output "RUTA_SALIDA" --verbose
```

No existe un CLI único que ejecute automáticamente todas las rondas V3. Cada etapa validada usa su API o módulo real. El gate vigente se ejecuta con:

```text
python -m legacy_documenter.knowledge.readiness
```

## 10. Flujo completo V3

Discovery determinista → resolución de contexto → composición con presupuesto → interpretación restringida por evidencia → síntesis documental → revisión humana → análisis profundo dirigido → segunda revisión → readiness.

## 11. Relación V1, V2 y V3

V1 establece el inventario básico. V2 amplía resolución y evidencia canónica. V3 consume esas bases, compone contexto, controla interpretación, genera documentación y aplica decisiones humanas y gates.

## 12. Archivos de salida

Los índices deterministas viven bajo el output elegido. Los levantamientos actuales son `output/LEVANTAMIENTO_FUNCIONAL.md` y `output/LEVANTAMIENTO_TECNICO.md`. El readiness está bajo `output/v3_r9/`.

## 13. Levantamiento Funcional

Resume alcance, áreas, pantallas, flujos, operaciones de datos, limitaciones, métricas y trazabilidad. Lea siempre las etiquetas `CONFIRMED`, `INTERPRETED` y `UNRESOLVED`.

## 14. Levantamiento Técnico

Describe soluciones, componentes, presentación WebForms, acceso a datos, dependencias, flujos, riesgos y límites arquitectónicos observables.

## 15. Revisión humana

La persona revisora aprueba si el documento representa correctamente tanto lo conocido como lo desconocido. Aprobar no significa conocer cada detalle del legado.

## 16. Estados y decisiones

Los documentos pasan por estados de ciclo de vida hasta `APPROVED`. Los ítems pueden quedar `HUMAN_CONFIRMED`, `ACCEPTED_AS_PARTIAL` o `ACCEPTED_AS_UNRESOLVED_EXTERNAL`.

## 17. Uso del proveedor LLM

Solo etapas de interpretación autorizadas llaman al proveedor. El proveedor recibe contexto sanitizado y acotado. Discovery, validación, revisión registrada y readiness son deterministas.

## 18. Seguridad y privacidad

No coloque contraseñas ni tokens en argumentos, ejemplos o archivos. Revise el reporte de sanitización antes de autorizar una llamada real. LegacyMapper no debe escribir en la fuente.

## 19. Interpretación de resultados

`CONFIRMED` tiene evidencia determinista; `INTERPRETED` es una lectura restringida por evidencia; `UNRESOLVED` declara que falta soporte. La trazabilidad indica de dónde proviene cada afirmación.

## 20. Información parcial

La información parcial puede ser útil, pero debe viajar con incertidumbre y procedencia. No equivale a una relación completa.

## 21. Información externa no disponible

Una limitación externa aceptada informa que el dato falta y que la evidencia disponible fue agotada. No proporciona el dato ausente.

## 22. Knowledge Readiness

R9 comprueba aprobaciones, claims, evidencia, métricas, arquitectura, seguridad y fronteras antes de permitir una etapa futura de conocimiento.

## 23. Qué significa AI_KNOWLEDGE_ALLOWED

`true` significa que una fase posterior puede generar conocimiento usando exclusivamente la proyección aprobada y sus límites.

## 24. Qué no significa AI_KNOWLEDGE_ALLOWED

No significa que `AI_KNOWLEDGE` exista, que todos los claims sean hechos, ni que lo parcial o externo haya sido resuelto.

## 25. Errores frecuentes

- Ruta fuente incorrecta o sin permiso de lectura.
- Output dentro del repositorio legado.
- Falta de artefactos de una fase previa.
- Documento no aprobado o disposición humana incompleta.
- Contexto mayor que el presupuesto o respuesta de proveedor inválida.

## 26. Diagnóstico

Use `--verbose` en discovery. En R9 revise `KNOWLEDGE_READINESS.json` y `READINESS_TRACEABILITY.json`; `unresolved_aliases` debe contener listas vacías.

## 27. Reejecución segura

Use la misma fuente, configuración y output esperado. Las etapas deterministas producen resultados repetibles. Antes de reemplazar outputs, conserve los artefactos aprobados que constituyen entradas canónicas.

## 28. Archivos que no deben modificarse

No modifique la fuente legado, decisiones humanas aprobadas, evidencia V2/R8 ni levantamientos aprobados para forzar un gate. Corrija el origen contractual y vuelva a validar.

## 29. Ejemplo de uso

```text
python -m legacy_documenter.main "C:\ruta\legado" --output "C:\ruta\salida" --verbose
python -m unittest discover -s tests
python -m legacy_documenter.knowledge.readiness
```

El ejemplo usa rutas ficticias y no contiene credenciales.

## 30. Preguntas frecuentes

**¿READY crea conocimiento?** No. `AI_KNOWLEDGE_GENERATED` continúa en `false`.

**¿Puedo confiar en un INTERPRETED como hecho?** No; consérvelo como interpretación con evidencia.

**¿La aplicación analizada es MVC?** V3 no lo establece. La evidencia soporta presentación WebForms, pero no una arquitectura formal única.

**¿Puedo editar un JSON generado?** No como solución normal. Corrija la entrada o implementación y regenere.

**¿R9 usa internet o un LLM?** No.

