# Framework Pack: Backend FastAPI

## Use Cases

- Python backend API endpoints
- Request/response validation
- Dependency injection and service layering

## Design Heuristics

1. Keep router thin, service layer explicit.
2. Validate input/output using Pydantic models.
3. Avoid business logic in endpoint functions.
4. Use explicit transaction boundaries for write paths.

## Common Pitfalls

- Mixing async and blocking I/O in request path
- Returning ORM objects directly without serialization control
- Missing timeout/retry policies on outbound calls

## Test Strategy

- Endpoint contract tests (status, schema, auth behavior)
- Service unit tests for business rules
- One failure-path test for each critical endpoint

