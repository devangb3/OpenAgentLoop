from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

TargetAgent = Literal["codex", "claude-code", "opencode"]


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(UTC)


class WorkOrder(BaseModel):
    id: str = Field(default_factory=lambda: new_id("wo"))
    intent: str
    objective: str
    source: str
    context: str
    scope: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    verification_evidence: list[str] = Field(default_factory=list)
    risk_policy: list[str] = Field(default_factory=list)
    iteration_policy: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)
    previous_attempts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class PromptBundle(BaseModel):
    id: str = Field(default_factory=lambda: new_id("pb"))
    target_agent: TargetAgent
    prompt_text: str
    metadata: dict[str, str] = Field(default_factory=dict)
    source_work_order_id: str
    assumptions: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class LintDimension(BaseModel):
    name: str
    passed: bool
    points: int
    max_points: int
    detail: str


class LintReport(BaseModel):
    score: int
    max_score: int
    dimensions: list[LintDimension]
    missing_fields: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

    @property
    def percentage(self) -> int:
        if self.max_score == 0:
            return 0
        return round((self.score / self.max_score) * 100)


class RepairContext(BaseModel):
    work_order: WorkOrder
    failure_log: str
    target_agent: TargetAgent
    previous_prompt: str | None = None
    previous_attempt_summary: str | None = None


class ReviewContext(BaseModel):
    diff: str
    target_agent: TargetAgent
    work_order: WorkOrder | None = None
