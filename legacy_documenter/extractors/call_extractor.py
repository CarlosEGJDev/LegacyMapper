"""Legacy import compatibility: pure re-exports; implementation lives in the adapter."""
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.call_extractor import (
    IMPORT_RE,
    TYPE_RE,
    END_TYPE_RE,
    METHOD_RE,
    END_METHOD_RE,
    VAR_RE,
    ASSIGN_NEW_RE,
    NEW_RE,
    QUALIFIED_CALL_RE,
    INTERNAL_CALL_RE,
    KEYWORDS,
    VB_INTRINSICS,
    DEFAULT_PROPERTY_ACCESSORS,
    CallExtractor,
 )
