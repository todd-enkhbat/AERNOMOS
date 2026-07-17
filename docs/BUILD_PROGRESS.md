# Nomos Build Progress

Current phase: F

## Completed
- Phase A: Current-system audit (`orbital-cortex/docs/current-system-audit.md`, commit `c5d6f90`)
- Phase B: Mission data model + TruthStatus enum (`feat: add private mission planning data model`)
- Phase C: Anonymous private sessions + share-link access (`feat: add private anonymous mission sessions and share links`)

## In progress
Phase F: STAC catalog discovery (next in canonical order)

## Blockers
None

## Decisions
- Focus on mission planning before GPU execution.
- All user-facing values require truth-status labels.
- User missions must not be publicly enumerable.
- Follow the dependency-corrected execution order in `docs/NOMOS_BUILD_PLAN.md` (not alphabetical A→T).
- Prefer updating `orbital-cortex/docs/current-system-audit.md` as the Phase A audit location (not a duplicate under `docs/`).
- Phase B: mission tables are additive UUID + PostGIS models; legacy Job/Scene/Detection string-ID tables are unchanged so the demo path stays intact.
- Phase B: `organization_id` / `converted_user_id` are UUID columns without FKs until org/auth tables exist.
- Phase B: missions require at least one owner (`anonymous_session_id` OR `organization_id`) via CHECK constraint.
- Phase C: session + share tokens use `secrets.token_urlsafe(32)` with SHA-256 hashes only; raw tokens never stored.
- Phase C: production cookies are HttpOnly + Secure + SameSite=Lax with optional `Domain=.nomosorbital.com`; local dev uses host-only cookies via Next.js `/api/oc/*` rewrite proxy.
- Phase C: curated public examples use `missions.is_example=true` and a stable examples org UUID; private lists exclude them.
- Phase C: legacy `/jobs` remains reachable by direct URL for the demo but is removed from primary nav.
- Follow-up: public `GET /v1/jobs` lists curated `is_example` jobs only; visitor submissions are hidden from the list (still openable by ID). Seed promotes up to 3 complete jobs as examples when none exist.

## Phase C — work completed
- Anonymous session bootstrap (`POST /v1/sessions`), current session (`GET /v1/sessions/me`), end session (`DELETE /v1/sessions/me`)
- Private mission CRUD list/create/get scoped to session cookie
- Share-link create + revoke; read access via `X-Nomos-Share-Token` or `share_token` query
- `is_example` migration + seeded public example mission
- Frontend `/missions` + `/missions/[id]`, demo environment banner, nav/footer updates, same-origin API proxy
- Unauthorized-access tests (cross-session, no cookie, revoked/expired share tokens, production cookie flags)

## Files changed
- API: `app/core/{tokens,sessions,missions,config}.py`, `app/deps/auth.py`, `app/models/mission.py`, `app/routes/{sessions,missions}.py`, `app/db/mission_orm.py`, `app/seed.py`, `app/main.py`, `.env.example`
- Migration: `a3b4c5d6e7f8_mission_is_example.py`
- Tests: `tests/test_mission_sessions.py`
- Web: `app/missions/**`, `lib/api.ts`, `next.config.mjs`, layout/header/footer/nav, `DemoEnvironmentBanner`, dashboard CTA
- Generated: `openapi.json`, `lib/generated/api-types.ts`
- `docs/BUILD_PROGRESS.md`

## Tests run
- `ruff check app tests scripts` — pass
- `mypy app` — pass
- `pytest tests -q` — 33 passed
- `npm run lint` / `npm run build` — pass

## Unresolved issues / risks
- Cross-origin cookie auth in production still requires `SESSION_COOKIE_DOMAIN=.nomosorbital.com` + CORS credentials (configured) on Fly; Vercel must call `api.nomosorbital.com` with credentials or use a same-origin proxy.
- Local mission APIs rely on `/api/oc` rewrite; job demo still uses `NEXT_PUBLIC_API_BASE_URL` without cookies.
- Guided mission builder UI is still minimal (title + default AOI); Phase E expands the form.
- `GET /v1/jobs` now returns curated `is_example` jobs only; non-example rows remain in DB and reachable by ID (not deleted). Ops analytics still TBD (Phase O).

## Architecture decisions
- Dependencies in `app/deps/auth.py` for optional/required session and mission access (owner vs share token vs public example).
- Expired anonymous sessions are cleaned on session bootstrap (CASCADE deletes their missions).
- Share tokens returned once at creation; only hashes persisted.

## Next phase
Phase F — STAC catalog discovery (Microsoft Planetary Computer / Earth Search behind `DataCatalogProvider`).
