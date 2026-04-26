# Dependency Review — SFT Results

**Model:** `unsloth/Qwen2.5-1.5B-Instruct`
**Task:** `dependency_review`
**Method:** Supervised Fine-Tuning on ground-truth findings
**Hardware:** NVIDIA A10G
**Epochs:** 3 (36 total steps)
**Training time:** ~25 seconds
**Scenarios:** 24

## Headline numbers

| Metric | Value |
|---|---|
| Baseline mean | 0.083 |
| Trained mean | **0.385** |
| **Improvement** | **+0.302** ⬆⬆⬆ |

## Per-scenario breakdown

| Scenario | Before | After | Δ |
|---|---|---|---|
| dep_001 | 0.010 | 0.010 | 0.000 |
| dep_002 | 0.010 | 0.060 | +0.050 |
| dep_003 | 0.010 | 0.060 | +0.050 |
| dep_004 | 0.010 | 0.060 | +0.050 |
| dep_005 | 0.010 | 0.010 | 0.000 |
| dep_006 | 0.020 | 0.060 | +0.040 |
| dep_007 | 0.020 | 0.230 | +0.210 |
| dep_008 | 0.300 | 0.650 | +0.350 |
| dep_009 | 0.020 | 0.290 | +0.270 |
| dep_010 | 0.010 | 0.790 | **+0.780** |
| dep_011 | 0.230 | 0.460 | +0.230 |
| dep_012 | 0.020 | 0.600 | +0.580 |
| dep_013 | 0.440 | 0.730 | +0.290 |
| dep_014 | 0.010 | 0.220 | +0.210 |
| dep_015 | 0.020 | 0.930 | **+0.910** |
| dep_016 | 0.520 | 0.520 | 0.000 |
| dep_017 | 0.020 | 0.010 | -0.010 |
| dep_018 | 0.170 | 0.470 | +0.300 |
| dep_019 | 0.020 | 0.300 | +0.280 |
| dep_020 | 0.020 | 0.520 | +0.500 |
| dep_021 | 0.010 | 0.350 | +0.340 |
| dep_022 | 0.060 | 0.720 | **+0.660** |
| dep_023 | 0.020 | 0.500 | +0.480 |
| dep_024 | 0.010 | 0.680 | **+0.670** |

**Wins:** 20 / 24 · **Flat:** 3 · **Regressions:** 1 (-0.01, negligible)

## Hyperparameters

```python
MODEL_NAME       = "unsloth/Qwen2.5-1.5B-Instruct"
MAX_SEQ_LEN      = 1536
NUM_EPOCHS       = 3
LEARNING_RATE    = 5e-5
LORA_RANK        = 16
GRAD_ACCUM_STEPS = 2
LR_SCHEDULER     = "cosine"
WARMUP_RATIO     = 0.05
```

## Loss curve

Loss decreased from 2.01 → 1.27 over 36 steps. Clean convergence.

## Files

- [dep_sft_logs.txt](dep_sft_logs.txt) — full training log
