"""Consumer Contract 1.0 (V5.8): descriptors, capabilities, requests, results and the closed error model.

A consumer asks for a *capability* and receives a versioned, read-only `ConsumerResult`; it never navigates
internal indexes, adapters or providers. This module is data only: standard library, no I/O, no imports of
concrete technologies or providers. Nothing here loads or executes code (`Plugin Contract != Plugin Runtime`).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

CONTRACT_NAME = "LegacyMapperConsumerContract"
CONTRACT_VERSION = "1.0"
SUPPORTED_CONTRACT_VERSIONS = ("1.0",)
RESULT_SCHEMA = "CONSUMER_RESULT"

MAX_TEXT_CHARS = 300
MAX_OPTION_COUNT = 8
SCOPE_RUN = "RUN"
SCOPE_ENTITIES = "ENTITIES"
STATUS_OK = "OK"
STATUS_ERROR = "ERROR"

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_VERSION_RE = re.compile(r"^(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,3})$")
_OPTION_KEY_RE = re.compile(r"^[a-z][a-z_]{0,31}$")
#: A capability whose name starts like this asks to change something; the contract is read-only (V5.8 section 16).
WRITE_CAPABILITY_PREFIXES = (
    "WRITE_", "MUTATE_", "APPROVE", "REJECT_", "CORRECT_", "DEFER_", "DECIDE", "CREATE_", "DELETE_", "MODIFY_", "UPDATE_",
    "INVOKE_", "CALL_", "EXECUTE", "INSTALL", "UNINSTALL", "PERSIST_", "CANONICALIZE",
)


class ConsumerCapability(str, Enum):
    """Explicit, read-only capabilities. A consumer sees only what it declares and is granted."""

    READ_EVIDENCE = "READ_EVIDENCE"
    READ_FLOW = "READ_FLOW"
    READ_PARTIAL_FLOW = "READ_PARTIAL_FLOW"
    READ_AI_CONTEXT = "READ_AI_CONTEXT"
    READ_CANONICAL = "READ_CANONICAL"
    READ_REVIEW_HISTORY = "READ_REVIEW_HISTORY"
    RENDER_HUMAN_DOC = "RENDER_HUMAN_DOC"
    EXPORT_JSON = "EXPORT_JSON"


class ConsumerErrorCode(str, Enum):
    """Closed, fail-closed error vocabulary of the consumer and plugin contracts."""

    UNKNOWN_CONSUMER = "UNKNOWN_CONSUMER"
    UNSUPPORTED_CONTRACT_VERSION = "UNSUPPORTED_CONTRACT_VERSION"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    INVALID_SCOPE = "INVALID_SCOPE"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    PARTIAL_NOT_SUPPORTED = "PARTIAL_NOT_SUPPORTED"
    CANONICAL_NOT_AVAILABLE = "CANONICAL_NOT_AVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_DESCRIPTOR = "INVALID_DESCRIPTOR"
    READ_ONLY_VIOLATION = "READ_ONLY_VIOLATION"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PLUGIN_MANIFEST_INVALID = "PLUGIN_MANIFEST_INVALID"
    PLUGIN_INCOMPATIBLE = "PLUGIN_INCOMPATIBLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ConsumerError(Exception):
    """Contractual failure: a stable `code` plus a short closed `detail`, never a traceback or source text."""

    def __init__(self, code: ConsumerErrorCode, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}" if detail else code.value)


@dataclass(frozen=True)
class CapabilitySpec:
    """What one capability accepts and returns; the single source for request validation and descriptor kinds."""

    capability: ConsumerCapability
    input_kinds: tuple[str, ...]
    output_kinds: tuple[str, ...]
    scopes: tuple[str, ...]
    max_entities: int
    profiles: tuple[str, ...] = ()
    options: Mapping[str, type] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", dict(self.options or {}))


HUMAN_DOC_PROFILES = ("human-functional", "human-technical")
AI_PROFILES = ("TINY", "SMALL", "MEDIUM", "LARGE")
_PAGING = {"limit": int, "offset": int}
CAPABILITY_SPECS: Mapping[ConsumerCapability, CapabilitySpec] = {
    spec.capability: spec for spec in (
        CapabilitySpec(ConsumerCapability.READ_EVIDENCE, ("EVIDENCE_REF",), ("EVIDENCE_RECORD",), (SCOPE_ENTITIES,), 200),
        CapabilitySpec(ConsumerCapability.READ_FLOW, ("FLOW_ID",), ("FLOW_RECORD",), (SCOPE_ENTITIES,), 50),
        CapabilitySpec(ConsumerCapability.READ_PARTIAL_FLOW, ("FLOW_ID",), ("PARTIAL_FLOW_SEGMENT",), (SCOPE_ENTITIES,), 10,
                       options={"max_characters": int, "segment_id": str}),
        CapabilitySpec(ConsumerCapability.READ_AI_CONTEXT, ("FLOW_ID",), ("AI_PROJECTION",), (SCOPE_ENTITIES,), 50, AI_PROFILES),
        CapabilitySpec(ConsumerCapability.READ_CANONICAL, ("CANONICAL_ID", "EVIDENCE_REF", "PROPOSAL_ID"), ("CANONICAL_RECORD",),
                       (SCOPE_RUN, SCOPE_ENTITIES), 200, options={"by": str, **_PAGING}),
        CapabilitySpec(ConsumerCapability.READ_REVIEW_HISTORY, ("PROPOSAL_ID",), ("REVIEW_HISTORY",), (SCOPE_RUN, SCOPE_ENTITIES), 200,
                       options={"include_audit_chain": bool, **_PAGING}),
        CapabilitySpec(ConsumerCapability.RENDER_HUMAN_DOC, ("DOC_PROFILE", "DOCUMENT_PATH"), ("HUMAN_DOCUMENT_INDEX", "HUMAN_DOCUMENT"),
                       (SCOPE_RUN, SCOPE_ENTITIES), 20, HUMAN_DOC_PROFILES, _PAGING),
        CapabilitySpec(ConsumerCapability.EXPORT_JSON, ("PARTITION_PATH",), ("CONSUMER_PROJECTION",), (SCOPE_RUN, SCOPE_ENTITIES), 10),
    )
}
KNOWN_INPUT_KINDS = frozenset(k for s in CAPABILITY_SPECS.values() for k in s.input_kinds)
KNOWN_OUTPUT_KINDS = frozenset(k for s in CAPABILITY_SPECS.values() for k in s.output_kinds)


def canonical_json(value: object) -> str:
    """Deterministic JSON used for every identity."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_of(value: object) -> str:
    """SHA-256 hex digest of the canonical JSON of `value`."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def is_write_capability_name(name: str) -> bool:
    """True when `name` reads as a mutation (approve, write, invoke a provider, execute...)."""
    return isinstance(name, str) and name.upper().startswith(WRITE_CAPABILITY_PREFIXES)


def parse_capability(name: object) -> ConsumerCapability:
    """Known read capability, or READ_ONLY_VIOLATION (write-like name) / UNSUPPORTED_CAPABILITY. Never a fallback."""
    if isinstance(name, ConsumerCapability):
        return name
    if not isinstance(name, str) or not name:
        raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "capability_must_be_text")
    if is_write_capability_name(name):
        raise ConsumerError(ConsumerErrorCode.READ_ONLY_VIOLATION, "write_capability_not_available")
    try:
        return ConsumerCapability(name)
    except ValueError:
        raise ConsumerError(ConsumerErrorCode.UNSUPPORTED_CAPABILITY, "unknown_capability") from None


def parse_version(value: object, code: ConsumerErrorCode = ConsumerErrorCode.INVALID_REQUEST) -> tuple[int, int]:
    """`major.minor` -> ints; anything else fails closed with `code`."""
    if not isinstance(value, str) or not _VERSION_RE.match(value):
        raise ConsumerError(code, "version_must_be_major_dot_minor")
    major, minor = value.split(".")
    return int(major), int(minor)


def negotiate_contract_version(requested: object, supported: tuple[str, ...] = SUPPORTED_CONTRACT_VERSIONS) -> str:
    """Highest supported version of the requested *major*; minors are additive. A different major fails closed."""
    major, _ = parse_version(requested)
    same_major = [v for v in supported if parse_version(v)[0] == major]
    if not same_major:
        raise ConsumerError(ConsumerErrorCode.UNSUPPORTED_CONTRACT_VERSION, f"supported:{','.join(supported)}")
    return max(same_major, key=parse_version)


def _text(value: object, field: str, code: ConsumerErrorCode, pattern: re.Pattern | None = None) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_CHARS or (pattern and not pattern.match(value)):
        raise ConsumerError(code, f"{field}_invalid")
    return value


def _string_list(value: object, field: str, code: ConsumerErrorCode, *, allow_empty: bool, limit: int) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or (not value and not allow_empty) or len(value) > limit:
        raise ConsumerError(code, f"{field}_invalid")
    items = tuple(_text(item, field, code) for item in value)
    if len(set(items)) != len(items):
        raise ConsumerError(code, f"{field}_duplicates")
    return tuple(sorted(items))


def _kinds(value: object, field: str, known: frozenset[str]) -> tuple[str, ...]:
    kinds = _string_list(value, field, ConsumerErrorCode.INVALID_DESCRIPTOR, allow_empty=False, limit=32)
    if not set(kinds) <= known:
        raise ConsumerError(ConsumerErrorCode.INVALID_DESCRIPTOR, f"{field}_unknown_kind")
    return kinds


def capability_names(value: object, field: str, code: ConsumerErrorCode, *, allow_empty: bool) -> tuple[ConsumerCapability, ...]:
    """Parses a list of capability names; write-like -> READ_ONLY_VIOLATION, unknown -> UNSUPPORTED_CAPABILITY."""
    names = _string_list(value, field, code, allow_empty=allow_empty, limit=32)
    return tuple(parse_capability(n) for n in names)


@dataclass(frozen=True)
class ConsumerDescriptor:
    """Declares one consumer: identity, versions, the read capabilities it may request, kinds, and `read_only`."""

    consumer_id: str
    consumer_version: str
    contract_version: str
    capabilities_required: tuple[ConsumerCapability, ...]
    input_kinds: tuple[str, ...]
    output_kinds: tuple[str, ...]
    read_only: bool = True

    _KEYS = frozenset({"consumer_id", "consumer_version", "contract_version", "capabilities_required", "input_kinds", "output_kinds", "read_only"})

    @classmethod
    def from_dict(cls, data: object) -> "ConsumerDescriptor":
        """Strict validation; any unknown key, bad type, write capability or `read_only != true` fails closed."""
        bad = ConsumerErrorCode.INVALID_DESCRIPTOR
        if not isinstance(data, dict) or set(data) != cls._KEYS:
            raise ConsumerError(bad, "descriptor_keys_mismatch")
        if data["read_only"] is not True:
            raise ConsumerError(ConsumerErrorCode.READ_ONLY_VIOLATION, "descriptor_must_be_read_only")
        consumer_version = data["consumer_version"]
        _text(consumer_version, "consumer_version", bad)
        parse_version(data["contract_version"], bad)
        return cls(
            consumer_id=_text(data["consumer_id"], "consumer_id", bad, _ID_RE), consumer_version=consumer_version,
            contract_version=data["contract_version"],
            capabilities_required=tuple(sorted(capability_names(data["capabilities_required"], "capabilities_required", bad, allow_empty=False))),
            input_kinds=_kinds(data["input_kinds"], "input_kinds", KNOWN_INPUT_KINDS),
            output_kinds=_kinds(data["output_kinds"], "output_kinds", KNOWN_OUTPUT_KINDS), read_only=True,
        )

    def to_dict(self) -> dict:
        """Stable JSON shape."""
        return {
            "consumer_id": self.consumer_id, "consumer_version": self.consumer_version, "contract_version": self.contract_version,
            "capabilities_required": [c.value for c in self.capabilities_required], "input_kinds": list(self.input_kinds),
            "output_kinds": list(self.output_kinds), "read_only": self.read_only,
        }


@dataclass(frozen=True)
class ConsumerRequest:
    """A request for one capability: identity, scope, entity ids, profile and bounded primitive options. Never code."""

    consumer_id: str
    contract_version: str
    capability: str
    scope: str
    entity_ids: tuple[str, ...] = ()
    profile: str | None = None
    options: Mapping[str, object] = None  # type: ignore[assignment]

    _KEYS = frozenset({"consumer_id", "contract_version", "capability", "scope", "entity_ids", "profile", "options"})
    _REQUIRED = frozenset({"consumer_id", "contract_version", "capability", "scope"})

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", dict(self.options or {}))

    @classmethod
    def from_dict(cls, data: object) -> "ConsumerRequest":
        """Structural validation only (shape, primitive types, bounds); semantics are checked against the capability."""
        bad = ConsumerErrorCode.INVALID_REQUEST
        if not isinstance(data, dict) or not cls._REQUIRED <= set(data) <= cls._KEYS:
            raise ConsumerError(bad, "request_keys_mismatch")
        options = data.get("options") or {}
        if not isinstance(options, dict) or len(options) > MAX_OPTION_COUNT:
            raise ConsumerError(bad, "options_invalid")
        for key, value in options.items():
            if not isinstance(key, str) or not _OPTION_KEY_RE.match(key) or not (
                    isinstance(value, (bool, int)) or (isinstance(value, str) and 0 < len(value) <= MAX_TEXT_CHARS)):
                raise ConsumerError(bad, "option_not_a_bounded_primitive")
        profile = data.get("profile")
        if profile is not None:
            _text(profile, "profile", bad)
        return cls(
            consumer_id=_text(data["consumer_id"], "consumer_id", bad), contract_version=_text(data["contract_version"], "contract_version", bad),
            capability=_text(data["capability"], "capability", bad), scope=_text(data["scope"], "scope", bad),
            entity_ids=_string_list(data.get("entity_ids", []), "entity_ids", bad, allow_empty=True, limit=200)
            if "entity_ids" in data else (), profile=profile, options=options,
        )

    def identity_parts(self) -> dict:
        """The request part of a result identity."""
        return {
            "consumer_id": self.consumer_id, "capability": self.capability, "scope": self.scope, "entity_ids": list(self.entity_ids),
            "profile": self.profile, "options": dict(sorted(self.options.items())),
        }


def validate_request_against_spec(request: ConsumerRequest, spec: CapabilitySpec) -> None:
    """Scope, entity count, profile and options must fit the capability exactly (INVALID_SCOPE / INVALID_REQUEST)."""
    if request.scope not in spec.scopes:
        raise ConsumerError(ConsumerErrorCode.INVALID_SCOPE, f"scope_not_allowed_for_{spec.capability.value}")
    if request.scope == SCOPE_ENTITIES and not request.entity_ids:
        raise ConsumerError(ConsumerErrorCode.INVALID_SCOPE, "entities_scope_requires_entity_ids")
    if request.scope == SCOPE_RUN and request.entity_ids:
        raise ConsumerError(ConsumerErrorCode.INVALID_SCOPE, "run_scope_takes_no_entity_ids")
    if len(request.entity_ids) > spec.max_entities:
        raise ConsumerError(ConsumerErrorCode.INVALID_SCOPE, f"too_many_entity_ids_max_{spec.max_entities}")
    if spec.profiles and request.profile is None and spec.capability is ConsumerCapability.RENDER_HUMAN_DOC:
        raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "profile_required")
    if request.profile is not None and request.profile not in spec.profiles:
        raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, "profile_not_allowed_for_capability")
    for key, value in request.options.items():
        expected = spec.options.get(key)
        if expected is None or type(value) is not expected:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, f"option_not_allowed:{key}")
        if expected is int and value < 0:
            raise ConsumerError(ConsumerErrorCode.INVALID_REQUEST, f"option_must_not_be_negative:{key}")


def consumer_result_id(contract_version: str, request_parts: dict, source_identities: list[str], error_code: str | None) -> str:
    """`CRES-sha256(contract + consumer + capability + scope + source identities)`; no time, random or provider data."""
    return "CRES-" + sha256_of([CONTRACT_NAME, contract_version, request_parts, sorted(source_identities), error_code])


@dataclass(frozen=True)
class ConsumerResult:
    """Versioned outcome of one request: `OK` with payload + provenance, or `ERROR` with a contractual code."""

    consumer_id: str
    contract_version: str
    capability: str
    status: str
    payload: object
    provenance: dict
    result_id: str
    error: dict | None = None

    def to_dict(self) -> dict:
        """Stable JSON shape (schema CONSUMER_RESULT)."""
        return {
            "schema": RESULT_SCHEMA, "contract_name": CONTRACT_NAME, "contract_version": self.contract_version,
            "result_id": self.result_id, "consumer_id": self.consumer_id, "capability": self.capability, "status": self.status,
            "payload": self.payload, "provenance": self.provenance, "error": self.error,
        }

    def to_json(self) -> str:
        """Deterministic serialization: same request + same artifacts -> same bytes."""
        return canonical_json(self.to_dict())

    @property
    def ok(self) -> bool:
        """True for an `OK` result."""
        return self.status == STATUS_OK
