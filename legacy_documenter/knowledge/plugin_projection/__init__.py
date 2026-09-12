"""V4-R12 Plugin-Facing Machine-Readable Output Contract.

This package projects the R10 `CanonicalKnowledgeCollection` (and only that
collection) into a deterministic, versioned, machine-readable
`PluginKnowledgePayload` for future Plugin consumption. It never reads
`legacy_documenter.knowledge.projection` (R11), never parses R11 Markdown,
and never mutates the R10 canonical input. See `service.py` for the
projection entry point and `contract_report.py`/`example_report.py` for the
deterministic contract/example artifacts.
"""
