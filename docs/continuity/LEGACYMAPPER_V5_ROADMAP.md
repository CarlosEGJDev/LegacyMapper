# LegacyMapper V5 — Roadmap oficial de trabajo

## Estado inicial

```text
V4_3_CLOSED
V5_0_READY_TO_START
```

Baseline real:

```text
Dev repo: C:\dev\LegacyMapper
Target real: C:\inetpub\wwwroot\2010\IST\Operacional
```

Principio:

> Python descubre, estructura, selecciona y valida; la IA interpreta.

Objetivo de proceso:

> Diseñar suficiente antes de implementar para reducir al mínimo rondas correctivas.

---

# Orden oficial

```text
V5.0 — Architecture & Contracts
V5.1 — Normalized Evidence Core
V5.2 — Template-Driven Documentation & Output Profiles
V5.3 — Incremental Engine & Cache
V5.4 — Technology / DB Adapters
V5.5 — Generic AI Provider + Context
V5.6 — Rich Flow Segmentation
V5.7 — Approval + Canonical Knowledge
V5.8 — Consumer / Plugin Contract
V5.9 — Real Multi-Technology Pilot
V5 Closure
```

---

# Patrón de rondas

```text
R0 — Empirical baseline
R1 — Contract & design
R2 — Implementation
R3 — Verification + real regression
R4 — Closure
```

No todas las fases necesitan cinco rondas. Si aparecen múltiples correcciones, detener y rediagnosticar.

---

# V5.0 — Architecture & Contracts

## R0 — Empirical Baseline & Architecture Preparation

Objetivo: medir y documentar el estado real de V4.3 antes de diseñar V5.

Debe cubrir arquitectura actual, acoplamientos tecnológicos/provider, contratos V4.3 a preservar, escala/rendimiento, baseline de documentación, candidatos de cache, runtime independence y observación de process exit.

No modificar producción.

Salida:

```text
docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md
```

Estado esperado:

```text
V5_0_R0_READY_FOR_ARCHITECTURE
```

## R1 — Architecture Contract

Definir normalized core, adapter boundaries, persistence/cache boundaries, projection model, template/profile/renderer contracts, provider abstraction y compatibilidad/migración.

## R2 — Contract Validation

Validar arquitectura contra IST, outputs V4.3, tests y distribución limpia.

## R3 — Final Architecture Package

Consolidar contratos aceptados.

## R4 — V5.0 Closure

Cerrar arquitectura y autorizar V5.1.

---

# V5.1 — Normalized Evidence Core

Crear contratos normalizados independientes de tecnología preservando determinismo, provenance, unresolved, IDs y traceability.

---

# V5.2 — Template-Driven Documentation & Output Profiles

Perfiles mínimos:

```text
human-functional
human-technical
ai-context
```

Debe permitir default templates, custom templates, idioma, audiencia, nivel de detalle y evidence appendices.

Regla:

```text
template cambia presentación
template NO cambia evidencia
```

---

# V5.3 — Incremental Engine & Cache

Objetivo:

```text
cambio pequeño
→ recomputación pequeña
```

Fingerprints, cache, invalidation, persisted index, scope analysis y métricas.

---

# V5.4 — Technology / DB Adapters

Separar tecnología específica del core. WebForms/Oracle serán el primer adapter real preservado.

---

# V5.5 — Generic AI Provider + Context

Provider intercambiable con capacidades declaradas.

---

# V5.6 — Rich Flow Segmentation

Flows gigantes sin truncación silenciosa y con provenance completa.

---

# V5.7 — Approval + Canonical Knowledge

```text
Evidence → Proposal → Human Decision → Canonical Knowledge
```

Sin auto-approval.

---

# V5.8 — Consumer / Plugin Contract

Consumidores desacoplados. Plugin Runtime no entra automáticamente.

---

# V5.9 — Real Multi-Technology Pilot

Validar IST + segunda tecnología + normalized core + templates + cache + provider + segmentation + runtime independence.

---

# Reglas de ejecución

1. Medir antes de diseñar.
2. Una responsabilidad por ronda.
3. Tests en la misma ronda que implementación.
4. IST como regresión real.
5. Sonnet 5 medium por defecto.
6. Opus solo donde aporte valor.
7. Cambiar modelo tras ~3 fallos atribuibles al modelo.
8. No ampliar scope automáticamente.
9. Runtime independiente de docs/prompts/tests/governance.
10. Templates no alteran verdad.
11. Python hace lo determinista.
12. IA interpreta.
