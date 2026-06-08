from __future__ import annotations

from openloop.models import WorkOrder
from openloop.utils.text import (
    compact,
    dedupe,
    extract_label_value,
    extract_matching_lines,
    extract_section_items,
    first_non_empty_line,
    sentence_summary,
)


def work_order_from_text(text: str, source: str) -> WorkOrder:
    objective = (
        extract_label_value(text, ("objective", "goal", "task"))
        or _objective_from_title_or_body(text)
    )
    success_criteria = extract_section_items(
        text,
        (
            "acceptance criteria",
            "success criteria",
            "definition of done",
            "done when",
            "requirements",
        ),
    )
    verification = extract_section_items(text, ("verification", "testing", "tests", "validate"))
    verification.extend(
        extract_matching_lines(
            text,
            (
                r"\buv run\b",
                r"\bpytest\b",
                r"\bruff\b",
                r"\bnpm test\b",
                r"\bpnpm test\b",
                r"\bcargo test\b",
                r"\bgo test\b",
            ),
        )
    )
    verification = dedupe(verification)

    boundaries = extract_section_items(
        text,
        ("scope", "constraints", "boundaries", "non-goals", "out of scope", "do not"),
    )
    boundaries.extend(extract_matching_lines(text, (r"^do not\b", r"^avoid\b", r"must not\b")))
    boundaries = dedupe(boundaries)

    risks = extract_section_items(text, ("risk policy", "risks", "safety", "migration policy"))
    iteration = extract_section_items(text, ("iteration policy", "repair", "retry", "loop policy"))
    stop_conditions = extract_section_items(
        text,
        ("stop conditions", "stop condition", "stop when"),
    )
    previous_attempts = extract_section_items(
        text,
        ("previous attempts", "attempts", "failure history", "what failed"),
    )

    assumptions = []
    if not success_criteria:
        assumptions.append("No explicit success criteria were found; infer them from the request.")
    if not verification:
        assumptions.append("No explicit verification commands were found; choose focused checks.")
    if not stop_conditions:
        assumptions.append(
            "No explicit stop condition was found; stop after objective and checks pass."
        )

    return WorkOrder(
        intent="implementation" if _looks_like_build_request(text) else "engineering task",
        objective=sentence_summary(objective),
        source=source,
        context=compact(text, limit=3000),
        scope=boundaries or ["Stay within the requested local CLI/package scope."],
        success_criteria=success_criteria
        or ["The requested behavior is implemented and documented enough to use."],
        verification_evidence=verification
        or ["Run focused tests or static checks relevant to the change."],
        risk_policy=risks
        or [
            "Keep changes scoped to the requested behavior.",
            "Avoid destructive actions and unrelated refactors.",
        ],
        iteration_policy=iteration
        or [
            (
                "If verification fails, inspect the failure, make the smallest relevant "
                "correction, and rerun."
            ),
        ],
        stop_conditions=stop_conditions
        or [
            (
                "Stop when the objective is satisfied, verification evidence is collected, "
                "and remaining risk is reported."
            ),
        ],
        previous_attempts=previous_attempts,
        assumptions=assumptions,
    )


def _objective_from_title_or_body(text: str) -> str:
    first_line = first_non_empty_line(text)
    if first_line.lower() in {"issue", "task", "plan"}:
        return sentence_summary(text)
    return first_line


def _looks_like_build_request(text: str) -> bool:
    lowered = text.lower()
    build_words = ("implement", "build", "create", "add", "fix", "scaffold")
    return any(word in lowered for word in build_words)
