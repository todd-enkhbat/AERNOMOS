# Nomos Orbital

*(repo: AERNOMOS — fka AERNOMOS / OrbitalCortex, product name is now Nomos Orbital)*

**Kubernetes for orbital infrastructure.** A routing and orchestration layer so
customers can submit a compute job to orbital infrastructure the same way
they'd call a cloud provider — one SDK, instead of building against every
supplier's own API from scratch.

## Status: MVS skeleton (v0.1)

This is the Week 1 scaffold: **submit → route → log**, working end-to-end
against one simulated node. No real hardware integration yet.

Note: the original plan named T-REX (Brown's NASA-NIAC quantum satellite) as
the first integration target. That node won't fly until 2032, so this
skeleton deliberately routes to a generic `SimulatedNode` instead of coupling
to T-REX specifically. Any real node — quantum, GPU, whatever comes online
first — plugs in later as a `Node` subclass without changing the client or
router.

### What's here

```
src/nomos/
  models.py        Job, JobResult, JobStatus
  nodes/base.py     Node — abstract interface every real node implements
  nodes/simulated.py SimulatedNode — stands in for real hardware for now
  router.py         picks an available node that supports the job type
  client.py         NomosClient.submit_job() — the one call a customer makes
  job_log.py        JSONL event log (submitted/routed/completed/failed)
examples/demo.py     end-to-end demo — the basis for the Week 2 demo video
tests/               pytest coverage of the happy path + failure paths
```

### What's explicitly out of scope (for now)

Multiple nodes / intelligent scheduling, billing, the full compliance/audit
layer, and any specific node integration (T-REX or otherwise) — per the PRD.

### Run it

```bash
pip install -e ".[dev]"
python examples/demo.py      # end-to-end run, prints result + log path
pytest                        # 4 tests: happy path, unsupported job type,
                               # no-node-available, simulated failure
```

### Next (Week 2, per Sprint Plan)

- Replace `SimulatedNode` with (or add alongside) a real node integration
- Record the 90-second demo video
- Start customer discovery calls
