# Skill: Dev Security Hardening

## Trigger

Apply when task touches authentication, input processing, data access, external calls, or deployment-sensitive code paths.

## Security Checklist

1. Input validation
- Validate and sanitize all external inputs.
- Reject invalid payloads with explicit errors.

2. Access control
- Verify auth and authorization checks are present at every sensitive boundary.
- Avoid relying on client-side checks.

3. Secret handling
- Never hardcode secrets.
- Read secrets from environment or secret store only.

4. Data protection
- Avoid logging sensitive fields.
- Use least-privilege database access.

5. Error handling
- Do not leak stack traces or sensitive internals to clients.
- Emit structured internal logs for debugging.

6. Dependency hygiene
- Check dependency vulnerabilities before release.
- Pin versions for critical dependencies where possible.

## Output Contract

1. Security checklist result (`pass` / `fail`) with evidence.
2. List of findings and remediation.
3. Residual risk statement before handoff to QA.

