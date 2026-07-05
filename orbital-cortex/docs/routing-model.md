# Routing Model

## Purpose

The router selects the best simulated execution path for a job. It should be deterministic, explainable, and simple enough to inspect during a demo.

## Candidate Inputs

Each candidate node is evaluated with:

- Model support
- Estimated latency
- Estimated cost
- Availability
- Contact window
- Compute preference fit
- Compliance tag fit
- Data locality

## Node Classes

| Type | Contact behavior | Notes |
| --- | --- | --- |
| `orbital` | Uses mocked `next_contact_minutes` | Better data locality, may wait for contact |
| `ground_cloud` | Always contact available | Reliable fallback, may cost more or add data movement |
| `ground_station` | Used as a downlink route, not primary AI compute | Paired with orbital nodes |

## Scoring Weights

The first implementation should use a transparent 100-point score.

| Factor | Max points | Notes |
| --- | ---: | --- |
| Model support | 25 | Required model support gets full credit |
| Latency | 20 | Lower estimated latency scores higher |
| Cost | 15 | Lower estimated cost scores higher |
| Availability | 15 | Uses node availability from sample data |
| Contact window | 10 | Immediate or near-term contact scores higher |
| Compute preference | 10 | Rewards user preference alignment |
| Compliance | 5 | Requires local demo compliance tags |

Candidates that do not support the requested job type should receive a very low score or be filtered out unless no compatible node exists.

## Latency Estimate

For orbital nodes:

```text
estimated_latency =
  next_contact_minutes
  + node.latency_minutes
  + selected_ground_station.latency_minutes
```

For cloud nodes:

```text
estimated_latency = node.latency_minutes
```

Ground/cloud nodes always have contact available.

## Cost Estimate

```text
estimated_cost =
  node.base_cost_usd
  * priority_multiplier
  * sensor_multiplier
```

Suggested multipliers:

| Field | Value | Multiplier |
| --- | --- | ---: |
| `priority` | `fastest` | 1.2 |
| `priority` | `cheapest` | 0.85 |
| `priority` | `most_reliable` | 1.1 |
| `sensor` | `SAR` | 1.1 |
| `sensor` | `optical` | 1.0 |
| `sensor` | `hyperspectral` | 1.25 |
| `sensor` | `any` | 0.95 |

## Compute Preference Rules

| Preference | Router behavior |
| --- | --- |
| `orbital_if_available` | Prefer compatible orbital nodes when cost and latency are reasonable |
| `ground_only` | Exclude orbital nodes from primary selection |
| `cheapest` | Increase cost weight and allow cloud fallback to win |
| `fastest` | Increase latency weight and allow immediate cloud execution to win |

## Compliance Rules

The MVP should only route jobs to nodes tagged for local commercial or research demo use. Any tag implying restricted, classified, or defense-only use should be excluded from the sample data and policy.

Required sample tag:

```text
non_defense
```

## Contact Windows

Contact windows are mocked. They should look realistic but not attempt orbital mechanics.

Suggested deterministic values:

| Node | Next contact |
| --- | ---: |
| `sim_leo_01` | 18 minutes |
| `sim_leo_02` | 11 minutes |
| `sim_kepler_like_node` | 27 minutes |
| `sim_starcloud_like_node` | 43 minutes |
| `aws_us_east_gpu` | 0 minutes |
| `coreweave_gpu_cluster` | 0 minutes |

## Example Explanation

Selected `sim_leo_02` because it supports SAR ship detection, has the next contact window in 11 minutes, meets the fastest priority, and costs 23% less than the cloud-only route.

## Candidate Score Shape

```json
{
  "node_id": "sim_leo_02",
  "score": 89.4,
  "model_support_score": 25,
  "latency_score": 17.2,
  "cost_score": 12.8,
  "availability_score": 13.8,
  "contact_score": 8.7,
  "preference_score": 8.9,
  "compliance_score": 5,
  "estimated_latency_minutes": 35,
  "estimated_cost_usd": 214,
  "reasons": [
    "Supports requested model",
    "Near-term contact window",
    "Matches orbital preference"
  ]
}
```

## Tie Breakers

When scores are within one point:

1. Prefer a node that supports the requested sensor and job type directly.
2. Prefer lower estimated latency for `fastest`.
3. Prefer lower estimated cost for `cheapest`.
4. Prefer higher availability for `most_reliable`.
5. Prefer the lexicographically smaller node id for deterministic output.
