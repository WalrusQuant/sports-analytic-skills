# Setup troubleshooting

| Symptom | What to do |
|---|---|
| `npx` or `skills` is missing | Install Node, then rerun `npx skills add` |
| Connector tools are absent | Read the manifest and Parquet URLs in `data-sources`. Do not invent a second data path |
| `get_data_status` fails | Check that the client can reach GitHub. The manifest URL is public |
| A season file 404s | That season is not published. Read `files` in the manifest |
| NBA and NFL `2024` do not align | NBA `2024` is the 2023-24 season. NFL `2024` starts in 2024 |
| `ModuleNotFoundError: pyarrow` or DuckDB | Install them in the user's venv only if they asked for local reads |
| Empty score columns | The `games` row is not `completed`, or the team file has no line for that game |
