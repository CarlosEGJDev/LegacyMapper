"""Deterministic JSON serialization for the V4-R12 Plugin-facing payload.

Every renderer in this module produces UTF-8 text with stable key ordering (`sort_keys=True`),
stable entry ordering (by `knowledge_id`), and stable nested-collection ordering (evidence refs
sorted by `evidence_id`, id lists sorted). No timestamp, UUID, runtime object identity, or
machine-specific path is ever written. Calling any renderer twice on equal input, in the same
process or a separate one, produces byte-identical output.

Canonical statement/metadata/provenance/evidence-identifier/relation-identifier content is
treated strictly as untrusted display/data text here: this module only ever places it inside a
JSON string value via `json.dumps`. It never evaluates, executes, dynamically imports, shell-
executes, template-executes, or deserializes any of it into an executable object, so
prompt-injection-shaped or HTML/Markdown-shaped canonical content always serializes as inert
JSON string data.
"""
import hashlib
import json

from legacy_documenter.knowledge.domain.models import EvidenceRef, Origin, Provenance
from legacy_documenter.knowledge.plugin_projection.models import (
    PluginKnowledgeEntry,
    PluginKnowledgeManifest,
    PluginKnowledgePayload,
)


def _origin_to_dict(origin: Origin | None) -> dict | None:
    """Renders an `Origin` structurally, or `None` when absent. Never invents an origin."""
    if origin is None:
        return None
    return {
        "kind": origin.kind,
        "reference": origin.reference,
        "contributor": origin.contributor,
        "captured_at": origin.captured_at,
    }


def _evidence_ref_to_dict(ref: EvidenceRef) -> dict:
    """Renders one `EvidenceRef` exactly as carried by the canonical entry, never resolved/expanded."""
    return {
        "evidence_id": ref.evidence_id,
        "source_type": ref.source_type.value,
        "origin": _origin_to_dict(ref.origin),
        "locator": ref.locator,
        "excerpt": ref.excerpt,
        "authoritative": ref.authoritative,
    }


def _provenance_to_dict(provenance: Provenance | None) -> dict | None:
    """Renders `Provenance` structurally when present; stays `None` when the canonical entry carries none."""
    if provenance is None:
        return None
    return {
        "origin": _origin_to_dict(provenance.origin),
        "material_ids": sorted(provenance.material_ids),
        "evidence_ids": sorted(provenance.evidence_ids),
        "contributor": provenance.contributor,
        "notes": provenance.notes,
    }


def entry_to_dict(entry: PluginKnowledgeEntry) -> dict:
    """Renders one `PluginKnowledgeEntry` as a plain, JSON-serializable, deterministically ordered dict."""
    return {
        "knowledge_id": entry.knowledge_id,
        "statement": entry.statement,
        "source_type": entry.source_type.value,
        "nature": entry.nature.value,
        "status": entry.status.value,
        "temporal_state": entry.temporal_state.value if entry.temporal_state is not None else None,
        "evidence_refs": [
            _evidence_ref_to_dict(ref) for ref in sorted(entry.evidence_refs, key=lambda r: r.evidence_id)
        ],
        "related_statement_ids": sorted(entry.related_statement_ids),
        "proposal_id": entry.proposal_id,
        "approval_decision_id": entry.approval_decision_id,
        "provenance": _provenance_to_dict(entry.provenance),
    }


def manifest_to_dict(manifest: PluginKnowledgeManifest) -> dict:
    """Renders a `PluginKnowledgeManifest` as a plain, JSON-serializable, deterministically ordered dict."""
    return {
        "canonical_entry_count": manifest.canonical_entry_count,
        "projected_entry_count": manifest.projected_entry_count,
        "knowledge_ids": sorted(manifest.knowledge_ids),
        "status_counts": dict(sorted(manifest.status_counts.items())),
        "source_type_counts": dict(sorted(manifest.source_type_counts.items())),
        "nature_counts": dict(sorted(manifest.nature_counts.items())),
        "temporal_state_counts": dict(sorted(manifest.temporal_state_counts.items())),
    }


def payload_to_dict(payload: PluginKnowledgePayload) -> dict:
    """Renders the full `PluginKnowledgePayload` as a plain, JSON-serializable, deterministically ordered dict."""
    return {
        "contract_name": payload.contract_name,
        "contract_version": payload.contract_version,
        "canonical_source": {
            "source_kind": payload.canonical_source.source_kind,
            "projection_kind": payload.canonical_source.projection_kind,
        },
        "entries": [entry_to_dict(entry) for entry in sorted(payload.entries, key=lambda e: e.knowledge_id)],
        "manifest": manifest_to_dict(payload.manifest),
    }


def render_payload_json(payload: PluginKnowledgePayload) -> str:
    """Renders `payload` as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(payload_to_dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_payload_fingerprint(payload: PluginKnowledgePayload) -> str:
    """Computes `payload_fingerprint = SHA256(canonical serialized payload content)`.

    Computed only from the already-serialized payload bytes (via `render_payload_json`); the
    fingerprint is never included inside the bytes it is computed from.
    """
    return hashlib.sha256(render_payload_json(payload).encode("utf-8")).hexdigest()


def render_payload_json_with_fingerprint(payload: PluginKnowledgePayload) -> str:
    """Renders `payload` as canonical JSON with an additional top-level `payload_fingerprint` key.

    The fingerprint is computed from the payload's own canonical serialization *without* the
    fingerprint key, then added as one extra key — it is never computed recursively over bytes
    that already include it.
    """
    data = payload_to_dict(payload)
    fingerprint = hashlib.sha256(
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    data_with_fingerprint = {**data, "payload_fingerprint": fingerprint}
    return json.dumps(data_with_fingerprint, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
