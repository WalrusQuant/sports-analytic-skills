# Environment

## Recommended analysis environment

- Python 3.10+
- git
- disk for parquet caches (multi-season NFL data can be hundreds of MB+)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional multi-sport loaders:

```bash
pip install -e ".[multi]"
```

## Core packages

Pulled by `sports_ds` / `pyproject.toml`:

- data: `pandas`, `numpy`, `pyarrow`
- stats/ML: `scipy`, `scikit-learn`, `statsmodels`
- NFL: `nflreadpy`
- viz: `matplotlib`

Optional:

- `sportsdataverse`, `pybaseball`
- `pingouin`, `seaborn` for richer classical stats / plots

## Verify

```bash
pytest -q
sports-ds nfl-eda --seasons 2024
python skills/predictive-modeling/scripts/leakage_smoke.py
```
