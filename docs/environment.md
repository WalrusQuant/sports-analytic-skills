# Environment

What people actually need installed to use the data-plane skills.

## Minimal judgment-only mode

If you only want methodology skills (doctrine/validation/etc.):

- any Agent Skills-compatible host
- no sports packages required

## Recommended analysis environment (Python)

### System

- Python 3.10+
- git
- enough disk for parquet caches (NFL multi-season PBP can be hundreds of MB+)

### Create an env

```bash
# uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -r requirements/python-data.txt

# or pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/python-data.txt
```

### Core packages

See `requirements/python-data.txt`:

- data: `pandas`, `polars`, `pyarrow`, `numpy`
- stats/ML: `scipy`, `scikit-learn`, `statsmodels`
- viz: `matplotlib`
- sports loaders: `nflreadpy`, `sportsdataverse`, `pybaseball`

### Optional extras

Install only when needed:

```bash
pip install statsbombpy
# R toolchain if using nflreadr/hoopR/cfbfastR instead of Python
```

## Network / cache expectations

Many loaders hit GitHub releases or public APIs.

- first call downloads; later calls should cache
- `nflreadpy` supports memory/filesystem cache via env vars:
  - `NFLREADPY_CACHE=memory|filesystem|off`
  - `NFLREADPY_CACHE_DIR=...`
  - `NFLREADPY_CACHE_DURATION=...`
- be polite with scrapers; expect rate limits and breakage

## Agent host expectations

For package skills with `scripts/`:

- host can run Python
- project venv is activated or interpreter path is known
- outbound HTTPS allowed for first data pull (unless using offline snapshots)

## Offline / air-gapped mode

Possible only if you pre-download datasets:

1. run loaders once on a networked machine
2. save parquet/csv snapshots into `data/` (not committed by default)
3. point analyses at local files
4. document snapshot date in `experiment-log`

## Sanity checks

```bash
python -c "import nflreadpy, sportsdataverse, pybaseball, polars, sklearn; print('ok')"
python skills/nflreadpy/scripts/smoke_load.py
```

If imports fail, fix environment before modeling.

## Related

- [data-ecosystem.md](./data-ecosystem.md)
- skills: `environment-setup`, `data-sources`, `nflreadpy`, `sportsdataverse-py`, `pybaseball`
