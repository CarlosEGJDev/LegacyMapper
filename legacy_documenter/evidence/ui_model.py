"""UI / navigation / style Evidence extension (post-V5 Gate B, DT-03): contract constants and neutral fact records.

Evidence Core persists FACTS (what exists, where it came from, relationships, resolved/unresolved references), never presentation.
The extension is additive: the Core partitions and `EVIDENCE_SCHEMA_VERSION` are unchanged; the manifest of a run that produced UI
Evidence carries `ui_evidence_schema_version`. Technology adapters fill these partitions during deterministic analysis; downstream
consumers (behavioral documentation, AI context, templates) only read them -- never the source repository.
"""
from __future__ import annotations

from dataclasses import dataclass, field

UI_EVIDENCE_SCHEMA_VERSION = "1.1"  # 1.1 (Gate B.1): elided child envelopes, shared style profiles, ~/ asset roots, menu_entry edges

PARTITION_DOCUMENTS = "ui_documents"
PARTITION_CONTROLS = "ui_controls"
PARTITION_EVENTS = "ui_event_bindings"
PARTITION_NAVIGATION = "ui_navigation"
PARTITION_MESSAGES = "ui_messages"
PARTITION_PARAMETERS = "ui_parameters"
PARTITION_STYLES = "ui_style_references"
PARTITION_ASSETS = "ui_assets"

#: Persisted order is also the write order. Every partition is a JSON array of records with `id`, `kind`, `logical_source_path`,
#: `source_refs`, `status`, `properties`, `relationships` (see the Gate B result document for the per-kind field list).
UI_PARTITIONS = (PARTITION_DOCUMENTS, PARTITION_CONTROLS, PARTITION_EVENTS, PARTITION_NAVIGATION, PARTITION_MESSAGES,
                 PARTITION_PARAMETERS, PARTITION_STYLES, PARTITION_ASSETS)

#: Entity kind of each partition (record field `kind`).
UI_KINDS = {
    PARTITION_DOCUMENTS: "UiDocument", PARTITION_CONTROLS: "UiControl", PARTITION_EVENTS: "UiEventBinding",
    PARTITION_NAVIGATION: "UiNavigationEdge", PARTITION_MESSAGES: "UiMessage", PARTITION_PARAMETERS: "UiParameter",
    PARTITION_STYLES: "UiStyleReference", PARTITION_ASSETS: "UiAssetReference",
}
ID_PREFIX = {
    PARTITION_DOCUMENTS: "UID", PARTITION_CONTROLS: "UIC", PARTITION_EVENTS: "UIE", PARTITION_NAVIGATION: "UIN",
    PARTITION_MESSAGES: "UIM", PARTITION_PARAMETERS: "UIP", PARTITION_STYLES: "UIS", PARTITION_ASSETS: "UIA",
}

#: Statuses of an observed relation. Absence of a resolved destination is never converted into absence of behavior.
CONFIRMED, INFERRED, UNRESOLVED = "CONFIRMED", "INFERRED", "UNRESOLVED"
STATUSES = (CONFIRMED, INFERRED, UNRESOLVED)

#: Largest image embedded in Evidence as base64 (documentary wireframes only draw small icons).
MAX_ASSET_BYTES = 16384
ASSET_EXTENSIONS = (".gif", ".png", ".jpg", ".jpeg")


@dataclass
class MarkupControl:
    id: str
    tag: str
    kind: str
    label: str
    line: int
    visible: bool = True
    attrs: dict = field(default_factory=dict)
    columns: list[str] = field(default_factory=list)
    bound_to: str = ""
    row: int = 0
    cell: int = 0
    depth: int = 0
    table_path: tuple = ()


@dataclass
class CodeFacts:
    file: str
    subs: list[dict] = field(default_factory=list)            # {name, kind, line, handles, end}
    declared: list[dict] = field(default_factory=list)       # {id, type, line}
    receives: list[dict] = field(default_factory=list)       # {name, line, via}
    session_keys: list[str] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)       # {kind, text, line, event}
    imports: list[str] = field(default_factory=list)
    navigation: list[dict] = field(default_factory=list)
    script_blocks: int = 0
    visible_toggles: int = 0                                  # `.Visible = ...` assignments: layout that depends on runtime state


@dataclass
class NavHit:
    file: str
    line: int
    folder: str
    view: str
    params: list[str]
    mechanism: str


def norm_logical_path(path: str) -> str:
    """Case-insensitive, separator-insensitive key of a repository-relative path."""
    return str(path or "").replace("\\", "/").lower()
