# Product Charter — Sports Analytic Skills

## What this is

A portable collection of agent skills for sports analytics and modeling.

The skills are the product. They operate on user-owned data and public
dependencies without requiring this repository's Python package. The optional
`sports_ds` toolkit supplies prebuilt public-data adapters and reference
workflows through the dedicated `sports-ds-bridge` skill.

## Users

- Analysts and builders working with sports data.
- AI coding agents that need rigorous, sports-specific decision guidance.
- Users who already have data and should not be forced into a new pipeline.
- Users who need public data and may opt into a supported loader or toolkit.

## In scope

- Team-game and player-game exploration.
- Time-safe features and as-of ratings.
- Statistical and predictive modeling.
- Time-ordered validation, leakage audits, and calibration.
- Simulation, interpretation, reproducibility, and honest reporting.
- Public-data source selection and loading guidance.
- An optional bridge to the `sports_ds` toolkit.

## Out of scope

- Requiring a canonical pipeline or panel for generic analysis.
- Treating `sports_ds` as an undeclared dependency of skill installation.
- Paid vendors, wagering execution, pick selling, or guaranteed-profit claims.
- A hosted dashboard or complete player-valuation platform.

## Success criteria

- A skill-only install can complete documented workflows on supplied artifacts.
- No generic skill imports or instructs users to install `sports_ds`.
- Every helper validates its input contract and runs outside the repository root.
- The bridge clearly discloses and isolates optional toolkit setup.
- Tests cover skill validation, forbidden imports, isolated help, and toy data.
- The optional toolkit retains its independent package test suite.
- A cold agent can choose a skill, identify required inputs, and produce an
  honest result without discovering hidden infrastructure.

## Non-negotiables

- Time safety at decision time T.
- Baselines before complexity.
- Time-ordered validation for ordered sports data.
- Explicit grain, schema, provenance, and limitations.
- No hidden runtime dependencies.
