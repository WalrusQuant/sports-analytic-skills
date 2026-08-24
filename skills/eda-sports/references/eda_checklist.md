# Sports EDA Checklist

## Identity

- [ ] Source package/version noted
- [ ] Grain stated
- [ ] Season/date range stated

## Structure

- [ ] row/col counts
- [ ] primary keys unique
- [ ] team/player IDs stable enough

## Time

- [ ] all expected seasons present
- [ ] week/date monotonic issues checked
- [ ] in-progress season handled

## Missingness

- [ ] null counts by column
- [ ] null rates by season for critical fields

## Targets

- [ ] base rates
- [ ] distribution plots
- [ ] impossible values (negative scores, etc.)

## Leakage scouts

- [ ] outcome columns identified
- [ ] same-game stats identified
- [ ] post-event fields identified

## Decision

- [ ] go / repair / stop with reasons
