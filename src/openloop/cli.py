from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from openloop.collectors.input import read_text_input, write_text_output
from openloop.compilers import compile_prompt
from openloop.generators.repair import generate_repair_prompt
from openloop.generators.review import generate_review_prompt
from openloop.generators.work_order import work_order_from_text
from openloop.linting.rules import lint_path
from openloop.models import RepairContext, ReviewContext, TargetAgent, WorkOrder
from openloop.trace.writer import TraceWriter

app = typer.Typer(
    no_args_is_help=True,
    help="Compile engineering context into coding-agent prompts.",
)
console = Console(highlight=False)
err_console = Console(stderr=True, highlight=False)


TargetOption = Annotated[
    TargetAgent,
    typer.Option("--target", "-t", help="Target agent: codex, claude-code, or opencode."),
]


@app.command()
def draft(
    from_path: Annotated[
        Path | None,
        typer.Option("--from", "-f", exists=True, dir_okay=False, help="Input markdown/text file."),
    ] = None,
    target: TargetOption = "codex",
    out: Annotated[Path | None, typer.Option("--out", "-o", help="Write prompt to a file.")] = None,
    trace: Annotated[bool, typer.Option("--trace", help="Write a local trace run.")] = False,
) -> None:
    """Generate a target-specific prompt from a file or stdin."""
    try:
        text, source = read_text_input(from_path)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    work_order = work_order_from_text(text, source)
    bundle = compile_prompt(work_order, target)
    write_text_output(bundle.prompt_text, out)

    if trace:
        writer = TraceWriter()
        writer.write_work_order(work_order)
        writer.write_prompt(bundle)
        err_console.print(f"Trace written: {writer.run_dir}")


@app.command()
def lint(
    input_path: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Prompt or WorkOrder JSON."),
    ],
    trace: Annotated[bool, typer.Option("--trace", help="Write a local trace run.")] = False,
) -> None:
    """Score a prompt or WorkOrder using deterministic checks."""
    report = lint_path(input_path)
    console.print(f"Score: {report.score}/{report.max_score} ({report.percentage}%)")
    if report.missing_fields:
        console.print("Missing fields:")
        for field in report.missing_fields:
            console.print(f"- {field}")
    else:
        console.print("Missing fields: none")

    if report.suggestions:
        console.print("Suggestions:")
        for suggestion in report.suggestions:
            console.print(f"- {suggestion}")
    else:
        console.print("Suggestions: none")

    if trace:
        writer = TraceWriter()
        writer.write_lint_report(report)
        err_console.print(f"Trace written: {writer.run_dir}")


@app.command()
def repair(
    work_order_path: Annotated[
        Path,
        typer.Option("--work-order", exists=True, dir_okay=False, help="Original WorkOrder JSON."),
    ],
    failure_path: Annotated[
        Path,
        typer.Option("--failure", exists=True, dir_okay=False, help="Failure log file."),
    ],
    target: TargetOption = "codex",
    previous_prompt: Annotated[
        Path | None,
        typer.Option(
            "--previous-prompt",
            exists=True,
            dir_okay=False,
            help="Previous prompt file.",
        ),
    ] = None,
    previous_attempt_summary: Annotated[
        str | None,
        typer.Option("--previous-attempt-summary", help="Short summary of the failed attempt."),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write repair prompt to a file."),
    ] = None,
    trace: Annotated[bool, typer.Option("--trace", help="Write a local trace run.")] = False,
) -> None:
    """Generate a focused repair prompt from a WorkOrder and failure log."""
    work_order = WorkOrder.model_validate_json(work_order_path.read_text(encoding="utf-8"))
    failure_log = failure_path.read_text(encoding="utf-8")
    previous_prompt_text = previous_prompt.read_text(encoding="utf-8") if previous_prompt else None
    context = RepairContext(
        work_order=work_order,
        failure_log=failure_log,
        target_agent=target,
        previous_prompt=previous_prompt_text,
        previous_attempt_summary=previous_attempt_summary,
    )
    prompt = generate_repair_prompt(context)
    write_text_output(prompt, out)

    if trace:
        writer = TraceWriter()
        writer.write_work_order(work_order)
        writer.write_repair(target, prompt)
        err_console.print(f"Trace written: {writer.run_dir}")


@app.command()
def review(
    diff_path: Annotated[
        Path | None,
        typer.Option(
            "--diff",
            "-d",
            exists=True,
            dir_okay=False,
            help="Diff file. Reads stdin if omitted.",
        ),
    ] = None,
    target: TargetOption = "claude-code",
    work_order_path: Annotated[
        Path | None,
        typer.Option("--work-order", exists=True, dir_okay=False, help="Optional WorkOrder JSON."),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write review prompt to a file."),
    ] = None,
    trace: Annotated[bool, typer.Option("--trace", help="Write a local trace run.")] = False,
) -> None:
    """Generate a code review prompt from a diff."""
    try:
        diff, _source = read_text_input(diff_path)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    work_order = None
    if work_order_path is not None:
        work_order = WorkOrder.model_validate_json(work_order_path.read_text(encoding="utf-8"))

    context = ReviewContext(diff=diff, target_agent=target, work_order=work_order)
    prompt = generate_review_prompt(context)
    write_text_output(prompt, out)

    if trace:
        writer = TraceWriter()
        if work_order is not None:
            writer.write_work_order(work_order)
        writer.write_review(target, prompt)
        err_console.print(f"Trace written: {writer.run_dir}")


if __name__ == "__main__":
    app()
