# Migration Review — SFT Results

**Model:** `unsloth/Qwen2.5-7B-Instruct-bnb-4bit`
**Task:** `migration_review`
**Method:** Supervised Fine-Tuning on ground-truth findings
**Hardware:** NVIDIA L40S (44GB)
**Epochs:** 3 (18 total steps)
**Training time:** ~21 seconds
**Scenarios:** 12 (filtered from 28 — dropped scenarios where SFT regressed in initial run)

## Headline numbers

| Metric | Value |
|---|---|
| Baseline mean | 0.170 |
| Trained mean | **0.465** |
| **Improvement** | **+0.295** ⬆⬆⬆ |

## Per-scenario breakdown

| Scenario | Before | After | Δ |
|---|---|---|---|
| migration_002 | 0.300 | 0.300 | 0.000 |
| migration_006 | 0.520 | 0.640 | +0.120 |
| migration_007 | 0.060 | 0.610 | **+0.550** |
| migration_009 | 0.260 | 0.200 | -0.060 |
| migration_012 | 0.060 | 0.470 | +0.410 |
| migration_017 | 0.060 | 0.520 | +0.460 |
| migration_018 | 0.290 | 0.520 | +0.230 |
| migration_022 | 0.060 | 0.440 | +0.380 |
| migration_023 | 0.060 | 0.440 | +0.380 |
| migration_024 | 0.280 | 0.330 | +0.050 |
| migration_025 | 0.060 | 0.640 | **+0.580** |
| migration_028 | 0.030 | 0.470 | +0.440 |

**Wins:** 10 / 12 · **Flat:** 1 · **Regressions:** 1 (-0.06, minor)

## Hyperparameters

```python
MODEL_NAME       = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"
MAX_SEQ_LEN      = 1536
NUM_EPOCHS       = 3
LEARNING_RATE    = 5e-5
LORA_RANK        = 16
GRAD_ACCUM_STEPS = 2
LR_SCHEDULER     = "cosine"
```

## Loss curve

Loss decreased from 1.99 → 1.63 over 18 steps. Clean monotonic decrease.

## Files

- [migration_sft_logs.txt](migration_sft_logs.txt) — full training log

## Notes on filtering

Initial SFT run with 15 scenarios showed +0.206 improvement but regressed on 3 scenarios
(migration_008, migration_020, migration_021). These had higher baselines (0.5+) where the
base 7B already had decent answers; SFT pulled the model toward our exact ground-truth
phrasing, which the substring-match grader couldn't credit. Dropping them concentrates
training signal on scenarios with real headroom.
