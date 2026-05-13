# Agent Brain — Obsidian Knowledge Base

## What Is This Folder?

This folder (`docs/agent-brain/`) is the **shared memory and handoff system** for all Multica/Hermes agents working in this repo. It is a Git-tracked, Obsidian-compatible Markdown knowledge base.

Think of it as the project's **shared brain** — a place where agents document current state, decisions, workflows, runbooks, and task handoffs so that any agent (or human) can pick up work without guessing.

## How Agents Should Use It

1. **Before starting any task**, read `00-START-HERE.md` and `01-CURRENT-STATE.md`
2. **Before making a significant decision**, read `03-WORKFLOW-RULES.md` and `decisions/`
3. **When handing off a task to another agent**, write a handoff file in `handoffs/`
4. **When documenting a repeatable process**, write a runbook in `runbooks/`
5. **When a blocker or known issue is discovered**, update `05-KNOWN-ISSUES.md`

## Files to Read Before Starting Work

| File | Purpose |
|------|---------|
| `00-START-HERE.md` | This file — overall orientation |
| `01-CURRENT-STATE.md` | Current project status, base branch, known blockers |
| `02-AGENT-ROLES.md` | Who owns what — agent roles and responsibilities |
| `03-WORKFLOW-RULES.md` | Branch discipline, review requirements, handoff rules |
| `04-DOCKER-RUNBOOK.md` | Docker safety guide — how to run/inspect containers |
| `05-KNOWN-ISSUES.md` | Current known issues and missing pieces |
| `agents/README.md` | Agent memory structure — each agent must read this |
| `agents/MrR9.md` | Mr.R9's role memory — **Mr.R9 must read before starting** |
| `agents/MrR7.md` | Mr.R7's role memory — **Mr.R7 must read before starting** |
| `agents/MrM1.md` | Mr.M1's role memory — **Mr.M1 must read before starting** |

## Before Starting Any Task

1. Read your own agent memory file from `agents/<YourAgentId>.md`
2. Read `01-CURRENT-STATE.md`
3. Review the handoff file in `handoffs/` if one exists for your task
4. Confirm your branch is based on the correct commit

## How Task Handoffs Work

When you complete a task or need to hand off to another agent:

1. Create a handoff file in `docs/agent-brain/handoffs/`
2. Naming convention: `<TASK_ID>-<YOUR_AGENT_ID>.md`
3. Include: task ID, branch, base branch, commit hash, files changed, commands run, verification results, blockers, next recommended action
4. Update `01-CURRENT-STATE.md` if the overall project state changed
5. Do NOT delete or overwrite another agent's handoff file

## Connections

- **Git**: This brain is fully Git-tracked. All changes go through normal Git workflow.
- **Multica**: Issues track work items. The brain supplements issue tracking with contextual knowledge.
- **Hermes Agents**: Agents use this brain as long-term memory. Each agent should read relevant sections before starting.
- **Docker**: See `04-DOCKER-RUNBOOK.md` for safe Docker operations.
- **Cursor**: Human supervisors use Cursor as the coding cockpit and preview layer. The brain informs but does not replace Cursor.

## Obsidian Compatibility

This folder is a plain-Markdown knowledge base usable as:
- A standalone Obsidian vault
- A folder inside a larger Obsidian vault

No Obsidian plugins are required. The `.obsidian/` directory (if created by your local Obsidian instance) is gitignored.

## Protected Paths

The following are gitignored to prevent local UI/cache pollution:
- `.obsidian/` — Obsidian app data
- `.trash/` — Obsidian trash

---

*Last updated by: Mr.R9 (setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001-FINALIZE)*