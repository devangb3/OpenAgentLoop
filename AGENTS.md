# AGENTS.md

## Project: OpenLoop

OpenLoop is a terminal-first, open-source prompt compiler for coding-agent loops.

It converts messy engineering context such as GitHub issues, failing logs, diffs, repo instructions, and previous attempts into high-quality, target-specific prompts for coding agents.

Primary supported agents:

* Codex
* Claude Code
* OpenCode

OpenLoop is not a coding agent, CI runner, workflow engine, or visual builder. It is the layer before the coding agent: it creates better work orders, prompts, repair prompts, review prompts, and trace artifacts.

## Product positioning

OpenLoop answers:

> Given an engineering task, what should I ask my coding agent to do, with what constraints, verification evidence, stop conditions, and repair memory?

Initially focus on:

* `openloop draft`
* `openloop lint`
* `openloop repair`
* `openloop review`

Do not build a web UI, cloud service, agent swarm, CI runner, or GitHub bot now.

## Tech stack

Use Python with `uv`.

Expected stack:

* Python 3.11+
* `uv` for project/package management
* `typer` for CLI
* `pydantic` for schemas
* `rich` for terminal output
* `pytest` for tests
* `ruff` for linting/formatting
* Local filesystem storage only

Avoid unnecessary dependencies.

## Core concepts

### WorkOrder

A WorkOrder is the agent-neutral internal representation of an engineering task.

It should include:

* `id`
* `intent`
* `objective`
* `source`
* `context`
* `scope`
* `success_criteria`
* `verification_evidence`
* `risk_policy`
* `iteration_policy`
* `stop_conditions`
* `previous_attempts`

The WorkOrder is the source of truth. Agent prompts are compiled outputs.

### PromptBundle

A PromptBundle is the target-specific generated prompt.

It should include:

* target agent
* generated prompt text
* metadata
* source WorkOrder id
* assumptions
* generated timestamp

### Target compilers

Implement target-specific prompt compilers for:

* `codex`
* `claude-code`
* `opencode`

The same WorkOrder should produce different prompts depending on the target.

Codex prompts should emphasize:

* objective
* definition of done
* verification commands or evidence
* boundaries
* iteration policy
* stop condition

Claude Code prompts should emphasize:

* transcript-visible evidence
* changed files summary
* verification evidence
* tool-use discipline
* stop condition

OpenCode prompts should be generic but structured:

* role
* objective
* context
* constraints
* expected output
* verification evidence
* stop condition

## Key commands

### `openloop draft`

Generate a target-specific prompt from an issue file, markdown file, or plain text input.

Example:

```bash
openloop draft --from issue.md --target codex
openloop draft --from issue.md --target claude-code
openloop draft --from issue.md --target opencode
```

Output:

* prompt text to stdout by default
* optional `--out` path support

### `openloop lint`

Score a prompt or WorkOrder for quality.

Example:

```bash
openloop lint prompt.md
openloop lint work-order.json
```

Lint dimensions:

* objective clarity
* success criteria
* verification evidence
* scope boundaries
* non-goals
* risk policy
* stop conditions
* target compatibility
* repair memory

The linter should return a score and actionable suggestions.

### `openloop repair`

Generate a repair prompt from:

* original WorkOrder
* previous prompt
* failure log
* previous attempt summary

Example:

```bash
openloop repair \
  --work-order .openloop/runs/run-id/work-order.json \
  --failure failure.log \
  --target codex
```

The repair prompt should:

* summarize the failure
* tell the agent what not to repeat
* narrow the next attempt
* preserve the original objective
* include verification evidence
* include stop conditions

### `openloop review`

Generate a review prompt from a diff.

Example:

```bash
openloop review --diff diff.patch --target claude-code
```

Review prompt should ask for:

* correctness risks
* test gaps
* security risks
* maintainability issues
* whether the diff satisfies the WorkOrder
* concrete next repair prompt if issues are found

## Example inputs

Support these inputs first:

* local markdown file
* local text file
* pasted stdin
* git diff from file
* failure log from file
* existing `AGENTS.md`
* existing `CLAUDE.md`
* existing `README.md`

Do not implement deep GitHub API integration in the first pass. It can come after the local CLI works.

## Local trace format

Every run should be optionally saved under:

```text
.openloop/runs/<run-id>/
  work-order.json
  prompt.<target>.md
  lint-report.json
  repair-001.<target>.md
  review-001.<target>.md
```

The trace should make it easy to answer:

* what prompt was generated?
* from what context?
* for which target?
* what did the linter say?
* what repair prompt was generated after failure?



## Engineering principles

1. Prefer simple deterministic generation before adding LLM-based generation.
2. Make all generated prompts inspectable.
3. Make target differences explicit.
4. Do not mutate user code.
5. Write small, testable modules.
6. Keep CLI output clean and copy-paste friendly.

## Desired user experience

A user should be able to run:

```bash
uvx openloop draft --from issue.md --target codex
```

And receive a strong agent-ready prompt.

Then, after a failed attempt:

```bash
uvx openloop repair --work-order .openloop/runs/latest/work-order.json --failure failure.log --target codex
```

And receive a focused repair prompt.

The product succeeds if developers say:

> This makes my coding-agent prompts much better and saves me from manually writing repair prompts.
