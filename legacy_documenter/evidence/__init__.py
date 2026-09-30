"""Normalized Evidence Core (V5.1 R2).

Implements the contract fixed by `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
(itself grounded in `docs/V5/V5_0_R3_FINAL_ARCHITECTURE_PACKAGE.md`). This
package wraps the existing V4.3 extractors/resolvers -- it never re-implements
their extraction logic (D-04: "envolver, no reescribir") -- and produces a
technology-neutral, persistable evidence model from the same dicts those
resolvers already return.

Runtime independence (AGENTS.md, R3 SS FINAL RUNTIME/TOOLING BOUNDARY): this
package reads only the `indexes` dict a completed deterministic run already
holds in memory (or the equivalent `index/*.json` files of a completed run)
plus, optionally, the scanned repository's own files for content hashing. It
never reads `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json`, or any other
development-only path.
"""
