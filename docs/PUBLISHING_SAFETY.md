# Publishing Safety — Autonomous SEO Agent OS

**Status:** Phase 2 — Stub (no implementation)

---

## Overview

Publishing is the most sensitive operation. This document defines safety protocols.

**Non-negotiable:** Human approval required before any content goes live.

---

## Publishing Workflow

### 1. Draft Creation

- WordPress: stored as WordPress auto-draft via REST API
- GitHub: stored as file in a private branch, PR created with draft status

Draft record status: `pending`.

### 2. Human Review

User reviews draft in dashboard:

- Approve → `approved`
- Reject → `rejected`
- Request changes → remains `pending`

### 3. Publish

Only approved drafts can be published.

```http
POST /publishing/jobs
{
  "draft_id": "uuid",
  "target": "wordpress|github",
  "initiated_by": "user_uuid"  // future auth
}
```

Background job applies the change.

---

## Safety Guarantees

- Endpoints return `202 Accepted` and queue background job
- Background job verifies:
  - Draft is approved
  - Human initiator (future auth)
  - Target credentials present
- Job records: who approved, when, what changed, job status
- On failure: alert human, do not auto-retry

---

## Rollback

- WordPress: restore previous post revision
- GitHub: revert commit/branch

Rollback is a human-initiated action. Audit log shows reason.

---

## What We Will NOT Do

- Auto-publish based on schedule or quality
- Push directly to production without human
- Overwrite without backup
- Bypass approval for any integration

---

## Open Items (TODO)

- [ ] Storage model for `ContentDraft`
- [ ] `PublishingApproval` table (status enum)
- [ ] Approve/Reject UI in dashboard
- [ ] Publish endpoint
- [ ] Rollback endpoint
- [ ] Audit log table (`PublishingJob`)
- [ ] Tests: approve → publish, reject → no change, rollback

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`