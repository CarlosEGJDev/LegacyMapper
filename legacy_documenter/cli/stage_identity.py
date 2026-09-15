"""Stable stage identity for the V4.2 full pipeline.

R1 established this vocabulary; `full` (`legacy_documenter.cli.full_pipeline`)
executes all thirteen stages through these identities: `SCAN, EXTRACTION,
CALL_RESOLUTION, WEB_ENTRY_RESOLUTION, DATABASE_RESOLUTION, FLOW_RESOLUTION,
DEPENDENCY_RESOLUTION, EXPORT, CONTEXT, DOCUMENTATION` always run (V4.2-R2
wired the deterministic backbone; V4.2-R3 added DOCUMENTATION);
`AI_INTERPRETATION` and `PROPOSAL_GENERATION` run only when the caller
explicitly opts in (`--allow-ai-interpretation`, V4.2-R4) -- otherwise they
appear in the stage list as `StageStatus.NOT_RUN`, never omitted, so a
`RUN_SUMMARY.json` reader can always see the full stage vocabulary and tell
"not requested" apart from "requested but failed". `FINAL_SUMMARY` always
runs last.
"""
from __future__ import annotations

from enum import Enum


class StageId(str, Enum):
    """Identifies one stage of the future full pipeline.

    Names mirror the concrete resolvers/exporters `analyze_repository` already
    calls (see `legacy_documenter/main.py`), plus the not-yet-wired knowledge
    stages described in docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md.
    `EXPORT` covers both `JSONExporter` and `MarkdownExporter`: today they always
    run together as one deterministic output step, so splitting them into two
    stage identities would not reflect any real independent failure boundary.
    """

    SCAN = "SCAN"
    EXTRACTION = "EXTRACTION"
    CALL_RESOLUTION = "CALL_RESOLUTION"
    WEB_ENTRY_RESOLUTION = "WEB_ENTRY_RESOLUTION"
    DATABASE_RESOLUTION = "DATABASE_RESOLUTION"
    FLOW_RESOLUTION = "FLOW_RESOLUTION"
    DEPENDENCY_RESOLUTION = "DEPENDENCY_RESOLUTION"
    EXPORT = "EXPORT"
    CONTEXT = "CONTEXT"
    DOCUMENTATION = "DOCUMENTATION"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    PROPOSAL_GENERATION = "PROPOSAL_GENERATION"
    FINAL_SUMMARY = "FINAL_SUMMARY"
