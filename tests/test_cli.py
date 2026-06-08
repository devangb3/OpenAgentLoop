from pathlib import Path

from typer.testing import CliRunner

from openloop.cli import app
from openloop.generators.work_order import work_order_from_text

runner = CliRunner()


def test_draft_cli_from_file(tmp_path: Path) -> None:
    issue = tmp_path / "issue.md"
    issue_text = (
        "# Build draft\n\n"
        "## Acceptance Criteria\n"
        "- Draft works\n\n"
        "## Verification\n"
        "- uv run pytest\n"
    )
    issue.write_text(
        issue_text,
        encoding="utf-8",
    )

    result = runner.invoke(app, ["draft", "--from", str(issue), "--target", "codex"])

    assert result.exit_code == 0
    assert "Codex Work Order" in result.stdout
    assert "Draft works" in result.stdout


def test_draft_cli_trace_writes_files(tmp_path: Path, monkeypatch) -> None:
    issue = tmp_path / "issue.md"
    issue.write_text("Objective: Build trace support\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["draft", "--from", str(issue), "--target", "codex", "--trace"],
    )

    assert result.exit_code == 0
    latest = Path(".openloop/runs/latest").read_text(encoding="utf-8").strip()
    run_dir = Path(".openloop/runs") / latest
    assert (run_dir / "work-order.json").exists()
    assert (run_dir / "prompt.codex.md").exists()


def test_draft_cli_from_stdin() -> None:
    result = runner.invoke(
        app,
        ["draft", "--target", "opencode"],
        input="Objective: Generate prompts from stdin\n",
    )

    assert result.exit_code == 0
    assert "OpenCode Prompt" in result.stdout
    assert "Generate prompts from stdin" in result.stdout


def test_lint_cli(tmp_path: Path) -> None:
    prompt = tmp_path / "prompt.md"
    prompt.write_text(
        "# Codex Work Order\n\n## Objective\nDo it\n\n## Stop Condition\nStop when done\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["lint", str(prompt)])

    assert result.exit_code == 0
    assert "Score:" in result.stdout
    assert "Suggestions:" in result.stdout


def test_repair_cli(tmp_path: Path) -> None:
    work_order = work_order_from_text(
        "Objective: Fix tests\n\n## Verification\n- uv run pytest\n",
        "issue.md",
    )
    work_order_path = tmp_path / "work-order.json"
    failure_path = tmp_path / "failure.log"
    work_order_path.write_text(work_order.model_dump_json(), encoding="utf-8")
    failure_path.write_text("pytest failed", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "repair",
            "--work-order",
            str(work_order_path),
            "--failure",
            str(failure_path),
            "--target",
            "codex",
        ],
    )

    assert result.exit_code == 0
    assert "Repair Prompt For codex" in result.stdout
    assert "pytest failed" in result.stdout


def test_review_cli_from_stdin() -> None:
    result = runner.invoke(
        app,
        ["review", "--target", "claude-code"],
        input="diff --git a/a.py b/a.py\n+print('x')\n",
    )

    assert result.exit_code == 0
    assert "Code Review Prompt For claude-code" in result.stdout
