from typing import List

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


class MigrationGrader(BaseGrader):
    """Matches findings by (operation_type, target_object).

    Primary match: match_key components found in finding description.
    Secondary match: same file + matching line number (within 2 lines).
    """

    @staticmethod
    def _operation_matches(operation: str, rule_id: str, desc_lower: str) -> bool:
        """Check if the agent's finding is about the same kind of operation."""
        op_info = OPERATION_RULE_MAP.get(operation)
        if op_info is None:
            return True  # Unknown operation, allow match on target alone
        valid_rules, keywords = op_info
        # Match if rule_id matches OR at least one keyword appears in description
        if rule_id.upper() in valid_rules:
            return True
        return any(kw in desc_lower for kw in keywords)

    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        result = MatchResult()
        matched_gt_keys: set = set()

        gt_by_key = {gt.match_key.lower(): gt for gt in ground_truth}

        for af in agent_findings:
            matched = False
            desc_lower = af.description.lower()

            # Strategy 1: Check if operation and target from match_key appear in description
            for key, gt in gt_by_key.items():
                if key in matched_gt_keys:
                    continue
                # match_key format: "operation|target" e.g. "add_column|users.email_verified"
                parts = key.split("|")
                if len(parts) == 2:
                    operation, target = parts
                    # Check operation type is consistent (rule_id must match)
                    if not self._operation_matches(operation, af.rule_id, desc_lower):
                        continue
                    # Check target object appears in description
                    # For target like "users.email_verified", check both full and parts
                    target_parts = target.split(".")
                    target_found = target in desc_lower
                    if not target_found and len(target_parts) == 2:
                        # Check if both table and column are mentioned
                        target_found = (
                            target_parts[0] in desc_lower
                            and target_parts[1] in desc_lower
                        )
                    if target_found:
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(key)
                        matched = True
                        break

            # Strategy 2: Match by file + line number (within 2 lines)
            if not matched and af.line is not None:
                for gt in ground_truth:
                    if (
                        gt.match_key.lower() not in matched_gt_keys
                        and gt.file.lower() == af.file.lower()
                        and gt.line is not None
                        and abs(gt.line - af.line) <= 2
                    ):
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(gt.match_key.lower())
                        matched = True
                        break

            # Strategy 3: Match by rule_id if same file and only one GT with that rule
            if not matched:
                rule_candidates = [
                    gt for gt in ground_truth
                    if gt.match_key.lower() not in matched_gt_keys
                    and gt.rule_id.upper() == af.rule_id.upper()
                    and gt.file.lower() == af.file.lower()
                ]
                if len(rule_candidates) == 1:
                    gt = rule_candidates[0]
                    result.true_positives.append((af, gt))
                    matched_gt_keys.add(gt.match_key.lower())
                    matched = True

            if not matched:
                result.false_positives.append(af)

        for gt in ground_truth:
            if gt.match_key.lower() not in matched_gt_keys:
                result.false_negatives.append(gt)

        return result
