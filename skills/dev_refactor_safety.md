# Skill: Dev Refactor Safety

## Trigger

Apply when task includes refactor, cleanup, or structural change.

## Input

- Task card
- Impacted files
- Existing test coverage note

## Output

1. Safe-change plan (smallest first)
2. Backward compatibility risks
3. Required tests

## Guardrails

- Keep API behavior unchanged unless explicitly approved.
- Separate pure refactor from feature changes when possible.

