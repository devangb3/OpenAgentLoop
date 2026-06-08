from __future__ import annotations

from openloop.models import PromptBundle, WorkOrder
from openloop.utils.text import markdown_list

STOP_FALLBACK = "Stop when implementation and verification are complete."


def compile_opencode(work_order: WorkOrder) -> PromptBundle:
    prompt = f"""# OpenCode Prompt

## Role
You are a coding agent working in a local repository.

## Objective
{work_order.objective}

## Context
{work_order.context}

## Constraints
{markdown_list(work_order.scope + work_order.risk_policy, "Keep changes scoped and reversible.")}

## Expected Output
- Implement the requested change.
- Provide a concise summary of what changed.
- Include any assumptions that affected the implementation.

## Verification Evidence
{markdown_list(work_order.verification_evidence, "Run relevant verification and report it.")}

## Success Criteria
{markdown_list(work_order.success_criteria, "The requested behavior works as described.")}

## Stop Condition
{markdown_list(work_order.stop_conditions, STOP_FALLBACK)}
"""
    return PromptBundle(
        target_agent="opencode",
        prompt_text=prompt.strip(),
        metadata={"compiler": "opencode", "style": "generic-structured"},
        source_work_order_id=work_order.id,
        assumptions=work_order.assumptions,
    )
