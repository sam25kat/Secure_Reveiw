from typing import List

from app.models import Finding, GroundTruthFinding
from app.graders.base import BaseGrader, MatchResult


class DependencyGrader(BaseGrader):
    """Matches findings by package name (exact, case-insensitive).

    Primary match: match_key (package name) found in finding description.
    Secondary match: line number matches ground truth line.
    """

    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        result = MatchResult()
        gt_by_key = {gt.match_key.lower(): gt for gt in ground_truth}
        gt_by_line = {}
        for gt in ground_truth:
            if gt.line is not None:
                gt_by_line[(gt.file, gt.line)] = gt

        matched_gt_keys: set = set()

        for af in agent_findings:
            matched = False

            # Strategy 1: Check if any ground truth match_key appears in the description
            for key, gt in gt_by_key.items():
                if key not in matched_gt_keys and key in af.description.lower():
                    result.true_positives.append((af, gt))
                    matched_gt_keys.add(key)
                    matched = True
                    break

            # Strategy 2: Match by line number
            if not matched and af.line is not None:
                line_key = (af.file, af.line)
                if line_key in gt_by_line:
                    gt = gt_by_line[line_key]
                    if gt.match_key.lower() not in matched_gt_keys:
                        result.true_positives.append((af, gt))
                        matched_gt_keys.add(gt.match_key.lower())
                        matched = True

            if not matched:
                result.false_positives.append(af)

        for gt in ground_truth:
            if gt.match_key.lower() not in matched_gt_keys:
                result.false_negatives.append(gt)

        return result
