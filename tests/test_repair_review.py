from openloop.generators.repair import generate_repair_prompt
from openloop.generators.review import generate_review_prompt
from openloop.models import RepairContext, ReviewContext, WorkOrder


def make_work_order() -> WorkOrder:
    return WorkOrder(
        intent="implementation",
        objective="Add lint command",
        source="issue.md",
        context="Need prompt linting.",
        success_criteria=["Reports missing fields"],
        verification_evidence=["uv run pytest"],
        scope=["Local CLI only"],
        stop_conditions=["Stop after tests pass"],
    )


def test_repair_prompt_preserves_objective_and_failure() -> None:
    prompt = generate_repair_prompt(
        RepairContext(
            work_order=make_work_order(),
            failure_log="pytest failed: missing stop condition check",
            target_agent="codex",
        )
    )

    assert "Add lint command" in prompt
    assert "missing stop condition check" in prompt
    assert "Do Not Repeat" in prompt


def test_review_prompt_includes_required_review_areas() -> None:
    prompt = generate_review_prompt(
        ReviewContext(diff="diff --git a/a.py b/a.py\n+print('x')", target_agent="claude-code")
    )

    assert "Correctness risks" in prompt
    assert "Test coverage" in prompt
    assert "Security risks" in prompt
    assert "Repair prompt" in prompt
