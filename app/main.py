from fastapi import FastAPI, HTTPException
from typing import List, Optional

from app.models import (
    ResetRequest, ResetResponse, StepRequest, StepResponse, TaskInfo
)
from app.environment import SecureReviewEnvironment

app = FastAPI(
    title="SecureReview",
    version="1.0.0",
    description="AI Security Code Review Environment for OpenEnv",
)

env = SecureReviewEnvironment()

DEFAULT_TASK_ID = "dependency_review"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskInfo])
async def get_tasks():
    return env.get_tasks()


@app.post("/reset", response_model=ResetResponse)
async def reset(request: Optional[ResetRequest] = None):
    """Reset the environment. Body is optional; defaults to dependency_review task."""
    try:
        if request is None:
            task_id = DEFAULT_TASK_ID
            scenario_id = None
        else:
            task_id = request.task_id or DEFAULT_TASK_ID
            scenario_id = request.scenario_id
        observation, info = env.reset(task_id, scenario_id)
        return ResetResponse(observation=observation, info=info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest):
    try:
        observation, reward, done, info = env.step(request.action)
        return StepResponse(
            observation=observation, reward=reward, done=done, info=info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/state")
async def get_state():
    try:
        return env.get_state()
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
