from __future__ import annotations

from openloop.compilers import compile_prompt
from openloop.models import RepairContext
from openloop.utils.text import compact, markdown_list

DO_NOT_REPEAT_FALLBACK = (
    "Do not retry the same approach without explaining why the failure evidence changes."
)
STOP_FALLBACK = "Stop when the repair is complete and verification evidence is reported."


def generate_repair_prompt(context: RepairContext) -> str:
    work_order = context.work_order
    base_prompt = compile_prompt(work_order, context.target_agent).prompt_text
    failure_summary = compact(context.failure_log, limit=1800)

    avoid = []
    if context.previous_attempt_summary:
        avoid.append(context.previous_attempt_summary)
    if context.previous_prompt:
        avoid.append("Do not repeat the previous prompt verbatim; adapt to the failure evidence.")

    verification_items = markdown_list(
        work_order.verification_evidence,
        "Run the focused verification that proves the repair.",
    )

    return f"""# Repair Prompt For {context.target_agent}

## Original Objective
{work_order.objective}

## Failure Evidence To Address
{failure_summary}

## Do Not Repeat
{markdown_list(avoid, DO_NOT_REPEAT_FALLBACK)}

## Narrowed Next Attempt
- Start from the failure evidence above.
- Identify the smallest plausible cause before editing.
- Preserve the original objective and scope.
- Change only what is needed to make the next verification pass.

## Verification Evidence Required
{verification_items}

## Stop Conditions
{markdown_list(work_order.stop_conditions, STOP_FALLBACK)}

## Original Target Prompt For Reference
{base_prompt}
""".strip()
