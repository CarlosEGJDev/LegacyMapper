"""Runtime version constants and the renderer-version registry (V5.3-R2.3).

Nothing here is consumed yet: the future incremental cache (V5.3 R1 contract) reads these values.
Standard library only; renderer constants are imported lazily and reused, never duplicated.
"""
from __future__ import annotations

#: Bump whenever a change can alter what the analysis produces: extractors, scanner/classification,
#: namespace normalization, partial-class consolidation, resolvers, sanitizer. It is a plain integer, never
#: a Git commit. `fingerprints.analyzer_code_fingerprint()` is the automatic safety net; a guard test fails
#: when relevant code changed and this number did not (see tests/test_v5_3_r2_3_versioning_and_fingerprints.py).
ANALYZER_VERSION = 2  # 2: R2.5 extraction refactored into per-file records (`_extract_file`); output unchanged

#: Version of the persisted extraction-cache contract (shard format, entry structure/key, `cache_bypass` rules,
#: loading/validation/writing; R2.6). Independent of `ANALYZER_VERSION` and of the manifest schema. Bump it whenever
#: the contract code changes in a way that could make an older cache parse but mean something else: the guard
#: test `test_extraction_contract_guard` fails when `fingerprints.extraction_contract_fingerprint()` moves while
#: this number does not. A different value in a manifest makes the extraction cache non-reusable (File State is
#: unaffected) and a missing value is treated the same way.
EXTRACTION_CACHE_SCHEMA_VERSION = 1

#: The legacy Markdown exporters (`exporters/` and the technical renderers) have no version constant of
#: their own; this is the one new constant the registry needs.
LEGACY_MARKDOWN_RENDERER_VERSION = "1"


def evidence_schema_version() -> str:
    """The existing Evidence Core schema version (reused, not redefined)."""
    from legacy_documenter.evidence.entities import EVIDENCE_SCHEMA_VERSION

    return EVIDENCE_SCHEMA_VERSION


def renderer_versions() -> dict[str, dict[str, str]]:
    """Version constants per output family, reusing each family's own constants where they exist."""
    from legacy_documenter.context import ai_projection, consumer_projection, hydration, system_context_builder
    from legacy_documenter.documentation import human_documentation_scaling, human_flow_documentation
    from legacy_documenter.documentation_v52 import config as v52_config

    return {
        "legacy_markdown": {"version": LEGACY_MARKDOWN_RENDERER_VERSION},
        "human_documentation": {
            "flow_model_version": human_flow_documentation.MODEL_VERSION,
            "flow_schema_version": human_flow_documentation.SCHEMA_VERSION,
            "scaling_model_version": human_documentation_scaling.MODEL_VERSION,
            "scaling_schema_version": human_documentation_scaling.SCHEMA_VERSION,
        },
        "consumer_projection": {
            "contract_version": consumer_projection.CONTRACT_VERSION,
            "schema_version": consumer_projection.SCHEMA_VERSION,
        },
        "ai_context": {
            "model_version": system_context_builder.SystemContextBuilder.MODEL_VERSION,
            "contract_version": ai_projection.CONTRACT_VERSION,
            "schema_version": ai_projection.SCHEMA_VERSION,
        },
        "hydration": {"model_version": hydration.MODEL_VERSION},
        "documentation_v52": {"contract_version": v52_config.CONTRACT_VERSION},
    }
