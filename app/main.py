from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page for the SecureReview OpenEnv Space.

    Rendered at the base URL so the Hugging Face Space preview shows
    environment info and quick-start guidance instead of a raw 404.
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SecureReview — OpenEnv</title>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #0d1117;
    color: #e6edf3;
    max-width: 860px;
    margin: 40px auto;
    padding: 0 24px;
    line-height: 1.6;
  }
  h1 { color: #f0883e; margin-bottom: 4px; }
  .subtitle { color: #8b949e; margin-bottom: 32px; }
  h2 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 6px; margin-top: 32px; }
  code {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 2px 6px;
    color: #f0883e;
    font-size: 0.9em;
  }
  pre {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 14px;
    overflow-x: auto;
  }
  pre code { background: none; border: none; padding: 0; color: #e6edf3; }
  .task-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 16px 0; }
  .task {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 14px;
  }
  .task h3 { margin: 0 0 6px 0; font-size: 1em; color: #f0883e; }
  .difficulty { font-size: 0.8em; color: #8b949e; }
  .endpoint-list li { margin: 4px 0; }
  a { color: #58a6ff; }
  .badge {
    display: inline-block;
    background: #1f6feb;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75em;
    margin-left: 6px;
  }
</style>
</head>
<body>
  <h1>🔐 SecureReview</h1>
  <div class="subtitle">
    OpenEnv environment for AI-powered security code review
    <span class="badge">v1.0.0</span>
  </div>

  <p>
    SecureReview evaluates an AI agent's ability to perform security-conscious
    code review across three critical domains: dependency supply chains, cloud
    infrastructure-as-code, and database migrations.
  </p>

  <h2>Tasks</h2>
  <div class="task-grid">
    <div class="task">
      <h3>Dependency Review</h3>
      <div class="difficulty">Easy · 15 steps · 6 scenarios</div>
      <p>Identify hallucinated, typosquatted, and CVE-vulnerable packages.</p>
    </div>
    <div class="task">
      <h3>IaC Review</h3>
      <div class="difficulty">Medium · 25 steps · 6 scenarios</div>
      <p>Detect security misconfigurations in Terraform / Kubernetes configs.</p>
    </div>
    <div class="task">
      <h3>Migration Review</h3>
      <div class="difficulty">Hard · 35 steps · 4 scenarios</div>
      <p>Analyze SQL migrations for safety risks considering production context.</p>
    </div>
  </div>

  <h2>API Endpoints</h2>
  <ul class="endpoint-list">
    <li><a href="/health"><code>GET /health</code></a> — Health check</li>
    <li><a href="/tasks"><code>GET /tasks</code></a> — List available tasks</li>
    <li><a href="/metadata"><code>GET /metadata</code></a> — Environment metadata</li>
    <li><a href="/schema"><code>GET /schema</code></a> — Action / observation / state schemas</li>
    <li><a href="/docs"><code>GET /docs</code></a> — Interactive OpenAPI docs</li>
    <li><code>POST /reset</code> — Start a new episode</li>
    <li><code>POST /step</code> — Execute an action</li>
    <li><code>GET /state</code> — Current episode state</li>
    <li><code>POST /mcp</code> — JSON-RPC 2.0 MCP endpoint</li>
  </ul>

  <h2>Quick Start</h2>
  <pre><code># Start an episode
curl -X POST https://sam25kat-securereview.hf.space/reset \\
  -H "Content-Type: application/json" \\
  -d '{"task_id": "dependency_review"}'

# Report a finding
curl -X POST https://sam25kat-securereview.hf.space/step \\
  -H "Content-Type: application/json" \\
  -d '{"action": {"action_type": "report_finding", "finding": {
    "file": "requirements.txt",
    "line": 2,
    "rule_id": "DEP-002",
    "severity": "critical",
    "description": "Typosquat detected"
  }}}'

# End the review
curl -X POST https://sam25kat-securereview.hf.space/step \\
  -H "Content-Type: application/json" \\
  -d '{"action": {"action_type": "mark_complete"}}'</code></pre>

  <h2>Links</h2>
  <ul>
    <li><a href="https://github.com/sam25kat/Secure_Reveiw">GitHub Repository</a></li>
    <li><a href="https://huggingface.co/spaces/sam25kat/securereview/tree/main">Source on Hugging Face</a></li>
  </ul>

  <p style="margin-top: 40px; color: #8b949e; font-size: 0.85em;">
    Built for the Meta PyTorch OpenEnv Hackathon by <strong>Team CookHouse</strong>.
  </p>
</body>
</html>"""


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
