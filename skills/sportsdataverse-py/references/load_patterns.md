# SDV Load Patterns

1. Start with schedule/scoreboard
2. Move to team/player box or pbp only if needed
3. Convert to pandas if downstream sports_ds expects pandas
4. Snapshot parquet with season/date in the filename
5. Log package version

Always verify column names — SDV APIs evolve.
