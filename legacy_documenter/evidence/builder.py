"""Legacy import compatibility: pure re-exports; implementation lives in the adapter."""
from legacy_documenter.adapters.vbnet_webforms_oracle.normalization import (
    REFERENCE_ADAPTER_ID,
    REFERENCE_ADAPTER_VERSION,
    PASSTHROUGH_INDEX_KEYS,
    _TERMINAL_UNRESOLVED_TYPES,
    NormalizedEvidence,
    NormalizedEvidenceBuilder,
    _hash_file,
    _whole_file_source_ref,
    _evidence_list_provenance,
    _connection_provenance,
 )
