# Compliance Guardrails — Autonomous SEO Agent OS

**Status:** Phase 2 — Definitions Only

---

## Principles

1. No fake claims, reviews, testimonials, credentials, awards, statistics
2. No black-hat SEO (keyword stuffing, doorway pages, cloaking, link schemes)
3. No auto-publish; human approval required
4. Respect robots.txt and ToS; use approved APIs
5. Every content output passes usefulness check
6. YMYL topics require mandatory human review
7. Cannabis businesses follow strict compliance rules

---

## YMYL (Your Money or Your Life)

YMYL topics include:
- Financial advice (loans, investments, taxes)
- Medical/health advice
- Legal advice
- Safety-critical instructions

**Rules:**

- `is_ymyl=True` flag in Business profile
- YMYL content never auto-publishes
- Sources must be cited; no vague claims
- Disclaimers required ("consult a professional")

---

## Cannabis Compliance

For `is_cannabis=True` businesses:

- No medical efficacy claims (unless licensed provider)
- Age restriction gating on website
- Platform rule awareness (Facebook, Google Ads)
- Follow state-specific marketing regulations
- Payment processing compliance

System must flag cannabis topics for extra review.

---

## No Fake Content Policy

**Writing/Editor Agent must never:**

- Invent customer names or testimonials
- Create fake reviews
- Claim awards/recognition not received
- State statistics without real data
- Add credentials not held
- Assert partnerships/affiliations that don't exist

**Enforcement:** QA agent scans outputs; mark as blocker if fake content detected.

---

## Acceptable Use

- Use real business information
- Use real customer testimonials (with permission)
- Use real statistics (cite source)
- Be honest about strengths/limitations

---

## Monitoring (TODO)

Potential table: `ContentComplianceFlag`

- `ContentDraft` ID and type
- `flag_type`: enum [YMYL, CANNABIS, FAKE_CLAIM, NEEDS_REVIEW]
- `flagged_by`: Agent or human
- `resolution`: approved/fixed/rejected
- `reviewer`: Human if any
- `published_at`: timestamp

Audit log should be queryable for compliance reviews.

---

*Last updated:* 2025-05-07
*Branch:* `feature/backend-phase2`