# Security Policy

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Reporting Vulnerabilities

Email: kaushikmangukiya360@gmail.com  
Subject: `[SECURITY] chronovault — brief description`

Include:

- Clear reproduction steps
- Impact assessment
- Suggested remediation (if known)

Target initial response: within 48 hours.

Do not open public GitHub issues for active security vulnerabilities.

## Supported Versions

Only the latest release receives security updates.

## Security Design Principles

1. Encrypt everything at rest.
2. Never persist derived keys.
3. Enforce authenticated decryption.
4. Use atomic file replacement for writes.
5. Lock all writes to prevent corruption.
6. Isolate tenants cryptographically and physically.
7. Validate IP and role before sensitive operations.
8. Keep audit logs append-only and chain-hashed.
9. Minimize secret exposure in errors.
10. Reject malformed encrypted envelopes.
11. Prefer explicit scope for tokens and links.
12. Fail fast on integrity or auth violations.

## PGP Key

PGP key publication will be added in a future release.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
