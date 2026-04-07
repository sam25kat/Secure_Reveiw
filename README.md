# SecureReview

**The first OpenEnv environment for AI-powered security code review**

SecureReview evaluates an AI agent's ability to perform security-conscious code review across three critical domains where human reviewers are most stretched: dependency supply chains, cloud infrastructure configurations, and database migrations.

## Why SecureReview?

As AI generates an ever-larger share of production code, the bottleneck shifts from *writing* code to *reviewing* it. SecureReview fills a gap in the agent evaluation landscape: no existing environment tests an agent's ability to critically review artifacts for correctness and safety.

Each domain represents a real category of production incidents that costs organizations billions annually:
- **Supply chain attacks** (SolarWinds, event-stream, ua-parser-js) via poisoned dependencies
- **Cloud misconfigurations** (Capital One breach, exposed S3 buckets) via insecure IaC
- **Database incidents** (GitHub, Slack outages) via unsafe migrations on large tables

## Tasks

| Task | Domain | Difficulty | Max Steps | Scenarios | Description |
|------|--------|------------|-----------|-----------|-------------|
| `dependency_review` | Supply Chain | Easy | 15 | 6 | Identify hallucinated, typosquatted, and vulnerable packages |
| `iac_review` | Infrastructure | Medium | 25 | 6 | Detect security misconfigurations in Terraform/K8s configs |
| `migration_review` | Database | Hard | 35 | 4 | Analyze migration scripts for safety risks and production impact |

### Task Details

**Dependency & Supply Chain Review (Easy)**
The agent reviews `requirements.txt` or `package.json` files containing 15-30 dependencies. Hidden among legitimate packages are 3-6 planted issues: typosquatted package names, hallucinated packages that don't exist on PyPI/npm, and packages pinned to versions with known critical CVEs.

**Infrastructure-as-Code Security Review (Medium)**
The agent reviews 2-5 Terraform or Kubernetes YAML files defining cloud infrastructure. Each scenario contains 4-6 security misconfigurations based on CIS Benchmarks, ranging from single-resource issues (public S3 buckets) to cross-resource problems (overly permissive IAM roles attached to public-facing services).

**Database Migration Safety Review (Hard)**
The agent reviews SQL migration scripts alongside production context (table sizes, traffic patterns, deployment strategy) and application code showing column usage. The agent must reason about why specific DDL operations are unsafe given the production environment — for example, adding a NOT NULL column without a default on a 12M-row table during a zero-downtime rolling deployment.

## Action Space

| Action | Parameters | Description |
|--------|-----------|-------------|
| `report_finding` | file, line, rule_id, severity, description | Submit a security finding |
| `request_context` | filename | Request additional files for review |
| `request_file_list` | none | List all available files in the scenario |
| `mark_complete` | none | End review and trigger grading |

### Rule IDs

**Dependency (DEP-001 to DEP-007):** Hallucinated package, typosquat, critical CVE, high CVE, suspicious install script, compromised maintainer, deprecated package.

**IaC (IAC-001 to IAC-012):** Public access, missing encryption (at rest / in transit), permissive security groups, IAM wildcards, missing logging, public subnet, missing network ACLs, privileged containers, cross-account access, missing backups, hardcoded credentials.

**Migration (MIG-001 to MIG-010):** NOT NULL without default, non-concurrent index, dropping used column, renaming during zero-downtime, type change rewrite, ordering dependency, missing expand-migrate-contract, FK without index, dropping referenced table, missing lock timeout.

## Observation Space

On `reset()`, the agent receives:
- **Task description** and difficulty level
- **Files to review** (source code, configs, schemas)
- **Review checklist** specific to the task domain
- **Available files** that can be requested via `request_context`
- **Step budget** (max steps remaining)

On each `step()`, the agent receives updated state including all findings submitted so far and feedback on the last action.

## Reward Function

```
Score = F1(precision, recall) * 0.85 + severity_bonus + efficiency_bonus - FP_penalty
```

| Component | Range | Description |
|-----------|-------|-------------|
| **F1 Score** | 0.0-0.85 | Precision/recall of findings vs ground truth |
| **Severity Bonus** | 0.0-0.10 | Correctly categorizing severity levels |
| **Efficiency Bonus** | 0.0-0.05 | Using fewer steps than the budget |
| **FP Penalty** | 0.0-0.20 | -0.03 per false positive (capped) |

Finding matching is task-specific:
- **Dependency:** Match by package name (exact, case-insensitive)
- **IaC:** Match by (resource_identifier, rule_category) with fuzzy fallback
- **Migration:** Match by (operation_type, target_object)

## Setup

### Docker

```bash
docker build -t securereview .
docker run -p 7860:7860 securereview
```

### Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860
```

### Running the Baseline Agent

```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
export HF_TOKEN="your-hf-token"
export ENV_URL="http://localhost:7860"  # optional, defaults to localhost
python inference.py
```

### API Endpoints

```
GET  /health              Health check
GET  /tasks               List available tasks
POST /reset               Start new episode: {"task_id": "dependency_review"}
POST /step                Execute action: {"action": {"action_type": "report_finding", ...}}
GET  /state               Get current episode state
```

## Baseline Scores

| Task | Model | Score |
|------|-------|-------|
| `dependency_review` | Llama-3.1-8B-Instruct | ~0.45-0.65 |
| `iac_review` | Llama-3.1-8B-Instruct | ~0.30-0.50 |
| `migration_review` | Llama-3.1-8B-Instruct | ~0.15-0.35 |

*Scores vary by scenario. The hard task (migration_review) is designed to challenge frontier models.*

## Project Structure

```
securereview/
├── Dockerfile
├── openenv.yaml
├── inference.py                 # Baseline agent
├── README.md
├── requirements.txt
├── app/
│   ├── main.py                  # FastAPI endpoints
│   ├── environment.py           # Core environment logic
│   ├── models.py                # Pydantic models
│   ├── graders/
│   │   ├── base.py              # Shared scoring formula
│   │   ├── dependency_grader.py # Package name matching
│   │   ├── iac_grader.py        # Resource+category matching
│   │   └── migration_grader.py  # Operation+target matching
│   └── tasks/
│       ├── task_registry.py     # Scenario loading
│       └── scenarios/           # 16 hand-crafted scenarios
│           ├── dependency/      # 6 scenarios
│           ├── iac/             # 6 scenarios
│           └── migration/       # 4 scenarios
└── tests/
```

## Team

**Team CookHouse** — Sai Jadhav & Sameer S Katte

Built for the Meta PyTorch OpenEnv Hackathon.
