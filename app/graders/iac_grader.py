"""IaC Grader — semantic + structural matching.

Designed to credit correct findings regardless of exact phrasing. Each ground-truth
finding has a `category` field (e.g. "public_access", "hardcoded_secret"). The
grader credits an agent finding if any of these hold:

1. The match_key resource identifier (e.g. `aws_db_instance.analytics`) appears
   in the finding description.
2. The category text or its constituent words (e.g. "hardcoded secret",
   "public access") appears in the finding description.
3. The finding sits on the same file within ±5 lines of a ground-truth finding
   AND a category keyword overlap exists.

This avoids the rule_id → category map of older versions, which was brittle when
new scenarios introduced new rule_ids.
"""
from typing import List, Set

from app.models import Finding, GroundTruthFinding
from app.graders.base import BaseGrader, MatchResult


# Aliases: words that should also match a given category. Helps when models
# phrase findings naturally instead of using snake_case keywords.
CATEGORY_ALIASES = {
    "public_access":              ["public", "publicly accessible", "public-read", "public-read-write", "principal: '*'", "principal '*'"],
    "encryption_at_rest":         ["encryption", "unencrypted", "storage_encrypted", "not encrypted", "encrypt at rest"],
    "encryption_in_transit":      ["tls", "ssl", "https", "in transit", "plaintext"],
    "permissive_security_group":  ["security group", "0.0.0.0/0", "ingress", "open to internet", "public ingress"],
    "iam_wildcard":               ["iam", "wildcard", "action: \"*\"", "resource: \"*\"", "least privilege"],
    "wildcard_iam":               ["iam", "wildcard", "action: \"*\"", "resource: \"*\""],
    "hardcoded_secret":           ["hardcoded", "hard-coded", "secret", "password", "credential", "api key", "token", "aws_access_key", "aws_secret"],
    "hardcoded_credentials":      ["hardcoded", "credential", "password", "api key"],
    "missing_logging":            ["log", "logging", "audit", "cloudtrail", "no logs"],
    "log_validation_disabled":    ["log validation", "log file validation", "tamper"],
    "single_region_trail":        ["single region", "multi-region", "is_multi_region"],
    "public_log_bucket":          ["public", "log bucket", "audit bucket"],
    "backups_disabled":           ["backup", "retention", "snapshot"],
    "image_latest_tag":           ["latest tag", ":latest", "image tag", "non-deterministic"],
    "eol_base_image":             ["eol", "end of life", "end-of-life", "outdated", "legacy version"],
    "eol_kubernetes_version":     ["eol", "kubernetes version", "eks version", "k8s version"],
    "host_network":               ["hostnetwork", "host network"],
    "host_pid":                   ["hostpid", "host pid", "host process"],
    "privileged_container":       ["privileged", "privileged: true"],
    "run_as_root":                ["root", "runasuser: 0", "user 0", "user directive", "non-root"],
    "host_path_mount":            ["hostpath", "host path", "host filesystem"],
    "ssh_in_container":           ["ssh", "openssh"],
    "ssh_port_exposed":           ["expose 22", "ssh port", "port 22"],
    "unrestricted_ssh":           ["ssh", "source_security_group", "ssh access"],
    "unverified_download":        ["unverified", "checksum", "ADD https", "supply chain"],
    "service_account_token":      ["serviceaccount", "service account", "automount", "automountservice"],
    "missing_resource_limits":    ["resource limit", "limits.cpu", "limits.memory", "no limits", "without limits"],
    "missing_network_policy":     ["networkpolicy", "network policy"],
    "public_service_exposure":    ["loadbalancer", "load balancer", "public service", "external traffic"],
    "missing_tls_in_cluster":     ["tls", "plaintext", "in-cluster traffic"],
    "exposed_internal_port":      ["0.0.0.0:", "exposed port", "host network", "binding"],
    "debug_mode_enabled":         ["debug", "debug=true", "debug: true", "stack trace"],
    "public_kubernetes_api":      ["endpoint_public_access", "public kubernetes api", "public api endpoint", "api server"],
    "private_endpoint_disabled":  ["endpoint_private_access", "private endpoint", "private api"],
    "secrets_encryption_disabled":["secrets encryption", "etcd encryption", "kms encryption", "envelope encryption"],
    "control_plane_logging_disabled": ["control plane log", "audit log", "cluster_log_types", "enabled_cluster_log"],
    "versioning_disabled":        ["versioning", "versioning_disabled", "versioning_configuration"],
    "pull_request_pwn":           ["pull_request", "pull request", "untrusted pr", "pr code", "pwn"],
    "unpinned_action":            ["unpinned", "pin", "@v", "tag"],
    "checkout_pr_head":           ["checkout", "pull_request.head", "head.sha"],
    "missing_permissions":        ["permissions:", "permission block", "least privilege"],
    "public_subnet":              ["public subnet", "publicly routable"],
    "missing_network_acl":        ["network acl", "nacl"],
    "cross_account_access":       ["cross-account", "cross account", "external account"],
    "missing_backup":             ["backup", "snapshot"],
}


def _category_keywords(category: str) -> List[str]:
    """Get all keywords/phrases that should credit a finding for this category."""
    cat = category.lower()
    keywords = [cat, cat.replace("_", " "), cat.replace("_", "-")]
    keywords.extend(CATEGORY_ALIASES.get(cat, []))
    return [k.lower() for k in keywords if k]


class IaCGrader(BaseGrader):
    """Multi-strategy matching for infrastructure findings.

    Credits an agent's finding against a ground-truth finding if any of:
    - resource identifier from match_key appears in description
    - category text (or its aliases) appears in description AND files match
    - line number is within ±5 of GT and category keyword overlap exists
    """

    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        result = MatchResult()
        matched_gt_keys: Set[str] = set()

        for af in agent_findings:
            matched = False
            af_desc = (af.description or "").lower()
            af_file = (af.file or "").lower()

            # Strategy 1 — match_key resource identifier in description
            for gt in ground_truth:
                key = gt.match_key.lower()
                if key in matched_gt_keys:
                    continue
                resource_part = key.split("|")[0]
                if resource_part and resource_part in af_desc:
                    result.true_positives.append((af, gt))
                    matched_gt_keys.add(key)
                    matched = True
                    break
            if matched:
                continue

            # Strategy 2 — same file + category keywords appear in description
            for gt in ground_truth:
                key = gt.match_key.lower()
                if key in matched_gt_keys or not gt.category:
                    continue
                if gt.file.lower() != af_file:
                    continue
                for kw in _category_keywords(gt.category):
                    if kw in af_desc:
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(key)
                        matched = True
                        break
                if matched:
                    break
            if matched:
                continue

            # Strategy 3 — same file + ±5 lines + any category keyword overlap
            if af.line is not None:
                for gt in ground_truth:
                    key = gt.match_key.lower()
                    if (
                        key in matched_gt_keys
                        or gt.file.lower() != af_file
                        or gt.line is None
                        or abs(gt.line - af.line) > 5
                    ):
                        continue
                    if not gt.category:
                        continue
                    for kw in _category_keywords(gt.category):
                        if kw in af_desc:
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
