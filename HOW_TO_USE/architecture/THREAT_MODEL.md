# Threat Model

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

## Assets

- Collection records
- Token metadata
- Tenant config
- Audit and migration logs
- Indexes and search metadata

## Threat Actors

1. External attacker with stolen disk.
2. Hosting operator with filesystem access.
3. Rogue internal admin.
4. Cross-tenant attacker.
5. Network attacker.
6. Compromised app host.

## Protected Threats

- Stolen encrypted files: unusable without token context.
- Tampering: GCM tag validation fails decryption.
- Cross-tenant leakage: tenant-specific key derivation.
- Replay/tamper of audit: chain hash verification detects breaks.

## Not Fully Covered

- Token compromise in memory.
- Keylogger capture during entry.
- Malicious runtime or interpreter compromise.

## Recommendations

- Store tokens in secrets manager.
- Never hardcode credentials.
- Apply strict filesystem ACLs.
- Use viewer-scoped service tokens by default.
- Review and export audits regularly.

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
