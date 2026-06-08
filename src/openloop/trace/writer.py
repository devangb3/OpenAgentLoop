from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from openloop.models import LintReport, PromptBundle, TargetAgent, WorkOrder


def new_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid4().hex[:8]}"


class TraceWriter:
    def __init__(self, root: Path = Path(".openloop/runs"), run_id: str | None = None) -> None:
        self.root = root
        self.run_id = run_id or new_run_id()
        self.run_dir = self.root / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "latest").write_text(f"{self.run_id}\n", encoding="utf-8")

    def write_work_order(self, work_order: WorkOrder) -> Path:
        return self._write_json("work-order.json", work_order)

    def write_prompt(self, bundle: PromptBundle) -> Path:
        return self._write_text(f"prompt.{bundle.target_agent}.md", bundle.prompt_text)

    def write_lint_report(self, report: LintReport) -> Path:
        return self._write_json("lint-report.json", report)

    def write_repair(self, target: TargetAgent, prompt: str, index: int = 1) -> Path:
        return self._write_text(f"repair-{index:03d}.{target}.md", prompt)

    def write_review(self, target: TargetAgent, prompt: str, index: int = 1) -> Path:
        return self._write_text(f"review-{index:03d}.{target}.md", prompt)

    def _write_json(self, name: str, model: BaseModel) -> Path:
        path = self.run_dir / name
        path.write_text(f"{model.model_dump_json(indent=2)}\n", encoding="utf-8")
        return path

    def _write_text(self, name: str, text: str) -> Path:
        path = self.run_dir / name
        path.write_text(f"{text.rstrip()}\n", encoding="utf-8")
        return path
