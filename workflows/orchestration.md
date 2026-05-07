# Orchestration Playbook

## Dispatch Order

1. PM creates/updates task card
2. Orchestrator approves scope
3. Dev executes changes
4. QA validates acceptance criteria
5. Ops prepares and verifies release
6. Orchestrator/human makes final go/no-go

## Handoff Contract

Every handoff includes:

- Task ID
- Current state
- Output artifact path
- Blocking risks
- Next owner

## Conflict Rule

- If two roles need same file, orchestrator serializes ownership.

