# TASK-002-model-and-cost-governance

## Meta

- Status: `done`
- Priority: `P1`
- Owner: `orchestrator`
- Due: `2026-05-08`
- Epic: `EPIC-001`
- Depends On: `TASK-001`
- Target Repo Path: `F:\AABRepository\AI-team\agent-system`
- Branch: `feature/model-cost-governance`
- Estimate: `0.5d`

## Goal

Build stable model routing and token cost visibility for daily delivery.

## Scope In

- Add model config and pricing config
- Add token usage logging script
- Add weekly cost report script

## Scope Out

- Auto API integration to vendor billing

## Constraints

- Keep scripts dependency-free (standard library only)

## Acceptance Criteria

1. Token usage rows can be appended by CLI.
2. Weekly cost report can aggregate by task/role/model.
3. Readme includes exact usage commands.

## Risks / Dependencies

- Pricing config drift from real vendor price

## Handoffs

- PM -> Dev: finalize scope and acceptance
- Dev -> QA: provide command output evidence
- QA -> Ops: confirm reporting can run in current environment
- Ops -> Orchestrator: release recommendation

