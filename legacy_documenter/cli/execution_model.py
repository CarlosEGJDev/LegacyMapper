"""Execution/result model for CLI commands.

A small, explicit representation of "what happened when a command ran" —
introduced so future orchestration rounds (V4.2-R2+) have somewhere to record
per-stage outcomes instead of a run being only "it raised or it didn't". R1
uses it minimally: `analyze` reports a single-outcome run, `full` reports its
NOT_IMPLEMENTED_FOR_R1 placeholder through the same shape. This is a data
model only — it is not a workflow engine, has no dependency graph, and does
not execute anything by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from legacy_documenter.cli.stage_identity import StageId


class RunStatus(str, Enum):
    """Overall outcome of one CLI command run."""

    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class StageStatus(str, Enum):
    """Outcome of a single stage within a run."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED_DUE_TO_UPSTREAM_FAILURE = "SKIPPED_DUE_TO_UPSTREAM_FAILURE"
    NOT_RUN = "NOT_RUN"


@dataclass(frozen=True)
class StageError:
    """Structured failure for one stage.

    Deliberately narrow: a stage, a short category, and a human-readable
    message. Never carries a raw traceback, environment contents, or secrets
    (see V4.1 GENERATED_ARTIFACT_POLICY.md); `reference` is only for pointing
    at the specific input that failed (e.g. a relative file path), not for
    arbitrary diagnostic payloads.
    """

    stage: StageId
    category: str
    message: str
    reference: str | None = None

    def to_dict(self) -> dict:
        """Renders this error as a plain, JSON-serializable dict."""
        payload: dict = {"stage": self.stage.value, "category": self.category, "message": self.message}
        if self.reference is not None:
            payload["reference"] = self.reference
        return payload


@dataclass(frozen=True)
class StageResult:
    """Outcome of one stage of a run."""

    stage: StageId
    status: StageStatus
    error: StageError | None = None

    def to_dict(self) -> dict:
        """Renders this stage outcome as a plain, JSON-serializable dict."""
        payload: dict = {"stage": self.stage.value, "status": self.status.value}
        if self.error is not None:
            payload["error"] = self.error.to_dict()
        return payload


@dataclass(frozen=True)
class RunResult:
    """Outcome of one CLI command invocation.

    `stages` is empty for commands that do not report stage-level detail
    (e.g. `analyze`, which still runs as a single deterministic call rather
    than through the stage model -- see `legacy_documenter.cli.pipeline_stages`).
    The three approval-boundary fields default to `False` and are always
    rendered explicitly: V4.2-R2 introduces AI-free, approval-free
    orchestration only, and the run summary must say so plainly rather than
    by omission (see docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md).
    """

    command: str
    status: RunStatus
    stages: tuple[StageResult, ...] = field(default_factory=tuple)
    message: str | None = None
    ai_invoked: bool = False
    canonical_knowledge_produced: bool = False
    technical_lead_approval: bool = False
    # V4.2-R5 additive UX fields (section 9): a developer reading RUN_SUMMARY.json
    # alone should be able to tell "AI requested" apart from "AI invoked", see
    # how many proposals (if any) await review, and get the same recommended
    # next action the console prints -- without re-deriving any of it themselves.
    # None of these change or replace an existing field.
    ai_requested: bool = False
    proposal_count: int = 0
    proposal_review_status: str | None = None
    next_action: str | None = None
    output_locations: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        """Renders this run outcome as a plain, JSON-serializable dict."""
        payload: dict = {
            "command": self.command,
            "status": self.status.value,
            "stages": [stage.to_dict() for stage in self.stages],
            "ai_invoked": self.ai_invoked,
            "canonical_knowledge_produced": self.canonical_knowledge_produced,
            "technical_lead_approval": self.technical_lead_approval,
            "ai_requested": self.ai_requested,
            "proposal_count": self.proposal_count,
            "proposal_review_status": self.proposal_review_status,
            "next_action": self.next_action,
            "output_locations": list(self.output_locations),
        }
        if self.message is not None:
            payload["message"] = self.message
        return payload
