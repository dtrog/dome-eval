# H-001: Pipeline smoke test

- **Experiment config:** configs/experiments/m1_smoke.yaml

## Question
Does a full run (config → backend → JSONL → manifest) work end to end?

## Prediction
Three records, no errors, manifest with git commit and config hash.

## What would change my mind
Any missing field in the manifest or a record with an error.

## Analysis plan
Inspect manifest.json and generations.jsonl by hand.

---
## Outcome
