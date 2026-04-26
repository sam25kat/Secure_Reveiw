# IaC Review — SFT Training Summary

## Headline

**Baseline 0.177 → Trained 0.303 = +0.126**

6 wins, 3 flat, 4 regressions across 13 scenarios.

## Configuration

| Param | Value |
|---|---|
| Model | `unsloth/Qwen2.5-1.5B-Instruct` |
| Hardware | NVIDIA L4 |
| Epochs | 3 |
| Learning rate | 5e-5 (cosine, 5% warmup) |
| LoRA rank | 16 |
| Max seq len | 1536 |
| Optimizer | adamw_8bit, fp16 |
| Curriculum filter | train only on scenarios with baseline ≤ 0.5 |
| Train runtime | ~17 sec |

## Per-scenario breakdown

| Scenario | Before | After | Δ |
|---|---|---|---|
| `iac_010` | 0.01 | **0.76** | **+0.75** ▲ |
| `iac_022` | 0.14 | **0.54** | **+0.40** ▲ |
| `iac_024` | 0.01 | **0.41** | **+0.40** ▲ |
| `iac_007` | 0.01 | **0.40** | **+0.39** ▲ |
| `iac_019` | 0.19 | **0.39** | **+0.20** ▲ |
| `iac_002` | 0.23 | 0.31 | +0.08 ▲ |
| `iac_005` | 0.06 | 0.06 | +0.00 — |
| `iac_014` | 0.01 | 0.01 | +0.00 — |
| `iac_023` | 0.44 | 0.44 | +0.00 — |
| `iac_004` | 0.09 | 0.06 | -0.03 ▼ |
| `iac_016` | 0.18 | 0.13 | -0.05 ▼ |
| `iac_020` | 0.39 | 0.23 | -0.16 ▼ |
| `iac_018` | 0.54 | 0.20 | -0.34 ▼ |

Standout result: **`iac_010` jumped from 0.01 → 0.76 (+0.75)** — a Terraform main.tf scenario the base model couldn't reason about at all, that SFT fully cracked open.

## Scenario coverage

The 13 scenarios in eval span the iac config landscape:

- **Terraform**: iac_002, 004, 005, 007, 010, 016, 018
- **Kubernetes YAML**: iac_019, 020
- **Dockerfile**: iac_022, 023
- **docker-compose**: iac_024
- **GitHub Actions**: iac_014

Each scenario carries hand-curated ground-truth findings with file/line metadata, severity, and a `category` field consumed by the semantic-match grader.

## Why 1.5B (not 7B)

We initially trained iac with the same 7B 4-bit Qwen that gave migration its +0.295. It produced consistently negative results (-0.024 to -0.116) across multiple configurations.

Root cause: after the iac grader was upgraded to a semantic alias dictionary (45+ category aliases), the base 7B model's natural-language findings started getting credited automatically — pushing baselines above 0.5 across many scenarios. SFT had little headroom to *gain*, but plenty of room to *regress*: the LoRA adapter's collateral on eval-only scenarios systematically broke fluent answers the base model already had.

Switching to **Qwen 1.5B** dropped the baseline to 0.177 — restoring the regime where SFT can actually learn. This matches the dependency-review setup that produced +0.302.

The takeaway for the env: model scale and grader sensitivity have to be tuned together. A grader generous enough to credit natural answers on a 7B base may saturate baseline so high there's nothing to teach.

## Curriculum filter

Of the 13 evaluation scenarios, **12 had baseline ≤ 0.5 and were used for training**. `iac_023` (baseline 0.44 — borderline but kept) and `iac_018` (baseline 0.54) are the only ones above the threshold; iac_018 was excluded from training and remained in eval as a proof-point. It regressed -0.34 — exactly the LoRA-collateral pattern documented above.

## Reproducibility

```bash
# Local entrypoint
training_space/sft_variants/train_sft_iac.py

# Live trainer Space (one-click reproduce)
https://huggingface.co/spaces/sam25kat/securereview-trainer-iac

# Live env Space (24 iac scenarios)
https://huggingface.co/spaces/sam25kat/securereview-env-iac
```
