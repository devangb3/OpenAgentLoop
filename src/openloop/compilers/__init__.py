from __future__ import annotations

from openloop.compilers.claude_code import compile_claude_code
from openloop.compilers.codex import compile_codex
from openloop.compilers.opencode import compile_opencode
from openloop.models import PromptBundle, TargetAgent, WorkOrder


def compile_prompt(work_order: WorkOrder, target: TargetAgent) -> PromptBundle:
    if target == "codex":
        return compile_codex(work_order)
    if target == "claude-code":
        return compile_claude_code(work_order)
    if target == "opencode":
        return compile_opencode(work_order)
    raise ValueError(f"Unsupported target: {target}")
