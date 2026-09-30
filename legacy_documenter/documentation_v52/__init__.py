"""V5.2 human documentation engine.

Evidence -> Audience Transformation -> Output Profile -> Template -> Renderer.
Contract: `docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md`.

Pure deterministic Python: it imports no AI provider, reads only the run's own
evidence/index data plus the declarative configuration under `defaults/`
(packaged with this module), and writes only under `<output>/documentation_v52/`.
"""
from .engine import DocumentationV52Result, generate_documentation_v52  # noqa: F401
