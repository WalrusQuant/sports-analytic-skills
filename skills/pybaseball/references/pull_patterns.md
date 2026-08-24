# pybaseball Pull Patterns

## Season tables
```python
from pybaseball import batting_stats, pitching_stats
batting_stats(2024)
pitching_stats(2024)
```

## Statcast (bounded)
```python
from pybaseball import statcast
statcast("2024-04-01", "2024-04-07")
```

Always snapshot and log the function + date window.
