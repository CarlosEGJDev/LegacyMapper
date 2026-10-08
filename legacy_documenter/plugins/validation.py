"""Manifest -> Contract Validator (V5.8). Never Manifest -> Runtime Loader.

Rules (fail closed, no silent fallback):
* contract *major* must match; minors are additive and compatible;
* an unknown required capability rejects the manifest; an unknown optional one is ignored and reported;
* any write-like capability (required or optional) or `read_only != true` is rejected (READ_ONLY_VIOLATION);
* nothing in the manifest is executed, imported or resolved.
"""
from __future__ import annotations

import re

from legacy_documenter.consumers.contracts import (
    KNOWN_INPUT_KINDS, KNOWN_OUTPUT_KINDS, SUPPORTED_CONTRACT_VERSIONS, ConsumerCapability, ConsumerDescriptor, ConsumerError,
    ConsumerErrorCode, is_write_capability_name, negotiate_contract_version, parse_version,
)
from legacy_documenter.consumers.registry import ConsumerRegistry

from .contracts import (
    ENTRYPOINT_METADATA_KEYS, MAX_TEXT_CHARS, SUPPORTED_PLUGIN_CONTRACT_VERSIONS, ManifestValidation, PluginManifest,
)

_TOP = frozenset({"plugin_id", "plugin_version", "plugin_contract_version", "requires", "provides", "read_only", "entrypoint_metadata"})
_REQUIRED_TOP = _TOP - {"entrypoint_metadata"}
_REQUIRES = frozenset({"consumer_contract", "capabilities", "optional_capabilities"})
_PROVIDES = frozenset({"input_kinds", "output_kinds"})
_PLUGIN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,55}$")
_INVALID = ConsumerErrorCode.PLUGIN_MANIFEST_INVALID


def _invalid(detail: str) -> ConsumerError:
    return ConsumerError(_INVALID, detail)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_CHARS:
        raise _invalid(f"{field}_invalid")
    return value


def _names(value: object, field: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 32:
        raise _invalid(f"{field}_invalid")
    items = tuple(_text(v, field) for v in value)
    if len(set(items)) != len(items):
        raise _invalid(f"{field}_duplicates")
    return tuple(sorted(items))


def _split_capabilities(names: tuple[str, ...], *, required: bool) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(known, unknown). Write-like names are rejected outright in either list; unknown ones reject only when required."""
    known, unknown = [], []
    for name in names:
        if is_write_capability_name(name):
            raise ConsumerError(ConsumerErrorCode.READ_ONLY_VIOLATION, "manifest_requests_write_capability")
        (known if name in ConsumerCapability.__members__ else unknown).append(name)
    if unknown and required:
        raise ConsumerError(ConsumerErrorCode.UNSUPPORTED_CAPABILITY, f"unknown_required_capability:{unknown[0]}")
    return tuple(known), tuple(unknown)


def _negotiate(value: object, supported: tuple[str, ...]) -> str:
    """Highest supported version of the declared major; an unsupported major is PLUGIN_INCOMPATIBLE."""
    parse_version(value, _INVALID)
    try:
        return negotiate_contract_version(value, supported)
    except ConsumerError:
        raise ConsumerError(ConsumerErrorCode.PLUGIN_INCOMPATIBLE, "contract_major_not_supported") from None


def validate_manifest(
    data: object, supported_plugin_versions: tuple[str, ...] = SUPPORTED_PLUGIN_CONTRACT_VERSIONS,
    supported_consumer_versions: tuple[str, ...] = SUPPORTED_CONTRACT_VERSIONS,
) -> ManifestValidation:
    """Validates a manifest dict. Returns the accepted manifest or raises `ConsumerError` (no partial acceptance)."""
    if not isinstance(data, dict) or not _REQUIRED_TOP <= set(data) <= _TOP:
        raise _invalid("manifest_keys_mismatch")
    requires, provides = data["requires"], data["provides"]
    if not isinstance(requires, dict) or set(requires) != _REQUIRES or not isinstance(provides, dict) or set(provides) != _PROVIDES:
        raise _invalid("requires_or_provides_malformed")
    plugin_id = _text(data["plugin_id"], "plugin_id")
    if not _PLUGIN_ID_RE.match(plugin_id):
        raise _invalid("plugin_id_invalid")
    plugin_version = _text(data["plugin_version"], "plugin_version")
    if data["read_only"] is not True:
        raise ConsumerError(ConsumerErrorCode.READ_ONLY_VIOLATION, "manifest_must_be_read_only")
    resolved_plugin = _negotiate(data["plugin_contract_version"], supported_plugin_versions)
    resolved_consumer = _negotiate(requires["consumer_contract"], supported_consumer_versions)
    required, _ = _split_capabilities(_names(requires["capabilities"], "capabilities", allow_empty=False), required=True)
    optional, ignored = _split_capabilities(_names(requires["optional_capabilities"], "optional_capabilities", allow_empty=True), required=False)
    input_kinds = _names(provides["input_kinds"], "input_kinds", allow_empty=False)
    output_kinds = _names(provides["output_kinds"], "output_kinds", allow_empty=False)
    if not set(input_kinds) <= KNOWN_INPUT_KINDS or not set(output_kinds) <= KNOWN_OUTPUT_KINDS:
        raise _invalid("provides_unknown_kind")
    entrypoint = data.get("entrypoint_metadata")
    if entrypoint is not None:
        if not isinstance(entrypoint, dict) or not set(entrypoint) <= set(ENTRYPOINT_METADATA_KEYS):
            raise _invalid("entrypoint_metadata_malformed")
        entrypoint = tuple(sorted((k, _text(v, "entrypoint_metadata")) for k, v in entrypoint.items()))
    manifest = PluginManifest(
        plugin_id=plugin_id, plugin_version=plugin_version, plugin_contract_version=data["plugin_contract_version"],
        requires_consumer_contract=requires["consumer_contract"], requires_capabilities=required, optional_capabilities=optional,
        input_kinds=input_kinds, output_kinds=output_kinds, read_only=True, entrypoint_metadata=entrypoint or (),
    )
    return ManifestValidation(manifest, resolved_plugin, resolved_consumer, ignored)


def descriptor_from_manifest(validation: ManifestValidation) -> ConsumerDescriptor:
    """The consumer descriptor an accepted manifest maps to: required + known optional capabilities, read-only."""
    manifest = validation.manifest
    capabilities = sorted(set(manifest.requires_capabilities) | set(manifest.optional_capabilities))
    return ConsumerDescriptor.from_dict({
        "consumer_id": f"plugin.{manifest.plugin_id}", "consumer_version": manifest.plugin_version,
        "contract_version": validation.resolved_consumer_contract_version, "capabilities_required": capabilities,
        "input_kinds": list(manifest.input_kinds), "output_kinds": list(manifest.output_kinds), "read_only": True,
    })


def register_manifests(registry: ConsumerRegistry, manifests: list[dict]) -> ConsumerRegistry:
    """A new registry with every manifest validated and mapped; one invalid manifest rejects the whole call."""
    return registry.with_descriptors(*(descriptor_from_manifest(validate_manifest(m)) for m in manifests))
