from typing import List, Optional

from app.models import Finding, GroundTruthFinding
from app.graders.base import BaseGrader, MatchResult

# Maps rule_id to category for fuzzy matching
RULE_CATEGORY_MAP = {
    "IAC-001": "public_access",
    "IAC-002": "encryption_at_rest",
    "IAC-003": "encryption_in_transit",
    "IAC-004": "permissive_security_group",
    "IAC-005": "iam_wildcard",
    "IAC-006": "missing_logging",
    "IAC-007": "public_subnet",
    "IAC-008": "missing_network_acl",
    "IAC-009": "privileged_container",
    "IAC-010": "cross_account_access",
    "IAC-011": "missing_backup",
    "IAC-012": "hardcoded_credentials",
}


class IaCGrader(BaseGrader):
    """Matches findings by (resource_identifier, rule_category).

    Primary match: exact match_key from ground truth found in finding description.
    Secondary match: same file + same rule category (via rule_id mapping).
    """

    def _get_category(self, rule_id: str) -> Optional[str]:
        return RULE_CATEGORY_MAP.get(rule_id.upper())

    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        result = MatchResult()
        matched_gt_keys: set = set()

        # Build lookup structures
        gt_by_key = {gt.match_key.lower(): gt for gt in ground_truth}
        gt_by_file_category = {}
        for gt in ground_truth:
            if gt.category:
                key = (gt.file.lower(), gt.category.lower())
                if key not in gt_by_file_category:
                    gt_by_file_category[key] = []
                gt_by_file_category[key].append(gt)

        for af in agent_findings:
            matched = False

            # Strategy 1: Check if any ground truth match_key appears in description
            for key, gt in gt_by_key.items():
                if key not in matched_gt_keys:
                    # Check if resource name from match_key appears in description
                    resource_part = key.split("|")[0] if "|" in key else key
                    if resource_part in af.description.lower():
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(key)
                        matched = True
                        break

            # Strategy 2: Match by file + rule category
            if not matched:
                agent_category = self._get_category(af.rule_id)
                if agent_category:
                    lookup_key = (af.file.lower(), agent_category.lower())
                    candidates = gt_by_file_category.get(lookup_key, [])
                    for gt in candidates:
                        if gt.match_key.lower() not in matched_gt_keys:
                            result.true_positives.append((af, gt))
                            matched_gt_keys.add(gt.match_key.lower())
                            matched = True
                            break

            # Strategy 3: Match by file + approximate line number (within 5 lines)
            if not matched and af.line is not None:
                for gt in ground_truth:
                    if (
                        gt.match_key.lower() not in matched_gt_keys
                        and gt.file.lower() == af.file.lower()
                        and gt.line is not None
                        and abs(gt.line - af.line) <= 5
                    ):
                        agent_cat = self._get_category(af.rule_id)
                        gt_cat = gt.category
                        if agent_cat and gt_cat and agent_cat.lower() == gt_cat.lower():
                            result.true_positives.append((af, gt))
                            matched_gt_keys.add(gt.match_key.lower())
                            matched = True
                            break

            if not matched:
                result.false_positives.append(af)

        for gt in ground_truth:
            if gt.match_key.lower() not in matched_gt_keys:
                result.false_negatives.append(gt)

        return result
