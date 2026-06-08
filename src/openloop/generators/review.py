from __future__ import annotations

from openloop.models import ReviewContext
from openloop.utils.text import compact, fenced_block


def generate_review_prompt(context: ReviewContext) -> str:
    work_order_section = "No original WorkOrder was provided."
    if context.work_order is not None:
        work_order_section = f"""Objective: {context.work_order.objective}
Success criteria:
{chr(10).join(f"- {item}" for item in context.work_order.success_criteria)}
Verification evidence:
{chr(10).join(f"- {item}" for item in context.work_order.verification_evidence)}"""

    role = (
        "Act as a careful code reviewer. Prioritize concrete bugs, behavioral regressions, "
        "missing tests, security risks, and maintainability issues."
    )
    stop_condition = (
        "Stop after the review has enough evidence for the implementer to act without "
        "rereading the whole diff."
    )

    return f"""# Code Review Prompt For {context.target_agent}

## Review Role
{role}

## Original WorkOrder
{work_order_section}

## Diff To Review
{fenced_block(compact(context.diff, limit=5000), "diff")}

## Review Checklist
- Correctness risks: identify logic errors, broken edge cases, and regressions.
- Test coverage: identify missing tests or weak verification evidence.
- Security risks: identify unsafe input handling, secrets exposure, or dangerous operations.
- Maintainability: identify confusing structure, excessive coupling, or unnecessary complexity.
- WorkOrder fit: state whether the diff satisfies the original WorkOrder when one is provided.
- Repair prompt: if issues are found, provide a concrete next repair prompt.

## Expected Output
- Findings first, ordered by severity.
- File/line references when available from the diff.
- A brief verification or test-gap summary.
- If no issues are found, say so clearly and name residual risk.

## Stop Condition
{stop_condition}
""".strip()
