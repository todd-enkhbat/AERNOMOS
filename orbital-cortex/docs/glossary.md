# Glossary

## Area Of Interest

The geographic area for a job. In v0.1 this can be represented as a bbox object or GeoJSON-like object.

## Candidate Score

A transparent score assigned to each possible compute node during routing.

## Cloud Fallback Node

A simulated ground cloud GPU resource used when orbital compute is unavailable, too slow, too expensive, or excluded by policy.

## Compute Node

A simulated resource that can execute an AI model. Nodes can be orbital, ground cloud, or ground station records.

## Compute Preference

The user's routing preference, such as `orbital_if_available`, `ground_only`, `cheapest`, or `fastest`.

## Contact Window

A real pass (AOS -> culminate -> LOS) computed by propagating the satellite's
TLE with SGP4 (Skyfield) against a ground station's location and 10-degree
elevation mask. Windows are precomputed into a cache from a pinned TLE
snapshot for deterministic demos; each carries a max elevation, duration, and
estimated downlink volume.

## Ground Station

A real public downlink site (KSAT, AWS Ground Station, Leaf Space) with
latitude/longitude/altitude and an elevation mask, paired with orbital nodes
by next-pass visibility.

## Job

A user-submitted request for AI analysis over a defined area of interest.

## Job Event

A lifecycle log entry attached to a job, such as `job_created`, `route_selected`, `execution_started`, or `result_ready`.

## Mock Inference

Deterministic fake model output used to make the local demo feel realistic without running a real model.

## Routing Decision

The selected route for a job, including selected compute node, selected ground station when relevant, fallback node, cost, latency, confidence, reasons, and candidate scores.

## SAR

Synthetic aperture radar. In this demo, SAR is the preferred sensor for ship detection and flood-like disaster response scenarios.
