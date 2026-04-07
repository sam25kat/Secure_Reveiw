from typing import Dict, List, Optional, Tuple, Any

from app.models import (
    Action, ActionType, Finding, Observation, ReviewContext,
    FileContent, Reward, TaskInfo, ScenarioConfig
)
from app.tasks.task_registry import TaskRegistry
from app.graders.dependency_grader import DependencyGrader
from app.graders.iac_grader import IaCGrader
from app.graders.migration_grader import MigrationGrader
from app.graders.base import BaseGrader


GRADER_MAP: Dict[str, BaseGrader] = {
    "dependency_review": DependencyGrader(),
    "iac_review": IaCGrader(),
    "migration_review": MigrationGrader(),
}


class EpisodeState:
    def __init__(
        self,
        task_id: str,
        task_info: TaskInfo,
        scenario: ScenarioConfig,
    ):
        self.task_id = task_id
        self.task_info = task_info
        self.scenario = scenario
        self.current_step = 0
        self.max_steps = task_info.max_steps
        self.findings: List[Finding] = []
        self.done = False
        self.last_feedback: Optional[str] = None
        self.final_reward: Optional[Reward] = None
        # Track which files the agent has access to
        self.revealed_files: Dict[str, FileContent] = {}
        for fname in scenario.initial_files:
            if fname in scenario.files:
                self.revealed_files[fname] = scenario.files[fname]


class SecureReviewEnvironment:
    def __init__(self):
        self.registry = TaskRegistry()
        self._state: Optional[EpisodeState] = None

    def get_tasks(self) -> List[TaskInfo]:
        return self.registry.get_tasks()

    def reset(
        self, task_id: str, scenario_id: Optional[str] = None
    ) -> Tuple[Observation, Dict[str, Any]]:
        task_info = self.registry.get_task_info(task_id)

        if scenario_id:
            scenario = self.registry.get_scenario(task_id, scenario_id)
        else:
            scenario = self.registry.get_random_scenario(task_id)

        self._state = EpisodeState(
            task_id=task_id,
            task_info=task_info,
            scenario=scenario,
        )

        observation = self._build_observation()
        info = {
            "task_id": task_id,
            "scenario_id": scenario.scenario_id,
            "difficulty": task_info.difficulty.value,
            "max_steps": task_info.max_steps,
        }
        return observation, info

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if self._state is None:
            raise RuntimeError("No active episode. Call /reset first.")
        if self._state.done:
            raise RuntimeError("Episode already complete. Call /reset to start a new one.")

        state = self._state
        state.current_step += 1
        reward = 0.0
        info: Dict[str, Any] = {"step": state.current_step}

        if action.action_type == ActionType.REPORT_FINDING:
            reward, feedback = self._handle_report_finding(action, state)
            state.last_feedback = feedback

        elif action.action_type == ActionType.REQUEST_CONTEXT:
            feedback = self._handle_request_context(action, state)
            state.last_feedback = feedback

        elif action.action_type == ActionType.REQUEST_FILE_LIST:
            all_files = list(state.scenario.files.keys())
            state.last_feedback = f"Available files: {', '.join(all_files)}"

        elif action.action_type == ActionType.MARK_COMPLETE:
            return self._finish_episode(state, info, "Agent marked review complete.")

        # Check step budget
        if state.current_step >= state.max_steps and not state.done:
            return self._finish_episode(
                state, info, "Step budget exhausted."
            )

        observation = self._build_observation()
        return observation, reward, state.done, info

    def get_state(self) -> Dict[str, Any]:
        if self._state is None:
            raise RuntimeError("No active episode. Call /reset first.")
        state = self._state
        return {
            "task_id": state.task_id,
            "scenario_id": state.scenario.scenario_id,
            "current_step": state.current_step,
            "max_steps": state.max_steps,
            "done": state.done,
            "findings_count": len(state.findings),
            "revealed_files": list(state.revealed_files.keys()),
            "final_score": state.final_reward.score if state.final_reward else None,
        }

    def _handle_report_finding(
        self, action: Action, state: EpisodeState
    ) -> Tuple[float, str]:
        if action.finding is None:
            return -0.01, "Error: report_finding requires a 'finding' field."

        finding = action.finding
        state.findings.append(finding)

        # Small step reward: check if finding references a known file
        if finding.file in state.revealed_files:
            file_content = state.revealed_files[finding.file].content
            line_count = len(file_content.splitlines())
            if finding.line is None or 1 <= finding.line <= line_count:
                reward = 0.02
                feedback = (
                    f"Finding recorded for '{finding.file}'. "
                    f"{state.max_steps - state.current_step} steps remaining."
                )
            else:
                reward = -0.01
                feedback = (
                    f"Finding recorded but line {finding.line} is outside file range "
                    f"(1-{line_count}). {state.max_steps - state.current_step} steps remaining."
                )
        else:
            reward = 0.0
            feedback = (
                f"Finding recorded for '{finding.file}' (file not yet in review context). "
                f"{state.max_steps - state.current_step} steps remaining."
            )

        return reward, feedback

    def _handle_request_context(self, action: Action, state: EpisodeState) -> str:
        if not action.filename:
            return "Error: request_context requires a 'filename' field."

        fname = action.filename
        if fname in state.revealed_files:
            return f"File '{fname}' is already in your review context."

        if fname in state.scenario.files:
            state.revealed_files[fname] = state.scenario.files[fname]
            return f"File '{fname}' loaded into review context."
        else:
            return (
                f"File '{fname}' not available. "
                f"Use request_file_list to see available files."
            )

    def _finish_episode(
        self, state: EpisodeState, info: Dict[str, Any], reason: str
    ) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        state.done = True

        grader = GRADER_MAP.get(state.task_id)
        if grader is None:
            raise RuntimeError(f"No grader found for task '{state.task_id}'")

        reward_result = grader.grade(
            agent_findings=state.findings,
            ground_truth=state.scenario.ground_truth,
            steps_used=state.current_step,
            max_steps=state.max_steps,
        )
        state.final_reward = reward_result
        state.last_feedback = f"{reason} Final score: {reward_result.score}"

        info["reward_breakdown"] = reward_result.breakdown
        info["final_score"] = reward_result.score

        observation = self._build_observation()
        return observation, reward_result.score, True, info

    def _build_observation(self) -> Observation:
        state = self._state
        if state is None:
            raise RuntimeError("No active episode.")

        # Build list of available files the agent can still request
        unrevealed = [
            fname for fname in state.scenario.files.keys()
            if fname not in state.revealed_files
            and fname != "ground_truth.json"
        ]

        context = ReviewContext(
            task_id=state.task_id,
            task_description=state.scenario.description,
            difficulty=state.task_info.difficulty,
            files=list(state.revealed_files.values()),
            available_files=unrevealed,
            review_checklist=state.scenario.review_checklist,
            max_steps=state.max_steps,
            current_step=state.current_step,
        )

        findings_serialized = [f.model_dump() for f in state.findings]

        return Observation(
            context=context,
            findings_so_far=findings_serialized,
            feedback=state.last_feedback,
        )
