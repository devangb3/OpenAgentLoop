# OpenLoop

OpenLoop is a terminal-first prompt compiler for coding-agent loops. It turns
messy engineering context such as issues, logs, diffs, repo instructions, and
previous attempts into target-specific prompts for coding agents.

Supported targets:

- Codex
- Claude Code
- OpenCode

OpenLoop is local-first. It does not execute agents, run CI, call GitHub APIs, or
mutate a target repository.

## Quickstart

Install dependencies and run the CLI from this checkout:

```bash
uv sync
uv run openloop --help
```

Generate a Codex prompt from an issue file:

```bash
uv run openloop draft --from issue.md --target codex
```

Generate target-specific variants:

```bash
uv run openloop draft --from issue.md --target claude-code
uv run openloop draft --from issue.md --target opencode
```

Lint a prompt or WorkOrder JSON:

```bash
uv run openloop lint prompt.md
uv run openloop lint work-order.json
```

Generate a focused repair prompt after a failed attempt:

```bash
uv run openloop repair \
  --work-order .openloop/runs/<run-id>/work-order.json \
  --failure failure.log \
  --target codex
```

Generate a review prompt from a diff:

```bash
uv run openloop review --diff diff.patch --target claude-code
```

Read input from stdin when a file option is omitted:

```bash
git diff | uv run openloop review --target claude-code
```

## Trace Files

Pass `--trace` to save local run artifacts under `.openloop/runs/<run-id>/`:

```text
.openloop/runs/<run-id>/
  work-order.json
  prompt.<target>.md
  lint-report.json
  repair-001.<target>.md
  review-001.<target>.md
```

`.openloop/runs/latest` contains the most recent run id.

## Development

Run tests and linting:

```bash
uv run pytest
uv run ruff check .
```
