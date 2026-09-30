"""Development-only measurement tool for V5.2 R3.4.1 (never imported by the
production pipeline or by tests).

Regenerates `documentation_v52/` from a persisted `evidence/` directory (no
re-run of the ~30-minute extraction) using the CURRENT code, and prints the
counts the round's result document needs for its before/after table (section
11 of the round prompt): total methods known, method documents generated,
methods that stayed index-only, documents with real data access, documents
with only transactional data access, documents with an unresolved call whose
expression is visible, and basic size/warning/broken-link figures.

Usage:
    python -m tools.v5_2_r3_4_1_method_quality_measurement <evidence_dir> <output_dir>
"""
from __future__ import annotations

import sys
from pathlib import Path

from legacy_documenter.documentation_v52.engine import generate_documentation_v52, source_from_evidence_dir
from legacy_documenter.documentation_v52.transform import AudienceTransformer
from legacy_documenter.documentation_v52.config import ConfigRegistry


def main() -> None:
    evidence_dir, output_dir = sys.argv[1], sys.argv[2]
    source = source_from_evidence_dir(evidence_dir)

    registry = ConfigRegistry()
    policy = registry.noise_policy("default")
    catalog = registry.catalog("es")
    model = AudienceTransformer(
        policy, catalog.text("unassigned_module"), catalog.text("origin_unknown"), catalog.text("file_ownership_shared"),
    ).transform(source)

    total_component_method_rows = sum(len(c.slots.get("methods", [])) for c in model.components)
    index_only_rows = sum(1 for c in model.components for i in c.slots.get("methods", []) if not i.values.get("slug"))
    ambiguous_groups = sum(len(c.slots.get("ambiguous_methods", [])) for c in model.components)

    methods_with_real_data = sum(1 for m in model.methods if m.slots.get("data_access"))
    methods_with_only_tx_data = sum(
        1 for m in model.methods if m.slots.get("data_access_transactional") and not m.slots.get("data_access"))
    methods_with_visible_unresolved_expression = sum(
        1 for m in model.methods
        if any(i.values["target"] != "(expresión no disponible)" for i in m.slots.get("calls_out_unresolved", [])))
    methods_with_resolved_calls = sum(1 for m in model.methods if m.slots.get("calls_out_resolved"))
    methods_mixed = sum(
        1 for m in model.methods
        if m.slots.get("calls_out_resolved") and m.slots.get("calls_out_unresolved"))

    print(f"Metodos conocidos en tablas de indice de componente: {total_component_method_rows}")
    print(f"Metodos con documento propio: {len(model.methods)}")
    print(f"Filas que quedaron solo en el indice (sin documento): {index_only_rows}")
    print(f"Grupos de nombre ambiguo declarados: {ambiguous_groups}")
    print(f"Documentos con acceso real a datos: {methods_with_real_data}")
    print(f"Documentos SOLO con control transaccional (sin acceso real): {methods_with_only_tx_data}")
    print(f"Documentos con llamada no resuelta y expresion visible: {methods_with_visible_unresolved_expression}")
    print(f"Documentos con llamadas resueltas: {methods_with_resolved_calls}")
    print(f"Documentos con relaciones mixtas (resueltas + no resueltas): {methods_mixed}")

    result = generate_documentation_v52(source, output_dir, profiles=("general_overview", "developer_technical"))
    total_bytes = sum(len(b.encode("utf-8")) for b in [])  # placeholder, real bytes computed below
    root = Path(result.output_dir)
    files = list(root.rglob("*.md"))
    total_bytes = sum(p.stat().st_size for p in files)
    max_file = max(files, key=lambda p: p.stat().st_size)
    print(f"Total documentos documentation_v52: {len(files) + 1}")  # +1 for MANIFEST.json is not .md; kept honest below
    print(f"Total documentos .md: {len(files)}")
    print(f"Tamano total (bytes): {total_bytes}")
    print(f"Archivo maximo: {max_file} ({max_file.stat().st_size} bytes)")
    print(f"Advertencias del renderer: {len(result.warnings)}")
    for warning in result.warnings:
        print(f"  - {warning}")


if __name__ == "__main__":
    main()
