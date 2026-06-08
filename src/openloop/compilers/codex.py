from __future__ import annotations

from openloop.models import PromptBundle, WorkOrder
from openloop.utils.text import markdown_list


def compile_codex(work_order: WorkOrder) -> PromptBundle:
    prompt = f"""Task

## Objective
{work_order.objective}

## Context
{work_order.context}

## Definition Of Done
{markdown_list(work_order.success_criteria, "The requested behavior is complete.")}

## Verification Evidence
{markdown_list(work_order.verification_evidence, "Run focused checks and report the results.")}

## Boundaries
{markdown_list(work_order.scope, "Stay within the requested scope.")}

## Risk Policy
{markdown_list(work_order.risk_policy, "Avoid unrelated changes.")}

## Iteration Policy
{markdown_list(work_order.iteration_policy, "Fix verification failures before stopping.")}

## Stop Condition
{markdown_list(work_order.stop_conditions, "Stop when the objective is complete and verified.")}

## Expected Final Response
- Summarize the files changed and why.
- Report verification commands or evidence exactly.
- Call out any remaining risk, skipped checks, or follow-up needed.
"""
    return PromptBundle(
        target_agent="codex",
        prompt_text=prompt.strip(),
        metadata={"compiler": "codex", "style": "definition-of-done"},
        source_work_order_id=work_order.id,
        assumptions=work_order.assumptions,
    )
