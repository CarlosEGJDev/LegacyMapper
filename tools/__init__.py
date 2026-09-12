"""Repository-level tooling, outside the `legacy_documenter` production package.

Nothing under `tools/` is imported by production code or by `main.py`. It
exists for analysis/report generation tasks (e.g. the V4.1-R0 maintainability
inventory) that must not blur responsibilities with the knowledge domain
packages under `legacy_documenter/knowledge/`.
"""
