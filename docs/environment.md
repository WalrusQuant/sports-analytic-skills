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
pytest -q -m "not live"
```

Run live provider integrations separately:

```bash
SPORTS_DS_LIVE_TESTS=1 pytest -q -rs -m live
```

The editable install is for developing the optional `sports_ds` toolkit. It is
not part of the generic skill user journey.

For the optional multi-sport dependencies:

```bash
# macOS only: required by the XGBoost dependency imported by sportsdataverse
brew install libomp
pip install -e ".[dev,multi]"
```

Linux environments normally provide the equivalent OpenMP runtime through the
XGBoost wheel or system packages. No OpenMP runtime is needed for skill-only
installation.
