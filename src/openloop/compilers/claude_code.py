from __future__ import annotations

from openloop.models import PromptBundle, WorkOrder
from openloop.utils.text import markdown_list

STOP_FALLBACK = "Stop after the goal is implemented and evidence is visible."


def compile_claude_code(work_order: WorkOrder) -> PromptBundle:
    prompt = f"""# Task

## Goal
{work_order.objective}

## Transcript-Visible Context
{work_order.context}

## Required Evidence In The Transcript
{markdown_list(work_order.verification_evidence, "Show the checks you ran and their outcomes.")}

## Success Criteria
{markdown_list(work_order.success_criteria, "The implementation satisfies the requested behavior.")}

## Scope Boundaries And Non-Goals
{markdown_list(work_order.scope, "Do not make unrelated changes.")}

## Tool-Use Discipline
- Inspect the current files before editing.
- Keep edits scoped and explain any assumption that affects behavior.
- Do not hide failed checks; include the failure and the next action.

## Changed Files Summary Required
- In the final response, list changed files and the purpose of each change.
- Include verification evidence and unresolved risks.

## Stop Condition
{markdown_list(work_order.stop_conditions, STOP_FALLBACK)}
"""
    return PromptBundle(
        target_agent="claude-code",
        prompt_text=prompt.strip(),
        metadata={"compiler": "claude-code", "style": "transcript-evidence"},
        source_work_order_id=work_order.id,
        assumptions=work_order.assumptions,
    )
