# Testing guide

Estado: vigente (post-H5). Los módulos `tests/test_v4_*`, `test_v5_*`, `test_post_v5_*` se conservan
como regresión histórica; el día a día se opera por **capacidad**, no por nombre de ronda.

## Runner por perfiles

```text
python -X utf8 -m legacy_documenter.devtest <perfil>       # fast | core | analysis | behavior | human_docs | ai_knowledge | visuals | packaging | distribution | provider | real_ist | full
python -X utf8 -m legacy_documenter.devtest list           # perfiles y tamaño
python -X utf8 -m legacy_documenter.devtest suggest <ruta> # qué perfil correr para una ruta cambiada
python -X utf8 -m legacy_documenter.devtest changed        # sugerencia desde git status
```

Solo usa `unittest` de la biblioteca estándar. Los patrones de cada perfil viven en
`legacy_documenter/devtest.py` (`PROFILE_PATTERNS`) y un test verifica que cada módulo de `tests/` esté
asignado al menos a un perfil.

| Perfil | Propósito | Dependencias externas | Duración |
| --- | --- | --- | --- |
| FAST | Humo: versiones/huellas, write-skip, max-path, procedencia, modelo, exit codes | ninguna | < 1 min |
| CORE | Modelo de dominio, contratos, aprobación, caches, contrato CLI | ninguna | minutos |
| ANALYSIS | Scanner, adapters, extractores, Evidence, flujos | ninguna (fixtures sintéticos) | minutos |
| BEHAVIOR | Pantallas, acciones, wireframes, prototipos | ninguna | ~10 s |
| HUMAN_DOCS | Documentación humana por audiencia, plantillas, layout | ninguna | minutos |
| AI_KNOWLEDGE | Interpretación IA, conocimiento, presupuesto de contexto | ninguna (proveedor simulado) | minutos |
| VISUALS | Proyecciones SVG/HTML/PDF | ninguna | minutos |
| PACKAGING | Paquete final humano + ai + internal | ninguna | ~1.5 min |
| DISTRIBUTION | Wheel, independencia de runtime, relocalización, contrato de plugin | ninguna | minutos |
| PROVIDER | Adaptadores de proveedor y guardia de proveedor real (stubs) | ninguna | segundos |
| REAL_IST | Regresiones sobre corpus real | `LEGACYMAPPER_REAL_IST_BASELINE` | segundos si se omite |
| FULL | Todo | ninguna requerida | larga |

## Qué correr cuando

Mapa mantenido en `CHANGED_AREA_MAP` (`legacy_documenter/devtest.py`):

```text
legacy_documenter/behavior/**      -> BEHAVIOR
legacy_documenter/visuals/**       -> VISUALS
legacy_documenter/deliver/**       -> PACKAGING
legacy_documenter/product/**       -> PACKAGING + HUMAN_DOCS
templates/human/**                 -> HUMAN_DOCS + PACKAGING
legacy_documenter/llm/**           -> PROVIDER + AI_KNOWLEDGE
legacy_documenter/utils/path_*     -> CORE + DISTRIBUTION
adapters/**                        -> ANALYSIS
legacy_documenter/models/**, versions.py -> FULL
```

**Suite completa** (`python -X utf8 -m unittest discover -s tests`) solo para: cierre de hito, checkpoint
de release, cambio arquitectónico transversal, cambio de contrato/esquema compartido. No para cada cambio.

## Política de fixtures

Clasificación: `SYNTHETIC_UNIT`, `SMALL_CONTRACT`, `REPOSITORY_LOCAL_INTEGRATION`, `GENERATED_IN_TEST`,
`REAL_IST_EXTERNAL`, `PROVIDER_EXTERNAL`. **`HISTORICAL_SNAPSHOT` requerido por tests activos = 0.**

* Usa fixtures sintéticos pequeños bajo `tests/fixtures/` o genéralos dentro del test (`tempfile`).
* No copies baselines de varios GB a Git.
* Un test nunca lee rutas absolutas de máquina (unidades de disco, carpetas de usuario, el antiguo workspace de pruebas) ni carpetas de salida de rondas históricas.
* Un test que necesite un recurso externo debe ser `REAL_IST` / `EXTERNAL_INTEGRATION`, recibir la ruta
  por variable de entorno y usar `skipUnless` con una razón explícita.

## Integración externa

* **IST real**: define `LEGACYMAPPER_REAL_IST_BASELINE=<WORK_ROOT>/Current/state/baseline` (y
  `LEGACYMAPPER_SOURCE_ROOT=<SOURCE_ROOT>` para herramientas en `tools/`). Solo por decisión explícita del
  responsable; un análisis IST completo toma ~10 min.
* **Proveedor de IA real**: nunca se invoca en tests; la guardia de proveedor real lo impide por defecto.
  Las pruebas usan proveedores simulados.

## Cómo añadir tests

1. Colócalo en `tests/test_<capacidad>_<tema>.py` y regístralo en un perfil (`PROFILE_PATTERNS`).
2. Genera sus entradas dentro del test o con un fixture del repositorio.
3. Usa `tempfile.TemporaryDirectory()`; nunca rutas absolutas ni el directorio actual.
4. Si cambia un contrato compartido, corre FULL antes de cerrar.

## Regresiones H5 que deben seguir activas

`tests/test_post_v5_h5_real_ist_scale.py`: membresía exacta de solución, paquete solo-máquina sin
UI/acciones, ids de datos en `knowledge.json`, wireframes dentro del marco, sin inferencia de propósito
de negocio a partir del nombre de la solución.
