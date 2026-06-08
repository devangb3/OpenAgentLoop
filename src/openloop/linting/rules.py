from __future__ import annotations

import re
from pathlib import Path

from pydantic import ValidationError

from openloop.models import LintDimension, LintReport, WorkOrder

DIMENSIONS: tuple[tuple[str, int], ...] = (
    ("objective clarity", 20),
    ("success criteria", 15),
    ("verification evidence", 20),
    ("scope boundaries", 15),
    ("stop conditions", 15),
    ("target compatibility", 15),
)


def lint_path(path: Path) -> LintReport:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            return lint_work_order(WorkOrder.model_validate_json(text))
        except (ValidationError, ValueError):
            pass
    return lint_prompt(text)


def lint_work_order(work_order: WorkOrder) -> LintReport:
    checks = [
        _dimension(
            "objective clarity",
            bool(work_order.objective and len(work_order.objective.split()) >= 4),
            "Objective has enough detail." if work_order.objective else "Objective is missing.",
        ),
        _dimension(
            "success criteria",
            bool(work_order.success_criteria),
            f"{len(work_order.success_criteria)} success criteria present.",
        ),
        _dimension(
            "verification evidence",
            bool(work_order.verification_evidence),
            f"{len(work_order.verification_evidence)} verification item(s) present.",
        ),
        _dimension(
            "scope boundaries",
            bool(work_order.scope),
            f"{len(work_order.scope)} scope boundary item(s) present.",
        ),
        _dimension(
            "stop conditions",
            bool(work_order.stop_conditions),
            f"{len(work_order.stop_conditions)} stop condition item(s) present.",
        ),
        _dimension(
            "target compatibility",
            True,
            "WorkOrder is agent-neutral and can be compiled for supported targets.",
        ),
    ]
    return _report(checks)


def lint_prompt(prompt: str) -> LintReport:
    lowered = prompt.lower()
    target_mentions = sum(target in lowered for target in ("codex", "claude code", "opencode"))
    checks = [
        _dimension(
            "objective clarity",
            _has_section_or_keyword(prompt, ("objective", "goal", "task"))
            and len(prompt.split()) >= 25,
            "Prompt includes an objective/goal cue.",
        ),
        _dimension(
            "success criteria",
            _has_section_or_keyword(
                prompt,
                ("success criteria", "definition of done", "done when"),
            ),
            "Prompt includes success criteria or definition of done.",
        ),
        _dimension(
            "verification evidence",
            _has_section_or_keyword(
                prompt,
                ("verification", "tests", "evidence", "pytest", "ruff"),
            ),
            "Prompt includes verification evidence cues.",
        ),
        _dimension(
            "scope boundaries",
            _has_section_or_keyword(prompt, ("scope", "boundaries", "constraints", "non-goals")),
            "Prompt includes scope or constraint cues.",
        ),
        _dimension(
            "stop conditions",
            _has_section_or_keyword(prompt, ("stop condition", "stop when")),
            "Prompt includes stop condition cues.",
        ),
        _dimension(
            "target compatibility",
            target_mentions == 1 or _has_section_or_keyword(prompt, ("role", "expected output")),
            "Prompt appears compatible with a target agent.",
        ),
    ]
    return _report(checks)


def _dimension(name: str, passed: bool, detail: str) -> LintDimension:
    max_points = dict(DIMENSIONS)[name]
    return LintDimension(
        name=name,
        passed=passed,
        points=max_points if passed else 0,
        max_points=max_points,
        detail=detail,
    )


def _report(dimensions: list[LintDimension]) -> LintReport:
    missing = [dimension.name for dimension in dimensions if not dimension.passed]
    suggestions = [_suggestion(name) for name in missing]
    return LintReport(
        score=sum(dimension.points for dimension in dimensions),
        max_score=sum(dimension.max_points for dimension in dimensions),
        dimensions=dimensions,
        missing_fields=missing,
        suggestions=suggestions,
    )


def _has_section_or_keyword(prompt: str, keywords: tuple[str, ...]) -> bool:
    for keyword in keywords:
        escaped = re.escape(keyword)
        if re.search(rf"(^|\n)\s*#+\s*{escaped}\b", prompt, re.I):
            return True
        if re.search(rf"\b{escaped}\b", prompt, re.I):
            return True
    return False


def _suggestion(name: str) -> str:
    suggestions = {
        "objective clarity": "Add a concrete objective that states the intended outcome.",
        "success criteria": "Add checkable success criteria or a definition of done.",
        "verification evidence": (
            "Add commands, test names, or observable evidence required for verification."
        ),
        "scope boundaries": "Add explicit scope boundaries, constraints, or non-goals.",
        "stop conditions": "Tell the agent when to stop and what to report if blocked.",
        "target compatibility": (
            "Name the target agent or use a structured role/objective/output format."
        ),
    }
    return suggestions[name]
