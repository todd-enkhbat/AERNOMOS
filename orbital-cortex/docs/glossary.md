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

A mocked period when an orbital node can communicate with a ground station. v0.1 uses deterministic `next_contact_minutes` values instead of physical orbital calculations.

## Ground Station

A simulated downlink location that can be paired with orbital nodes.

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
