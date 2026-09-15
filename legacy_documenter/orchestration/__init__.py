"""AI interpretation and proposal-adaptation integration (V4.2-R4).

Kept separate from `legacy_documenter/cli/` deliberately: `router.py`,
`main.py`, `full_pipeline.py`, `pipeline_stages.py`, and
`technical_documentation_renderer.py` are all maintainability-sensitive and
must never gain AI domain logic (see
docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md).
`full_pipeline.py` only orchestrates *calling into* this package, the same
way it orchestrates calling into `pipeline_stages.py` for the deterministic
stages, without containing any interpretation/proposal logic itself.
"""
