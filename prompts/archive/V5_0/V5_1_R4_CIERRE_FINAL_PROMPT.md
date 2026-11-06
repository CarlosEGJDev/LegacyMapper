# V5.1 R4 — Cierre final de Normalized Evidence Core

## Rol

Trabaja sobre el repositorio:

C:\dev\LegacyMapper

Esta ronda es la revisión final y cierre formal de V5.1.

NO es una ronda de implementación.
NO debe introducir nuevas funcionalidades.
NO debe adelantar V5.2–V5.9.

El objetivo es determinar si V5.1 puede declararse formalmente cerrada.

---

# 1. Documentos obligatorios

Leer como mínimo:

- docs/V5/V5_1_R0_NEW_TARGET_REBASELINE.md
- docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md
- docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md
- docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md
- docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md
- docs/V5/V5_1_R3_1_CORRECCIONES_BLOQUEANTES.md
- docs/V5/V5_1_R3_REVALIDATION.md
- docs/V5/V5_1_R3_2_EVIDENCE_REFERENCE_TRACEABILITY.md

También revisar el contrato V5.0 aplicable a V5.1.

No asumir que una ronda anterior está correcta únicamente porque su documento diga READY.

Contrastar las conclusiones finales con:

- código actual;
- tests;
- outputs reales;
- contratos;
- invariantes.

---

# 2. Objetivo de R4

Responder una única pregunta:

> ¿V5.1 — Normalized Evidence Core cumple su alcance, contrato y arquitectura lo suficiente para declararse cerrada?

R4 debe verificar cierre.

NO debe corregir silenciosamente problemas encontrados.

Si aparece un defecto real dentro del alcance V5.1:

- documentarlo;
- marcar BLOCKED;
- no implementar la solución en esta ronda.

---

# 3. Estado de las decisiones anteriores

Confirmar que siguen cerradas:

## D-1 — identidad de dependencias externas

Debe continuar sin colisiones canónicas.

No modificar la solución.

---

## D-2 — SHA-256 obligatorio

`SourceArtifact.sha256` debe continuar:

- obligatorio;
- calculado en producción;
- no nulo;
- determinista.

No modificar la decisión.

---

## D-3 — Evidence Core obligatorio

Si Evidence Core falla:

- la ejecución V5 debe quedar FAILURE;
- no debe existir SUCCESS silencioso;
- un manifest inválido o antiguo no debe ocultar el fallo.

No modificar esta decisión.

---

## D-4 — trazabilidad del origen

Confirmar que:

- `provenance` se emite realmente;
- `EvidenceReference` se usa realmente;
- I-4 e I-5 se ejecutan en producción;
- referencias inválidas fallan;
- la trazabilidad real no contiene referencias rotas.

No rediseñar la solución.

---

# 4. D-5 — lector de evidence persistido

D-5 significa:

> actualmente no existe un lector completo `evidence/ → entidades normalizadas` para reconstruir posteriormente las proyecciones desde los archivos persistidos.

Esta deuda ya fue clasificada como NO bloqueante para V5.1.

R4 debe:

- confirmar que sigue siendo deuda conocida;
- dejarla registrada;
- indicar que debe resolverse en una versión futura cuando sea necesaria para integración/cache/reutilización desde disco.

NO implementar D-5 en R4.

NO usar D-5 como excusa para ampliar V5.1.

---

# 5. Arquitectura V5.1

Confirmar que el producto respeta conceptualmente:

Legacy Source
    ↓
Technology Adapter
    ↓
Normalized Evidence Core
    ↓
Evidence Persistence
    ↓
Projections

Verificar que:

- `evidence/` representa la evidencia normalizada;
- `index/` sigue siendo compatibilidad legacy;
- documentación no es la evidencia canónica;
- IA no es necesaria para construir Evidence Core.

---

# 6. Evidence Core

Confirmar que el núcleo normalizado contiene y persiste correctamente los conceptos acordados en R1/R2.

No es necesario listar todos los campos en detalle si ya están cubiertos por las pruebas anteriores.

Debe quedar claro que:

- las entidades esenciales existen;
- las identidades canónicas son estables;
- las relaciones relevantes son válidas;
- no existen referencias colgantes relevantes;
- la evidencia es determinista.

---

# 7. Invariantes

Revisar el estado final de I-1 a I-11.

No repetir innecesariamente todas las pruebas si existe evidencia reciente válida y el código no cambió.

Debe quedar explícitamente confirmado que:

- ninguna invariante obligatoria de V5.1 queda conocida como incumplida;
- I-4/I-5 ya no están pendientes después de R3.2;
- cualquier invariante vacía por ausencia de casos reales está correctamente documentada.

Si una invariante obligatoria queda incumplida:

V5.1 no puede cerrarse.

---

# 8. Persistencia

Confirmar:

- `evidence/` se genera desde producción;
- manifest válido;
- particiones consistentes;
- hashes de partición correctos;
- formato determinista;
- evidencia incompleta no se considera válida.

No cambiar formato físico en R4.

---

# 9. Determinismo

Confirmar que las dos últimas ejecuciones equivalentes de R3.2 demostraron determinismo.

Solo ejecutar nuevas corridas reales completas si:

- el código cambió desde R3.2;
- existe una duda real sobre la evidencia anterior;
- o alguna validación de cierre lo requiere.

No repetir dos corridas de ~30 minutos sin necesidad si el árbol de código relevante es idéntico al validado en R3.2.

---

# 10. Compatibilidad V4.3

Confirmar que las correcciones V5.1 no rompieron:

- index/
- documentation/
- RUN_SUMMARY
- stages legacy

Las diferencias operacionales ya conocidas como `duration_seconds` no son regresiones funcionales.

No modificar V4.3 en R4.

---

# 11. Production integration

Confirmar que:

- `main.py full` genera Evidence Core;
- `main.py analyze` genera Evidence Core;
- Evidence Core no depende exclusivamente de herramientas de desarrollo;
- las validaciones de Evidence Core forman parte del camino productivo.

---

# 12. Runtime independence

Confirmar que runtime productivo no depende de:

- tools/
- tests/
- docs/
- prompts/
- PROJECT_STATE
- rutas personales de desarrollo

Debe mantenerse:

tools → runtime

y no:

runtime → tools

---

# 13. AI independence

Confirmar que Evidence Core no depende de:

- Claude;
- OpenAI;
- Ollama;
- Anthropic;
- otro provider LLM;
- prompts;
- ai_context.

V5.5 sigue siendo responsable de la integración genérica de IA.

---

# 14. Technology Adapter boundary

Confirmar que el núcleo genérico no quedó acoplado innecesariamente a:

- VB.NET;
- WebForms;
- Oracle.

La implementación de referencia puede usar esos datos a través del adapter correspondiente.

No implementar nuevos adapters.

---

# 15. Suite final

Ejecutar:

python -m unittest discover -s tests

Reportar únicamente lo necesario:

- total;
- failures;
- errors;
- skipped.

Para cerrar V5.1:

failures = 0
errors = 0

---

# 16. Deuda técnica final de V5.1

Crear una lista corta y explícita de deuda restante.

Separar:

A. deuda aceptable fuera del alcance actual;
B. defecto que contradice V5.1.

Para poder cerrar V5.1:

B debe estar vacío.

D-5 puede figurar en A.

No ocultar deuda conocida.

---

# 17. Criterios de cierre

V5.1 puede cerrarse únicamente si:

1. Evidence Core funciona desde producción.
2. Las identidades canónicas son válidas.
3. SHA-256 obligatorio está operativo.
4. Los fallos de Evidence Core invalidan la ejecución.
5. Provenance / EvidenceReference está integrado.
6. I-4 e I-5 funcionan realmente.
7. Persistencia es válida y determinista.
8. Compatibilidad V4.3 se mantiene.
9. Runtime independence se mantiene.
10. AI independence se mantiene.
11. Technology Adapter boundary se mantiene.
12. Suite completa termina sin failures/errors.
13. No queda defecto conocido que contradiga el alcance o arquitectura de V5.1.

---

# 18. No hacer

NO:

- implementar D-5;
- implementar V5.2;
- implementar templates;
- implementar profiles;
- implementar V5.3 cache;
- implementar V5.4 adapters;
- implementar V5.5 AI provider;
- implementar V5.6 segmentation;
- implementar V5.7 approval;
- implementar V5.8 plugin contract;
- implementar V5.9 pilot;
- refactorizar código sin necesidad;
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

# 19. Documento de resultado

Crear EXACTAMENTE:

docs/V5/V5_1_R4_CIERRE_FINAL.md

El documento debe ser conciso y contener:

1. Estado final.
2. Qué se validó.
3. Estado de D-1, D-2, D-3 y D-4.
4. Estado de D-5.
5. Arquitectura final V5.1.
6. Invariantes.
7. Persistencia y determinismo.
8. Compatibilidad V4.3.
9. Integración productiva.
10. Independencia runtime / IA / adapter.
11. Suite final.
12. Deuda técnica restante.
13. Conclusión de cierre.

Evitar repetir métricas extensas ya demostradas en rondas anteriores salvo que sean necesarias para justificar una conclusión.

---

# 20. Estados finales permitidos

El documento debe terminar exactamente con uno:

V5_1_CLOSED

V5_1_R4_BLOCKED

V5_1_R4_CONFLICT

V5_1_R4_OPEN_DECISION

Solo usar:

V5_1_CLOSED

si no queda ningún defecto conocido que contradiga el alcance o arquitectura aprobada de V5.1.

---

# 21. Regla final

Al terminar:

- crear únicamente `docs/V5/V5_1_R4_CIERRE_FINAL.md`;
- no crear el prompt de V5.2;
- no modificar roadmap;
- no modificar PROJECT_STATE;
- no avanzar automáticamente;
- esperar revisión externa.