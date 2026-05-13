# Known Issues

> ⚠️ **IMPORTANT**: Document only verified issues. Do not invent fake fixes or fake verification. If you don't know the fix, document the problem and move on.

## Verified Issues

| Issue | Severity | Discovered | Details |
|-------|----------|------------|---------|
| None recorded | — | — | No issues verified at setup time |

## Missing Pieces Identified During Setup

| Missing | Notes |
|---------|-------|
| Docker/Compose files | Not surveyed — Mr.R7 should inspect as part of verification |
| Env var documentation | Check `.env.example` for required variables |
| FK audit incomplete | Memory notes indicate some SQLAlchemy models may be missing ForeignKey constraints |

## Instructions for Agents

1. **Do not invent fake fixes** — If you discover an issue, document it clearly. Do not write "fixed" without actually fixing.
2. **Do not invent verification** — Run actual checks. If you didn't run it, don't report the result.
3. **Update this file when you discover new issues** — Add verified issues only.
4. **Mark issues as resolved only when actually resolved** — Include the fix commit hash when resolving.

## How to Add an Issue

```markdown
| Issue description | Severity | Discovered by | Date | Details |
```

Severity guide:
- **Critical**: Breaks the build or prevents deployment
- **High**: Major feature broken or significantly degraded
- **Medium**: Feature partially works with known workaround
- **Low**: Minor issue or cosmetic

---

*Last updated by: Mr.R9 (setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001)*