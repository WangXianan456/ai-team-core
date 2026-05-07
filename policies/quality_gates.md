# Quality Gates

Release is blocked if any required gate fails.

## Required Gates

1. Acceptance criteria mapped to tests
2. Critical tests pass
3. No unresolved critical defects
4. Rollback procedure documented
5. Human approval recorded
6. Secret scan completed with no critical findings
7. Dependency vulnerability check completed for changed ecosystem

## Recommended Gates

- Static checks pass
- Performance sanity check for hot paths
- Observability signals confirmed
