# Delivery Flow

## State Machine

`todo -> doing -> qa -> release -> done`

Optional rollback path: `release -> doing`

## Stage Rules

1. `todo`
- Task card complete
- Acceptance criteria complete

2. `doing`
- Dev owns implementation
- Self-test evidence attached

3. `qa`
- QA executes matrix
- Defects logged with severity

4. `release`
- Ops checklist complete
- Rollback validated
- Human approval required

5. `done`
- Release verified
- Notes written to `memory/` and `decisions/` if needed

