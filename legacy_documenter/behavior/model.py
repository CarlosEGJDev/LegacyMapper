"""Structured human-explanation model (post-V5 H4-R4).

Every important statement is a `Claim`: text + epistemic status + source references + basis/reason. The model is plain data: an AI
interpretation may only *fill* it; `validate.py` decides what survives. Statuses are the project-wide five.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

CONFIRMED, INFERRED, UNRESOLVED, AI_INTERPRETATION, CANONICAL = "CONFIRMED", "INFERRED", "UNRESOLVED", "AI_INTERPRETATION", "CANONICAL"
STATUSES = (CONFIRMED, INFERRED, UNRESOLVED, AI_INTERPRETATION, CANONICAL)
CONTRACT = "LegacyMapperBehavioralExplanation"
CONTRACT_VERSION = "0.1-prototype"

MODULE_CONFIRMED, MODULE_INFERRED, MODULE_NONE = "MODULE_STRUCTURE_CONFIRMED", "MODULE_STRUCTURE_INFERRED", "NO_SAFE_MODULE_STRUCTURE"
WIREFRAME_UNAVAILABLE = "WIRE_FRAME_UNAVAILABLE_FROM_CURRENT_EVIDENCE"


@dataclass
class Claim:
    """One statement. `origin` is `deterministic` (produced by Python from evidence) or `ai` (produced by an interpretation layer)."""
    text: str
    status: str
    source_refs: list[str] = field(default_factory=list)
    basis: str = ""                      # why: the rule / evidence that supports the status
    origin: str = "deterministic"
    entities: list[dict] = field(default_factory=list)   # [{type: view|event|method|class|procedure, name}] the statement relies on


@dataclass
class ViewInvocation:
    """`source_view` opens/calls `target_view` (a popup/dialog or a navigation)."""
    source_view: str
    target_view: str
    mechanism: str                       # window_open | url_literal | navigate_url
    parameters: list[str] = field(default_factory=list)
    file: str = ""
    line: int = 0
    status: str = CONFIRMED
    target_exists: bool = True
    note: str = ""
    source_refs: list[str] = field(default_factory=list)


@dataclass
class BehaviorPath:
    """An evidence-backed route: ordered steps `{kind, label, status, source_refs}` (kind: view/event/handler/method/data_operation/procedure/unresolved)."""
    action: str
    steps: list[dict] = field(default_factory=list)
    flow_id: str = ""
    status: str = CONFIRMED
    unresolved_calls: list[dict] = field(default_factory=list)


@dataclass
class DataInteractionExplanation:
    object_name: str
    kind: str                            # stored_procedure | sql | table_binding
    effect: str                          # read | create | update | delete | mixed | unknown
    effect_status: str = INFERRED
    plain: str = ""
    via: str = ""                        # class.method that reaches it
    source_refs: list[str] = field(default_factory=list)
    status: str = CONFIRMED


@dataclass
class ActionExplanation:
    action: str                          # human label
    trigger: str                         # control id / lifecycle
    event: str
    handler: str
    simple: Claim | None = None
    technical_path: BehaviorPath | None = None
    data: list[DataInteractionExplanation] = field(default_factory=list)
    result: list[Claim] = field(default_factory=list)
    status: str = CONFIRMED
    source_refs: list[str] = field(default_factory=list)


@dataclass
class UIControl:
    id: str
    tag: str
    kind: str                            # label | text | dropdown | button | link | grid | panel | other
    label: str = ""
    visible_initially: bool = True
    line: int = 0
    columns: list[str] = field(default_factory=list)
    bound_to: str = ""                   # declared data binding (class.method) when present in the markup
    event_bound: bool = False


@dataclass
class UIReconstruction:
    status: str                          # DOCUMENTARY_RECONSTRUCTION | WIRE_FRAME_UNAVAILABLE_FROM_CURRENT_EVIDENCE
    source: str = ""
    controls: list[UIControl] = field(default_factory=list)
    rows: list[list[list[str]]] = field(default_factory=list)   # layout skeleton: rows -> cells -> control ids
    svg: str = ""
    reason: str = ""
    notice: str = "RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE PANTALLA"
    fidelity: str = "STRUCTURE_ONLY"      # STRUCTURE_ONLY | STYLE_PARTIAL | STYLE_HIGH_CONFIDENCE
    style_report: dict = field(default_factory=dict)


@dataclass
class UnresolvedExplanation:
    known: list[Claim] = field(default_factory=list)
    inferred: list[Claim] = field(default_factory=list)
    unresolved: list[Claim] = field(default_factory=list)


@dataclass
class ClassRole:
    name: str
    role: str                            # ui_code_behind | business | data_access | helper | other
    status: str
    basis: str = ""
    source_refs: list[str] = field(default_factory=list)


@dataclass
class ViewMessage:
    kind: str                            # msgbox | alert | error_display
    text: str                            # literal found in the code (never invented); empty when only the call is known
    event: str
    line: int
    file: str
    status: str = CONFIRMED


@dataclass
class ViewExplanation:
    view: str                            # path as in the baseline
    name: str
    kind: str                            # user_control | page
    family: str = ""                     # name-prefix family (INFERRED, not a module)
    title: str = ""
    what_it_does: list[Claim] = field(default_factory=list)
    reached_by: list[ViewInvocation] = field(default_factory=list)
    reaches: list[ViewInvocation] = field(default_factory=list)
    receives: list[Claim] = field(default_factory=list)
    ui: UIReconstruction | None = None
    actions: list[ActionExplanation] = field(default_factory=list)
    classes: list[ClassRole] = field(default_factory=list)
    messages: list[ViewMessage] = field(default_factory=list)
    unresolved: UnresolvedExplanation = field(default_factory=UnresolvedExplanation)
    ai_interpretation: list[Claim] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    usage: dict = field(default_factory=dict)                   # observable-usage classification (usage.py)
    ai_narrative: dict = field(default_factory=dict)            # validated AI sections: {section: [Claim]} (always AI_INTERPRETATION)
    ai_action_notes: dict = field(default_factory=dict)         # {handler: [Claim]} AI explanation per important action


@dataclass
class ModuleExplanation:
    classification: str                  # MODULE_STRUCTURE_* constant
    claim: Claim
    evidence_considered: list[dict] = field(default_factory=list)
    families: list[dict] = field(default_factory=list)          # name-prefix families (inferred; never called modules)


@dataclass
class ProjectExplanation:
    name: str
    path: str
    summary: list[Claim] = field(default_factory=list)
    role_in_solution: list[Claim] = field(default_factory=list)
    structural_areas: list[Claim] = field(default_factory=list)
    dependencies: list[Claim] = field(default_factory=list)
    data_patterns: list[Claim] = field(default_factory=list)
    unresolved: UnresolvedExplanation = field(default_factory=UnresolvedExplanation)
    facts: dict = field(default_factory=dict)                   # compact facts box (counts live here, never in the narrative)
    ai_summary: list[Claim] = field(default_factory=list)       # validated AI project-level narrative (AI_INTERPRETATION)


@dataclass
class SolutionExplanation:
    name: str
    projects: list[dict] = field(default_factory=list)
    summary: list[Claim] = field(default_factory=list)
    not_inferable: list[Claim] = field(default_factory=list)
    facts: dict = field(default_factory=dict)


@dataclass
class BehavioralDocument:
    solution: SolutionExplanation
    project: ProjectExplanation
    module: ModuleExplanation
    views: list[ViewExplanation]                                # the detailed (pilot) views
    catalog: list[dict]                                         # one row per view of the project
    cross_view: list[ViewInvocation] = field(default_factory=list)
    measurements: dict = field(default_factory=dict)
    usage_summary: dict = field(default_factory=dict)
    ai_manifest: dict = field(default_factory=dict)
    baseline: dict = field(default_factory=dict)
    domain_knowledge: list = field(default_factory=list)       # human-confirmed terms (origin HUMAN_CONFIRMED; never source evidence)
    contract: str = CONTRACT
    contract_version: str = CONTRACT_VERSION


def to_dict(obj) -> dict:
    return asdict(obj)
