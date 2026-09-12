"""V4-R11 Human-Readable Document Projection package.

Projects the R10 Canonical Knowledge Source (`CanonicalKnowledgeCollection`) into
deterministic, human-readable Markdown documents. This package never mutates canonical
knowledge, never implements AI/provider-based mapping, and never implements any R12
Plugin-facing payload or schema.
"""
from legacy_documenter.knowledge.projection.markdown_renderer import EMPTY_DOCUMENT_MARKER, render_document, render_documents
from legacy_documenter.knowledge.projection.models import (
    DocumentProjection,
    ProjectionManifest,
    ProjectionPathError,
    ProjectionRule,
    ProjectionTarget,
    validate_target_path,
)
from legacy_documenter.knowledge.projection.rules import ALL_TARGETS, DEFAULT_RULES, PROJECTION_CATEGORIES
from legacy_documenter.knowledge.projection.service import ProjectionResult, ProjectionService

__all__ = [
    "ALL_TARGETS",
    "DEFAULT_RULES",
    "PROJECTION_CATEGORIES",
    "DocumentProjection",
    "EMPTY_DOCUMENT_MARKER",
    "ProjectionManifest",
    "ProjectionPathError",
    "ProjectionResult",
    "ProjectionRule",
    "ProjectionService",
    "ProjectionTarget",
    "render_document",
    "render_documents",
    "validate_target_path",
]
