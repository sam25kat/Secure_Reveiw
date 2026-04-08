from fastapi import FastAPI, HTTPException, Request
from typing import List, Optional, Any, Dict

from app.models import (
    ResetRequest, ResetResponse, StepRequest, StepResponse, TaskInfo,
    Action, Observation
)
from app.environment import SecureReviewEnvironment

ENV_NAME = "securereview"
ENV_DESCRIPTION = (
    "AI Security Code Review Environment — evaluates an agent's ability "
    "to identify security vulnerabilities across dependency supply chains, "
    "infrastructure-as-code, and database migrations"
)

app = FastAPI(
    title="SecureReview",
    version="1.0.0",
    description=ENV_DESCRIPTION,
)

env = SecureReviewEnvironment()

DEFAULT_TASK_ID = "dependency_review"


@app.get("/health")
async def health():
    """OpenEnv health endpoint — must return ``status: healthy``."""
    return {"status": "healthy"}


@app.get("/metadata")
async def metadata():
    """OpenEnv metadata endpoint — returns environment name and description."""
    return {
        "name": ENV_NAME,
        "description": ENV_DESCRIPTION,
        "version": "1.0.0",
        "author": "Team CookHouse",
        "tasks": [t.model_dump() for t in env.get_tasks()],
    }


@app.get("/schema")
async def schema():
    """OpenEnv schema endpoint — returns action, observation, and state schemas."""
    return {
        "action": Action.model_json_schema(),
        "observation": Observation.model_json_schema(),
        "state": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "scenario_id": {"type": "string"},
                "current_step": {"type": "integer"},
                "max_steps": {"type": "integer"},
                "done": {"type": "boolean"},
                "findings_count": {"type": "integer"},
                "revealed_files": {"type": "array", "items": {"type": "string"}},
                "final_score": {"type": ["number", "null"]},
            },
        },
    }


@app.post("/mcp")
async def mcp(request: Request):
    """Minimal JSON-RPC 2.0 MCP endpoint for OpenEnv validator compatibility.

    Exposes the environment's available tasks as MCP tools. This is a
    lightweight shim — agents should prefer the typed ``/reset`` and ``/step``
    endpoints for interaction.
    """
    try:
        payload: Dict[str, Any] = await request.json()
    except Exception:
        payload = {}

    req_id = payload.get("id", 1)
    method = payload.get("method", "")

    if method == "initialize":
        result: Dict[str, Any] = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": ENV_NAME, "version": "1.0.0"},
        }
    elif method == "tools/list":
        result = {
            "tools": [
                {
                    "name": t.id,
                    "description": t.description,
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "scenario_id": {"type": "string"},
                        },
                    },
                }
                for t in env.get_tasks()
            ]
        }
    elif method == "tools/call":
        result = {
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Use the HTTP /reset and /step endpoints to interact "
                        "with SecureReview. MCP tool-calling mode is not the "
                        "primary interface for this environment."
                    ),
                }
            ],
            "isError": False,
        }
    else:
        result = {"ok": True, "env": ENV_NAME}

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": result,
    }


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
