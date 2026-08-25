# Public Sports Source Matrix

This is a discovery checklist, not a current ranking or coverage guarantee.
Verify upstream documentation, access, release freshness, and terms when making
the plan; record the evidence in the source-plan artifact.

| Need | Candidate ecosystem examples | Selection evidence |
|---|---|---|
| NFL PBP / schedules / rosters / weekly | nflverse via `nflreadpy`; maintained public league tooling | required table, season, grain, schema, terms |
| College football | maintained public college modules, including SportsDataverse where applicable | competition, season, stable IDs, rate/access terms |
| Basketball | maintained league/public modules, including SportsDataverse where applicable | league/table coverage, field definitions, IDs |
| MLB pitch / Statcast / season data | public MLB tooling such as `pybaseball`; maintained releases | query grain, bounded dates, revision behavior |
| Hockey | maintained league/public modules, including SportsDataverse where applicable | league/table coverage, timestamps, stable IDs |
| Soccer events | documented open event providers and maintained public modules | competition rights, event semantics, redistribution terms |

Rules:

- Prefer release loaders over live scrapers
- State analytical grain and each source's native grain/key
- Document aggregation and joins whenever those grains differ
- Snapshot for reproducible offline analysis
- Source choice does not create predictive value by itself
