# V5.1 R3.2 — Cierre de D-4: EvidenceReference y trazabilidad

## Rol

Trabaja sobre el repositorio:

C:\dev\LegacyMapper

Esta ronda existe exclusivamente para resolver D-4:

D-4 = la trazabilidad del origen de los datos no cumple todavía literalmente el contrato V5.1 porque `provenance` / `EvidenceReference` existe como diseño, pero no se emite realmente en producción.

NO es R4.
NO es una nueva fase arquitectónica.
NO debe ampliar alcance hacia V5.2–V5.9.

---

# 1. Documentos obligatorios

Leer como mínimo:

- docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md
- docs/V5/V5_1_R2_NORMALIZED_EVIDENCE_IMPLEMENTATION.md
- docs/V5/V5_1_R2_1_NORMALIZED_EVIDENCE_SANEAMIENTO.md
- docs/V5/V5_1_R3_VERIFICATION_REGRESSION.md
- docs/V5/V5_1_R3_1_CORRECCIONES_BLOQUEANTES.md
- docs/V5/V5_1_R3_REVALIDATION.md

También revisar el contrato V5.0 que define `provenance` / `EvidenceReference` como parte del modelo común.

No reinterpretar silenciosamente el contrato para evitar implementarlo.

---

# 2. Objetivo único

Implementar de forma real y productiva la trazabilidad definida por el contrato:

Entity
  ↓
provenance[]
  ↓
EvidenceReference
  ↓
SourceArtifact / source span / entity / textual reference

La evidencia normalizada debe poder indicar de dónde proviene.

No reemplazar esta obligación únicamente con foreign keys existentes como:

- source_ref
- source_artifact
- legacy_ref

Estas pueden seguir existiendo, pero `provenance` debe cumplir el contrato V5.

---

# 3. EvidenceReference

Revisar la implementación existente en:

legacy_documenter/evidence/reference.py

Reutilizarla.

NO crear un segundo modelo paralelo.

EvidenceReference debe conservar los tipos definidos por contrato:

- entity
- source
- source_span
- textual

y `legacy_ref` cuando corresponda.

No inventar nuevos tipos salvo que exista una contradicción demostrable con R1.

---

# 4. Provenance

Agregar `provenance` a las entidades para las que el contrato lo exige.

Regla general:

- toda entidad normalizada debe tener al menos una referencia de origen válida;
- `SourceArtifact` raíz puede ser la excepción si así lo define el contrato;
- no generar provenance ficticio;
- no crear referencias a entidades inexistentes;
- no convertir texto ambiguo en evidencia estructurada sin base real.

La implementación debe utilizar la evidencia ya disponible en el pipeline.

---

# 5. I-4 — Trazabilidad

La invariante I-4 debe pasar realmente en producción:

Toda entidad con provenance debe resolver a al menos un EvidenceReference válido.

No basta con que exista el método de validación.

Debe:

- ejecutarse;
- tener tests;
- verificarse sobre evidencia real;
- formar parte del gate de producción antes de persistir.

---

# 6. I-5 — Referencias inválidas

La invariante I-5 debe pasar realmente en producción:

Una referencia rota no puede pasar silenciosamente.

Si un EvidenceReference apunta a:

- una entidad inexistente;
- un SourceArtifact inexistente;
- un source span inválido;
- una referencia estructural inválida;

la validación debe fallar.

El run V5 debe terminar FAILURE conforme a la semántica ya acordada en R3.1.

---

# 7. Compatibilidad

La implementación debe ser aditiva.

Cuando la evidencia es válida:

- `index/` no debe cambiar funcionalmente;
- `documentation/` no debe cambiar;
- `RUN_SUMMARY.json` no debe sufrir cambios incompatibles;
- V4.3 debe seguir funcionando como antes.

No modificar los formatos legacy para introducir provenance.

`provenance` pertenece al Evidence Core.

---

# 8. Persistencia

Verificar que `provenance` se persiste correctamente dentro de `evidence/`.

Debe ser:

- determinista;
- serializable;
- reproducible;
- estable entre ejecuciones equivalentes.

No crear una nueva carpeta paralela.

No crear otro store de trazabilidad.

---

# 9. Alcance mínimo

No rediseñar todas las entidades si no es necesario.

Aplicar el cambio mínimo que permita cumplir correctamente el contrato.

Evitar:

- refactorizaciones generales;
- cambios de nombres innecesarios;
- nuevos frameworks;
- nuevas capas;
- nuevas abstracciones sin necesidad.

---

# 10. D-5 no se toca

D-5 = lector `evidence/ → entidades`.

Sigue fuera de alcance.

NO implementar:

- read_evidence completo;
- reconstrucción física de index desde evidence persistido;
- cache incremental.

D-5 continúa siendo deuda aceptable posterior.

---

# 11. No tocar otras decisiones cerradas

No modificar:

- identidad XDP;
- detector I-1;
- SourceArtifact.sha256 obligatorio;
- semántica FAILURE de Evidence Core;
- formato físico json_compact;
- Instantiation;
- Technology Adapter boundary;
- AI independence.

Solo verificar que no haya regresión.

---

# 12. Tests mínimos obligatorios

Agregar o ajustar tests para demostrar:

1. entidad con provenance válido ⇒ PASS;
2. provenance hacia entidad inexistente ⇒ FAIL;
3. provenance hacia SourceArtifact inexistente ⇒ FAIL;
4. source_span válido ⇒ PASS;
5. source_span inválido ⇒ FAIL;
6. EvidenceReference serializa de forma determinista;
7. evidencia real contiene provenance donde corresponde;
8. I-4 se ejecuta realmente;
9. I-5 se ejecuta realmente;
10. fallo de I-4/I-5 provoca FAILURE del run;
11. dos builds equivalentes producen provenance idéntico.

No usar solamente fixtures sintéticos.

---

# 13. Regresión real obligatoria

Target:

C:\Users\cgalianj\source\IST_40\Operacional

Usar una carpeta nueva bajo:

C:\PruebasLegacyMapper\Resultados\

Ejecutar al menos una corrida productiva completa.

Si determinismo no puede demostrarse reutilizando una corrida equivalente previa, ejecutar dos corridas nuevas.

Verificar:

- Evidence Core válido;
- provenance persistido;
- I-4 PASS;
- I-5 PASS;
- cero referencias rotas;
- determinismo;
- compatibilidad V4.3.

---

# 14. Suite completa

Ejecutar:

python -m unittest discover -s tests

Reportar:

- total;
- passed;
- failures;
- errors;
- skipped.

Debe terminar con:

0 failures
0 errors

---

# 15. Runtime independence

Mantener:

runtime ≠ tools/tests/docs/prompts/PROJECT_STATE

Permitido:

tools → runtime

Prohibido:

runtime → tools

---

# 16. AI independence

Evidence Core debe continuar sin depender de:

- Claude
- OpenAI
- Ollama
- Anthropic
- providers
- prompts
- ai_context

No implementar V5.5.

---

# 17. No hacer

NO:

- implementar V5.2;
- implementar V5.3;
- implementar V5.4;
- implementar V5.5;
- implementar V5.6;
- implementar V5.7;
- implementar V5.8;
- implementar V5.9;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentación auxiliar;
- crear FIX_NOTES.md;
- crear PATCH_RESULT.md;
- crear DIAGNOSTICO_EXTRA.md;
- crear TODO_FIX.md;
- crear prompts adicionales.

---

# 18. Documento de resultado

Crear EXACTAMENTE:

docs/V5/V5_1_R3_2_EVIDENCE_REFERENCE_TRACEABILITY.md

Debe incluir:

1. Estado final.
2. Qué se corrigió.
3. Cómo quedó provenance.
4. Cómo se usa EvidenceReference.
5. Resultado I-4.
6. Resultado I-5.
7. Validación de referencias reales.
8. Persistencia.
9. Determinismo.
10. Compatibilidad V4.3.
11. Resultado sobre IST real.
12. Suite completa.
13. Deuda restante.
14. Si V5.1 está lista para R4.

No crear documentos adicionales.

---

# 19. Estados finales permitidos

Terminar exactamente con uno:

V5_1_R3_2_READY_FOR_R4_REVALIDATION

V5_1_R3_2_BLOCKED

V5_1_R3_2_CONFLICT

V5_1_R3_2_OPEN_DECISION

No declarar cierre de V5.1.

No declarar R4 completada.

---

# 20. Regla final

Al terminar:

- crear únicamente el documento solicitado;
- no crear el prompt siguiente;
- no avanzar automáticamente;
- esperar revisión externa.