from openloop.linting.rules import lint_prompt, lint_work_order
from openloop.models import WorkOrder


def test_lint_prompt_reports_missing_fields() -> None:
    report = lint_prompt("Fix it.")

    assert report.score < report.max_score
    assert "success criteria" in report.missing_fields
    assert report.suggestions


def test_lint_work_order_scores_complete_work_order() -> None:
    work_order = WorkOrder(
        intent="implementation",
        objective="Implement deterministic prompt generation",
        source="test",
        context="Context",
        scope=["No GitHub integration"],
        success_criteria=["Draft command works"],
        verification_evidence=["uv run pytest"],
        stop_conditions=["Stop after verification passes"],
    )

    report = lint_work_order(work_order)

    assert report.score == report.max_score
    assert report.missing_fields == []
