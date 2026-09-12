"""Closed vocabularies for the V4 knowledge domain model.

Every enum here is a deterministic, closed contract from `docs/V4/V4_CONTRACT_FOUNDATION.md`.
Free-form strings are intentionally rejected wherever one of these types applies.
"""
from enum import Enum


class SourceType(str, Enum):
    """Identifies where a piece of material or knowledge originates from.

    `DETERMINISTIC_CODE_FACT` is one member among several; it is never
    privileged as the root of the domain model. Human- and document-derived
    source types are equally first-class.
    """

    DETERMINISTIC_CODE_FACT = "DETERMINISTIC_CODE_FACT"
    HUMAN_REQUIREMENT = "HUMAN_REQUIREMENT"
    USER_STORY = "USER_STORY"
    BUSINESS_REQUIREMENT = "BUSINESS_REQUIREMENT"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"
    TECHNICAL_CONSTRAINT = "TECHNICAL_CONSTRAINT"
    CORPORATE_STANDARD = "CORPORATE_STANDARD"
    APPROVED_DECISION = "APPROVED_DECISION"
    EXTERNAL_DOCUMENT = "EXTERNAL_DOCUMENT"
    PROJECT_DOCUMENT = "PROJECT_DOCUMENT"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    UNRESOLVED = "UNRESOLVED"


class KnowledgeNature(str, Enum):
    """Describes what kind of knowledge a statement represents, independent of its source.

    Nature must be preserved through the whole future pipeline and must not be
    conflated with a target document/section name.
    """

    NORM = "NORM"
    LEVANTAMIENTO = "LEVANTAMIENTO"
    REQUIREMENT = "REQUIREMENT"
    NEED = "NEED"
    BUSINESS_RULE = "BUSINESS_RULE"
    DECISION = "DECISION"
    ARCHITECTURE = "ARCHITECTURE"
    PROCESS = "PROCESS"
    FLOW = "FLOW"
    CATALOG = "CATALOG"
    PROJECT = "PROJECT"
    RESOLUTION = "RESOLUTION"
    LESSON = "LESSON"
    TRAINING = "TRAINING"
    GLOSSARY = "GLOSSARY"
    CONSTRAINT = "CONSTRAINT"
    EXISTING_IMPLEMENTATION = "EXISTING_IMPLEMENTATION"


class KnowledgeStatus(str, Enum):
    """Represents the current confidence/lifecycle state of a knowledge statement.

    `CONFIRMED`, `INTERPRETED` and `UNRESOLVED` preserve their V3 meaning.
    The remaining values extend the vocabulary for later V4 rounds (partial
    disclosure, missing information, detected conflicts and superseded facts)
    without those rounds' detection engines being implemented here.
    """

    CONFIRMED = "CONFIRMED"
    INTERPRETED = "INTERPRETED"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    SUPERSEDED = "SUPERSEDED"


class TemporalState(str, Enum):
    """Distinguishes what currently exists from what should exist.

    `AS_IS` and `TO_BE` statements about the same subject may coexist; this
    module does not detect or resolve the resulting GAP, it only allows both
    to be represented without contradiction.
    """

    AS_IS = "AS_IS"
    TO_BE = "TO_BE"
    HISTORICAL = "HISTORICAL"


class ApprovalStatus(str, Enum):
    """Represents Technical Lead approval state without implementing the R9 workflow.

    This is a data holder only: no automated transition logic belongs here.
    """

    NOT_APPROVED = "NOT_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CORRECTED = "CORRECTED"
