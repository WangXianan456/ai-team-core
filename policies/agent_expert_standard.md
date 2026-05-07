# Agent Expert Standard

Objective: each role should reach production-grade engineering quality comparable to strong human engineers in scoped tasks.

## Capability Dimensions

1. Code and framework fluency
2. Software design and architecture judgment
3. Engineering delivery discipline
4. Security and compliance awareness
5. Debugging and incident handling
6. Cost and performance tradeoff awareness

## Role-Specific Bar

- PM: writes unambiguous, testable requirements with explicit scope and risk.
- Dev: delivers maintainable code with tests and minimal regression risk.
- QA: catches critical regressions early and provides reproducible reports.
- Ops: guarantees release safety, rollback readiness, and observability checks.
- Orchestrator: enforces quality gates and resolves cross-role conflicts.

## Expert Acceptance Criteria

1. First-pass QA rate >= 85%
2. Escaped critical defect rate <= 2% per release window
3. Mean rollback rate <= 3%
4. Cost per completed task shows non-increasing 4-week trend
5. Security checklist pass rate = 100% for release tasks

## Non-Negotiables

- No secret leakage.
- No release without rollback path.
- No bypass of security checks for P0/P1 tasks.

