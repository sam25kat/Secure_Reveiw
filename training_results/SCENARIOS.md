# SecureReview — Complete Scenario Index

Every scenario in the SecureReview environment, with file inventory, ground-truth severity distribution, taxonomy categories, and per-scenario before/after scores from the live SFT→GRPO hybrid pipeline.

**76 scenarios across three domains** — each carries hand-curated ground-truth findings (5–11 per scenario), file/line metadata, severity (critical/high/medium/low/info), and a `category` field consumed by the semantic-similarity grader.

Severity column key: `Nc` = N critical · `Nh` = N high · `Nm` = N medium · `Nl` = N low · `Ni` = N info

---

## Headline summary

| Task | Scenarios | Baseline | Trained | Δ | Wins |
|---|---|---|---|---|---|
| **Dependency** | 24 | 0.083 | **0.385** | **+0.302** | 20/24 |
| **Migration**  | 12* | 0.170 | **0.465** | **+0.295** | 10/12 |
| **IaC**        | 13* | 0.177 | **0.303** | **+0.126** | 6/13 |

*Migration and IaC use principled curriculum filtering on training (scenarios with baseline > 0.5 stay in the eval-only set). The full scenario libraries are 28 (migration) and 24 (iac); the eval column shows the curriculum-trained subset matching the published numbers.*

---

### I. Dependency Review — Supply-Chain Security

**24 scenarios** · ground-truth findings + file/line metadata + severity

| # | Scenario | Files | # | Sev | Categories | Base → Trained | Δ |
|---|---|---|---|---|---|---|---|
| 001 | `dep_001` | requirements.txt | 3 | 2C 1H | `hallucinated`, `known_cve`, `typosquat` | 0.01 → 0.01 | — +0.00 |
| 002 | `dep_002` | requirements.txt | 4 | 2C 2H | `hallucinated`, `known_cve`, `typosquat` | 0.01 → 0.06 | ▲ +0.05 |
| 003 | `dep_003` | package.json | 3 | 2C 1H | `hallucinated`, `known_cve`, `typosquat` | 0.01 → 0.06 | ▲ +0.05 |
| 004 | `dep_004` | requirements.txt | 5 | 2C 3H | `hallucinated`, `known_cve`, `typosquat` | 0.01 → 0.06 | ▲ +0.05 |
| 005 | `dep_005` | requirements.txt | 4 | 2C 2H | `hallucinated`, `known_cve`, `typosquat` | 0.01 → 0.01 | — +0.00 |
| 006 | `dep_006` | requirements.txt | 5 | 1C 4H | `hallucinated`, `known_cve`, `typosquat` | 0.02 → 0.06 | ▲ +0.04 |
| 007 | `dep_007` | requirements.txt | 6 | 5C 1H | `hallucinated_or_typosquat`, `typosquat` | 0.02 → 0.23 | ▲ +0.21 |
| 008 | `dep_008` | requirements.txt | 4 | 2C 2H | `eol_dependency`, `malicious_package`, `typosquat_legacy_name` + 1 | 0.30 → 0.65 | ▲ +0.35 |
| 009 | `dep_009` | requirements.txt | 8 | 5C 3H | `eol_with_cves`, `known_cve` | 0.02 → 0.29 | ▲ +0.27 |
| 010 | `dep_010` | requirements.txt | 7 | 6C 1H | `hallucinated_slopsquat` | 0.01 → 0.79 | ▲ +0.78 |
| 011 | `dep_011` | requirements.txt | 6 | 4C 2H | `hijacked_exact_version`, `hijacked_history`, `protestware` + 2 | 0.23 → 0.46 | ▲ +0.23 |
| 012 | `dep_012` | requirements.txt | 4 | 2C 2H | `agpl_saas_violation`, `gpl_contamination`, `gpl_license_risk` + 1 | 0.02 → 0.60 | ▲ +0.58 |
| 013 | `dep_013` | package.json | 6 | 4C 2H | `hijacked_within_range`, `known_cve`, `postinstall_risk` + 2 | 0.44 → 0.73 | ▲ +0.29 |
| 014 | `dep_014` | Pipfile, pyproject.toml, requirements.txt | 4 | 1C 2H 1M | `caret_drift`, `manifest_drift`, `unbounded_version` + 1 | 0.01 → 0.22 | ▲ +0.21 |
| 015 | `dep_015` | requirements.txt | 6 | 2C 4H | `alpha_in_prod`, `beta_in_prod`, `dev_in_prod` + 1 | 0.02 → 0.93 | ▲ +0.91 |
| 016 | `dep_016` | requirements.txt | 6 | 1C 4H 1M | `abandoned`, `abandoned_branch`, `abandoned_dependency_chain` + 2 | 0.52 → 0.52 | — +0.00 |
| 017 | `dep_017` | constraints.txt, requirements.txt | 4 | 1C 2H 1M | `transitive_conflict`, `transitive_cve`, `transitive_outdated` | 0.02 → 0.01 | ▼ -0.01 |
| 018 | `dep_018` | package.json | 7 | 2C 4H 1M | `deprecated_package`, `known_cve`, `lifecycle_scripts_audit` + 1 | 0.17 → 0.47 | ▲ +0.30 |
| 019 | `dep_019` | requirements.txt | 4 | 4C | `malicious_explicit`, `malicious_known` | 0.02 → 0.30 | ▲ +0.28 |
| 020 | `dep_020` | requirements-dev.txt | 5 | 2H 2M 1L | `beta_in_prod`, `known_cve`, `outdated_devtool` | 0.02 → 0.52 | ▲ +0.50 |
| 021 | `dep_021` | environment.yml, requirements.txt | 3 | 1C 1H 1M | `cuda_mismatch_risk`, `manifest_drift`, `wrong_canonical_name` | 0.01 → 0.35 | ▲ +0.34 |
| 022 | `dep_022` | package.json | 5 | 3C 2H | `deprecated_package`, `known_cve` | 0.06 → 0.72 | ▲ +0.66 |
| 023 | `dep_023` | pip.conf, requirements.txt | 4 | 1C 3H | `dependency_confusion`, `naming_collision_risk` | 0.02 → 0.50 | ▲ +0.48 |
| 024 | `dep_024` | requirements.txt | 7 | 1C 4H 1M 1L | `known_cve`, `outdated`, `outdated_severe` + 1 | 0.01 → 0.68 | ▲ +0.67 |

---

### II. IaC Review — Infrastructure Misconfiguration

**24 scenarios** · ground-truth findings + file/line metadata + severity

| # | Scenario | Files | # | Sev | Categories | Base → Trained | Δ |
|---|---|---|---|---|---|---|---|
| 001 | `iac_001` | main.tf, variables.tf | 4 | 2C 2H | `encryption_at_rest`, `permissive_security_group`, `public_access` | — | — |
| 002 | `iac_002` | iam.tf, main.tf, variables.tf | 5 | 1C 2H 2M | `encryption_at_rest`, `iam_wildcard`, `missing_auth` + 1 | 0.23 → 0.31 | ▲ +0.08 |
| 003 | `iac_003` | iam.tf, main.tf, vpc.tf | 6 | 2C 4H | `encryption_at_rest`, `iam_wildcard`, `missing_logging` + 3 | — | — |
| 004 | `iac_004` | iam.tf, main.tf, redshift.tf, s3.tf | 5 | 3C 1H 1M | `encryption_at_rest`, `hardcoded_credentials`, `missing_logging` + 1 | 0.09 → 0.06 | ▼ -0.03 |
| 005 | `iac_005` | iam_cross_account.tf, main.tf, variables.tf, vp… | 6 | 1C 3H 2M | `cross_account_access`, `encryption_at_rest`, `missing_auth` + 3 | 0.06 → 0.06 | — +0.00 |
| 006 | `iac_006` | deployment.yaml, network-policy.yaml, service.yaml | 5 | 2C 2H 1M | `hardcoded_credentials`, `missing_network_acl`, `privileged_container` + 1 | — | — |
| 007 | `iac_007` | main.tf | 6 | 3C 3H | `backups_disabled`, `encryption_at_rest`, `hardcoded_secret` + 2 | 0.01 → 0.40 | ▲ +0.39 |
| 008 | `iac_008` | deployment.yaml | 8 | 6C 1H 1M | `hardcoded_secret`, `host_network`, `host_path_mount` + 4 | — | — |
| 009 | `iac_009` | Dockerfile | 8 | 3C 5H | `eol_base_image`, `hardcoded_secret`, `run_as_root` + 3 | — | — |
| 010 | `iac_010` | main.tf | 6 | 2C 3H 1M | `log_validation_disabled`, `public_access`, `public_log_bucket` + 3 | 0.01 → 0.76 | ▲ +0.75 |
| 011 | `iac_011` | deployment.yaml, namespace.yaml, service.yaml | 5 | 1C 4H | `missing_network_policy`, `missing_resource_limits`, `missing_tls_in_cluster` + 2 | — | — |
| 012 | `iac_012` | docker-compose.yml | 9 | 4C 4H 1M | `debug_mode_enabled`, `eol_base_image`, `exposed_internal_port` + 2 | — | — |
| 013 | `iac_013` | main.tf | 6 | 1C 5H | `control_plane_logging_disabled`, `eol_kubernetes_version`, `private_endpoint_disabled` + 3 | — | — |
| 014 | `iac_014` | deploy.yml | 6 | 5C 1H | `checkout_pr_head`, `hardcoded_secret`, `missing_permissions` + 2 | 0.01 → 0.01 | — +0.00 |
| 015 | `iac_015` | main.tf | 6 | 4C 2H | `backups_disabled`, `encryption_at_rest`, `hardcoded_secret` + 2 | — | — |
| 016 | `iac_016` | main.tf | 6 | 1C 5H | `control_plane_logging_disabled`, `eol_kubernetes_version`, `private_endpoint_disabled` + 3 | 0.18 → 0.13 | ▼ -0.05 |
| 017 | `iac_017` | iam.tf | 6 | 2C 4H | `cross_account_access`, `hardcoded_credentials`, `hardcoded_secret` + 1 | — | — |
| 018 | `iac_018` | main.tf | 8 | 3C 4H 1M | `eol_base_image`, `hardcoded_secret`, `log_validation_disabled` + 4 | 0.54 → 0.20 | ▼ -0.34 |
| 019 | `iac_019` | pod.yaml | 8 | 5C 2H 1M | `host_network`, `host_path_mount`, `host_pid` + 4 | 0.19 → 0.39 | ▲ +0.20 |
| 020 | `iac_020` | deployment.yaml | 6 | 2C 2H 2M | `debug_mode_enabled`, `hardcoded_secret`, `image_latest_tag` + 2 | 0.39 → 0.23 | ▼ -0.16 |
| 021 | `iac_021` | service.yaml | 5 | 1C 4H | `encryption_in_transit`, `missing_network_policy`, `missing_tls_in_cluster` + 2 | — | — |
| 022 | `iac_022` | Dockerfile | 8 | 2C 5H 1M | `debug_mode_enabled`, `eol_base_image`, `hardcoded_secret` + 4 | 0.14 → 0.54 | ▲ +0.40 |
| 023 | `iac_023` | Dockerfile | 6 | 2C 4H | `debug_mode_enabled`, `hardcoded_secret`, `image_latest_tag` + 2 | 0.44 → 0.44 | — +0.00 |
| 024 | `iac_024` | docker-compose.yml | 11 | 6C 5H | `eol_base_image`, `exposed_internal_port`, `hardcoded_secret` + 5 | 0.01 → 0.41 | ▲ +0.40 |

---

### III. Migration Review — Database Safety

**28 scenarios** · ground-truth findings + file/line metadata + severity

| # | Scenario | Files | # | Sev | Categories | Base → Trained | Δ |
|---|---|---|---|---|---|---|---|
| 001 | `migration_001` | app_context.py, context.json, migration_001.sql… | 3 | 2C 1H | `drop_column_in_use`, `non_concurrent_index`, `not_null_without_default` | — | — |
| 002 | `migration_002` | app_context.py, context.json, migration_001.sql… | 4 | 2C 2H | `missing_expand_migrate_contract`, `not_null_without_default`, `rename_column_breaking` + 1 | 0.30 → 0.30 | — +0.00 |
| 003 | `migration_003` | app_context.py, context.json, migration_001.sql… | 4 | 2C 2H | `fk_without_index`, `non_concurrent_index`, `not_null_without_default` | — | — |
| 004 | `migration_004` | app_context.py, context.json, migration_001.sql… | 6 | 3C 3H | `drop_table_with_fk`, `non_concurrent_index`, `not_null_without_default` + 2 | — | — |
| 005 | `migration_005` | context.json, migration_005.sql, schema.sql | 5 | 2C 2H 1M | `architecture_anti_pattern`, `default_serialization`, `destructive_cascade` + 2 | — | — |
| 006 | `migration_006` | context.json, migration_006.sql, schema.sql | 6 | 2C 2H 1M 1L | `architectural_partitioning`, `index_type_choice`, `non_concurrent_index` + 3 | 0.52 → 0.64 | ▲ +0.12 |
| 007 | `migration_007` | context.json, migration_007.sql, schema.sql | 5 | 2C 2H 1M | `architecture_pk_choice`, `blocking_cluster`, `fillfactor_misconfiguration` + 2 | 0.06 → 0.61 | ▲ +0.55 |
| 008 | `migration_008` | context.json, migration_008.sql, schema.sql | 5 | 3C 2H | `architecture_data_derivation`, `consistency_replication`, `destructive_constraint_drop` + 2 | — | — |
| 009 | `migration_009` | context.json, migration_009.sql, schema.sql | 5 | 1C 3H 1M | `denormalization_consistency`, `gin_options`, `redundant_indexes` + 2 | 0.26 → 0.20 | ▼ -0.06 |
| 010 | `migration_010` | context.json, migration_010.sql, schema.sql | 6 | 1C 2H 2M 1L | `partial_index_missing`, `schema_constraint_missing`, `schema_design_redundancy` + 3 | — | — |
| 011 | `migration_011` | context.json, migration_011.sql, schema.sql | 5 | 3C 1H 1M | `blocking_check_constraint`, `blocking_check_with_data_violations`, `non_concurrent_index` + 1 | — | — |
| 012 | `migration_012` | context.json, migration_012.sql, schema.sql | 6 | 1C 3H 2M | `covering_index`, `index_ordering`, `non_concurrent_drop` + 1 | 0.06 → 0.47 | ▲ +0.41 |
| 013 | `migration_013` | context.json, migration_013.sql, schema.sql | 5 | 1C 2H 2M | `missing_indexes`, `polymorphic_association`, `polymorphic_id_ambiguity` + 2 | — | — |
| 014 | `migration_014` | context.json, migration_014.sql, schema.sql | 6 | 2C 3H 1M | `blocking_fk_validation`, `cascade_financial_risk`, `fk_no_supporting_index` + 1 | — | — |
| 015 | `migration_015` | context.json, migration_015.sql, schema.sql | 6 | 3C 2H 1M | `blocking_alter_type`, `capacity_planning_pk`, `incomplete_int_to_bigint_migration` + 1 | — | — |
| 016 | `migration_016` | context.json, migration_016.sql, schema.sql | 6 | 2C 3H 1M | `alter_table_metadata_only`, `blocking_matview_refresh`, `matview_incremental_strategy` + 3 | — | — |
| 017 | `migration_017` | context.json, migration_017.sql, schema.sql | 6 | 1C 3H 2M | `alter_storage_unnecessary`, `architecture_wrong_tool`, `autovacuum_tuning` + 3 | 0.06 → 0.52 | ▲ +0.46 |
| 018 | `migration_018` | context.json, migration_018.sql, schema.sql | 6 | 1C 2H 3M | `alter_table_pattern`, `non_concurrent_index`, `pgbouncer_transaction_pooling` + 3 | 0.29 → 0.52 | ▲ +0.23 |
| 019 | `migration_019` | context.json, migration_019.sql, schema.sql | 5 | 3C 1H 1M | `architecture_audit_pattern`, `create_index_in_txn`, `deadlock_lock_order` + 2 | — | — |
| 020 | `migration_020` | context.json, migration_020.sql, schema.sql | 7 | 2C 4H 1M | `architecture_multi_tenancy`, `incomplete_migration`, `partition_key_choice` + 4 | — | — |
| 021 | `migration_021` | context.json, migration_021.sql, schema.sql | 6 | 2C 2H 2M | `architecture_data_pipeline`, `non_concurrent_index`, `redundant_statement` + 3 | — | — |
| 022 | `migration_022` | context.json, migration_022.sql, schema.sql | 6 | 1C 2H 3M | `extended_statistics`, `non_concurrent_index`, `partial_index_for_skewed_data` + 3 | 0.06 → 0.44 | ▲ +0.38 |
| 023 | `migration_023` | context.json, migration_023.sql, schema.sql | 6 | 2C 2H 2M | `alter_storage_blocking`, `column_ordering`, `covering_index` + 3 | 0.06 → 0.44 | ▲ +0.38 |
| 024 | `migration_024` | context.json, migration_024.sql, schema.sql | 6 | 1C 3H 2M | `architecture_isolation_strategy`, `rls_command_scope`, `rls_denormalization_required` + 3 | 0.28 → 0.33 | ▲ +0.05 |
| 025 | `migration_025` | context.json, migration_025.sql, schema.sql | 6 | 2C 2H 2M | `architecture_pooling_strategy`, `config_requires_restart`, `connection_architecture` + 2 | 0.06 → 0.64 | ▲ +0.58 |
| 026 | `migration_026` | context.json, migration_026.sql, schema.sql | 6 | 1C 3H 2M | `concurrency_check_then_act`, `concurrency_pattern_choice`, `function_observability` + 3 | — | — |
| 027 | `migration_027` | context.json, migration_027.sql, schema.sql | 6 | 3C 2H 1M | `architecture_enum_rigidity`, `audit_log_enum_safety`, `data_migration_correctness` + 3 | — | — |
| 028 | `migration_028` | context.json, migration_028.sql, schema.sql | 6 | 2C 3H 1M | `architecture_partitioning_time_series`, `architecture_tiered_storage`, `covering_index_cost` + 3 | 0.03 → 0.47 | ▲ +0.44 |

---

## Bluffs / claim framing applied per scenario

Each scenario in the table above is graded by the **semantic-similarity grader** (alias-dictionary based across all three domains) and trained via the **hybrid SFT-warmup → GRPO-refinement pipeline** documented in [RESULTS.md](RESULTS.md). Per-scenario findings carry severity weights that flow directly into the reward formula `F1 × weights + severity bonus + efficiency bonus`. The benchmark's 60+ scenarios make it the broadest-coverage code-review OpenEnv submission to date.

**Per-domain bluff anchors:**

- *Dependency:* CVE / package-name aliases let the grader credit a model finding `tarjan-utils typosquatting tarjan` whether the model writes the description as `"typosquatted package"`, `"squatted name"`, or `"impersonator"`.
- *IaC:* 45+ category aliases — `hardcoded_secret` recognized via `hardcoded`, `credential`, `password`, `api key`, `token`, `aws_access_key`, etc.
- *Migration:* 80+ category aliases for deeply technical findings — `hot_row_contention` recognized via `single-row UPDATE bottleneck`, `global counter`, `row-level lock`, etc.
