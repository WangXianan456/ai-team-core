# Agent System

Single-repo operating system for a solo developer with multiple AI roles.

## Goals

- Turn one-person development into a repeatable multi-agent workflow.
- Keep all prompts, policies, tasks, and memory versioned in Git.
- Enforce quality gates before release.

## Structure

```text
agent-system/
  agents/                 # role definitions
  config/                 # model/pricing routing config
  skills/                 # reusable role skill packs
  workflows/              # orchestration and state machine docs
  policies/               # permission and quality policies
  templates/              # task/ADR/release templates
  tasks/                  # live task cards
  memory/                 # long-term memory and project notes
  decisions/              # ADR records
  logs/                   # execution logs (local by default)
  mcp/                    # MCP integration placeholders
```

## Core Roles

- `orchestrator`: plans, dispatches, and approves stage transitions.
- `pm`: converts goals into executable tasks and acceptance criteria.
- `dev`: implements code changes with minimal diff.
- `qa`: validates behavior, regression, and edge cases.
- `ops`: prepares deployment, rollback, and observability checks.

## Workflow

1. Intake requirement.
2. PM creates task card.
3. Orchestrator validates scope and assigns.
4. Dev implements.
5. QA validates.
6. Ops prepares release checklist.
7. Orchestrator (human) approves merge/release.

See `workflows/delivery_flow.md`.

## Quick Start

1. Copy `templates/task_card.md` to `tasks/TASK-xxx.md`.
2. Fill scope and acceptance criteria.
3. Run one delivery cycle following `workflows/delivery_flow.md`.
4. Record decision in `decisions/ADR-xxx.md` if architecture changed.
5. Commit results and logs.

## CLI Orchestrator

Use the local helper script to manage task state:

```bash
python scripts/orchestrate.py list
python scripts/orchestrate.py next TASK-001
python scripts/orchestrate.py advance TASK-001
python scripts/orchestrate.py set TASK-001 qa
python scripts/orchestrate.py blockers TASK-001
```

State changes (`advance` and `set`) are appended to:

- `logs/orchestration_events.jsonl`

Generate weekly report:

```bash
python scripts/report.py weekly
python scripts/report.py weekly --week 2026-W19
```

Log token usage and generate cost report:

```bash
python scripts/log_usage.py --task TASK-001 --role dev --model gpt-5.5 --input 1200 --output 800
python scripts/cost_report.py weekly
python scripts/log_quality.py --task TASK-001 --type escaped_defect --severity high --notes "example"
python scripts/scorecard.py weekly --output reports/scorecard-YYYY-Wxx.md
python scripts/autopilot.py daily --output reports/daily-YYYY-MM-DD.md
python scripts/dependency_audit.py plan --repo F:\path\to\business-repo
python scripts/sync_external.py
```

## Configuration

- Model routing: `config/models.yaml`
- Pricing and budget: `config/pricing.yaml` and `config/pricing.json`
- Codex Azure env template: `config/codex.env.example` (copy to local `.env`)
- External mirrors and import status: `external/README.md`

## Large Project Pattern

1. Create one `EPIC` card from `templates/epic_card.md`.
2. Split into task cards from `templates/task_card.md`.
3. Fill `Depends On` for each task.
4. Run `orchestrate.py blockers TASK-xxx` before moving to `doing`.

## Self-Evolution

- Policy: `policies/self_improvement_loop.md`
- Workflow: `workflows/self_evolution_workflow.md`
- Keep human approval as final gate for any self-update.
- Expert bar: `policies/agent_expert_standard.md`
- Expert growth loop: `workflows/expert_growth_loop.md`
- Multi-pass protocol: `policies/multi_pass_answer_protocol.md`

## GitHub

- This folder can be an independent repository.
- Do not commit secrets. Keep keys in `.env` and local secure stores.
- `logs/` and `memory/` may contain sensitive content; sanitize before push.
