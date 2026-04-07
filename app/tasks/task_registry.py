import json
import random
from pathlib import Path
from typing import Dict, List, Optional

from app.models import (
    ScenarioConfig, FileContent, GroundTruthFinding,
    TaskInfo, Difficulty, Severity
)

SCENARIOS_DIR = Path(__file__).parent / "scenarios"

EXTENSION_TO_LANGUAGE = {
    ".tf": "hcl",
    ".hcl": "hcl",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sql": "sql",
    ".py": "python",
    ".txt": "txt",
    ".json": "json",
    ".md": "markdown",
}

TASK_DEFINITIONS: Dict[str, TaskInfo] = {
    "dependency_review": TaskInfo(
        id="dependency_review",
        name="Dependency & Supply Chain Review",
        description="Review dependency files for hallucinated packages, typosquatting, and known vulnerabilities",
        difficulty=Difficulty.EASY,
        max_steps=15,
    ),
    "iac_review": TaskInfo(
        id="iac_review",
        name="Infrastructure-as-Code Security Review",
        description="Review Terraform/Kubernetes configurations for security misconfigurations",
        difficulty=Difficulty.MEDIUM,
        max_steps=25,
    ),
    "migration_review": TaskInfo(
        id="migration_review",
        name="Database Migration Safety Review",
        description="Review SQL migration scripts for backward-incompatibility, safety risks, and production impact",
        difficulty=Difficulty.HARD,
        max_steps=35,
    ),
}

TASK_SCENARIO_DIRS = {
    "dependency_review": "dependency",
    "iac_review": "iac",
    "migration_review": "migration",
}


def _detect_language(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(suffix, "txt")


def _load_file_content(filepath: Path) -> FileContent:
    content = filepath.read_text(encoding="utf-8")
    return FileContent(
        filename=filepath.name,
        content=content,
        language=_detect_language(filepath.name),
    )


class TaskRegistry:
    def __init__(self):
        self._scenarios: Dict[str, Dict[str, ScenarioConfig]] = {}
        self._load_all_scenarios()

    def _load_all_scenarios(self):
        for task_id, subdir in TASK_SCENARIO_DIRS.items():
            self._scenarios[task_id] = {}
            task_dir = SCENARIOS_DIR / subdir
            if not task_dir.exists():
                continue
            for scenario_dir in sorted(task_dir.iterdir()):
                if not scenario_dir.is_dir():
                    continue
                scenario = self._load_scenario(task_id, scenario_dir)
                if scenario:
                    self._scenarios[task_id][scenario.scenario_id] = scenario

    def _load_scenario(self, task_id: str, scenario_dir: Path) -> Optional[ScenarioConfig]:
        gt_path = scenario_dir / "ground_truth.json"
        if not gt_path.exists():
            return None

        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        # Load all non-ground-truth files in the directory
        all_files: Dict[str, FileContent] = {}
        for filepath in sorted(scenario_dir.iterdir()):
            if filepath.is_file() and filepath.name != "ground_truth.json":
                all_files[filepath.name] = _load_file_content(filepath)

        # Parse ground truth findings
        ground_truth = []
        for gt in gt_data.get("ground_truth", []):
            ground_truth.append(GroundTruthFinding(
                file=gt["file"],
                line=gt.get("line"),
                rule_id=gt["rule_id"],
                severity=Severity(gt["severity"]),
                description=gt["description"],
                match_key=gt["match_key"],
                category=gt.get("category"),
            ))

        return ScenarioConfig(
            scenario_id=gt_data.get("scenario_id", scenario_dir.name),
            task_id=task_id,
            description=gt_data.get("description", ""),
            files=all_files,
            initial_files=gt_data.get("initial_files", list(all_files.keys())),
            available_files=gt_data.get("available_files", []),
            ground_truth=ground_truth,
            review_checklist=gt_data.get("review_checklist", []),
        )

    def get_tasks(self) -> List[TaskInfo]:
        return list(TASK_DEFINITIONS.values())

    def get_task_info(self, task_id: str) -> TaskInfo:
        if task_id not in TASK_DEFINITIONS:
            raise ValueError(
                f"Unknown task_id '{task_id}'. Valid: {list(TASK_DEFINITIONS.keys())}"
            )
        return TASK_DEFINITIONS[task_id]

    def get_scenario(self, task_id: str, scenario_id: str) -> ScenarioConfig:
        if task_id not in self._scenarios:
            raise ValueError(f"Unknown task_id '{task_id}'")
        scenarios = self._scenarios[task_id]
        if scenario_id not in scenarios:
            raise ValueError(
                f"Unknown scenario_id '{scenario_id}' for task '{task_id}'. "
                f"Valid: {list(scenarios.keys())}"
            )
        return scenarios[scenario_id]

    def get_random_scenario(self, task_id: str) -> ScenarioConfig:
        if task_id not in self._scenarios:
            raise ValueError(f"Unknown task_id '{task_id}'")
        scenarios = list(self._scenarios[task_id].values())
        if not scenarios:
            raise ValueError(f"No scenarios found for task '{task_id}'")
        return random.choice(scenarios)

    def get_scenario_ids(self, task_id: str) -> List[str]:
        if task_id not in self._scenarios:
            raise ValueError(f"Unknown task_id '{task_id}'")
        return list(self._scenarios[task_id].keys())
