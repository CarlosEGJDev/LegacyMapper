"""Deterministic fingerprints and the semantic content hash (V5.3-R2.3).

Nothing here is consumed yet (no cache exists): it only computes values the future incremental cache will use to
decide what may be reused. Standard library only; reads no docs, prompts, tests, governance files, Git state,
timestamps or AI. Modules, one responsibility each: `code` (analyzer code), `configuration` (config + CLI
classification), `templates` (documentation_v52 defaults/custom), `semantic` (semantic file hash).
"""
from ._common import FINGERPRINT_ALGORITHM, canonical_json
from .code import (
    ANALYZER_CODE_DIRECTORIES, ANALYZER_CODE_FILES, AVAILABLE, PIPELINE_STAGES_FILE, PIPELINE_STAGES_FUNCTIONS,
    UNAVAILABLE, CodeFingerprint, analyzer_code_fingerprint,
)
from .configuration import (
    AI_ONLY, ANALYSIS_AFFECTING, CLI_OPTION_CLASSES, OUTPUT_LOCATION_ONLY, PROJECTION_AFFECTING, REPOSITORY_IDENTITY,
    RUNTIME_ONLY, V52_PARAMETER_CLASSES, analysis_config_fingerprint, config_fingerprint, projection_config_fingerprint,
)
from .semantic import ANALYZED_FILE_TYPES, semantic_content_sha256, semantic_file_sha256
from .templates import TEMPLATE_KINDS, template_profile_fingerprint

__all__ = [name for name in dir() if not name.startswith("_")]
