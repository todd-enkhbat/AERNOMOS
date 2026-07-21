# Analytics event schema

Privacy-safe product and planning analytics (Phase O). Storage: Postgres `analytics_events` table (`event_name`, allowlisted `payload` JSONB, `created_at`).

**Allowlist rule:** each event has exactly one Pydantic payload model with `extra='forbid'`. Unknown keys raise at emit time — never silently dropped.

**Hashing:** `session_id_hash` uses HMAC-SHA256 with `ANALYTICS_HASH_SALT` (separate from auth keys). Raw session cookies and share tokens are never logged.

**Forbidden everywhere:** `aoi_geometry`, `aoi_polygon`, `mission_notes`, `raw_query_text`, `session_token`, `share_token`, `user_email`, `ip_address`, or any unbounded free-form user text.

Regenerate this file:

```bash
cd orbital-cortex/apps/api && python -m app.scripts.generate_analytics_schema_doc
```

## Event names

- `mission_started`
- `mission_completed`
- `plan_generated`
- `data_candidates_found`
- `plan_exported`
- `plan_shared`
- `example_viewed`
- `user_returned`
- `provider_connection_requested`
- `planning_failure_reason`

## Planning failure reasons (enum only — no raw exception text)

- `no_candidates_found`
- `provider_timeout`
- `invalid_aoi`
- `schema_validation_failed`
- `unknown`

## Payload allowlists

### `mission_started`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `session_id_hash` | `str` |
| `resource_types_requested` | `list[str]` |
| `timestamp` | `datetime` |

### `mission_completed`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `plan_id` | `UUID` |
| `session_id_hash` | `str` |
| `timestamp` | `datetime` |

### `plan_generated`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `plan_id` | `UUID` |
| `step_count` | `int` |
| `candidate_count` | `int` |
| `generation_seconds` | `float` |
| `timestamp` | `datetime` |

### `data_candidates_found`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `candidate_count` | `int` |
| `provider_id` | `str` |
| `search_duration_seconds` | `float` |
| `timestamp` | `datetime` |

### `plan_exported`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `export_type` | `str` |
| `success` | `bool` |
| `timestamp` | `datetime` |

### `plan_shared`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `share_link_id` | `UUID` |
| `session_id_hash` | `str` |
| `timestamp` | `datetime` |

### `example_viewed`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `timestamp` | `datetime` |

### `user_returned`

| Field | Type |
| --- | --- |
| `session_id_hash` | `str` |
| `days_since_last_seen` | `float` |
| `timestamp` | `datetime` |

### `provider_connection_requested`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `provider_name` | `str` |
| `integration_status` | `str` |
| `timestamp` | `datetime` |

### `planning_failure_reason`

| Field | Type |
| --- | --- |
| `mission_id` | `UUID` |
| `reason` | `PlanningFailureReason` |
| `timestamp` | `datetime` |
