"""V3-R1 language-neutral documentation contracts; no AI or I/O dependencies."""
from dataclasses import dataclass, field, asdict
import hashlib, json

SCHEMA_VERSION="3.0.0"
DOCUMENT_TYPES={"FUNCTIONAL_ASSESSMENT","TECHNICAL_ASSESSMENT"}
STATUSES={"DRAFT","GENERATED","VALIDATED","NEEDS_CHANGES","APPROVED","REJECTED","SUPERSEDED"}
FACT_STATUSES={"CONFIRMED","INTERPRETED","UNRESOLVED"}
SOURCE_TYPES={"DETERMINISTIC_CODE_FACT","APPROVED_FUNCTIONAL_DOCUMENT","APPROVED_TECHNICAL_DOCUMENT","APPROVED_EXTERNAL_INFORMATION","AI_INTERPRETATION","UNRESOLVED"}

def stable_id(prefix,*parts):
    """Performs stable id while preserving this module's deterministic contract."""
    raw=json.dumps(parts,ensure_ascii=False,separators=(",",":"))
    return f"{prefix}-{hashlib.sha256(raw.encode()).hexdigest()}"

@dataclass
class EvidenceReference:
    """Provides the cohesive EvidenceReference responsibility for this module."""
    source_type:str; reference_id:str; authoritative:bool=False
@dataclass
class DocumentClaim:
    """Provides the cohesive DocumentClaim responsibility for this module."""
    claim_id:str; document_id:str; section_id:str; claim_type:str; text_or_structured_value:object; status:str; confidence:str; source_refs:list[EvidenceReference]=field(default_factory=list); evidence_refs:list[str]=field(default_factory=list); related_entities:list[str]=field(default_factory=list); validation_state:str="OPEN"
@dataclass
class MissingInformation:
    """Provides the cohesive MissingInformation responsibility for this module."""
    missing_id:str; document_type:str; scope:str; category:str; description:str; reason:str; impact:str; required_information:str; source_refs:list[str]=field(default_factory=list); status:str="OPEN"
@dataclass
class DocumentMetadata:
    """Provides the cohesive DocumentMetadata responsibility for this module."""
    document_id:str; document_type:str; source_snapshot:dict; generated_at:str|None=None; generator:str|None=None; provider:str|None=None; model:str|None=None; generation_mode:str="CONTRACT"; status:str="DRAFT"; revision:int=1; scope:dict=field(default_factory=dict); source_refs:list[str]=field(default_factory=list); validation_status:str="NOT_VALIDATED"; approval_status:str="NOT_APPROVED"; approved_by:str|None=None; approved_at:str|None=None; schema_version:str=SCHEMA_VERSION
@dataclass
class FunctionalModule:
    """Provides the cohesive FunctionalModule responsibility for this module."""
    module_id:str; name:str; description:str; status:str; confidence:str; source_refs:list[str]=field(default_factory=list); functionalities:list[dict]=field(default_factory=list); entry_points:list[str]=field(default_factory=list); flows:list[str]=field(default_factory=list); data_dependencies:list[str]=field(default_factory=list); unresolved_items:list[str]=field(default_factory=list)
@dataclass
class ArchitecturePatternAssessment:
    """Provides the cohesive ArchitecturePatternAssessment responsibility for this module."""
    pattern_id:str; pattern_name:str; classification:str; status:str; confidence:str; evidence_refs:list[str]=field(default_factory=list); supporting_observations:list[str]=field(default_factory=list); contradicting_observations:list[str]=field(default_factory=list); scope:dict=field(default_factory=dict); notes:str=""
@dataclass
class DocumentationContract:
    """Provides the cohesive DocumentationContract responsibility for this module."""
    metadata:DocumentMetadata; claims:list[DocumentClaim]=field(default_factory=list); modules:list[FunctionalModule]=field(default_factory=list); patterns:list[ArchitecturePatternAssessment]=field(default_factory=list); missing_information:list[MissingInformation]=field(default_factory=list)
    def validate(self):
        """Performs validate while preserving this module's deterministic contract."""
        m=self.metadata
        if m.document_type not in DOCUMENT_TYPES or m.status not in STATUSES or not m.source_snapshot: raise ValueError("invalid metadata")
        for values,name in [(self.claims,"claim_id"),(self.modules,"module_id"),(self.patterns,"pattern_id"),(self.missing_information,"missing_id")]:
            ids=[getattr(x,name) for x in values]
            if len(ids)!=len(set(ids)): raise ValueError(f"duplicate {name}")
        for c in self.claims:
            if c.status not in FACT_STATUSES or c.confidence not in FACT_STATUSES: raise ValueError("invalid claim status")
            if c.status=="CONFIRMED" and not any(x.authoritative for x in c.source_refs): raise ValueError("confirmed claim requires authoritative evidence")
        if m.approval_status=="APPROVED" and m.validation_status!="VALIDATED": raise ValueError("approval requires validation")
        return True
    def canonical_json(self): return json.dumps(asdict(self),ensure_ascii=False,sort_keys=True,separators=(",",":"))

def approval_gate(functional:DocumentationContract, technical:DocumentationContract):
    """Performs approval gate while preserving this module's deterministic contract."""
    return functional.metadata.approval_status=="APPROVED" and technical.metadata.approval_status=="APPROVED"

def functional_markdown_template():
    """Performs functional markdown template while preserving this module's deterministic contract."""
    return "# LEVANTAMIENTO FUNCIONAL\n\n## Metadata\n## Application Purpose\n## Scope\n## Functional Modules\n## Flows\n## Rules\n## Unresolved Areas\n## Traceability\n## Review and Approval\n"
def technical_markdown_template():
    """Performs technical markdown template while preserving this module's deterministic contract."""
    return "# LEVANTAMIENTO TECNICO\n\n## Metadata\n## Technical Overview\n## Scope\n## Solutions and Projects\n## Components\n## Patterns\n## Data Access\n## Configuration\n## Risks\n## Traceability\n## Review and Approval\n"
