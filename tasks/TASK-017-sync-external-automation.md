# TASK-017-sync-external-automation

## Meta

- Status: `done`
- Priority: `P1`
- Owner: `orchestrator`
- Due: `2026-05-07`
- Epic: `EPIC-002`
- Depends On: `TASK-016`
- Target Repo Path: `F:\AABRepository\AI-team\agent-system`
- Branch: `feature/sync-external-automation`
- Estimate: `0.5d`

## Goal

Automate external mirror synchronization and status documentation.

## Scope In

- Add `scripts/sync_external.py`
- Sync clone/pull for curated upstream list
- Update `external/README.md` with latest sync status

## Scope Out

- Auto conflict resolution for divergent branches

## Acceptance Criteria

1. One command can sync all configured upstream repos.
2. Sync result summary is persisted to `external/README.md`.
3. Failures are reported with brief reason for retry.

## Risks / Dependencies

- Public network instability may cause transient clone/pull failures.

