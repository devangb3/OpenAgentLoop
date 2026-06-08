from openloop.models import LintReport, PromptBundle, WorkOrder
from openloop.trace.writer import TraceWriter


def test_trace_writer_writes_expected_files(tmp_path) -> None:
    writer = TraceWriter(root=tmp_path / ".openloop" / "runs", run_id="run-1")
    work_order = WorkOrder(
        intent="implementation",
        objective="Build CLI",
        source="issue.md",
        context="Context",
    )
    bundle = PromptBundle(
        target_agent="codex",
        prompt_text="Prompt",
        source_work_order_id=work_order.id,
    )
    report = LintReport(score=0, max_score=100, dimensions=[])

    writer.write_work_order(work_order)
    writer.write_prompt(bundle)
    writer.write_lint_report(report)
    writer.write_repair("codex", "Repair")
    writer.write_review("codex", "Review")

    assert (writer.run_dir / "work-order.json").exists()
    assert (writer.run_dir / "prompt.codex.md").read_text(encoding="utf-8") == "Prompt\n"
    assert (writer.run_dir / "lint-report.json").exists()
    assert (writer.run_dir / "repair-001.codex.md").exists()
    assert (writer.run_dir / "review-001.codex.md").exists()
    assert (tmp_path / ".openloop" / "runs" / "latest").read_text(encoding="utf-8") == "run-1\n"
