# TASK-016-external-repo-skill-sync

## Meta

- Status: `done`
- Priority: `P1`
- Owner: `orchestrator`
- Due: `2026-05-06`
- Epic: `EPIC-002`
- Depends On: `none`
- Target Repo Path: `F:\AABRepository\AI-team\agent-system`
- Branch: `feature/external-repo-skill-sync`
- Estimate: `0.5d`

## Goal

Download official upstream repositories and import selected skill packs into local agent-system.

## Scope In

- Clone OpenAI Codex repo
- Clone Anthropic Claude Code and skills repos
- Import selected skills into local `skills/anthropic_imports`
- Record success/failure in external mirror manifest

## Scope Out

- Deep integration of every external plugin

## Acceptance Criteria

1. Local mirrors exist for reachable repositories.
2. Imported skill packs available under local skills directory.
3. Network failures are documented for retry.

## Risks / Dependencies

- Public network connectivity to GitHub may be unstable.

