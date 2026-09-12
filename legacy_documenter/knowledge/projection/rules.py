"""Closed target-document configuration and default deterministic projection rules (V4-R11).

This module is the single place where the fixed human-readable information architecture is
declared. It intentionally does **not** define one Python domain class per folder/document
family: every target document is one plain, validated `ProjectionTarget` value, and the whole
architecture is one flat, closed tuple. `DOCUMENT_STRUCTURE_IS_PROJECTION_CONCERN=true`;
`DOCUMENT_STRUCTURE_IS_DOMAIN_MODEL=false`.

Mapping is performed only through explicit structured `CanonicalKnowledgeEntry` fields
(`source_type`, `nature`, `status`, `temporal_state`, and the explicit
`metadata["projection_categories"]` tag set). No rule here ever inspects `entry.statement`
free text. `metadata["projection_categories"]` is itself a structured, closed-vocabulary
field (see `ProjectionCategory` below) supplied explicitly at canonical-composition time or
by the caller assembling entries for projection — never inferred by this module from prose.
"""
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.projection.models import ProjectionRule, ProjectionTarget

# ---------------------------------------------------------------------------
# 00 - El area (ONBOARDING / CONTEXT)
# ---------------------------------------------------------------------------
T_00_QUE_ES = ProjectionTarget("00-el-area/que-es-el-area.md", "00-el-area", "Qué es el área", "ONBOARDING")
T_00_FUNCIONES = ProjectionTarget("00-el-area/funciones.md", "00-el-area", "Funciones del área", "ONBOARDING")
T_00_EQUIPO = ProjectionTarget("00-el-area/equipo-y-roles.md", "00-el-area", "Equipo y roles", "ONBOARDING")
T_00_ESPACIOS = ProjectionTarget("00-el-area/espacios-de-trabajo.md", "00-el-area", "Espacios de trabajo", "ONBOARDING")
T_00_PRIMER_DIA = ProjectionTarget("00-el-area/primer-dia.md", "00-el-area", "Primer día", "ONBOARDING")
T_00_GLOSARIO = ProjectionTarget("00-el-area/glosario.md", "00-el-area", "Glosario", "ONBOARDING")

# ---------------------------------------------------------------------------
# 01 - Gobernanza (NORMA)
# ---------------------------------------------------------------------------
# NOTE (spec-required distinction): "fuente-de-verdad.md" below is only a human-facing
# filename retained from the target information architecture. It must NOT be confused with,
# or presented as, a redefinition of the R10 "Canonical Knowledge Source" architectural
# concept. The Canonical Knowledge Source remains exactly the R10
# `CanonicalKnowledgeCollection`; this document is a projection of (a subset of) it.
T_01_FUENTE_DE_VERDAD = ProjectionTarget(
    "01-gobernanza/fuente-de-verdad.md", "01-gobernanza", "Fuente de verdad (proyección humana)", "NORMA",
)
T_01_RAMAS = ProjectionTarget("01-gobernanza/ramas-y-versionamiento.md", "01-gobernanza", "Ramas y versionamiento", "NORMA")
T_01_TABLERO = ProjectionTarget("01-gobernanza/gestion-del-tablero.md", "01-gobernanza", "Gestión del tablero", "NORMA")
T_01_SEGURIDAD = ProjectionTarget("01-gobernanza/seguridad-y-datos.md", "01-gobernanza", "Seguridad y datos", "NORMA")
T_01_IMPUTACION = ProjectionTarget("01-gobernanza/imputacion-y-reporte.md", "01-gobernanza", "Imputación y reporte", "NORMA")

# ---------------------------------------------------------------------------
# 02 - Flujos (FLUJO)
# ---------------------------------------------------------------------------
T_02_BLANCO = ProjectionTarget("02-flujos/desarrollo-en-blanco.md", "02-flujos", "Desarrollo en blanco", "FLUJO")
T_02_EVOLUTIVO = ProjectionTarget(
    "02-flujos/desarrollo-evolutivo-y-soporte.md", "02-flujos", "Desarrollo evolutivo y soporte", "FLUJO",
)
T_02_INGESTA = ProjectionTarget(
    "02-flujos/ingesta-y-actualizacion-de-contexto.md", "02-flujos", "Ingesta y actualización de contexto", "FLUJO",
)
T_02_ACOMPANAMIENTO = ProjectionTarget("02-flujos/acompanamiento.md", "02-flujos", "Acompañamiento", "FLUJO")
T_02_SOPORTE = ProjectionTarget("02-flujos/soporte-y-capacitacion.md", "02-flujos", "Soporte y capacitación", "FLUJO")
T_02_PREVENTA = ProjectionTarget("02-flujos/propuesta-preventa.md", "02-flujos", "Propuesta preventa", "FLUJO")

# ---------------------------------------------------------------------------
# 03 - Desarrollo de software (NORMA)
#
# DESIGN DECISION (flagged in the R11 result document): the spec lists the category set for
# this family in prose ("methodology, DoD, deliverables, coding standards, naming standards,
# config standards, source-control standards, dev-environment standards, design principles,
# patterns, anti-patterns, DevSecOps, pipeline, quality, security, environments") without
# fixing concrete filenames. This module models each category as exactly one closed target
# document (one file per category, no sub-hierarchy, no per-category Python domain class).
# ---------------------------------------------------------------------------
T_03_METHODOLOGY = ProjectionTarget("03-desarrollo-de-software/methodology.md", "03-desarrollo-de-software", "Metodología", "NORMA")
T_03_DOD = ProjectionTarget("03-desarrollo-de-software/definition-of-done.md", "03-desarrollo-de-software", "Definition of Done", "NORMA")
T_03_DELIVERABLES = ProjectionTarget("03-desarrollo-de-software/deliverables.md", "03-desarrollo-de-software", "Entregables", "NORMA")
T_03_CODING_STANDARDS = ProjectionTarget("03-desarrollo-de-software/coding-standards.md", "03-desarrollo-de-software", "Estándares de código", "NORMA")
T_03_NAMING_STANDARDS = ProjectionTarget("03-desarrollo-de-software/naming-standards.md", "03-desarrollo-de-software", "Estándares de nomenclatura", "NORMA")
T_03_CONFIG_STANDARDS = ProjectionTarget("03-desarrollo-de-software/configuration-standards.md", "03-desarrollo-de-software", "Estándares de configuración", "NORMA")
T_03_SOURCE_CONTROL = ProjectionTarget("03-desarrollo-de-software/source-control-standards.md", "03-desarrollo-de-software", "Estándares de control de versiones", "NORMA")
T_03_DEV_ENV_STANDARDS = ProjectionTarget("03-desarrollo-de-software/dev-environment-standards.md", "03-desarrollo-de-software", "Estándares de entorno de desarrollo", "NORMA")
T_03_DESIGN_PRINCIPLES = ProjectionTarget("03-desarrollo-de-software/design-principles.md", "03-desarrollo-de-software", "Principios de diseño", "NORMA")
T_03_PATTERNS = ProjectionTarget("03-desarrollo-de-software/patterns.md", "03-desarrollo-de-software", "Patrones", "NORMA")
T_03_ANTIPATTERNS = ProjectionTarget("03-desarrollo-de-software/anti-patterns.md", "03-desarrollo-de-software", "Anti-patrones", "NORMA")
T_03_DEVSECOPS = ProjectionTarget("03-desarrollo-de-software/devsecops.md", "03-desarrollo-de-software", "DevSecOps", "NORMA")
T_03_PIPELINE = ProjectionTarget("03-desarrollo-de-software/pipeline.md", "03-desarrollo-de-software", "Pipeline", "NORMA")
T_03_QUALITY = ProjectionTarget("03-desarrollo-de-software/quality.md", "03-desarrollo-de-software", "Calidad", "NORMA")
T_03_SECURITY = ProjectionTarget("03-desarrollo-de-software/security.md", "03-desarrollo-de-software", "Seguridad", "NORMA")
T_03_ENVIRONMENTS = ProjectionTarget("03-desarrollo-de-software/environments.md", "03-desarrollo-de-software", "Ambientes", "NORMA")

# ---------------------------------------------------------------------------
# 04 - Arquitecturas de referencia (NORMA / REFERENCE ARCHITECTURE)
# ---------------------------------------------------------------------------
T_04_HERRAMIENTAS = ProjectionTarget("04-arquitecturas-de-referencia/herramientas.md", "04-arquitecturas-de-referencia", "Herramientas", "NORMA")
T_04_AGENTES = ProjectionTarget("04-arquitecturas-de-referencia/agentes.md", "04-arquitecturas-de-referencia", "Agentes", "NORMA")
T_04_CAPACIDADES = ProjectionTarget("04-arquitecturas-de-referencia/capacidades.md", "04-arquitecturas-de-referencia", "Capacidades", "NORMA")
T_04_PLATAFORMA = ProjectionTarget("04-arquitecturas-de-referencia/plataforma-agentica.md", "04-arquitecturas-de-referencia", "Plataforma agéntica", "NORMA")

# ---------------------------------------------------------------------------
# 05/06/07/08/09 - projection families
#
# DESIGN DECISION (flagged in the R11 result document): the spec defines these as
# "projection families" without fixing individual filenames (unlike 00/01/02/04). Each
# family is modeled here as one closed general document. This keeps the target set closed
# and avoids inventing a Python domain class per project/catalog entry; adding a more
# granular closed target later (e.g. one additional named project document) remains a purely
# additive configuration change, never a dynamic path derived from untrusted content.
# ---------------------------------------------------------------------------
T_05_PLANTILLAS = ProjectionTarget("05-plantillas/plantillas.md", "05-plantillas", "Plantillas", "PLANTILLA")
T_06_CATALOGO = ProjectionTarget("06-catalogo/catalogo.md", "06-catalogo", "Catálogo", "LEVANTAMIENTO")
T_07_PROYECTOS = ProjectionTarget("07-proyectos/proyectos.md", "07-proyectos", "Proyectos", "PROJECT")
T_08_HISTORIAL = ProjectionTarget("08-historial/historial.md", "08-historial", "Historial", "HISTORICAL")
T_09_CAPACITACION = ProjectionTarget("09-capacitacion/capacitacion.md", "09-capacitacion", "Capacitación", "TRAINING")

ALL_TARGETS: tuple[ProjectionTarget, ...] = (
    T_00_QUE_ES, T_00_FUNCIONES, T_00_EQUIPO, T_00_ESPACIOS, T_00_PRIMER_DIA, T_00_GLOSARIO,
    T_01_FUENTE_DE_VERDAD, T_01_RAMAS, T_01_TABLERO, T_01_SEGURIDAD, T_01_IMPUTACION,
    T_02_BLANCO, T_02_EVOLUTIVO, T_02_INGESTA, T_02_ACOMPANAMIENTO, T_02_SOPORTE, T_02_PREVENTA,
    T_03_METHODOLOGY, T_03_DOD, T_03_DELIVERABLES, T_03_CODING_STANDARDS, T_03_NAMING_STANDARDS,
    T_03_CONFIG_STANDARDS, T_03_SOURCE_CONTROL, T_03_DEV_ENV_STANDARDS, T_03_DESIGN_PRINCIPLES,
    T_03_PATTERNS, T_03_ANTIPATTERNS, T_03_DEVSECOPS, T_03_PIPELINE, T_03_QUALITY, T_03_SECURITY,
    T_03_ENVIRONMENTS,
    T_04_HERRAMIENTAS, T_04_AGENTES, T_04_CAPACIDADES, T_04_PLATAFORMA,
    T_05_PLANTILLAS, T_06_CATALOGO, T_07_PROYECTOS, T_08_HISTORIAL, T_09_CAPACITACION,
)

#: Closed vocabulary of explicit projection-category tags. A canonical entry declares zero or
#: more of these via `metadata["projection_categories"]`. This is a structured, closed field
#: (like `nature`/`source_type`), never free text parsed for keywords.
PROJECTION_CATEGORIES: tuple[str, ...] = (
    "gobernanza_fuente_de_verdad", "gobernanza_ramas_y_versionamiento", "gobernanza_gestion_del_tablero",
    "gobernanza_seguridad_y_datos", "gobernanza_imputacion_y_reporte",
    "flujo_desarrollo_en_blanco", "flujo_desarrollo_evolutivo_y_soporte",
    "flujo_ingesta_y_actualizacion_de_contexto", "flujo_acompanamiento", "flujo_soporte_y_capacitacion",
    "flujo_propuesta_preventa",
    "dev_methodology", "dev_definition_of_done", "dev_deliverables", "dev_coding_standards",
    "dev_naming_standards", "dev_configuration_standards", "dev_source_control_standards",
    "dev_environment_standards", "dev_design_principles", "dev_patterns", "dev_anti_patterns",
    "dev_devsecops", "dev_pipeline", "dev_quality", "dev_security", "dev_environments",
    "arquitectura_herramientas", "arquitectura_agentes", "arquitectura_capacidades",
    "arquitectura_plataforma_agentica",
    "el_area_que_es", "el_area_funciones", "el_area_equipo_y_roles", "el_area_espacios_de_trabajo",
    "el_area_primer_dia",
    "plantillas_general", "proyectos_general",
)

_CATEGORY_TARGET = {
    "gobernanza_fuente_de_verdad": T_01_FUENTE_DE_VERDAD,
    "gobernanza_ramas_y_versionamiento": T_01_RAMAS,
    "gobernanza_gestion_del_tablero": T_01_TABLERO,
    "gobernanza_seguridad_y_datos": T_01_SEGURIDAD,
    "gobernanza_imputacion_y_reporte": T_01_IMPUTACION,
    "flujo_desarrollo_en_blanco": T_02_BLANCO,
    "flujo_desarrollo_evolutivo_y_soporte": T_02_EVOLUTIVO,
    "flujo_ingesta_y_actualizacion_de_contexto": T_02_INGESTA,
    "flujo_acompanamiento": T_02_ACOMPANAMIENTO,
    "flujo_soporte_y_capacitacion": T_02_SOPORTE,
    "flujo_propuesta_preventa": T_02_PREVENTA,
    "dev_methodology": T_03_METHODOLOGY,
    "dev_definition_of_done": T_03_DOD,
    "dev_deliverables": T_03_DELIVERABLES,
    "dev_coding_standards": T_03_CODING_STANDARDS,
    "dev_naming_standards": T_03_NAMING_STANDARDS,
    "dev_configuration_standards": T_03_CONFIG_STANDARDS,
    "dev_source_control_standards": T_03_SOURCE_CONTROL,
    "dev_environment_standards": T_03_DEV_ENV_STANDARDS,
    "dev_design_principles": T_03_DESIGN_PRINCIPLES,
    "dev_patterns": T_03_PATTERNS,
    "dev_anti_patterns": T_03_ANTIPATTERNS,
    "dev_devsecops": T_03_DEVSECOPS,
    "dev_pipeline": T_03_PIPELINE,
    "dev_quality": T_03_QUALITY,
    "dev_security": T_03_SECURITY,
    "dev_environments": T_03_ENVIRONMENTS,
    "arquitectura_herramientas": T_04_HERRAMIENTAS,
    "arquitectura_agentes": T_04_AGENTES,
    "arquitectura_capacidades": T_04_CAPACIDADES,
    "arquitectura_plataforma_agentica": T_04_PLATAFORMA,
    "el_area_que_es": T_00_QUE_ES,
    "el_area_funciones": T_00_FUNCIONES,
    "el_area_equipo_y_roles": T_00_EQUIPO,
    "el_area_espacios_de_trabajo": T_00_ESPACIOS,
    "el_area_primer_dia": T_00_PRIMER_DIA,
    "plantillas_general": T_05_PLANTILLAS,
    "proyectos_general": T_07_PROYECTOS,
}


def _category_rule(rule_id: str, category: str) -> ProjectionRule:
    """Builds one category-tag-based rule, resolved against the closed `_CATEGORY_TARGET` map."""
    return ProjectionRule(rule_id=rule_id, target=_CATEGORY_TARGET[category], category=category)


#: The default, deterministic, explicit structured rule set (rule order is not itself
#: semantically meaningful for the projection outcome, but is fixed for determinism).
DEFAULT_RULES: tuple[ProjectionRule, ...] = tuple(
    _category_rule(f"RULE-CATEGORY-{category.upper()}", category) for category in _CATEGORY_TARGET
) + (
    ProjectionRule(rule_id="RULE-NATURE-GLOSSARY", target=T_00_GLOSARIO, nature=KnowledgeNature.GLOSSARY),
    ProjectionRule(rule_id="RULE-NATURE-CATALOG", target=T_06_CATALOGO, nature=KnowledgeNature.CATALOG),
    ProjectionRule(rule_id="RULE-NATURE-TRAINING", target=T_09_CAPACITACION, nature=KnowledgeNature.TRAINING),
    ProjectionRule(rule_id="RULE-NATURE-RESOLUTION", target=T_08_HISTORIAL, nature=KnowledgeNature.RESOLUTION),
    ProjectionRule(rule_id="RULE-NATURE-LESSON", target=T_08_HISTORIAL, nature=KnowledgeNature.LESSON),
)

__all__ = [
    "ALL_TARGETS",
    "DEFAULT_RULES",
    "PROJECTION_CATEGORIES",
]
