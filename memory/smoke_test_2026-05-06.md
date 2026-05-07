# Smoke Test 2026-05-06

## Objective

Verify Codex can call Azure relay model (`gpt-5.3-codex`) with configured env.

## Result

- Status: pass
- Prompt: `Reply with exactly: CODEX_SMOKE_OK`
- Model output: `CODEX_SMOKE_OK`

## Usage Snapshot

- input_tokens: 15454
- output_tokens: 47
- logged_cost: 0.06238 USD

## Notes

- Test was executed with elevated permissions due local sandbox limitations.
- Core model call path is validated and can be used for self-improvement loops.

