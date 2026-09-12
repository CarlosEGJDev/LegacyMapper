"""Closed vocabularies for the V4 knowledge-classification layer.

`KnowledgeNature` itself is NOT redefined here — it is reused unchanged from
`legacy_documenter.knowledge.domain.enums`. Only classification-specific
vocabulary (how a classification was produced, and its resolution state)
lives in this module.
"""
from enum import Enum


class ClassificationMethod(str, Enum):
    """Describes how a `ClassificationRecord` was produced, independent of its outcome.

    `EXPLICIT` is the primary usable mode in R5: a human/caller directly
    supplied a selected nature or an explicit candidate list. `UNRESOLVED`
    marks the absence of any reliable classification. `DETERMINISTIC_RULE` is
    reserved for a genuine deterministic structural rule (none is introduced
    in R5). `AI_PROPOSED` is reserved for a future round; R5 never produces
    it and never calls an AI/provider.
    """

    EXPLICIT = "EXPLICIT"
    DETERMINISTIC_RULE = "DETERMINISTIC_RULE"
    AI_PROPOSED = "AI_PROPOSED"
    UNRESOLVED = "UNRESOLVED"


class ClassificationStatus(str, Enum):
    """Represents the resolution state of a classification, never its truth or approval.

    `CLASSIFIED` means exactly one `KnowledgeNature` was selected — nothing
    more. `UNCLASSIFIED` is a legitimate, permanent-until-revisited lifecycle
    state, not an error. `AMBIGUOUS` means two or more candidates are known
    but none was resolved; R5 never picks a winner on its own.
    """

    CLASSIFIED = "CLASSIFIED"
    UNCLASSIFIED = "UNCLASSIFIED"
    AMBIGUOUS = "AMBIGUOUS"
