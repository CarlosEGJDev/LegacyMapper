"""ConsumerFacade: the stable, read-only entry point between Evidence/Core projections and consumers (V5.8).

    Evidence/Core -> existing projection (hydration, segmentation, AI projection, review store, documentation,
    consumer_projection) -> ConsumerFacade -> consumer

Every capability *calls* a projection that already exists; none re-implements budget, segmentation, grounding or
rendering. The facade only reads: it never writes, approves, canonicalizes, touches the cache, calls a provider
or loads code. Contract failures come back as `ConsumerResult(status="ERROR")`, never as a traceback.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.context.ai_projection import AiProjectionBuilder
from legacy_documenter.context.flow_segmentation import FlowSegmenter, SegmentationError, SegmentationPolicy
from legacy_documenter.context.hydration import EvidenceHydrator, UnknownFlowError
from legacy_documenter.review.models import ReviewError
from legacy_documenter.review.store import ReviewStore

from .contracts import (
    CAPABILITY_SPECS, CONTRACT_NAME, CONTRACT_VERSION, HUMAN_DOC_PROFILES, SCOPE_RUN, STATUS_ERROR, STATUS_OK,
    ConsumerCapability, ConsumerError, ConsumerErrorCode, ConsumerRequest, ConsumerResult, consumer_result_id,
    negotiate_contract_version, parse_capability, sha256_of, validate_request_against_spec,
)
from .registry import ConsumerRegistry, builtin_registry
from .sources import CONSUMER_PROJECTION_DIR, CONSUMER_PROJECTION_MANIFEST, DOCUMENTATION_DIR, HUMAN_DOC_MANIFEST, RunArtifacts, scrub

#: Consumer-facing profile -> directory under `documentation_v52/` (pinned against the shipped profiles by a test).
HUMAN_DOC_DIRECTORIES = {"human-functional": "general", "human-technical": "developer"}
DEFAULT_PAGE_LIMIT = 100
MAX_PAGE_LIMIT = 500
CANONICAL_LOOKUPS = ("canonical_id", "evidence_ref", "proposal_id")
DEFAULT_SEGMENT_CHARACTERS = 16000


@dataclass
class _Outcome:
    payload: object
    identities: list[str] = field(default_factory=list)
    partial: bool = False


def _page(items: list, request: ConsumerRequest) -> tuple[list, dict]:
    limit = request.options.get("limit", DEFAULT_PAGE_LIMIT)
    offset = request.options.get("offset", 0)
    if not 0 < limit <= MAX_PAGE_LIMIT:
        raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, f"limit_must_be_1_to_{MAX_PAGE_LIMIT}")
    return items[offset:offset + limit], {"total": len(items), "offset": offset, "limit": limit}


def _review_guard(call):
    """Runs a review-store read, mapping its failures to contractual codes (never a traceback)."""
    try:
        return call()
    except ReviewError as exc:
        raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, f"review:{exc.code.value}") from None
    except (OSError, ValueError, KeyError, TypeError):
        raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, "review_store_unreadable") from None


def _canonical_view(record) -> dict:
    data = record.to_dict()
    return {
        "canonical_id": data["canonical_id"], "source_proposal_id": data["source_proposal_id"], "decision_id": data["decision_id"],
        "decision_action": data["decision_action"], "content": data["content"], "evidence_refs": data["evidence_refs"],
        "scope": data["scope"], "partial": bool(data["scope"].get("partial")), "provenance": data["provenance"],
        "created_at": data["created_at"], "version": data["version"], "status": data["status"], "supersedes": data["supersedes"],
        "corrected_from": data["corrected_from"],
    }


class ConsumerFacade:
    """Serves `ConsumerRequest`s against one run directory. Instance-scoped caches; no global state."""

    def __init__(self, run_dir: str | Path, registry: ConsumerRegistry | None = None) -> None:
        self.run_dir = Path(run_dir)
        self.registry = registry if registry is not None else builtin_registry()
        self._artifacts = RunArtifacts(self.run_dir)
        self._hydrator = EvidenceHydrator()
        self._store = ReviewStore(self.run_dir)
        self._doc_entries: dict[str, list[dict]] = {}
        self._handlers = {
            ConsumerCapability.READ_EVIDENCE: self._read_evidence, ConsumerCapability.READ_FLOW: self._read_flow,
            ConsumerCapability.READ_PARTIAL_FLOW: self._read_partial_flow, ConsumerCapability.READ_AI_CONTEXT: self._read_ai_context,
            ConsumerCapability.READ_CANONICAL: self._read_canonical, ConsumerCapability.READ_REVIEW_HISTORY: self._read_review_history,
            ConsumerCapability.RENDER_HUMAN_DOC: self._render_human_doc, ConsumerCapability.EXPORT_JSON: self._export_json,
        }

    # -- entry point ------------------------------------------------------------------------------
    def handle(self, request: ConsumerRequest | dict) -> ConsumerResult:
        """Validates and serves one request. Never raises for contract failures; fails closed."""
        raw = request if isinstance(request, dict) else {}
        try:
            parsed = request if isinstance(request, ConsumerRequest) else ConsumerRequest.from_dict(request)
        except ConsumerError as exc:
            return self._error(None, raw, exc)
        try:
            resolved = negotiate_contract_version(parsed.contract_version)
            descriptor = self.registry.get(parsed.consumer_id)
            if negotiate_contract_version(descriptor.contract_version) != resolved:
                raise ConsumerError(ConsumerErrorCode.UNSUPPORTED_CONTRACT_VERSION, "descriptor_contract_mismatch")
            capability = parse_capability(parsed.capability)
            if capability not in descriptor.capabilities_required:
                raise ConsumerError(ConsumerErrorCode.UNSUPPORTED_CAPABILITY, "capability_not_granted_to_consumer")
            validate_request_against_spec(parsed, CAPABILITY_SPECS[capability])
            outcome = self._handlers[capability](parsed)
        except ConsumerError as exc:
            return self._error(parsed, raw, exc)
        except Exception as exc:  # noqa: BLE001 - contract boundary: only the class name leaves, never text or traceback
            return self._error(parsed, raw, ConsumerError(ConsumerErrorCode.INTERNAL_ERROR, type(exc).__name__))
        return self._ok(parsed, resolved, outcome)

    def _ok(self, request: ConsumerRequest, version: str, outcome: _Outcome) -> ConsumerResult:
        identities = sorted(outcome.identities)
        provenance = {
            "contract_name": CONTRACT_NAME, "contract_version": version, "read_only": True, "provider_calls": 0,
            "partial": outcome.partial, "completeness": "PARTIAL" if outcome.partial else "COMPLETE", "source_identities": identities,
        }
        result_id = consumer_result_id(version, request.identity_parts(), identities, None)
        return ConsumerResult(request.consumer_id, version, request.capability, STATUS_OK, outcome.payload, provenance, result_id)

    @staticmethod
    def _error(request: ConsumerRequest | None, raw: dict, exc: ConsumerError) -> ConsumerResult:
        def text(key: str, parsed_value: str | None) -> str:
            value = parsed_value if parsed_value is not None else raw.get(key)
            return value if isinstance(value, str) and 0 < len(value) <= 300 else "UNKNOWN"

        consumer_id = text("consumer_id", request.consumer_id if request else None)
        capability = text("capability", request.capability if request else None)
        parts = request.identity_parts() if request else {"consumer_id": consumer_id, "capability": capability}
        provenance = {"contract_name": CONTRACT_NAME, "contract_version": CONTRACT_VERSION, "read_only": True, "provider_calls": 0,
                      "partial": False, "completeness": "NOT_APPLICABLE", "source_identities": []}
        error = {"code": exc.code.value, "detail": exc.detail}
        return ConsumerResult(consumer_id, CONTRACT_VERSION, capability, STATUS_ERROR, None, provenance,
                              consumer_result_id(CONTRACT_VERSION, parts, [], exc.code.value), error)

    # -- evidence / flows -------------------------------------------------------------------------
    def _read_evidence(self, request: ConsumerRequest) -> _Outcome:
        lookup = self._artifacts.evidence()
        missing = [ref for ref in request.entity_ids if ref not in lookup]
        if missing:
            raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, ",".join(missing[:5]))
        items, identities = [], []
        for ref in request.entity_ids:
            for kind, record in sorted(lookup[ref], key=lambda pair: pair[0]):
                clean = scrub(record)
                digest = sha256_of(clean)
                items.append({"ref": ref, "kind": kind, "record": clean, "record_fingerprint": digest})
                identities.append(f"EVIDENCE:{kind}:{ref}:{digest}")
        return _Outcome({"evidence": items}, identities)

    def _hydrate(self, flow_id: str) -> dict:
        try:
            return self._hydrator.hydrate_flow(flow_id, self._artifacts.ix())
        except UnknownFlowError:
            raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, flow_id) from None

    def _read_flow(self, request: ConsumerRequest) -> _Outcome:
        flows, identities = [], []
        for flow_id in request.entity_ids:
            record = scrub(self._hydrate(flow_id))
            record.update(partial=False, completeness="COMPLETE")
            flows.append(record)
            identities.append(f"FLOW:{flow_id}:{sha256_of(record)}")
        return _Outcome({"flows": flows}, identities)

    def _read_partial_flow(self, request: ConsumerRequest) -> _Outcome:
        try:
            policy = SegmentationPolicy(max_characters=request.options.get("max_characters", DEFAULT_SEGMENT_CHARACTERS))
        except SegmentationError:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "max_characters_must_be_positive") from None
        wanted = request.options.get("segment_id")
        flows, identities = [], []
        for flow_id in request.entity_ids:
            parent = self._hydrate(flow_id)
            try:
                segments = FlowSegmenter().segment(parent, policy)
            except SegmentationError as exc:
                raise ConsumerError(ConsumerErrorCode.PARTIAL_NOT_SUPPORTED, f"{exc.code}:{flow_id}") from None
            if not segments:
                raise ConsumerError(ConsumerErrorCode.PARTIAL_NOT_SUPPORTED, f"flow_fits_budget:{flow_id}")
            if wanted is not None:
                segments = [s for s in segments if s["segment_id"] == wanted]
                if not segments:
                    raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, f"segment:{wanted}")
            views = []
            for segment in segments:
                views.append({
                    "segment_id": segment["segment_id"], "ordinal": segment["ordinal"], "partial": True, "completeness": "PARTIAL",
                    "parent_flow_id": segment["parent_flow_id"], "included_paths": segment["included_paths"],
                    "omitted_paths": segment["omitted_paths"], "evidence_refs": segment["evidence_refs"], "record": scrub(segment),
                })
                identities.append(f"SEGMENT:{segment['segment_id']}")
            flows.append({"parent_flow_id": flow_id, "partial": True, "segmentation_policy_id": policy.identity, "segments": views})
        return _Outcome({"flows": flows}, identities, partial=True)

    def _read_ai_context(self, request: ConsumerRequest) -> _Outcome:
        try:
            package = AiProjectionBuilder(hydrator=self._hydrator).build(
                list(request.entity_ids), self._artifacts.ix(), profile=request.profile or "SMALL")
        except UnknownFlowError as exc:
            raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, str(exc)) from None
        except ValueError:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "ai_projection_rejected") from None
        truncated = bool((package.get("truncation") or {}).get("truncated"))
        return _Outcome({"package": scrub(package)}, [f"AI_PROJECTION:{package['package_id']}"], partial=truncated)

    # -- canonical / review -----------------------------------------------------------------------
    def _read_canonical(self, request: ConsumerRequest) -> _Outcome:
        lookup = request.options.get("by", "canonical_id")
        if lookup not in CANONICAL_LOOKUPS:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "by_must_be_canonical_id_evidence_ref_or_proposal_id")
        records = _review_guard(self._store.canonical_records)
        if not records:
            raise ConsumerError(ConsumerErrorCode.CANONICAL_NOT_AVAILABLE, "no_canonical_knowledge_in_run")
        meta: dict | None = None
        if request.scope == SCOPE_RUN:
            selected, meta = _page(records, request)
        else:
            attribute = {"canonical_id": lambda r, v: r.canonical_id == v, "evidence_ref": lambda r, v: v in r.evidence_refs,
                         "proposal_id": lambda r, v: r.source_proposal_id == v}[lookup]
            selected, missing = [], []
            for value in request.entity_ids:
                found = [r for r in records if attribute(r, value)]
                (selected.extend(found) if found else missing.append(value))
            if missing:
                raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, ",".join(missing[:5]))
            selected = sorted({r.canonical_id: r for r in selected}.values(), key=lambda r: r.canonical_id)
        views = [_canonical_view(r) for r in selected]
        payload = {"canonical": scrub(views)}
        if meta:
            payload["page"] = meta
        return _Outcome(payload, [f"CANONICAL:{v['canonical_id']}" for v in views], partial=any(v["partial"] for v in views))

    def _read_review_history(self, request: ConsumerRequest) -> _Outcome:
        store, audit = self._store, request.options.get("include_audit_chain", False)
        decisions = _review_guard(store.decisions)  # loaded once: per-proposal views are built from memory, never by rescanning
        known = sorted({d.proposal_id for d in decisions})
        meta: dict | None = None
        if request.scope == SCOPE_RUN:
            proposal_ids, meta = _page(known, request)
        else:
            missing = [p for p in request.entity_ids if p not in known]
            if missing:
                raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, ",".join(missing[:5]))
            proposal_ids = list(request.entity_ids)
        baselines = _review_guard(store.baselines)
        canonical = _review_guard(store.canonical_records) if audit else []
        history, identities, partial = [], [], False
        for proposal_id in proposal_ids:
            chain = _review_guard(lambda p=proposal_id: store.chain_of(decisions, p))
            snapshot = _review_guard(lambda p=proposal_id: store.snapshot_for(p))
            own_baselines = [b for b in baselines if b.proposal_id == proposal_id]
            entry = {
                "proposal_id": proposal_id, "decisions": [d.to_dict() for d in chain], "baselines": [b.to_dict() for b in own_baselines],
                "proposal_snapshot": snapshot.to_dict() if snapshot else None,
            }
            if audit:
                own_canonical = [r for r in canonical if r.source_proposal_id == proposal_id]
                entry["audit_chain"] = [
                    self._audit_view(_review_guard(lambda d=d: store.verify_audit_chain(d, snapshot, own_baselines, own_canonical))) for d in chain]
            partial = partial or any(bool(d.scope.get("partial")) for d in chain)
            identities.extend(f"DECISION:{d.decision_id}" for d in chain)
            history.append(entry)
        payload = {"history": scrub(history)}
        if meta:
            payload["page"] = meta
        return _Outcome(payload, identities, partial=partial)

    @staticmethod
    def _audit_view(chain: dict) -> dict:
        canonical = chain["canonical"]
        return {
            "decision_id": chain["decision"].decision_id, "proposal_snapshot_id": chain["proposal_snapshot"].proposal_id,
            "baseline_id": chain["baseline"].baseline_id, "canonical_id": canonical.canonical_id if canonical else None,
            "evidence_fingerprint": chain["evidence_fingerprint"], "links_verified": True,
        }

    # -- human documentation / export -------------------------------------------------------------
    def _doc_manifest_entries(self, profile: str) -> list[dict]:
        if profile not in self._doc_entries:
            manifest = self._artifacts.read_json(HUMAN_DOC_MANIFEST)
            files = manifest.get("files") if isinstance(manifest, dict) else None
            if not isinstance(files, list):
                raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, "documentation_manifest_invalid")
            prefix = HUMAN_DOC_DIRECTORIES[profile] + "/"
            self._doc_entries[profile] = sorted((e for e in files if str(e.get("path", "")).startswith(prefix)), key=lambda e: e["path"])
        return self._doc_entries[profile]

    def _render_human_doc(self, request: ConsumerRequest) -> _Outcome:
        profile = request.profile
        if profile not in HUMAN_DOC_PROFILES:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "profile_required")
        entries = self._doc_manifest_entries(profile)
        if not entries:
            raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, f"no_documents_for_profile:{profile}")
        directory = HUMAN_DOC_DIRECTORIES[profile]
        if request.scope == SCOPE_RUN:
            page, meta = _page(entries, request)
            index_path = f"{directory}/README.md"
            index_entry = next((e for e in entries if e["path"] == index_path), None)
            payload = {"profile": profile, "document_count": len(entries), "documents": [
                {"path": e["path"], "sha256": e["sha256"], "size_bytes": e["size_bytes"]} for e in page], "page": meta,
                "index_document": self._read_document(index_entry) if index_entry else None}
            return _Outcome(payload, [f"HUMAN_DOC_INDEX:{profile}:{sha256_of(page)}"])
        by_path = {e["path"]: e for e in entries}
        missing = [p for p in request.entity_ids if p not in by_path]
        if missing:
            raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, ",".join(missing[:5]))
        documents = [self._read_document(by_path[p]) for p in request.entity_ids]
        return _Outcome({"profile": profile, "documents": documents}, [f"HUMAN_DOC:{d['path']}:{d['sha256']}" for d in documents])

    def _read_document(self, entry: dict) -> dict:
        """Reads one manifest-listed document (never a caller-built path) and verifies it against its manifest hash."""
        try:
            data = (self.run_dir / DOCUMENTATION_DIR / entry["path"]).read_bytes()
        except OSError:
            raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, f"document_unreadable:{entry['path']}") from None
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, f"document_hash_mismatch:{entry['path']}")
        return {"path": entry["path"], "sha256": entry["sha256"], "size_bytes": entry["size_bytes"], "content": scrub(data.decode("utf-8"))}

    def _export_json(self, request: ConsumerRequest) -> _Outcome:
        manifest = self._artifacts.read_json(CONSUMER_PROJECTION_MANIFEST)
        if not isinstance(manifest, dict) or not isinstance(manifest.get("partitions"), list):
            raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, "consumer_projection_manifest_invalid")
        if request.scope == SCOPE_RUN:
            return _Outcome({"manifest": scrub(manifest)}, [f"CONSUMER_PROJECTION:{manifest.get('package_id')}"])
        entries = {e["relative_path"]: e for e in manifest["partitions"]}
        missing = [p for p in request.entity_ids if p not in entries]
        if missing:
            raise ConsumerError(ConsumerErrorCode.ENTITY_NOT_FOUND, ",".join(missing[:5]))
        bodies, identities = [], []
        for relative in request.entity_ids:
            body = self._artifacts.read_json(CONSUMER_PROJECTION_DIR / relative)
            if not isinstance(body, dict) or body.get("partition_id") != entries[relative]["partition_id"]:
                raise ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, f"partition_id_mismatch:{relative}")
            bodies.append(scrub(body))
            identities.append(f"CONSUMER_PARTITION:{body['partition_id']}")
        return _Outcome({"partitions": bodies}, identities)
