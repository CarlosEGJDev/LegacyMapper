"""Plugin Contract 1.0 (V5.8): the declarative manifest. Data only -- a manifest is never executed.

`Plugin Contract != Plugin Runtime`. Nothing in this package discovers plugins on disk, imports or loads code,
installs, sandboxes, signs or runs anything. `entrypoint_metadata` is reserved descriptive text: it is validated
for shape and length and never resolved, imported or executed.
"""
from __future__ import annotations

from dataclasses import dataclass

PLUGIN_CONTRACT_NAME = "LegacyMapperPluginContract"
PLUGIN_CONTRACT_VERSION = "1.0"
SUPPORTED_PLUGIN_CONTRACT_VERSIONS = ("1.0",)
ENTRYPOINT_METADATA_KEYS = ("kind", "reference")
MAX_TEXT_CHARS = 200


@dataclass(frozen=True)
class PluginManifest:
    """A validated, immutable manifest. Constructed only by `validation.validate_manifest`."""

    plugin_id: str
    plugin_version: str
    plugin_contract_version: str
    requires_consumer_contract: str
    requires_capabilities: tuple[str, ...]
    optional_capabilities: tuple[str, ...]
    input_kinds: tuple[str, ...]
    output_kinds: tuple[str, ...]
    read_only: bool
    entrypoint_metadata: tuple[tuple[str, str], ...] = ()

    def to_dict(self) -> dict:
        """Stable JSON shape."""
        return {
            "plugin_id": self.plugin_id, "plugin_version": self.plugin_version,
            "plugin_contract_version": self.plugin_contract_version,
            "requires": {"consumer_contract": self.requires_consumer_contract, "capabilities": list(self.requires_capabilities),
                         "optional_capabilities": list(self.optional_capabilities)},
            "provides": {"input_kinds": list(self.input_kinds), "output_kinds": list(self.output_kinds)},
            "read_only": self.read_only, "entrypoint_metadata": dict(self.entrypoint_metadata) or None,
        }


@dataclass(frozen=True)
class ManifestValidation:
    """Outcome of an accepted manifest: the manifest plus what the validator ignored and negotiated."""

    manifest: PluginManifest
    resolved_plugin_contract_version: str
    resolved_consumer_contract_version: str
    ignored_optional_capabilities: tuple[str, ...]
