from openloop.models import LintReport, WorkOrder


def test_work_order_defaults_are_populated() -> None:
    work_order = WorkOrder(
        intent="implementation",
        objective="Build a local CLI",
        source="issue.md",
        context="Implement the CLI.",
    )

    assert work_order.id.startswith("wo-")
    assert work_order.created_at.tzinfo is not None


def test_lint_report_percentage() -> None:
    report = LintReport(score=75, max_score=100, dimensions=[])

    assert report.percentage == 75
