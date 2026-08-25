# Environment Verify Checklist

- [ ] isolated environment active
- [ ] Python and installer versions recorded
- [ ] installer points to the active environment
- [ ] minimum scientific packages import
- [ ] selected public loaders import
- [ ] every helper returns usage text with `--help`
- [ ] one bounded loader sample succeeds, or network check is explicitly skipped
- [ ] Parquet, JSON, and image outputs can be written where required
- [ ] package versions saved to a lock file
- [ ] verifier stdout parses as one JSON document
- [ ] when `--out` is used, the saved report parses as JSON and matches stdout
- [ ] verifier `checks_not_run` items are completed separately or explicitly waived
