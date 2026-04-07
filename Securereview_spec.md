# SecureReview — OpenEnv Hackathon Specification

## Table of Contents
1. [Hackathon Requirements (What They Want)](#1-hackathon-requirements)
2. [Our Idea (What We're Building)](#2-our-idea)
3. [Technical Architecture](#3-technical-architecture)
4. [Task Definitions & Grading](#4-task-definitions--grading)
5. [Action & Observation Spaces](#5-action--observation-spaces)
6. [Reward Function Design](#6-reward-function-design)
7. [Data & Scenarios](#7-data--scenarios)
8. [Project Structure](#8-project-structure)
9. [Implementation Plan](#9-implementation-plan)
10. [Key Technical Decisions](#10-key-technical-decisions)

---

## 1. Hackathon Requirements

### What is OpenEnv?
OpenEnv is Meta's interface library for RL post-training with environments. It standardizes how AI agents interact with real-world task simulations via a Gymnasium-style API. The repo is at `github.com/meta-pytorch/OpenEnv`.

### Submission Deliverables (ALL required or disqualified)
- [ ] **Hugging Face Space** — deployed, tagged with `openenv`, returns 200 and responds to `reset()`
- [ ] **OpenEnv spec compliance** — `openenv.yaml`, typed Pydantic models, `step()`/`reset()`/`state()` endpoints. Must pass `openenv validate`
- [ ] **Working Dockerfile** — `docker build && docker run` succeeds cleanly
- [ ] **3+ tasks with graders** — each scores 0.0–1.0, easy → medium → hard
- [ ] **Baseline inference script** — named `inference.py` in root, uses OpenAI client, reads `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN` from env vars
- [ ] **README** — environment description, motivation, action/observation spaces, task descriptions with difficulty, setup instructions, baseline scores

### Infrastructure Constraints
- Runtime of inference.py: **< 20 minutes**
- Machine specs: **vcpu=2, memory=8GB**
- Must use **OpenAI Client** for all LLM calls
- Environment variables: `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`

### Scoring Weights
| Parameter | Weight | What Scores 26-30 (max) |
|-----------|--------|-------------------------|
| Real-world utility | 30% | "Fills a real gap, immediate value for RL/agent community" |
| Task & grader quality | 25% | 3+ tasks, difficulty range, deterministic graders, hard task challenges frontier models |
| Environment design | 20% | Clean state, good reward shaping, sensible episode boundaries |
| Code quality & spec compliance | 15% | Passes openenv validate, Docker works, HF Space deploys, baseline reproduces |
| Creativity & novelty | 10% | Novel domain, interesting mechanics, clever reward design |

### Judging Process
1. **Phase 1: Automated Validation** — pass/fail gate (deploy, spec, Docker, baseline, 3+ tasks)
2. **Phase 2: Agentic Evaluation** — baseline re-run + standard Open LLM agent (e.g., Nemotron 3 Super) run against all environments
3. **Phase 3: Human Review** — top submissions reviewed by **Meta and Hugging Face engineers** for real-world utility, creativity, exploit checks

### Disqualification Triggers
- Environment doesn't deploy or respond
- Plagiarized or trivially modified existing environments
- Graders always return same score
- No baseline inference script

---

## 2. Our Idea

### Name: `SecureReview`
### Tagline: "The first OpenEnv environment for AI-powered security code review"

### The Concept
An environment where an AI agent performs **security review** of code artifacts across three critical domains:
1. **Dependency & Supply Chain Security** (Easy)
2. **Infrastructure-as-Code Misconfiguration Detection** (Medium)
3. **Database Migration Safety Analysis** (Hard)

### Why This Wins

**Real-world utility (targeting 26-30/30):**
- No existing OpenEnv environment tests code REVIEW capability — all 33+ existing envs test generation/execution/gameplay
- Every software team does security review daily — this is universal
- With AI generating increasing amounts of code (Copilot, Claude Code, Cursor), reviewing AI-generated artifacts is THE emerging problem
- Directly aligned with Meta's "AI engineer" initiative

**Creativity & novelty (targeting 8-10/10):**
- Zero overlap with any of the 33+ existing OpenEnv environments
- Zero overlap with existing benchmarks (SWE-bench tests code generation, not review)
- Three domains in one environment = unprecedented breadth
- Tests JUDGMENT, not generation — a fundamentally different cognitive capability

**Why judges (Meta/HF engineers) will care:**
- They deal with Terraform/K8s configs, dependency vulnerabilities, and database migrations daily
- This environment could actually be used internally for evaluating AI review tools
- Clean integration with smolagents and the broader HF ecosystem

### Narrative for README/Presentation
> "As AI generates an ever-larger share of production code, infrastructure, and database schemas, the critical bottleneck shifts from writing code to REVIEWING it. SecureReview is the first environment that evaluates an AI agent's ability to perform security-conscious code review across three domains where human reviewers are most stretched: dependency supply chains, cloud infrastructure configurations, and database migrations. Each domain represents a real category of production incidents that costs organizations billions annually."

---

## 3. Technical Architecture

### How OpenEnv Works (our environment is a server)

```
┌─────────────────────┐         ┌──────────────────────┐
│   inference.py       │         │   SecureReview Env   │
│   (the AI agent)     │ HTTP    │   (HF Space/Docker)  │
│                      │◄──────►│                      │
│  Uses OpenAI client  │        │  step() / reset()    │
│  to call LLM for     │        │  / state()           │
│  decisions           │        │                      │
└─────────────────────┘         └──────────────────────┘
```

### API Endpoints (FastAPI)

```
POST /reset
  Body: { "task_id": "dependency_review" | "iac_review" | "migration_review" }
  Returns: { "observation": { initial scenario data }, "info": { task metadata } }

POST /step
  Body: { "action": { action object } }
  Returns: { "observation": {...}, "reward": float, "done": bool, "info": {...} }

GET /state
  Returns: { current environment state }

GET /tasks
  Returns: list of available tasks with metadata

GET /health
  Returns: 200 OK
```

### State Machine Per Episode

```
RESET (task selected)
  ├── Agent receives: files to review + task description + review checklist
  │
  ├── STEP 1..N: Agent actions
  │   ├── report_finding(file, line, rule_id, severity, description)
  │   ├── request_context(filename)  → get additional files
  │   ├── request_file_list()        → see available files
  │   └── mark_review_complete()     → end episode, trigger grading
  │
  └── DONE: Grader computes final score (0.0 - 1.0)
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from enum import Enum

# === Observation Space ===
class FileContent(BaseModel):
    filename: str
    content: str
    language: str  # "terraform", "yaml", "sql", "json", "txt"

class ReviewContext(BaseModel):
    task_id: str
    task_description: str
    difficulty: Literal["easy", "medium", "hard"]
    files: List[FileContent]
    available_files: List[str]  # files agent can request
    review_checklist: List[str]  # what to look for
    max_steps: int
    current_step: int

class Observation(BaseModel):
    context: ReviewContext
    findings_so_far: List[dict]  # agent's submitted findings
    feedback: Optional[str] = None  # immediate feedback on last action

# === Action Space ===
class ActionType(str, Enum):
    REPORT_FINDING = "report_finding"
    REQUEST_CONTEXT = "request_context"
    REQUEST_FILE_LIST = "request_file_list"
    MARK_COMPLETE = "mark_complete"

class Severity(str, Enum):
    CRITICAL = "critical"    # data loss, RCE, credential exposure
    HIGH = "high"            # security misconfiguration, unsafe pattern
    MEDIUM = "medium"        # best practice violation, potential risk
    LOW = "low"              # style issue, minor improvement
    INFO = "info"            # informational observation

class Finding(BaseModel):
    file: str
    line: Optional[int] = None
    rule_id: str            # e.g., "DEP-001", "IAC-012", "MIG-005"
    severity: Severity
    description: str

class Action(BaseModel):
    action_type: ActionType
    finding: Optional[Finding] = None       # for REPORT_FINDING
    filename: Optional[str] = None          # for REQUEST_CONTEXT

# === Reward ===
class Reward(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    breakdown: dict  # { precision, recall, severity_accuracy, false_positive_penalty }
```

---

## 4. Task Definitions & Grading

### Task 1: Dependency & Supply Chain Review (EASY)

**What the agent sees:** A `requirements.txt` or `package.json` file with 15-30 dependencies.

**What's hidden (ground truth):** 3-6 planted issues:
- Hallucinated packages (names that don't exist on PyPI/npm)
- Typosquatting variants of real packages (e.g., `reqeusts` instead of `requests`)
- Packages with known critical CVEs (pulled from OSV database)
- Packages with suspicious install scripts or metadata

**Grader logic:**
```python
def grade_dependency_review(agent_findings, ground_truth):
    # True positives: agent found a real issue
    tp = len(set(agent_findings) & set(ground_truth))
    # False positives: agent flagged something that's fine
    fp = len(set(agent_findings) - set(ground_truth))
    # False negatives: agent missed a real issue
    fn = len(set(ground_truth) - set(agent_findings))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    # Weighted F1 with severity bonus
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # Penalty for false positives (0.05 per FP, capped at 0.3)
    fp_penalty = min(fp * 0.05, 0.3)

    score = max(0.0, f1 - fp_penalty)
    return round(score, 2)
```

**Why it's easy:** Mostly lookup-based. Agent can reason: "Does this package exist? Is it spelled correctly? Does it have known CVEs?"

**Scenario count:** 5-8 scenarios with varying numbers of issues.

### Task 2: Infrastructure-as-Code Security Review (MEDIUM)

**What the agent sees:** 2-5 Terraform (.tf) or Kubernetes (.yaml) files defining cloud infrastructure.

**What's hidden (ground truth):** 4-8 misconfigurations per scenario, based on CIS Benchmarks:

**Easy misconfigs (single-resource):**
- S3 bucket with public access enabled
- RDS instance without encryption at rest
- Security group allowing 0.0.0.0/0 on port 22
- EKS cluster without logging enabled

**Medium misconfigs (cross-resource):**
- Security group allows access but referenced VPC has no flow logs
- IAM role has admin policy but is attached to a publicly-accessible Lambda
- ECS task definition uses privileged mode in a public subnet

**Hard misconfigs (architectural):**
- Database in public subnet with security group that LOOKS restricted but has a permissive NACL
- Cross-account access role with overly broad trust policy
- Missing encryption in transit between services that handle PII

**Grader logic:** Same precision/recall framework as Task 1, but findings are matched by (resource_id, rule_category) rather than exact rule_id. Severity accuracy gives bonus points:
```python
severity_bonus = sum(1 for f in true_positives if f.agent_severity == f.ground_truth_severity) / len(true_positives) * 0.1
```

**Why it's medium:** Requires reading multiple files, understanding resource relationships, and reasoning about security implications of configurations. Not just pattern matching.

**Scenario count:** 5-8 scenarios with increasing architectural complexity.

### Task 3: Database Migration Safety Review (HARD)

**What the agent sees:** 1-3 SQL migration files + the current schema (CREATE TABLE statements) + a context file describing the production environment (table sizes, traffic patterns, deployment strategy).

**What's hidden (ground truth):** 3-6 unsafe patterns per scenario:

**Unsafe patterns to detect:**
- Adding NOT NULL column without default on large table (locks table)
- Dropping column still referenced by application code (provided in context)
- Renaming column during zero-downtime deployment
- Creating index non-concurrently on table with 10M+ rows (blocks writes)
- Changing column type causing implicit cast on large table
- Migration depends on another migration not yet deployed
- Missing data backfill step in expand-migrate-contract pattern
- Foreign key constraint on high-write table without index

**Production context clues (agent must use these):**
- Table row counts (determines if concurrent index creation is needed)
- Deployment strategy (rolling vs. blue-green affects what's safe)
- Application code snippets showing column usage
- Service dependencies (which other services read this table)

**Grader logic:** Same framework, but with additional scoring:
```python
# Bonus for identifying the correct REASON an operation is unsafe
reason_accuracy = sum(1 for f in tp if f.agent_reason_category == f.ground_truth_reason) / len(tp) * 0.15
# Bonus for suggesting the correct safe alternative
fix_bonus = sum(1 for f in tp if f.agent_suggested_fix is not None) / len(tp) * 0.05
```

**Why it's hard:** Requires:
1. Understanding SQL semantics and DDL implications
2. Reasoning about production context (table sizes, traffic)
3. Understanding deployment strategies and temporal ordering
4. Knowing safe alternatives (e.g., "use CREATE INDEX CONCURRENTLY")

This genuinely challenges frontier models because it requires multi-step reasoning with domain-specific knowledge.

**Scenario count:** 3-5 scenarios (fewer but more complex).

---

## 5. Action & Observation Spaces

### Action Space Summary

| Action | Parameters | Purpose | Available Steps |
|--------|-----------|---------|-----------------|
| `report_finding` | file, line, rule_id, severity, description | Submit a security finding | Any step |
| `request_context` | filename | Get content of an additional file | Any step (costs 1 step) |
| `request_file_list` | none | See all available files | Any step (costs 1 step) |
| `mark_complete` | none | End review, trigger grading | Any step |

### Step Budget
- Task 1 (Easy): 15 steps max
- Task 2 (Medium): 25 steps max
- Task 3 (Hard): 35 steps max

If agent exceeds step budget, episode auto-ends and is graded on findings so far.

### Observation Space Summary

On `reset()`, agent receives:
```json
{
  "task_id": "iac_review",
  "task_description": "Review the following Terraform configuration for security misconfigurations...",
  "difficulty": "medium",
  "files": [
    {"filename": "main.tf", "content": "...", "language": "terraform"},
    {"filename": "variables.tf", "content": "...", "language": "terraform"}
  ],
  "available_files": ["outputs.tf", "providers.tf", "iam.tf"],
  "review_checklist": [
    "Check for public access to storage resources",
    "Verify encryption at rest and in transit",
    "Check IAM policies for least privilege",
    "Verify logging and monitoring configuration",
    "Check network security group rules"
  ],
  "max_steps": 25,
  "current_step": 0
}
```

On `step(report_finding(...))`, agent receives:
```json
{
  "context": { "...same context, updated step count..." },
  "findings_so_far": [
    {"file": "main.tf", "line": 42, "rule_id": "IAC-003", "severity": "high", "description": "..."}
  ],
  "feedback": "Finding recorded. 23 steps remaining."
}
```

---

## 6. Reward Function Design

### Per-Step Rewards (partial progress signals)
The environment provides small intermediate rewards to guide learning:

```python
def compute_step_reward(action, state):
    if action.type == "report_finding":
        # Quick check: is this finding in the ballpark? (not exact grading)
        if is_plausible_finding(action.finding, state.files):
            return 0.02  # small positive signal for relevant findings
        else:
            return -0.01  # small negative for clearly irrelevant findings

    if action.type == "request_context":
        if action.filename in state.files_with_issues:
            return 0.01  # good instinct to look at relevant files
        return 0.0  # neutral

    if action.type == "mark_complete":
        return 0.0  # final reward computed by grader

    return 0.0
```

### Episode-End Reward (grader score)
When `mark_complete` is called or step budget exhausted:

```python
def compute_final_reward(agent_findings, ground_truth, task_config):
    # 1. Match findings to ground truth
    matches = match_findings(agent_findings, ground_truth, task_config.matching_strategy)

    tp = len(matches.true_positives)
    fp = len(matches.false_positives)
    fn = len(matches.false_negatives)

    # 2. Core precision/recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # 3. Severity accuracy bonus (up to 0.10)
    sev_correct = sum(1 for m in matches.true_positives if m.severity_match) / max(tp, 1)
    severity_bonus = sev_correct * 0.10

    # 4. False positive penalty (0.03 per FP, capped at 0.20)
    fp_penalty = min(fp * 0.03, 0.20)

    # 5. Efficiency bonus (used fewer steps = small bonus, up to 0.05)
    steps_used_ratio = state.current_step / task_config.max_steps
    efficiency_bonus = max(0, (1 - steps_used_ratio) * 0.05)

    # 6. Final score
    score = max(0.0, min(1.0, f1 * 0.85 + severity_bonus + efficiency_bonus - fp_penalty))

    return Reward(
        score=round(score, 2),
        breakdown={
            "f1": round(f1, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "severity_bonus": round(severity_bonus, 3),
            "fp_penalty": round(fp_penalty, 3),
            "efficiency_bonus": round(efficiency_bonus, 3),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
        }
    )
```

### Finding Matching Strategy
Findings are matched to ground truth using fuzzy matching:
- **Task 1 (Dependency):** Match by package name (exact)
- **Task 2 (IaC):** Match by (resource_identifier, rule_category) — e.g., ("aws_s3_bucket.data", "public_access")
- **Task 3 (Migration):** Match by (operation_type, target_object) — e.g., ("add_column", "users.email")

This prevents penalizing agents who describe the same issue with different wording.

---

## 7. Data & Scenarios

### Task 1: Dependency Scenarios

**Data sources:**
- Hallucinated package names: generate by common LLM misspellings (well-documented in slopsquatting research)
- Typosquatting: use known typosquat patterns (character swap, homoglyph, etc.)
- Vulnerable packages: pull from OSV (https://osv.dev) API for real CVEs
- Malicious packages: reference patterns from Datadog's malicious package dataset

**Scenario generation approach:**
1. Start with a real `requirements.txt` from a popular open-source project
2. Inject 3-6 issues: replace some packages with typosquats, add hallucinated ones, pin vulnerable versions
3. Store ground truth as JSON alongside

**Example scenario:**
```
# requirements.txt
flask==2.3.2
reqeusts==2.31.0          # TYPOSQUAT: should be "requests"
numpy==1.24.0
colorama==0.4.6
python-jwt==4.0.0         # CVE-2024-33663: critical auth bypass
torch-utils==0.1.2        # HALLUCINATED: doesn't exist on PyPI
pandas==2.0.3
cryptography==3.4.8       # CVE-2023-49083: vulnerable version
```

### Task 2: IaC Scenarios

**Data approach:**
- Curate 5-8 Terraform configurations representing common architectures:
  - Basic web app (EC2 + RDS + S3)
  - Serverless API (Lambda + API Gateway + DynamoDB)
  - Kubernetes cluster (EKS + VPC + IAM)
  - Data pipeline (S3 + Glue + Redshift)
- Inject known CIS Benchmark violations from Checkov's rule set
- Cross-reference with real-world breach patterns

**Each scenario includes:**
- 2-5 `.tf` files
- `ground_truth.json` with all misconfigurations, their locations, severity, and rule IDs
- Checkov rule IDs for reference (e.g., CKV_AWS_18: S3 logging disabled)

**Example misconfiguration:**
```hcl
# main.tf
resource "aws_s3_bucket" "data" {
  bucket = "company-data-prod"
  # MISSING: server-side encryption configuration
  # MISSING: bucket logging
  # MISSING: public access block
}

resource "aws_s3_bucket_policy" "data_policy" {
  bucket = aws_s3_bucket.data.id
  policy = jsonencode({
    Statement = [{
      Effect    = "Allow"
      Principal = "*"              # ISSUE: public access
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.data.arn}/*"
    }]
  })
}
```

### Task 3: Migration Scenarios

**Data approach:**
- Hand-craft 3-5 scenarios based on documented anti-patterns from:
  - strong_migrations (Rails) rule set
  - django-safe-migration rules
  - Atlas schema linting rules
  - Real incident postmortems

**Each scenario includes:**
- Current schema (`schema.sql`)
- Migration file(s) (`migration_001.sql`, etc.)
- Production context (`context.json` with table sizes, traffic, deployment strategy)
- Application code snippets showing column usage (`app_context.py`)
- `ground_truth.json`

**Example scenario:**
```sql
-- migration_001.sql
-- Ticket: Add email verification to users table

ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL;
-- UNSAFE: NOT NULL without DEFAULT on table with 12M rows, will lock table

CREATE INDEX idx_users_email_verified ON users(email_verified);
-- UNSAFE: not CONCURRENT, table has 12M rows, will block writes

ALTER TABLE users DROP COLUMN legacy_auth_token;
-- UNSAFE: column still referenced in auth_service (shown in app_context)
```

```json
// context.json
{
  "tables": {
    "users": {
      "row_count": 12000000,
      "avg_writes_per_second": 150,
      "read_replicas": 2
    }
  },
  "deployment_strategy": "rolling",
  "downtime_budget": "zero",
  "dependent_services": ["auth_service", "notification_service"]
}
```

---

## 8. Project Structure

```
securereview/
├── Dockerfile
├── openenv.yaml
├── inference.py                    # Baseline agent
├── README.md
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app with /reset, /step, /state
│   ├── environment.py              # Core environment logic
│   ├── models.py                   # Pydantic models (Observation, Action, Reward)
│   ├── graders/
│   │   ├── __init__.py
│   │   ├── base.py                 # Base grader class
│   │   ├── dependency_grader.py    # Task 1 grader
│   │   ├── iac_grader.py           # Task 2 grader
│   │   └── migration_grader.py     # Task 3 grader
│   └── tasks/
│       ├── __init__.py
│       ├── task_registry.py        # Task loading and management
│       └── scenarios/              # Scenario data
│           ├── dependency/
│           │   ├── scenario_001/
│           │   │   ├── requirements.txt
│           │   │   └── ground_truth.json
│           │   ├── scenario_002/
│           │   └── ...
│           ├── iac/
│           │   ├── scenario_001/
│           │   │   ├── main.tf
│           │   │   ├── variables.tf
│           │   │   ├── iam.tf
│           │   │   └── ground_truth.json
│           │   └── ...
│           └── migration/
│               ├── scenario_001/
│               │   ├── schema.sql
│               │   ├── migration_001.sql
│               │   ├── context.json
│               │   ├── app_context.py
│               │   └── ground_truth.json
│               └── ...
│
├── tests/
│   ├── test_environment.py
│   ├── test_graders.py
│   └── test_models.py
│
└── scripts/
    └── generate_scenarios.py       # Helper to create/validate scenarios
```

### openenv.yaml
```yaml
name: securereview
version: "1.0.0"
description: "AI Security Code Review Environment — evaluates an agent's ability to identify security vulnerabilities across dependency supply chains, infrastructure-as-code, and database migrations"
author: "Team CookHouse"

environment:
  type: http
  url: "http://localhost:7860"

tasks:
  - id: dependency_review
    name: "Dependency & Supply Chain Review"
    description: "Review dependency files for hallucinated packages, typosquatting, and known vulnerabilities"
    difficulty: easy
    max_steps: 15

  - id: iac_review
    name: "Infrastructure-as-Code Security Review"
    description: "Review Terraform/Kubernetes configurations for security misconfigurations"
    difficulty: medium
    max_steps: 25

  - id: migration_review
    name: "Database Migration Safety Review"
    description: "Review SQL migration scripts for backward-incompatibility, safety risks, and production impact"
    difficulty: hard
    max_steps: 35

action_space:
  type: structured
  actions:
    - report_finding
    - request_context
    - request_file_list
    - mark_complete

observation_space:
  type: structured
  fields:
    - context (ReviewContext)
    - findings_so_far (List[Finding])
    - feedback (Optional[str])
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

### requirements.txt (environment)
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
openenv-core>=0.1.0
```

---

## 9. Implementation Plan

### Build Order (Priority Sequence for Claude Code)

**Phase 1: Skeleton (do this first)**
1. Create project structure (all dirs and empty files)
2. Implement Pydantic models (`models.py`)
3. Implement basic FastAPI app with /reset, /step, /state endpoints
4. Implement environment state machine (`environment.py`)
5. Create `openenv.yaml`
6. Write Dockerfile
7. Verify: `docker build && docker run` → endpoints respond

**Phase 2: Task 1 — Dependency Review (easiest to build)**
1. Create 5 dependency scenarios with ground truth
2. Implement `dependency_grader.py`
3. Wire into environment
4. Write basic inference.py that can solve Task 1
5. Verify: grader produces scores 0.0-1.0

**Phase 3: Task 2 — IaC Review**
1. Create 5 IaC scenarios with ground truth (Terraform files)
2. Implement `iac_grader.py` with resource-level matching
3. Wire into environment
4. Test with inference.py

**Phase 4: Task 3 — Migration Review**
1. Create 3 migration scenarios with ground truth
2. Implement `migration_grader.py` with operation-level matching
3. Include production context in scenarios
4. Wire into environment
5. Test with inference.py

**Phase 5: Polish**
1. Refine reward function (per-step + episode-end)
2. Run `openenv validate` and fix any issues
3. Write comprehensive README with baseline scores
4. Deploy to Hugging Face Spaces
5. Run pre-submission validation script
6. Test end-to-end: reset → agent runs → scores produced

### Time Estimates
- Phase 1: 2-3 hours
- Phase 2: 3-4 hours
- Phase 3: 4-5 hours
- Phase 4: 4-5 hours
- Phase 5: 2-3 hours
- **Total: ~15-20 hours**

---

## 10. Key Technical Decisions

### Why not run Checkov/scanners at runtime?
- Runtime constraint: vcpu=2, 8GB RAM
- Checkov adds ~500MB to Docker image
- Instead: pre-compute ground truth using scanners, store as JSON
- The environment serves pre-validated scenarios, not live scanning
- This is standard practice for benchmarks (SWE-bench does the same)

### Why structured actions instead of free-text?
- Deterministic grading requires structured findings
- Prevents prompt injection via finding descriptions
- Makes the environment spec-compliant with typed Pydantic models
- Agent still uses free-text reasoning internally (via LLM), but submits structured actions

### How to prevent grader gaming?
- Agent doesn't see ground truth during episode
- Findings must specify file + line + rule_id + severity — can't just spam
- False positive penalty discourages "report everything" strategy
- Step budget limits brute-force approaches
- Grading uses semantic matching, not exact string matching

### Scenario randomization
- Each task has multiple scenarios
- On `reset()`, a random scenario is selected (or specified by ID for reproducibility)
- inference.py runs all scenarios sequentially for baseline scores

### How the inference.py agent works
```
For each task:
  1. Call reset(task_id) → get observation
  2. Send observation to LLM with system prompt explaining the review task
  3. LLM responds with an action (parsed from structured output)
  4. Call step(action) → get new observation
  5. Repeat until done=True or LLM calls mark_complete
  6. Record final score
```

The system prompt for the LLM should explain:
- What the agent is reviewing (dependency file / Terraform / migration)
- What kinds of issues to look for
- How to format findings (rule_id conventions, severity levels)
- When to request additional context vs. submit findings

---

## Appendix A: Rule ID Conventions

### Task 1 — Dependency Rules
| Rule ID | Description |
|---------|-------------|
| DEP-001 | Package does not exist in registry (hallucinated) |
| DEP-002 | Package name is typosquat of known package |
| DEP-003 | Package has known critical CVE |
| DEP-004 | Package has known high-severity CVE |
| DEP-005 | Package has suspicious install script |
| DEP-006 | Package maintainer account compromised |
| DEP-007 | Package is deprecated with known replacement |

### Task 2 — IaC Rules
| Rule ID | Description |
|---------|-------------|
| IAC-001 | Public access to storage resource |
| IAC-002 | Missing encryption at rest |
| IAC-003 | Missing encryption in transit |
| IAC-004 | Overly permissive security group (0.0.0.0/0) |
| IAC-005 | IAM policy with wildcard actions |
| IAC-006 | Missing logging/monitoring |
| IAC-007 | Resource in public subnet without justification |
| IAC-008 | Missing network access control |
| IAC-009 | Privileged container/execution |
| IAC-010 | Cross-account access without restrictions |
| IAC-011 | Missing backup/recovery configuration |
| IAC-012 | Hardcoded credentials or secrets |

### Task 3 — Migration Rules
| Rule ID | Description |
|---------|-------------|
| MIG-001 | Adding NOT NULL column without default on large table |
| MIG-002 | Non-concurrent index creation on large table |
| MIG-003 | Dropping column still in use by application |
| MIG-004 | Renaming column in zero-downtime deployment |
| MIG-005 | Type change with implicit cast on large table |
| MIG-006 | Migration ordering dependency not satisfied |
| MIG-007 | Missing expand-migrate-contract pattern |
| MIG-008 | Foreign key on high-write table without index |
| MIG-009 | Dropping table with active foreign key references |
| MIG-010 | Lock-heavy operation without timeout |

---

## Appendix B: Prompt for Claude Code

When starting implementation with Claude Code, use this prompt:

```
I'm building an OpenEnv environment called SecureReview for a hackathon.
Read the full specification in SECUREREVIEW_SPEC.md first, then start
with Phase 1 (skeleton). Build each phase completely before moving to
the next.

Key constraints:
- Must pass `openenv validate`
- Must work with `docker build && docker run`
- Must run on vcpu=2, 8GB RAM
- inference.py must use OpenAI client with API_BASE_URL, MODEL_NAME, HF_TOKEN env vars
- All graders must produce scores between 0.0 and 1.0
- The environment is a FastAPI server exposing /reset, /step, /state endpoints

Start with Phase 1: create the project structure, Pydantic models, and FastAPI skeleton.
```

---

## Appendix C: README Template

```markdown
# SecureReview 🔒

**The first OpenEnv environment for AI-powered security code review**

SecureReview evaluates an AI agent's ability to perform security-conscious
code review across three critical domains where human reviewers are most
stretched: dependency supply chains, cloud infrastructure configurations,
and database migrations.

## Why SecureReview?

As AI generates an ever-larger share of production code, the bottleneck
shifts from *writing* code to *reviewing* it. SecureReview fills a gap
in the agent evaluation landscape: no existing environment tests an agent's
ability to critically review artifacts for correctness and safety.

## Tasks

| Task | Domain | Difficulty | Max Steps | Description |
|------|--------|------------|-----------|-------------|
| `dependency_review` | Supply Chain | Easy | 15 | Identify hallucinated, typosquatted, and vulnerable packages |
| `iac_review` | Infrastructure | Medium | 25 | Detect security misconfigurations in Terraform/K8s configs |
| `migration_review` | Database | Hard | 35 | Analyze migration scripts for safety risks and production impact |

## Action Space

| Action | Description |
|--------|-------------|
| `report_finding` | Submit a security finding with file, line, rule_id, severity |
| `request_context` | Request additional files for review |
| `request_file_list` | List available files in the scenario |
| `mark_complete` | End review and trigger grading |

## Observation Space

On reset, the agent receives the task description, files to review,
a review checklist, and metadata. On each step, the agent receives
updated state including findings submitted so far.

## Reward Function

Score = F1(precision, recall) × 0.85 + severity_bonus + efficiency_bonus − FP_penalty

- **Precision/Recall**: based on matching agent findings to ground truth
- **Severity bonus**: +0.10 for correctly categorizing severity levels
- **Efficiency bonus**: +0.05 for using fewer steps
- **FP penalty**: −0.03 per false positive (capped at 0.20)

## Setup

### Docker
```bash
docker build -t securereview .
docker run -p 7860:7860 securereview
```

### Running the baseline
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="your-model-name"
export HF_TOKEN="your-hf-token"
python inference.py
```

## Baseline Scores

| Task | Model | Score |
|------|-------|-------|
| dependency_review | [MODEL] | [SCORE] |
| iac_review | [MODEL] | [SCORE] |
| migration_review | [MODEL] | [SCORE] |
```