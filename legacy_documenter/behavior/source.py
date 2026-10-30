"""UI fact records of a view (post-V5 H4-R4, relocated by Gate B).

The control tree, code-behind facts and view-to-view invocations are discovered ONCE by the deterministic adapter
(`adapters/vbnet_webforms_oracle/ui_extraction.py`) and persisted as UI Evidence. This module only re-exports the neutral records the
explainer consumes; it parses nothing and never reads a file.
"""
from __future__ import annotations

from legacy_documenter.evidence.ui_model import CodeFacts, MarkupControl, NavHit

from .ui_evidence import PersistedMarkup

__all__ = ["CodeFacts", "MarkupControl", "NavHit", "PersistedMarkup"]
