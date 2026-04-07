from abc import ABC, abstractmethod
from typing import List, Tuple

from app.models import Finding, GroundTruthFinding, Reward


class MatchResult:
    def __init__(self):
        self.true_positives: List[Tuple[Finding, GroundTruthFinding]] = []
        self.false_positives: List[Finding] = []
        self.false_negatives: List[GroundTruthFinding] = []


class BaseGrader(ABC):

    @abstractmethod
    def match_findings(
        self, agent_findings: List[Finding], ground_truth: List[GroundTruthFinding]
    ) -> MatchResult:
        ...

    def grade(
        self,
        agent_findings: List[Finding],
        ground_truth: List[GroundTruthFinding],
        steps_used: int,
        max_steps: int,
    ) -> Reward:
        matches = self.match_findings(agent_findings, ground_truth)
        tp = len(matches.true_positives)
        fp = len(matches.false_positives)
        fn = len(matches.false_negatives)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        # Severity accuracy bonus (up to 0.10)
        sev_correct = sum(
            1 for af, gt in matches.true_positives if af.severity == gt.severity
        )
        severity_bonus = (sev_correct / max(tp, 1)) * 0.10

        # False positive penalty: 0.03 per FP, capped at 0.20
        fp_penalty = min(fp * 0.03, 0.20)

        # Efficiency bonus: up to 0.05
        steps_ratio = steps_used / max(max_steps, 1)
        efficiency_bonus = max(0.0, (1.0 - steps_ratio) * 0.05)

        score = max(0.0, min(1.0, f1 * 0.85 + severity_bonus + efficiency_bonus - fp_penalty))

        return Reward(
            score=round(score, 2),
            breakdown={
                "f1": round(f1, 3),
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "true_positives": tp,
                "false_positives": fp,
                "false_negatives": fn,
                "severity_bonus": round(severity_bonus, 3),
                "fp_penalty": round(fp_penalty, 3),
                "efficiency_bonus": round(efficiency_bonus, 3),
            },
        )
