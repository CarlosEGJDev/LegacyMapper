"""Deterministic, source-neutral semantic catalog for R1's `KnowledgeNature` taxonomy.

Describes the intended semantic role of each of the 17 existing
`KnowledgeNature` values without depending on VB.NET, .NET Framework, Web
Forms, Oracle, source-code paths, projects, symbols, or any other
code/framework-specific concept. This is descriptive metadata about the
taxonomy, not a new taxonomy, not approval, and not a temporal-state
declaration.
"""
from dataclasses import dataclass

from legacy_documenter.knowledge.domain.enums import KnowledgeNature


class UnknownKnowledgeNatureError(ValueError):
    """Raised when a `KnowledgeNature` has no registered catalog entry."""


@dataclass(frozen=True)
class NatureSemantics:
    """Describes one `KnowledgeNature`'s intended semantic role.

    `prescriptive_or_descriptive` is `"prescriptive"` (states how something
    should be/must be done), `"descriptive"` (documents an observed/current
    state), or `"context-dependent"` (either, depending on the material).
    This distinction is descriptive only — never approval, never a temporal
    (AS_IS/TO_BE) declaration, which R6 owns.
    """

    nature: KnowledgeNature
    semantic_role: str
    prescriptive_or_descriptive: str
    notes: str


NATURE_SEMANTICS: dict[KnowledgeNature, NatureSemantics] = {
    KnowledgeNature.NORM: NatureSemantics(
        KnowledgeNature.NORM,
        "Prescriptive rule defining how something should be done (governance rule, "
        "development standard, security rule, methodology, mandatory operating rule).",
        "prescriptive",
        "Does not imply implementation or compliance.",
    ),
    KnowledgeNature.LEVANTAMIENTO: NatureSemantics(
        KnowledgeNature.LEVANTAMIENTO,
        "Descriptive inventory or documented observation of the current state "
        "(current tool inventory, current agent inventory, system survey, technical/functional survey).",
        "descriptive",
        "Describes what has been observed/documented, not what must be.",
    ),
    KnowledgeNature.REQUIREMENT: NatureSemantics(
        KnowledgeNature.REQUIREMENT,
        "Explicit requirement stating something that must be satisfied.",
        "prescriptive",
        "Do not assume REQUIREMENT implies TO_BE unless temporal state was explicitly established elsewhere.",
    ),
    KnowledgeNature.NEED: NatureSemantics(
        KnowledgeNature.NEED,
        "Need, problem, or objective that motivates work but may not yet be a formal requirement.",
        "context-dependent",
        "Precedes REQUIREMENT in maturity; not itself a formal commitment.",
    ),
    KnowledgeNature.BUSINESS_RULE: NatureSemantics(
        KnowledgeNature.BUSINESS_RULE,
        "Rule belonging to business/domain behavior.",
        "prescriptive",
        "Not automatically equivalent to corporate governance NORM.",
    ),
    KnowledgeNature.DECISION: NatureSemantics(
        KnowledgeNature.DECISION,
        "Explicit choice among alternatives or direction selected by an authorized process/person.",
        "descriptive",
        "Classification as DECISION does not itself establish approval authority.",
    ),
    KnowledgeNature.ARCHITECTURE: NatureSemantics(
        KnowledgeNature.ARCHITECTURE,
        "Architectural description, principle, topology, component relationship, "
        "or technical structural design.",
        "context-dependent",
        "May describe an existing (descriptive) or intended (prescriptive) architecture.",
    ),
    KnowledgeNature.PROCESS: NatureSemantics(
        KnowledgeNature.PROCESS,
        "Ordered business or technical process.",
        "context-dependent",
        "May be broader than a single FLOW; R5 does not decompose one into the other.",
    ),
    KnowledgeNature.FLOW: NatureSemantics(
        KnowledgeNature.FLOW,
        "Specific flow/path through a process/system.",
        "context-dependent",
        "May be narrower than a PROCESS; R5 does not attempt semantic decomposition.",
    ),
    KnowledgeNature.CATALOG: NatureSemantics(
        KnowledgeNature.CATALOG,
        "Inventory/listing of available or existing entities, capabilities, or resources.",
        "descriptive",
        "A structural listing, not a narrative process description.",
    ),
    KnowledgeNature.PROJECT: NatureSemantics(
        KnowledgeNature.PROJECT,
        "Knowledge describing a project, accompaniment, initiative, or project-specific context.",
        "context-dependent",
        "Scope is the project itself, not a specific rule/process/architecture within it.",
    ),
    KnowledgeNature.RESOLUTION: NatureSemantics(
        KnowledgeNature.RESOLUTION,
        "Formal resolution/outcome addressing a previously identified matter.",
        "descriptive",
        "Kept distinct from generic DECISION only when the caller explicitly distinguishes them.",
    ),
    KnowledgeNature.LESSON: NatureSemantics(
        KnowledgeNature.LESSON,
        "Recorded lesson learned or experience-derived guidance.",
        "descriptive",
        "Reflective/retrospective in nature, not a mandatory rule by itself.",
    ),
    KnowledgeNature.TRAINING: NatureSemantics(
        KnowledgeNature.TRAINING,
        "Training, onboarding, or learning material.",
        "descriptive",
        "Instructional content aimed at people, not a system specification.",
    ),
    KnowledgeNature.GLOSSARY: NatureSemantics(
        KnowledgeNature.GLOSSARY,
        "Defined terminology and vocabulary.",
        "descriptive",
        "Definitional reference material.",
    ),
    KnowledgeNature.CONSTRAINT: NatureSemantics(
        KnowledgeNature.CONSTRAINT,
        "Technical, organizational, regulatory, operational, or project constraint.",
        "prescriptive",
        "A bounding condition, not evidence that the current system already satisfies or violates it.",
    ),
    KnowledgeNature.EXISTING_IMPLEMENTATION: NatureSemantics(
        KnowledgeNature.EXISTING_IMPLEMENTATION,
        "Description of what is currently implemented.",
        "descriptive",
        "Classification alone does not prove the implementation currently exists; "
        "evidence/provenance is still required by later knowledge stages.",
    ),
}


class KnowledgeNatureCatalog:
    """Closed, deterministic lookup from `KnowledgeNature` to its `NatureSemantics`."""

    @staticmethod
    def covered_natures() -> frozenset[KnowledgeNature]:
        """Returns the closed set of `KnowledgeNature`s this catalog describes."""
        return frozenset(NATURE_SEMANTICS.keys())

    @staticmethod
    def get(nature: KnowledgeNature) -> NatureSemantics:
        """Returns the semantics for `nature`, failing deterministically if unregistered."""
        if not isinstance(nature, KnowledgeNature):
            raise UnknownKnowledgeNatureError(f"unknown_knowledge_nature:{nature!r}")
        entry = NATURE_SEMANTICS.get(nature)
        if entry is None:
            raise UnknownKnowledgeNatureError(f"no_semantics_for_knowledge_nature:{nature}")
        return entry

    @staticmethod
    def assert_complete() -> bool:
        """Verifies every `KnowledgeNature` enum member has exactly one registered catalog entry."""
        if set(KnowledgeNature) != KnowledgeNatureCatalog.covered_natures():
            missing = set(KnowledgeNature) - KnowledgeNatureCatalog.covered_natures()
            extra = KnowledgeNatureCatalog.covered_natures() - set(KnowledgeNature)
            raise UnknownKnowledgeNatureError(f"catalog_incomplete:missing={missing}:extra={extra}")
        return True
