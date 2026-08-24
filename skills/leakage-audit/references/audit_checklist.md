# Leakage Audit Checklist

## Target and T
- [ ] Target written
- [ ] T written
- [ ] Labels post-T only

## Features
- [ ] Inventory complete
- [ ] Each feature legal at T
- [ ] shift(1)/as-of verified
- [ ] opponent joins pre-game only

## Splits
- [ ] train time < test time
- [ ] preprocessors fit on train only
- [ ] no test-fold tuning

## Too-good triggers
- [ ] absurd metrics investigated
- [ ] automated audit run

## Verdict
- [ ] CLEAN, REVIEW REQUIRED, or NOT CLEAN with fixes
