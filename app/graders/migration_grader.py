"""Migration Grader — operation-aware matching with semantic category aliases.

Original behavior preserved:
- Strategy 1: match by (operation, target) extracted from match_key
- Strategy 2: file + line proximity (±2 lines)
- Strategy 3: unique rule_id match within a file

New strategy added (Strategy 4): file + category-keyword overlap. This credits
findings that are correct but phrased naturally (e.g. the model says
"single-row update bottleneck" without naming the exact resource).
"""
from typing import List, Set

from app.models import Finding, GroundTruthFinding
from app.graders.base import BaseGrader, MatchResult


# Maps operation keywords in match_key to expected rule_ids and description keywords
OPERATION_RULE_MAP = {
    "add_column": ({"MIG-001"}, {"add", "not null", "column", "default"}),
    "create_index": ({"MIG-002"}, {"index", "concurrent", "create"}),
    "drop_column": ({"MIG-003"}, {"drop", "column", "referenced", "in use"}),
    "rename_column": ({"MIG-004"}, {"rename", "column"}),
    "alter_type": ({"MIG-005"}, {"type", "change", "alter", "cast", "rewrite"}),
    "missing_pattern": ({"MIG-007"}, {"expand", "migrate", "contract", "pattern"}),
    "add_constraint": ({"MIG-008"}, {"foreign key", "constraint", "fk"}),
    "drop_table": ({"MIG-009"}, {"drop", "table", "foreign key", "reference"}),
}


# Category → list of phrases the model is likely to use for that issue.
# Same alias-dictionary approach as the iac_grader fix.
CATEGORY_ALIASES = {
    "hot_row_contention":            ["hot row", "single-row update", "row-level lock", "row contention", "global counter", "serialize"],
    "lock_duration":                 ["lock duration", "lock held", "row lock", "select for update", "long-running lock"],
    "destructive_cascade":           ["cascade", "drop sequence", "destructive", "silent drop"],
    "default_serialization":         ["default expression", "default function", "serializ", "per-row"],
    "architecture_anti_pattern":     ["architecture", "anti-pattern", "snowflake", "ulid", "shared counter"],
    "non_concurrent_index":          ["concurrently", "create index concurrently", "share lock", "blocks writes", "access exclusive"],
    "index_type_choice":             ["brin", "btree", "wrong index", "index type", "block range"],
    "architectural_partitioning":    ["partition", "partitioning", "partition by range"],
    "non_immutable_default":         ["non-immutable", "immutable default", "table rewrite", "rewrite", "metadata-only"],
    "schema_design":                 ["denormalization", "schema design", "denormalized", "generated column"],
    "operational_blocking":          ["vacuum", "analyze", "blocking", "operational"],
    "consistency_replication":       ["read-after-write", "replication lag", "replica lag", "stale read", "replica"],
    "idempotency":                   ["idempot", "retry", "double-credit", "double credit"],
    "destructive_constraint_drop":   ["check constraint", "drop constraint", "invariant", "constraint dropped"],
    "lock_serialization":            ["row lock", "serialize", "hot account", "lock serialization"],
    "architecture_data_derivation":  ["event sourcing", "derived data", "ledger", "trigger-based"],
    "gin_options":                   ["gin", "jsonb_path_ops", "gin index"],
    "unbatched_update":              ["unbatched", "without batching", "single transaction", "wal volume", "batch in"],
    "schema_design_jsonb_abuse":     ["jsonb", "json column", "queryable", "schemaless", "promote to columns"],
    "denormalization_consistency":   ["denormalized", "stale", "drift", "generated column"],
    "redundant_indexes":             ["redundant", "duplicate index", "overlapping index"],
    "soft_delete_uniqueness":        ["soft delete", "soft-delete", "deleted_at", "tombstone", "unique constraint"],
    "partial_index_missing":         ["partial index", "where clause", "where deleted_at"],
    "tombstone_scan_overhead":       ["tombstone", "deleted rows", "soft-deleted"],
    "schema_design_redundancy":      ["redundant", "two columns", "drift", "duplicate state"],
    "schema_constraint_missing":     ["check constraint", "enum", "constraint missing", "free text"],
    "blocking_check_constraint":     ["not valid", "validate constraint", "check constraint", "access exclusive"],
    "blocking_check_with_data_violations": ["existing rows", "data violations", "validate", "not valid"],
    "non_concurrent_drop":           ["drop index", "concurrently", "access exclusive lock"],
    "covering_index":                ["include", "covering index", "index-only scan", "heap fetch"],
    "redundant_existing_index":      ["redundant", "drop index", "duplicate"],
    "polymorphic_association":       ["polymorphic", "target_type", "foreign key enforcement", "no fk"],
    "polymorphic_id_ambiguity":      ["polymorphic", "ambiguous", "target_id"],
    "missing_indexes":               ["missing index", "no index", "seq scan", "sequential scan"],
    "blocking_fk_validation":        ["foreign key", "fk validation", "not valid", "validate constraint", "access exclusive"],
    "fk_no_supporting_index":        ["supporting index", "no index on", "fk on", "missing index on referencing"],
    "cascade_financial_risk":        ["cascade", "on delete", "audit", "financial"],
    "fk_nullable_no_index":          ["nullable", "fk", "no index"],
    "blocking_alter_type":           ["alter column type", "table rewrite", "access exclusive", "full rewrite"],
    "incomplete_int_to_bigint_migration": ["sequence", "alter sequence", "integer", "bigint", "overflow"],
    "capacity_planning_pk":          ["bigint", "integer overflow", "primary key", "serial"],
    "wal_replication_risk":          ["wal", "replication slot", "wal volume"],
    "alter_table_metadata_only":     ["metadata-only", "metadata only", "fast path", "default", "pg 11"],
    "view_drop_dependency_break":    ["drop view", "matview", "dependent objects", "consumers"],
    "blocking_matview_refresh":      ["refresh materialized view", "concurrently", "access exclusive"],
    "matview_unique_index":          ["unique index", "matview", "concurrently"],
    "matview_incremental_strategy":  ["incremental", "pg_ivm", "continuous aggregate"],
    "schema_type_choice":            ["char", "varchar", "padding", "type choice"],
    "hot_update_breaking":           ["hot update", "heap-only", "fillfactor", "non-hot"],
    "fillfactor_missing":            ["fillfactor", "page headroom", "heap-only", "in-page"],
    "alter_storage_unnecessary":     ["alter storage", "rewrite", "no-op", "default storage"],
    "autovacuum_tuning":             ["autovacuum", "vacuum_scale_factor", "vacuum_threshold", "dead tuples"],
    "schema_design_high_update_column": ["update frequency", "high update", "non-hot"],
    "architecture_wrong_tool":       ["postgres", "queue", "redis", "wrong tool", "throughput"],
    "pgbouncer_transaction_pooling": ["pgbouncer", "transaction pooling", "set local", "session"],
    "session_setting_scope":         ["set local", "session-level", "set local statement_timeout"],
    "alter_table_pattern":           ["add column", "default", "metadata-only"],
    "deadlock_lock_order":           ["deadlock", "lock order", "lock ordering"],
    "transaction_scope_too_large":   ["transaction scope", "multi-table", "all in one transaction"],
    "create_index_in_txn":           ["create index", "transaction", "cannot run inside"],
    "premature_index":               ["all-null", "before backfill", "premature"],
    "architecture_audit_pattern":    ["audit log", "audit pattern", "centralized audit"],
    "partition_key_choice":          ["partition key", "partition by", "tenant_id"],
    "partition_strategy_pareto":     ["pareto", "skew", "hash partition", "list partition"],
    "partition_pk_breaks_fks":       ["primary key", "partitioning", "fk", "foreign key"],
    "partitioned_index_pruning":     ["partition pruning", "global index", "local index"],
    "partition_rollover_missing":    ["pg_partman", "rollover", "future partitions"],
    "incomplete_migration":          ["data move", "backfill", "cutover", "incomplete"],
    "architecture_multi_tenancy":    ["cell-based", "tenant", "dedicated cluster"],
    "replication_pii_leak":          ["pii", "all tables", "publication", "column-list"],
    "replica_identity_choice":       ["replica identity", "wal volume", "old image", "full image"],
    "slot_disk_fill_risk":           ["replication slot", "wal disk", "fill"],
    "redundant_statement":           ["redundant", "no-op", "already set"],
    "architecture_data_pipeline":    ["debezium", "kafka", "cdc", "change data capture"],
    "partial_index_for_skewed_data": ["partial index", "where status", "skewed"],
    "statistics_target_misuse":      ["statistics", "set statistics", "low cardinality"],
    "extended_statistics":           ["extended statistics", "create statistics", "correlation"],
    "vacuum_blocking_migration":     ["vacuum analyze", "vacuum", "blocking"],
    "redundant_index_skewed":        ["useless index", "redundant", "skewed"],
    "toast_compression_misuse":      ["toast", "storage external", "compression"],
    "toast_strategy_correct":        ["toast", "external", "compression"],
    "alter_storage_blocking":        ["alter storage", "rewrite", "access exclusive"],
    "generated_column_opportunity":  ["generated column", "generated always as", "stored"],
    "column_ordering":               ["column order", "padding", "alignment"],
    "rls_denormalization_required":  ["row level security", "rls", "denormaliz", "tenant_id"],
    "rls_with_check_missing":        ["with check", "rls policy", "insert"],
    "rls_setting_safety":            ["current_setting", "missing_ok", "guc"],
    "rls_role_audit":                ["bypassrls", "force row level security", "owner"],
    "rls_command_scope":             ["for all", "for select", "policy command"],
    "architecture_isolation_strategy": ["cell architecture", "rls", "tenant isolation"],
    "connection_architecture":       ["max_connections", "pgbouncer", "connection pool"],
    "config_requires_restart":       ["restart", "pg_reload_conf", "shared_buffers"],
    "memory_sizing":                 ["work_mem", "shared_buffers", "memory budget"],
    "lock_table_sizing":             ["max_locks", "lock table", "shared memory"],
    "architecture_pooling_strategy": ["connection pool", "hikari", "asyncpg", "pgbouncer"],
    "concurrency_check_then_act":    ["check-then-act", "race condition", "for update", "concurrent"],
    "isolation_level":               ["isolation", "read committed", "serializable", "snapshot"],
    "hot_row_for_update":            ["for update", "hot row", "skip locked", "queue"],
    "function_observability":        ["return value", "boolean", "function returns"],
    "concurrency_pattern_choice":    ["optimistic", "version column", "compare-and-swap"],
    "schema_sharding_for_hot_data":  ["shard", "bucket", "hot data", "pareto"],
    "enum_alter_constraints":        ["alter type", "add value", "transaction", "enum"],
    "rolling_deploy_enum_rename":    ["rename value", "rolling deploy", "enum"],
    "enum_drop_value_unsupported":   ["drop value", "alter type", "not supported"],
    "data_migration_correctness":    ["semantic", "data migration", "wrong mapping"],
    "architecture_enum_rigidity":    ["enum", "lookup table", "reference table"],
    "audit_log_enum_safety":         ["audit log", "enum", "historical"],
    "online_index_swap_order":       ["concurrently", "drop before create", "atomic swap"],
    "architecture_partitioning_time_series": ["partition by range", "time series", "brin"],
    "architecture_tiered_storage":   ["tiered", "redis", "clickhouse", "hot storage"],
}


def _category_keywords(category: str) -> List[str]:
    """Get all phrases that should credit a finding for this category."""
    cat = (category or "").lower()
    if not cat:
        return []
    keywords = [cat, cat.replace("_", " "), cat.replace("_", "-")]
    keywords.extend(CATEGORY_ALIASES.get(cat, []))
    return [k.lower() for k in keywords if k]


class MigrationGrader(BaseGrader):
    """Matches findings by (operation_type, target_object).

    Primary match: match_key components found in finding description.
    Secondary match: same file + matching line number (within 2 lines).
    Tertiary match: unique rule_id within file.
    Quaternary match: same file + category-keyword overlap (semantic alias).
    """

    @staticmethod
    def _operation_matches(operation: str, rule_id: str, desc_lower: str) -> bool:
        """Check if the agent's finding is about the same kind of operation."""
        op_info = OPERATION_RULE_MAP.get(operation)
        if op_info is None:
            return True  # Unknown operation, allow match on target alone
        valid_rules, keywords = op_info
        if rule_id.upper() in valid_rules:
            return True
        return any(kw in desc_lower for kw in keywords)

    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        result = MatchResult()
        matched_gt_keys: Set[str] = set()

        gt_by_key = {gt.match_key.lower(): gt for gt in ground_truth}

        for af in agent_findings:
            matched = False
            desc_lower = (af.description or "").lower()
            af_file = (af.file or "").lower()

            # Strategy 1: match_key (operation|target) components in description
            for key, gt in gt_by_key.items():
                if key in matched_gt_keys:
                    continue
                parts = key.split("|")
                if len(parts) == 2:
                    operation, target = parts
                    if not self._operation_matches(operation, af.rule_id, desc_lower):
                        continue
                    target_parts = target.split(".")
                    target_found = target in desc_lower
                    if not target_found and len(target_parts) == 2:
                        target_found = (
                            target_parts[0] in desc_lower
                            and target_parts[1] in desc_lower
                        )
                    if target_found:
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(key)
                        matched = True
                        break
            if matched:
                continue

            # Strategy 2: file + line proximity (±2 lines)
            if af.line is not None:
                for gt in ground_truth:
                    if (
                        gt.match_key.lower() not in matched_gt_keys
                        and gt.file.lower() == af_file
                        and gt.line is not None
                        and abs(gt.line - af.line) <= 2
                    ):
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(gt.match_key.lower())
                        matched = True
                        break
            if matched:
                continue

            # Strategy 3: unique rule_id within file
            rule_candidates = [
                gt for gt in ground_truth
                if gt.match_key.lower() not in matched_gt_keys
                and gt.rule_id.upper() == af.rule_id.upper()
                and gt.file.lower() == af_file
            ]
            if len(rule_candidates) == 1:
                gt = rule_candidates[0]
                result.true_positives.append((af, gt))
                matched_gt_keys.add(gt.match_key.lower())
                matched = True
            if matched:
                continue

            # Strategy 4 (NEW): file + category-keyword overlap (semantic alias)
            for gt in ground_truth:
                key = gt.match_key.lower()
                if key in matched_gt_keys or not gt.category:
                    continue
                if gt.file.lower() != af_file:
                    continue
                for kw in _category_keywords(gt.category):
                    if kw in desc_lower:
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(key)
                        matched = True
                        break
                if matched:
                    break
            if matched:
                continue

            result.false_positives.append(af)

        for gt in ground_truth:
            if gt.match_key.lower() not in matched_gt_keys:
                result.false_negatives.append(gt)

        return result
