"""V4.1-R0 maintainability inventory and refactor-plan generation tooling.

Analysis-only. Read-only over the repository tree; performs no filesystem
write except the two deterministic JSON artifacts it is explicitly asked to
produce under `output/v4_1_r0/`. Uses only the Python standard library
(`ast`, `pathlib`, `json`, `hashlib`) -- no new dependency.
"""
