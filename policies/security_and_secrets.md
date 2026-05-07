# Security And Secrets

## Rules

1. Never commit plaintext credentials.
2. Keep environment values in `.env` (ignored by Git).
3. Redact sensitive data from logs before sharing.
4. Scope MCP/API credentials to minimum required access.

## Review Checklist

- Secret scan before push
- Permissions follow least privilege
- Production actions require explicit approval

