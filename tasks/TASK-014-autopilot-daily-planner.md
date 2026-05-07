# TASK-014-autopilot-daily-planner

## Meta

- Status: `done`
- Priority: `P1`
- Owner: `orchestrator`
- Due: `2026-05-06`
- Epic: `EPIC-002`
- Depends On: `TASK-010`
- Target Repo Path: `F:\AABRepository\AI-team\agent-system`
- Branch: `feature/autopilot-daily-planner`
- Estimate: `0.5d`

## Goal

Add daily autopilot planner to recommend top tasks, blocked tasks, and budget alerts.

## Scope In

- Implement `scripts/autopilot.py`
- Integrate budget limits from `config/pricing.json`
- Generate markdown-ready daily plan output

## Scope Out

- Calendar integration

## Acceptance Criteria

1. Command `python scripts/autopilot.py daily` works.
2. Top tasks and blocked tasks are listed.
3. Budget alert section is included.

## Risks / Dependencies

- Plan quality depends on task card data consistency.

