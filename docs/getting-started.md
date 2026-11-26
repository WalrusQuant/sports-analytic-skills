# Getting started

## Install the skills

```bash
npx skills add WalrusQuant/sports-analytic-skills
```

One skill:

```bash
npx skills add WalrusQuant/sports-analytic-skills --skill eda-sports -y
```

The full pack:

```bash
npx skills add WalrusQuant/sports-analytic-skills --all
```

No clone is required.

## Point the agent at data

sportsleader-data is the default source. The file list is the [manifest](https://github.com/WalrusQuant/sportsleader-data/releases/download/manifest/manifest.json). When the sports-leader connector is connected, `data-sources` uses that instead of a manual download. The connector repository is [sports-leader-mcp](https://github.com/WalrusQuant/sports-leader-mcp). A client may show the connector as `sports-leader-v05`.

```text
Use data-sources and eda-sports on the NFL games file for the 2024 season.
Confirm completed games, score nulls, and home and away ids before modeling.
```

```text
Use validation-design on this feature table. The prediction is made at
kickoff. Create season walk-forward folds and lock the primary metric.
```

Each skill names the fields it needs. If a sportsleader-data column is not in the manifest entry, the agent should say so instead of inventing it.

## What a skill contains

```text
skills/<id>/SKILL.md
skills/<id>/references/
```

Examples in a skill are illustrative. Analysis runs in the user's environment, against sportsleader-data or a file the user owns.
