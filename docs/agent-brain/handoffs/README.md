# Task Handoffs

This folder stores task handoff documents created when an agent completes a task or hands off to another agent.

## Purpose

When you finish a task or need another agent to continue:

1. Create a handoff document in this folder
2. Name it: `<TASK_ID>-<YOUR_AGENT_ID>.md`
3. Fill in all required sections (see template below)
4. Update `01-CURRENT-STATE.md` if project state changed

## Handoff Template

```markdown
# Handoff: <TASK_ID>

## Identity
- **Task ID**: <TASK_ID>
- **Branch name**: <branch>
- **Base branch**: <base>
- **Commit hash**: <hash>

## Files Changed
- <file 1>
- <file 2>

## Commands Run
- <command 1>
- <command 2>

## Docker/Compose Status
- Files found: Yes/No
- Services status: <status>

## Verification Results
- Check 1: <result>
- Check 2: <result>

## Blockers
- <blocker 1>
- <blocker 2> (or "None")

## Next Recommended Action
For <next agent>:
1. <action 1>
2. <action 2>
```

## Rules

- **Do not delete another agent's handoff file**
- **Do not overwrite another's handoff** — create a new file with your own name
- Handoffs are owned by the agent who created them

---

*Folder created by Mr.R9 — setup task MULTICA-OBSIDIAN-BRAIN-SETUP-001*