from openloop.compilers import compile_prompt
from openloop.models import WorkOrder


def make_work_order() -> WorkOrder:
    return WorkOrder(
        intent="implementation",
        objective="Implement prompt compilation.",
        source="test",
        context="Build deterministic compilers.",
        success_criteria=["Codex prompt is generated"],
        verification_evidence=["uv run pytest"],
        scope=["No web UI"],
        stop_conditions=["Stop after tests pass"],
    )


def test_compilers_are_target_specific() -> None:
    work_order = make_work_order()

    codex = compile_prompt(work_order, "codex")
    claude = compile_prompt(work_order, "claude-code")
    opencode = compile_prompt(work_order, "opencode")

    assert codex.target_agent == "codex"
    assert "Definition Of Done" in codex.prompt_text
    assert "Transcript-Visible Context" in claude.prompt_text
    assert "Role" in opencode.prompt_text
    assert len({codex.prompt_text, claude.prompt_text, opencode.prompt_text}) == 3
