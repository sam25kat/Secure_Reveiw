# IaC Grader — Root-Cause Fix

## Problem

Multiple iac SFT runs landed negative (-0.05 to -0.19) despite training loss decreasing cleanly. Investigation showed:

1. The original `iac_grader.py` had a hardcoded `RULE_CATEGORY_MAP` containing only `IAC-001` → `IAC-012`.
2. New scenarios used `IAC-013` → `IAC-037`. The grader's Strategy 2 (match-by-rule-id-category) **silently failed** for any unknown rule_id — agent_category resolved to `None`.
3. Strategy 3 (line-proximity match) also depended on the rule_id map.
4. So the grader effectively only used Strategy 1 (resource-identifier substring) for new scenarios — too brittle, missed correct findings phrased naturally.

After SFT, the model's natural answers no longer matched the grader's exact substring expectations, while its in-training-distribution answers were credited only narrowly. Net effect: regressions on existing scenarios, marginal gains on new ones.

## Fix (committed to [app/graders/iac_grader.py](../app/graders/iac_grader.py))

Replaced the rule_id-based match map with a **category alias dictionary** containing 45+ semantic aliases. Each ground-truth finding's `category` (e.g. `public_access`, `hardcoded_secret`) maps to natural-language phrases the model is likely to use.

Examples:
- `hardcoded_secret` → ["hardcoded", "credential", "password", "api key", "token", "aws_access_key"]
- `permissive_security_group` → ["security group", "0.0.0.0/0", "ingress", "open to internet"]
- `public_kubernetes_api` → ["endpoint_public_access", "api server", "public api endpoint"]

### Three-strategy match (in order)

1. **Resource identifier**: split match_key on `|`, check if the resource part appears in description
2. **File + category-keyword**: same file as ground truth + any category keyword/alias appears in description
3. **File + line ±5 + category-keyword**: looser, picks up findings the model placed slightly off

If any strategy fires, the agent finding is credited as a true positive.

### What this does NOT change

- The reward formula (F1 × weights + severity bonus + efficiency bonus)
- Severity grading
- Per-task reward floors / participation bonus
- Anything in the dependency / migration graders

It only makes the iac grader recognize correct findings phrased naturally — closing the gap that was causing the SFT-then-regress pattern.

## Files updated

- [app/graders/iac_grader.py](../app/graders/iac_grader.py) — local
- Pushed to `sam25kat/securereview-env-iac` (HF Space) — env rebuild ~3 min

## Validation plan

After Space rebuilds, re-run iac SFT. Expected behavior:

| Metric | Old grader | New grader (expected) |
|---|---|---|
| Baseline mean | 0.22 | **higher** (~0.30-0.40) — natural answers now credited |
| Trained mean | varies | **0.50-0.65** |
| Improvement | -0.10 to -0.19 | **+0.15 to +0.30** |
