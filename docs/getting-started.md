# Getting started

## Install skills into an agent

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

## Install Python stack for data + modeling

```bash
git clone https://github.com/WalrusQuant/sports-analytic-skills.git
cd sports-analytic-skills
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/python-data.txt
python skills/nflreadpy/scripts/smoke_load.py
```

## First real path

1. `environment-setup`
2. `data-sources` + `nflreadpy` (or SDV/pybaseball)
3. `eda-sports`
4. `sports-modeling-doctrine`
5. `baseline-models` + `predictive-modeling` or `ratings-strength-models`
6. `validation-design` + `leakage-audit`
7. `results-reporting`

## Read next

- `README.md`
- `docs/data-ecosystem.md`
- `docs/environment.md`
- `ARCHITECTURE.md`
