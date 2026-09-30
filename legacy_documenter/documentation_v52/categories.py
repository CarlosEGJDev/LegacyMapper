"""Presentation categories and the neutral document model (R1 sections 7, 16).

`AudienceDocumentModel` is what Profile/Template/Renderer see. It carries
human-facing `values` only: internal ids live in `Item.evidence_ids`, which no
template can reference (INTERNAL_ONLY by construction).
"""
from __future__ import annotations

from dataclasses import dataclass, field

KEEP_SIMPLE = "KEEP_SIMPLE"
KEEP_TECHNICAL = "KEEP_TECHNICAL"
DETAIL_ON_DEMAND = "DETAIL_ON_DEMAND"
INTERNAL_ONLY = "INTERNAL_ONLY"
CATEGORIES = (KEEP_SIMPLE, KEEP_TECHNICAL, DETAIL_ON_DEMAND, INTERNAL_ONLY)

DETERMINISTIC = "DETERMINISTIC"
INTERPRETED = "INTERPRETED"


@dataclass
class Item:
    """One presentable fact. `values` are strings/ints already sanitized;
    `level` (1-4) is the reading level it belongs to (R1 section 2)."""

    values: dict
    category: str
    level: int = 3
    nature: str = DETERMINISTIC
    noise_category: str | None = None
    detail_refs: tuple = ()  # human-readable "file:line" origins
    evidence_ids: tuple = ()  # INTERNAL_ONLY: never exposed to templates


@dataclass
class ModuleModel:
    """A `Project` (the only deterministic module notion available, GAP-M1)."""

    slug: str
    values: dict
    slots: dict[str, list[Item]] = field(default_factory=dict)


@dataclass
class SolutionModel:
    """A real `.sln` (V5.2 R3.3): navigation from Solution to the Projects it
    demonstrably contains (`slots["projects"]`), never a Project's own document."""

    slug: str
    values: dict
    slots: dict[str, list[Item]] = field(default_factory=dict)


@dataclass
class FileModel:
    """A `SourceArtifact` (V5.2 R3.3): a physical source file, distinct from any
    `Component` it may declare. `slots["components"]` may hold zero, one or
    several components -- never assumed 1:1 with the file."""

    slug: str
    values: dict
    slots: dict[str, list[Item]] = field(default_factory=dict)


@dataclass
class ComponentModel:
    """A `Component` (V5.2 R3.3): a class-like symbol or a WebForm/UserControl/
    MasterPage, with its own file of origin and, when the evidence has them,
    its known methods (`slots["methods"]`, never a fabricated signature/line)."""

    slug: str
    values: dict
    slots: dict[str, list[Item]] = field(default_factory=dict)


@dataclass
class MethodModel:
    """A method (V5.2 R3.4): one member of a `Component`, promoted to its own
    navigable document only when it has at least one individually verifiable
    technical relation (call, data access) -- see `transform._build_methods`.
    A method whose name is not unique within its owning component (an overload
    or accidental homonym the extractor cannot tell apart, GAP-M2) never gets
    one of these: its relations cannot be attributed to a single signature
    without fabricating a distinction the evidence does not carry."""

    slug: str
    values: dict
    slots: dict[str, list[Item]] = field(default_factory=dict)


@dataclass
class InterpretedSection:
    """Optional externally supplied interpretation (R1 section 13). Never
    replaces evidence; may be absent."""

    target: str  # "system" or "module:<project path>"
    content: str
    origin: str
    created_at: str
    language: str | None = None


@dataclass
class AudienceDocumentModel:
    system: dict
    slots: dict[str, list[Item]]
    modules: list[ModuleModel]
    solutions: list[SolutionModel] = field(default_factory=list)
    files: list[FileModel] = field(default_factory=list)
    components: list[ComponentModel] = field(default_factory=list)
    methods: list[MethodModel] = field(default_factory=list)
    interpreted: dict[str, InterpretedSection] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
