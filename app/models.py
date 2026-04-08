from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from enum import Enum


# === Enums ===

class ActionType(str, Enum):
    REPORT_FINDING = "report_finding"
    REQUEST_CONTEXT = "request_context"
    REQUEST_FILE_LIST = "request_file_list"
    MARK_COMPLETE = "mark_complete"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# === Observation Space ===

class FileContent(BaseModel):
    filename: str
    content: str
    language: str


class ReviewContext(BaseModel):
    task_id: str
    task_description: str
    difficulty: Difficulty
    files: List[FileContent]
    available_files: List[str]
    review_checklist: List[str]
    max_steps: int
    current_step: int


class Observation(BaseModel):
    context: ReviewContext
    findings_so_far: List[Dict[str, Any]]
    feedback: Optional[str] = None


# === Action Space ===

class Finding(BaseModel):
    file: str
    line: Optional[int] = None
    rule_id: str
    severity: Severity
    description: str


class Action(BaseModel):
    action_type: ActionType
    finding: Optional[Finding] = None
    filename: Optional[str] = None


# === Reward ===

class Reward(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    breakdown: Dict[str, Any]


# === API Request/Response Models ===

class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    scenario_id: Optional[str] = None


class StepRequest(BaseModel):
    action: Action


class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]


class ResetResponse(BaseModel):
    observation: Observation
    info: Dict[str, Any]


class TaskInfo(BaseModel):
    id: str
    name: str
    description: str
    difficulty: Difficulty
    max_steps: int


# === Internal: Ground Truth (not exposed via API) ===

class GroundTruthFinding(BaseModel):
    file: str
    line: Optional[int] = None
    rule_id: str
    severity: Severity
    description: str
    match_key: str
    category: Optional[str] = None


class ScenarioConfig(BaseModel):
    scenario_id: str
    task_id: str
    description: str
    files: Dict[str, FileContent]
    initial_files: List[str]
    available_files: List[str]
    ground_truth: List[GroundTruthFinding]
    review_checklist: List[str]
