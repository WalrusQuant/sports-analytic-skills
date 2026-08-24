# Environment Troubleshooting

| Symptom | Fix |
|---|---|
| command not found: sports-ds | activate venv; `pip install -e .` |
| ModuleNotFoundError: sports_ds | run from repo root editable install |
| nflverse download fail | check network; retry; update nflreadpy |
| empty panel | incomplete season / null scores |
| skill script import path errors | cwd = repo root; venv on |
| optional multi-sport missing | `pip install -e ".[multi]"` |
