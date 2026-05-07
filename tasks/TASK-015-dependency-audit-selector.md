# TASK-015-dependency-audit-selector

## Meta

- Status: `done`
- Priority: `P1`
- Owner: `orchestrator`
- Due: `2026-05-06`
- Epic: `EPIC-002`
- Depends On: `TASK-011`
- Target Repo Path: `F:\AABRepository\AI-team\agent-system`
- Branch: `feature/dependency-audit-selector`
- Estimate: `0.5d`

## Goal

Add ecosystem-aware dependency audit command selector and optional runner.

## Scope In

- Implement `scripts/dependency_audit.py`
- Support plan/run modes
- Detect node/python/go/rust repositories

## Scope Out

- Auto installation of missing audit binaries

## Acceptance Criteria

1. `plan` outputs ecosystem-specific commands.
2. `run` executes available commands and reports missing tooling.
3. Script handles unknown ecosystems safely.

## Risks / Dependencies

- Local environment may not have all security tools installed.

