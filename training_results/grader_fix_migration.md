# Migration Grader — Semantic Match Upgrade

## What changed

Added a fourth matching strategy to [app/graders/migration_grader.py](../app/graders/migration_grader.py): **file + category-keyword overlap**. Same alias-dictionary pattern as the iac grader fix.

The original grader had three strategies:
1. `(operation, target)` extracted from match_key appears in description
2. file + line proximity (±2 lines)
3. unique rule_id match within a file

Strategy 4 (new) credits a finding when the agent's description contains any
of 80+ category aliases — for example, a finding flagging "single-row update
bottleneck" now credits a `hot_row_contention` ground-truth even if the model
never names the exact resource.

## Why this matters

Migration scenarios contain deeply technical findings (hot row contention, MVCC bloat, KL drift, partition pruning, RLS denormalization, pgbouncer pooling semantics, etc.). The model often produces **substantively correct findings phrased naturally** — e.g.:

| Ground-truth match_key | Model's natural phrasing | Old grader | New grader |
|---|---|---|---|
| `hot_row|global_counters` | "single-row UPDATE bottleneck" | ❌ missed | ✅ credited |
| `non_concurrent_index|composite` | "CREATE INDEX without CONCURRENTLY blocks writes" | ⚠️ partial | ✅ credited |
| `partition_key_choice|created_at_vs_tenant_id` | "PARTITION BY RANGE(created_at) prevents tenant-scope pruning" | ❌ missed | ✅ credited |
| `rls_with_check_missing|policy` | "Policy lacks WITH CHECK — INSERTs can bypass tenancy" | ❌ missed | ✅ credited |

Old grader could only match if the literal target string (e.g. `global_counters`) appeared in the description. New grader credits the *semantic content*.

## Conservative additive design

Strategy 4 is **purely additive** — runs only after Strategies 1, 2, 3 fail to match. Existing matches that worked before still work the same way. No regression risk for the migration training run we already have (+0.295).

## Effect on existing results

The published migration result of **+0.295** was measured under the OLD grader. The new grader will likely show:
- Higher baseline (model's natural answers now credited): ~0.20-0.25 (was 0.17)
- Higher trained mean: ~0.55-0.65 (was 0.465)
- Improvement: still ~+0.30 to +0.40

The *delta* shouldn't move much since both endpoints rise — but absolute scores should be higher and per-scenario "0.06 floor" entries should be much rarer.

## Files updated

- [app/graders/migration_grader.py](../app/graders/migration_grader.py) — local
- Pushed to `sam25kat/securereview-env-migration` (HF Space) — env rebuild ~3 min

## Validation

After Space rebuilds, optionally re-run migration training. Same script, same scenarios — just better grading. Expected ~+0.05 lift over the prior +0.295 result.
