# Agent Roles and Responsibilities

This document defines the roles and ownership areas for all agents working in this repo.

## Agent Role Definitions

### Mr.R9 — Primary Builder / Integration Owner

- **Primary responsibility**: Implementation, feature development, integration
- **Areas**: Backend API development, router implementation, model fixes
- **Secondary**: Project brain setup and documentation foundation
- **Key strengths**: Building new functionality, connecting components
- **Memory file**: `agents/MrR9.md` — must read before starting any task

### Mr.R7 — Secondary Builder / Verification and Repeatability Owner

- **Primary responsibility**: Verification, repeatability, test coverage
- **Areas**: Running verification scripts, ensuring tests pass, confirming Docker behavior
- **Secondary**: Supporting implementation under Mr.R9's direction
- **Key strengths**: Validation, repeatability, catching edge cases
- **Memory file**: `agents/MrR7.md` — must read before starting any task

### Mr.M1 — Gatekeeper / Reviewer / Merge Safety Owner

- **Primary responsibility**: Review, safety, merge fitness
- **Areas**: Code review, blocking unsafe changes, ensuring Step Flash reviews happen
- **Secondary**: Final approval before any branch merges
- **Key strengths**: Security, correctness, risk assessment
- **Memory file**: `agents/MrM1.md` — must read before starting any task

### Cursor — Human-Supervised Coding Cockpit and Preview Layer

- **Primary responsibility**: Human-in-the-loop coding, visual preview, final verification
- **Areas**: IDE-based coding, manual review, final human sign-off
- **Role**: Not an autonomous agent — a human tool with AI assistance
- **Key strengths**: Visual feedback, contextual judgment, immediate human oversight

## Role Interaction Model

```
Mr.R9 (build) → Mr.R7 (verify) → Mr.M1 (review) → Cursor (human sign-off) → Merge
```

## Ownership Summary

| Area | Owner | Reviewer |
|------|-------|----------|
| Backend implementation | Mr.R9 | Mr.M1 |
| Verification/repeatability | Mr.R7 | Mr.M1 |
| Merge safety | Mr.M1 | Cursor (human) |
| Final human sign-off | Cursor | — |

---

*Last updated by: Mr.R9 (setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001-FINALIZE)*