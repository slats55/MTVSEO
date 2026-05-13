# Agent Memory Files

Each agent has a dedicated memory file in this folder. These files define permanent roles, responsibilities, checklists, and known failure risks.

## Purpose

- Keep agents focused on their designated role long-term
- Provide start/end checklists so each agent knows exactly what to do before and after a task
- Document known failure risks so agents can self-correct before problems occur

## Rules

- **Read your own memory file before starting any task**
- **Update your own memory file when your role evolves** — do not update another agent's file unless explicitly assigned
- **Handoffs still go in `docs/agent-brain/handoffs/`** — individual memory files are for persistent role definition, not task handoffs
- **GitHub is the source of truth** — all memory files are Git-tracked; local Obsidian edits must be committed

## Agent Memory Files

| File | Agent | Role |
|------|-------|------|
| `MrR9.md` | Mr.R9 | Primary Builder / Integration Owner |
| `MrR7.md` | Mr.R7 | Secondary Builder / Verification and Repeatability Owner |
| `MrM1.md` | Mr.M1 | Gatekeeper / Reviewer / Merge Safety Owner |

---

*Created by Mr.R9 — setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001-FINALIZE*