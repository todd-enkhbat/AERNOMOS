# Phase P — Mission feedback and design-partner capture

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

After a plan is generated, collect lightweight feedback and optional design-partner leads without blocking the planner.

## UI (on `/missions/[id]` after plans exist)

### “Was this plan useful?”

- yes / partly / no
- optional comment (cap length; do not require)

### “Use this for a real mission”

Fields:

- name, work email, organization, role
- mission type, requested integration
- permission to contact (required checkbox)

Do **not** require this before plan generation.

## Backend

- Tables or models for `MissionFeedback` and `DesignPartnerRequest` (private; session-linked optional)
- Rate limit + honeypot field for spam
- Internal export endpoint (admin token) — leads never public

## Acceptance criteria

- [ ] Feedback submittable quickly
- [ ] Design-partner requests stored privately
- [ ] Spam protection present
- [ ] Tests for validation + rate limit basics
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add mission feedback and design partner requests
```

## Stop

Next is Phase Q.
