# Phase M — Lightweight real CPU execution (no GPUs)

**Copy this entire file into a new agent chat. Execute only this phase. Stop when done.**

## Product goal

Prove Nomos can **execute** one real plan step without GPUs or onboard satellites. Measure real durations as `OBSERVED`. Planner distinguishes planned vs executed steps.

## Interface

```python
class ExecutionProvider:
    def capabilities(self) -> ProviderCapabilities: ...
    def estimate(self, task: ExecutionTask) -> ExecutionEstimate: ...
    def submit(self, task: ExecutionTask, idempotency_key: str) -> ExternalJob: ...
    def status(self, external_job_id: str) -> ExternalJobStatus: ...
    def cancel(self, external_job_id: str) -> None: ...
    def result(self, external_job_id: str) -> ExecutionResult: ...
```

Implement `LocalCpuExecutionProvider` running on the existing ARQ worker.

## First real tasks (pick ≥1 end-to-end; more is better)

- Fetch remote metadata (SSRF-safe allowlist — harden fully in Phase S, but do not fetch arbitrary URLs)
- Copy / download a small asset (prefer Planetary Computer SAS or local fixture GeoTIFF)
- Crop a GeoTIFF (rasterio)
- Generate a thumbnail
- Raster statistics
- Checksum
- Inspect dimensions
- Metadata → JSON
- Save result artifact to R2/local object store

## Requirements

- Measure transfer time, execution duration, input/output size, storage location → store as **OBSERVED**
- Idempotent submit via `idempotency_key`
- Failures visible and recoverable
- Mission plan steps update from `planned` → `executed` / `failed`
- **No GPU inference**, no fake onboard completion

## API

- `POST /v1/missions/{id}/plans/{plan_id}/execute` (owner) for an allowed step type
- `GET` execution status / result

## Tests

- End-to-end local CPU task with fixture raster
- Idempotent retry
- Failure path
- Artifact exists in object store

## Dependencies

- Add `rasterio` / pillow as needed; update Docker image

## Acceptance criteria

- [ ] ≥1 real CPU task runs end-to-end
- [ ] Artifact stored; measured duration shown as OBSERVED
- [ ] Idempotent retries; failures visible
- [ ] Planner/UI distinguishes planned vs executed
- [ ] `BUILD_PROGRESS.md` updated

## Commit message

```
feat: add lightweight real CPU execution provider
```

## Stop

Next is Phase N.
