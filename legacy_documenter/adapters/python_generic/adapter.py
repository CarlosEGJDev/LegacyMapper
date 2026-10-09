"""python-generic: one composed adapter (extraction, resolution, flows, normalization) for Python source trees."""
from pathlib import Path

from legacy_documenter.adapters.contracts import AdapterCapabilities

from . import analysis, extraction, resolution
from .normalization import ADAPTER_ID, ADAPTER_VERSION, PythonEvidenceBuilder


class PythonGenericAdapter:
    descriptor = AdapterCapabilities(
        ADAPTER_ID, ADAPTER_VERSION, frozenset({"python_source"}),
        frozenset({"extraction", "calls", "entries", "dependencies", "file_operations", "normalized_evidence"}),
        documentation_terminology="python-generic",
    )

    def normalize(self, indexes: dict, repo_root: Path | None = None):
        return PythonEvidenceBuilder(repo_root=repo_root, adapter_id=self.descriptor.adapter_id,
                                     adapter_version=self.descriptor.adapter_version).build(indexes)

    def extract(self, files, root, extraction_cache=None):
        return extraction.extract_repository(files, root, extraction_cache)

    def resolve_calls(self, calls, symbols):
        return resolution.resolve_calls(calls, symbols)

    def resolve_entries(self, webforms, symbols, events, calls):
        return resolution.resolve_entries(calls, symbols, events, calls)

    def resolve_database(self, indexes, projects):
        return analysis.resolve_database(indexes, projects)

    def resolve_dependencies(self, solutions, projects, symbols, webforms):
        return analysis.resolve_dependencies(projects)

    def resolve_legacy_flows(self, max_depth, *inputs):
        return analysis.PythonFlowResolver(max_depth).resolve(*inputs)
