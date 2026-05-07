# Framework Pitfalls Checklist

Use before final handoff on framework-specific tasks.

## Backend

- [ ] Async vs blocking calls checked
- [ ] Input/output validation enforced
- [ ] Transaction boundaries explicit
- [ ] Error surfaces sanitized

## Frontend

- [ ] Loading/error/empty states handled
- [ ] Effect dependencies stable
- [ ] API error handling consistent
- [ ] Accessibility checks for key interactions

## Cross-Cutting

- [ ] Logs do not expose sensitive data
- [ ] Tests include at least one failure path

