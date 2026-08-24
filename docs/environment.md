# Environment

## Skill users

A skill-only installation has no shared mandatory Python environment. Use the
user's existing project environment and install only the public dependencies
disclosed by the selected helper.

Common optional packages include:

- tabular work: `pandas`, `numpy`, `pyarrow`;
- modeling: `scikit-learn`, `scipy`, `statsmodels`;
- visualization: `matplotlib`, optionally `seaborn`;
- public data: `nflreadpy`, `sportsdataverse`, or `pybaseball`.

Bundled helpers must display `--help` before importing optional heavy packages.

## Repository contributors

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

The editable install is for developing the optional `sports_ds` toolkit. It is
not part of the generic skill user journey.
