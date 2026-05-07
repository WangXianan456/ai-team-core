# Role Access Matrix

| Role | Code Repo | Issue Tracker | Test Env | Prod Deploy | Monitoring | DB |
|---|---|---|---|---|---|---|
| orchestrator | read | write | read | approve-only | read | read |
| pm | read | write | none | none | read | none |
| dev | write-pr | read/write | read/write | none | read | read-only |
| qa | read | write | read/write | none | read | read-only |
| ops | read | read | write | write | write | read-only |

## Notes

- `write-pr`: allowed via branch/PR flow, no force push to protected branches.
- `approve-only`: can approve release gates, not execute deployments directly.

