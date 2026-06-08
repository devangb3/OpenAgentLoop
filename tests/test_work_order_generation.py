from openloop.generators.work_order import work_order_from_text


def test_work_order_extracts_sections_and_commands() -> None:
    text = """# Add draft command

Objective: Generate Codex prompts from issue files.

## Acceptance Criteria
- Reads markdown input
- Writes prompt output

## Verification
- uv run pytest

## Non-Goals
- Do not call agent CLIs

## Stop Conditions
- Stop after tests pass
"""

    work_order = work_order_from_text(text, "issue.md")

    assert work_order.objective == "Generate Codex prompts from issue files."
    assert "Reads markdown input" in work_order.success_criteria
    assert "uv run pytest" in work_order.verification_evidence
    assert work_order.verification_evidence.count("uv run pytest") == 1
    assert "Do not call agent CLIs" in work_order.scope
    assert work_order.scope.count("Do not call agent CLIs") == 1
    assert "Stop after tests pass" in work_order.stop_conditions
