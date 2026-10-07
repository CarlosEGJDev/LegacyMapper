"""One composed adapter: technology and database parsing share source context."""
from pathlib import Path

from legacy_documenter.adapters.contracts import AdapterCapabilities
from .normalization import NormalizedEvidenceBuilder, REFERENCE_ADAPTER_ID, REFERENCE_ADAPTER_VERSION
from . import extraction
from .analysis.call_resolver import CallResolver
from .analysis.database_resolver import DatabaseResolver
from .analysis.dependency_resolver import DependencyResolver
from .analysis.web_entry_resolver import WebEntryResolver
from .analysis.flow_resolver import FunctionalFlowResolver


class ReferenceAdapter:
    descriptor = AdapterCapabilities(
        REFERENCE_ADAPTER_ID, REFERENCE_ADAPTER_VERSION,
        frozenset({'solution', 'vb_project', 'vb_source', 'aspx', 'ascx', 'master', 'web_config'}),
        frozenset({'extraction', 'calls', 'entries', 'dependencies', 'database', 'normalized_evidence'}),
    )

    def normalize(self, indexes: dict, repo_root: Path | None = None):
        return NormalizedEvidenceBuilder(repo_root=repo_root,
                                         adapter_id=self.descriptor.adapter_id,
                                         adapter_version=self.descriptor.adapter_version).build(indexes)

    def extract(self, files, root, extraction_cache=None):
        return extraction.extract_repository(files, root, extraction_cache)

    def resolve_calls(self, calls, symbols):
        return CallResolver().resolve(calls, symbols)

    def resolve_entries(self, webforms, symbols, events, calls):
        return WebEntryResolver().resolve(webforms, symbols, events, calls)

    def resolve_database(self, indexes, projects):
        return DatabaseResolver().resolve(indexes, projects)

    def resolve_dependencies(self, solutions, projects, symbols, webforms):
        return [dep.to_dict() for dep in DependencyResolver().resolve(solutions, projects, symbols, webforms)]

    def resolve_legacy_flows(self, max_depth, *inputs):
        # Legacy graph labels/projection are technology-specific; no neutral
        # core consumer needs to parse them. Preserve their approved IDs.
        return FunctionalFlowResolver(max_depth).resolve(*inputs)
