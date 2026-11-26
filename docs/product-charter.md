# Product charter

## What this is

A portable collection of agent skills for sports analytics and modeling.

The skills are the product. They describe how to work on user-owned tables and on sportsleader-data. This repository does not ship a runtime.

## Users

- Analysts working with sports data.
- Agents that need sports-specific decision guidance.
- People who already have a table and should not be sent through a hidden pipeline.

## In scope

- Team-game and player-game exploration on the six leagues in sportsleader-data.
- Time-safe features and as-of ratings.
- Statistical and predictive modeling.
- Time-ordered validation, leakage audits, and calibration.
- Simulation, interpretation, and honest reporting.

## Out of scope

- A Python toolkit, bundled programs, or a required panel schema.
- Play-by-play or pitch-level acquisition. Those grains are not in sportsleader-data.
- Wagering execution, pick selling, or guaranteed-profit claims.
- A hosted dashboard.

## Success criteria

- An installed skill can be followed on a sportsleader-data file or a user-owned table.
- Dataset names in the skills match the manifest.
- A cold agent can name the required inputs and produce an honest limit.

## Non-negotiables

- Time safety at decision time T.
- Baselines before complexity.
- Time-ordered validation for ordered sports data.
- Explicit grain, schema, provenance, and limitations.
- Research use. Not a claim of betting edge.
