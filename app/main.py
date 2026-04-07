from fastapi import FastAPI, HTTPException
from typing import List

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


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[TaskInfo])
async def get_tasks():
    return env.get_tasks()


@app.post("/reset", response_model=ResetResponse)
async def reset(request: ResetRequest):
    try:
        observation, info = env.reset(request.task_id, request.scenario_id)
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
