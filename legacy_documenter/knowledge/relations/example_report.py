"""Deterministic synthetic example fixture for the V4-R7 relation layer.

Every material id below is a synthetic, hand-authored constant (not derived
from any real repository content), used only to demonstrate the five R7
example scenarios required by the active prompt.
"""
import json

from legacy_documenter.knowledge.relations.enums import RelationBasis, RelationKind
from legacy_documenter.knowledge.relations.service import RelationRequest, RelationService

SCHEMA_VERSION = "V4-R7"

_SERVICE = RelationService()


def build_relation_example() -> dict:
    """Builds the full deterministic R7 example-fixture payload as a plain dict."""
    material_a = "MAT-EXAMPLE-A"
    material_b = "MAT-EXAMPLE-B"
    material_c = "MAT-EXAMPLE-C"
    material_d = "MAT-EXAMPLE-D"

    difference = _SERVICE.create_relation(RelationRequest(
        relation_kind=RelationKind.DIFFERENCE, material_a=material_a, material_b=material_b,
        basis=RelationBasis.EXPLICIT, notes="Architecture A vs target architecture B, stated neutrally.",
    ))
    gap = _SERVICE.create_relation(RelationRequest(
        relation_kind=RelationKind.GAP, material_a=material_a, material_b=material_b,
        basis=RelationBasis.EXPLICIT, notes="Explicit gap: AS_IS capability vs TO_BE requirement, caller-declared.",
    ))
    conflict = _SERVICE.create_relation(RelationRequest(
        relation_kind=RelationKind.CONFLICT, material_a=material_c, material_b=material_d,
        basis=RelationBasis.EXPLICIT, notes="Two simultaneously applicable authentication requirements.",
    ))
    evolution = _SERVICE.create_relation(RelationRequest(
        relation_kind=RelationKind.TEMPORAL_EVOLUTION, material_a=material_a, material_b=material_b,
        basis=RelationBasis.EXPLICIT, notes="Explicit historical-to-current/current-to-target evolution.",
    ))

    return {
        "kind": "GAP_CONFLICT_RELATION_EXAMPLE_FIXTURE",
        "schema_version": SCHEMA_VERSION,
        "example_1_neutral_difference": {
            "materials": [material_a, material_b],
            "relation": difference.relation_kind.value,
            "relation_id": difference.relation_id,
            "gap": "NOT_INFERRED",
            "conflict": "NOT_INFERRED",
            "approval": "NOT_PERFORMED",
        },
        "example_2_explicit_gap": {
            "materials": {"from_as_is": material_a, "to_to_be": material_b},
            "relation": gap.relation_kind.value,
            "relation_id": gap.relation_id,
            "direction_explicitly_supplied": True,
            "gap": "REPRESENTED",
            "conflict": "NOT_INFERRED",
            "proposal": "NOT_CREATED",
        },
        "example_3_explicit_conflict": {
            "materials": [material_c, material_d],
            "relation": conflict.relation_kind.value,
            "relation_id": conflict.relation_id,
            "winner": "NOT_SELECTED",
            "truth": "NOT_DETERMINED",
            "approval": "NOT_PERFORMED",
        },
        "example_4_temporal_evolution": {
            "materials": {"from": material_a, "to": material_b},
            "relation": evolution.relation_kind.value,
            "relation_id": evolution.relation_id,
            "supersession": "NOT_INFERRED",
            "migration": "NOT_INFERRED",
        },
        "example_5_no_relation_from_temporal_separation_alone": {
            "materials": {"as_is": material_a, "to_be": material_b},
            "explicit_relation_request": None,
            "relation": "NONE",
            "gap": "NOT_INFERRED",
            "conflict": "NOT_INFERRED",
            "temporal_evolution": "NOT_INFERRED",
        },
    }


def render_relation_example_json() -> str:
    """Renders the example fixture as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_relation_example(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
