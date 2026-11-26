---
name: skill
description: >
  One or two sentences. State WHAT the skill does and WHEN an agent should
  load it. Write for discovery, not marketing.
license: MIT
metadata:
  version: "1.0.0"
---

# Skill Name

## When to use

- …

## When not to use

- …

## Required inputs

- …
- State the file format, grain, and minimum fields. For sportsleader-data, copy column names from the manifest entry.

## Procedure

1. …
2. …
3. …

## Decision guide

| Situation | Choose | Why / caveat |
|---|---|---|
| … | … | … |

## Diagnostics and failure modes

- Check …
- If …, then …

## Hard constraints

- Predictive inputs must be knowable at decision time T.
- Do not invent a sportsleader-data dataset or column.
- Do not require a program stored in this repository. Illustrative snippets read the user's files or a public Parquet URL.

## Anti-patterns

- …
- …

## Output contract

Done means:

- [ ] …
- [ ] …

## Handoffs

- Suggest another skill when it helps. The core job stays usable without it.
- Stop if …

## Worked example

Use a sportsleader-data file or a clearly synthetic table. Show the input assumption, the decision, and how to read the output.

## Reporting requirements

- State sample size, baseline, and limits.
- Do not claim a betting edge.

## References

- Put conditional detail in `references/` and link it from the step that needs it. The link must resolve.
