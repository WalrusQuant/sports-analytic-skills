---
name: environment-setup
description: >
  Create and verify a portable Python environment for sports analysis. Use for
  machine setup, onboarding, dependency diagnosis, or reproducibility checks.
license: MIT
metadata:
  version: "0.12.0"
---

# Environment Setup

## Outcome

Produce an isolated environment, explicit dependency record, and
machine-readable verification report for the selected analysis. Install only
the public scientific libraries and loaders the work actually requires.

Read [the verification checklist](references/verify_checklist.md) while
verifying a new environment and
[the troubleshooting guide](references/troubleshooting.md) when an install,
import, output, or loader probe fails.

## When to Use This Skill

Use when:

- onboarding a new machine or project for sports analysis;
- diagnosing broken imports, wrong interpreters, or conflicting packages;
- locking a reproducible environment before serious modeling;
- verifying that selected skill helpers and loaders work offline at `--help`.

Do **not** use this skill to:

- install the optional repository toolkit / bridge path → `sports-ds-bridge`;
- choose a public data source → `data-sources`;
- run EDA or modeling once the environment already works.

| Need | Go instead |
|---|---|
| Optional toolkit bridge | `sports-ds-bridge` |
| Source selection | `data-sources` |
| Analysis after setup | the relevant modeling skill |

## Plan before installing

Record operating system/architecture, Python version and executable, analysis
tasks, named loaders, required file/plot formats, CPU/memory/storage constraints,
network/proxy constraints, and whether exact reproduction or flexible minimum
versions are needed. Separate core packages from optional loaders and dev tools.

## Create an isolated environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas scipy scikit-learn statsmodels matplotlib pyarrow
```

On Windows PowerShell use `.venv\Scripts\Activate.ps1`. Use `python -m pip` so
the installer follows the active interpreter. Do not modify the system Python.

Install public loaders only when the source plan requires them:

```bash
python -m pip install nflreadpy
python -m pip install pybaseball
python -m pip install sportsdataverse
```

Do not install every loader “just in case”; optional native/transitive
dependencies add conflicts and weaken reproducibility.

## Verification ladder

Work from cheapest/local to bounded/networked. Stop at the first unexplained
failure; later successes do not erase it.

1. Record `python --version`, executable path, platform, and `python -m pip --version`.
2. Confirm Python and pip resolve inside the same environment.
3. Import the minimum scientific packages and record resolved versions.
4. Run every selected helper or loader's `--help`; help must not make a network call.
5. Test required local outputs: JSON, Parquet, and images as applicable.
6. If network is authorized, run one small bounded public-data sample.
7. Save the verification report; freeze dependencies only after success.
8. Recreate from the lock in a clean environment for high-stakes reproducibility.

```bash
python /path/to/environment-setup/scripts/verify_install.py
python /path/to/environment-setup/scripts/verify_install.py \
  --packages numpy,pandas,sklearn --out data/environment.json
python -m pip freeze > requirements-lock.txt
```

The portable verifier accepts comma-separated import names through `--packages`.
Import names can differ from distribution names (`sklearn` versus
`scikit-learn`); document both when that matters.

The verifier checks the current interpreter, `python -m pip`, and the requested
imports only. Its JSON lists helper, output, network, and lock-recreation checks
as not run; `OK` is therefore not full environment sign-off. A standard-library
venv is detected from Python prefixes, but other environment managers may not be.
Run and document the remaining ladder steps separately. On a completed probe,
stdout is exactly one JSON document; package import output is captured inside
the relevant package result. With `--out`, the same JSON is also written to that
path, and no human status line is mixed into stdout.

## Verification matrix

| Layer | Probe | Pass evidence |
|---|---|---|
| Interpreter | version, executable, prefixes | intended environment path/version |
| Installer | `python -m pip --version` | pip invoked by that exact interpreter |
| Core imports | minimal package list | import + resolved versions (covered by verifier) |
| Skill helpers | `--help` | usage text, status 0, no network |
| File formats | tiny round trip | readable output in user-owned path |
| Loader import | lightweight import | module/version recorded |
| Network sample | bounded query | plausible rows + provenance |
| Reproduction | clean reinstall | same checks pass from lock |

## Troubleshooting by layer

| Symptom | Diagnose | Remediation |
|---|---|---|
| `ModuleNotFoundError` | active executable and exact import name | install named distribution in venv |
| install succeeds, import fails | compare Python/pip paths and architecture | reactivate; use `python -m pip` |
| Parquet write fails | engine and output permissions | install `pyarrow`; test bounded path |
| loader request fails | network, provider, rate limit, requested coverage | retry bounded documented probe |
| native-library error | OS/CPU, wheel, native runtime | choose compatible version/install prerequisite |
| stale notebook import | kernel executable and process state | select venv kernel; restart |
| resolver conflict | incompatible constraints | isolate optional loader or revise pins explicitly |
| empty load | season/status/filter semantics | inspect request and provider coverage |

Capture the complete error, command, interpreter, package versions, and minimal
reproduction before changing dependencies. Never silently substitute a package
or broaden versions until something happens to install.

## Reproducibility policy

Keep a human-edited dependency specification separate from a resolved lock.
Record Python minor version, OS/architecture, package versions, loader versions,
and relevant environment variables without secrets. Treat caches as performance
artifacts, not provenance; data snapshots need their own source metadata.

Lock files are platform-sensitive. For multiple supported platforms, maintain
and test explicit platform locks or a reproducible resolver workflow. A freeze
from a contaminated environment is not a dependency design.

## Worked example

For a new NFL analysis: create `.venv`; install scientific packages and
`nflreadpy`; run the verifier for `numpy,pandas,sklearn,nflreadpy`; run every
selected helper's `--help`; perform a one-season or smaller authorized sample;
write `environment.json`; inspect it; freeze dependencies; then repeat the
local checks in a clean environment before claiming setup is reproducible.

## Output contract and integrity rules

The complete sign-off should report Python version/executable, platform,
requested distributions and import names, resolved versions, helper/loader
probes, skipped network checks, output round trips, exact failures/remediations,
and paths to report and lock. The portable verifier emits only the subset stated
above and enumerates the checks it did not run.

1. Use an isolated environment and `python -m pip`.
2. Never hide failed imports, skipped checks, or platform limitations.
3. `--help` must remain offline; network samples must be bounded and authorized.
4. Freeze only after verification; verify the lock by recreation when required.
5. Use `verify_checklist.md` for sign-off and `troubleshooting.md` for failure routing.
