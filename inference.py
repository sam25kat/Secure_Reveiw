"""
SecureReview Baseline Inference Script
======================================
Runs an LLM-based agent against the SecureReview environment to produce
baseline scores across all three security review tasks.

MANDATORY environment variables:
    API_BASE_URL   The API endpoint for the LLM (e.g. https://router.huggingface.co/v1)
    MODEL_NAME     The model identifier to use for inference
    HF_TOKEN       Your Hugging Face API key
"""

import os
import re
import sys
import json
import time
import functools
import requests as http_requests
from openai import OpenAI

# All print calls flush stdout immediately so the validator can parse
# [START]/[STEP]/[END] markers in real time.
print = functools.partial(print, flush=True)

# === Configuration ===
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

if not HF_TOKEN:
    print("WARNING: HF_TOKEN environment variable not set. LLM calls will fail.")
    print("Set it with: export HF_TOKEN='your-huggingface-token'")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "")

TASKS = ["dependency_review", "iac_review", "migration_review"]

# === System Prompts ===
SYSTEM_PROMPTS = {
    "dependency_review": """You are a security reviewer analyzing dependency files for supply chain risks.

Your job is to identify suspicious packages in the dependency file. Look for:
1. Typosquatted packages (misspelled names of popular packages, e.g., 'reqeusts' instead of 'requests')
2. Hallucinated/non-existent packages (names that don't exist in the package registry)
3. Packages with known critical CVEs at the pinned version
4. Deprecated packages with known security issues

For each issue found, respond with a JSON action. You MUST respond with exactly ONE JSON object per message.

To report a finding:
{
    "action_type": "report_finding",
    "finding": {
        "file": "requirements.txt",
        "line": <line_number>,
        "rule_id": "<DEP-001|DEP-002|DEP-003|DEP-004|DEP-007>",
        "severity": "<critical|high|medium|low>",
        "description": "Explain the issue and name the specific package"
    }
}

Rule IDs:
- DEP-001: Package does not exist in registry (hallucinated)
- DEP-002: Package name is typosquat of known package
- DEP-003: Package has known critical CVE
- DEP-004: Package has known high-severity CVE
- DEP-007: Package is deprecated

To end the review:
{"action_type": "mark_complete"}

Respond with ONLY the JSON object, no explanation.""",

    "iac_review": """You are a cloud security reviewer analyzing Infrastructure-as-Code configurations.

Check for CIS benchmark violations and security misconfigurations in Terraform/Kubernetes files.

FIRST: Use request_file_list to see all files, then request_context for any additional files.

For each issue found, respond with a JSON action:
{
    "action_type": "report_finding",
    "finding": {
        "file": "<filename>",
        "line": <line_number>,
        "rule_id": "<IAC-001 through IAC-012>",
        "severity": "<critical|high|medium|low>",
        "description": "Explain the misconfiguration, naming the specific resource"
    }
}

Rule IDs:
- IAC-001: Public access to storage resource
- IAC-002: Missing encryption at rest
- IAC-003: Missing encryption in transit
- IAC-004: Overly permissive security group (0.0.0.0/0)
- IAC-005: IAM policy with wildcard actions
- IAC-006: Missing logging/monitoring
- IAC-007: Resource in public subnet without justification
- IAC-008: Missing network access control
- IAC-009: Privileged container/execution
- IAC-010: Cross-account access without restrictions
- IAC-011: Missing backup/recovery configuration
- IAC-012: Hardcoded credentials or secrets

Other actions:
{"action_type": "request_file_list"}
{"action_type": "request_context", "filename": "<filename>"}
{"action_type": "mark_complete"}

Respond with ONLY the JSON object, no explanation.""",

    "migration_review": """You are a database migration safety reviewer analyzing SQL migration scripts.

CRITICAL: Before analyzing migrations, request context.json and app_context.py to understand:
- Table sizes (determines if operations will lock tables)
- Deployment strategy (rolling = zero-downtime required)
- Which services depend on which columns

Check for unsafe migration patterns:
- MIG-001: Adding NOT NULL column without DEFAULT on large table (causes table lock/rewrite)
- MIG-002: Non-concurrent index creation on large table (blocks writes)
- MIG-003: Dropping column still referenced by application code
- MIG-004: Renaming column during zero-downtime deployment
- MIG-005: Type change with implicit cast on large table
- MIG-006: Migration ordering dependency not satisfied
- MIG-007: Missing expand-migrate-contract pattern
- MIG-008: Foreign key on high-write table without supporting index
- MIG-009: Dropping table with active foreign key references
- MIG-010: Lock-heavy operation without timeout

For each issue found:
{
    "action_type": "report_finding",
    "finding": {
        "file": "<migration_file.sql>",
        "line": <line_number>,
        "rule_id": "<MIG-001 through MIG-010>",
        "severity": "<critical|high|medium|low>",
        "description": "Explain WHY the operation is unsafe given the production context (mention table size, deployment strategy). Suggest the safe alternative."
    }
}

Other actions:
{"action_type": "request_file_list"}
{"action_type": "request_context", "filename": "<filename>"}
{"action_type": "mark_complete"}

Respond with ONLY the JSON object, no explanation.""",
}


def build_prompt(task_id: str, observation: dict) -> str:
    """Build a user prompt from the current observation."""
    ctx = observation["context"]
    prompt_parts = []

    prompt_parts.append(f"Task: {ctx['task_description']}")
    prompt_parts.append(f"Difficulty: {ctx['difficulty']}")
    prompt_parts.append(f"Step: {ctx['current_step']}/{ctx['max_steps']}")
    prompt_parts.append("")

    # Review checklist
    prompt_parts.append("Review checklist:")
    for item in ctx["review_checklist"]:
        prompt_parts.append(f"  - {item}")
    prompt_parts.append("")

    # Files in context
    prompt_parts.append("=== Files to Review ===")
    for f in ctx["files"]:
        prompt_parts.append(f"\n--- {f['filename']} ({f['language']}) ---")
        prompt_parts.append(f["content"])
    prompt_parts.append("")

    # Available files not yet loaded
    if ctx["available_files"]:
        prompt_parts.append(
            f"Additional files available (use request_context): {', '.join(ctx['available_files'])}"
        )
        prompt_parts.append("")

    # Findings so far
    if observation["findings_so_far"]:
        prompt_parts.append(f"Findings submitted so far: {len(observation['findings_so_far'])}")
        for finding in observation["findings_so_far"]:
            prompt_parts.append(
                f"  - [{finding['severity']}] {finding['file']}:{finding.get('line', '?')} "
                f"{finding['rule_id']}: {finding['description'][:80]}..."
            )
        prompt_parts.append("")

    # Feedback
    if observation.get("feedback"):
        prompt_parts.append(f"Feedback: {observation['feedback']}")
        prompt_parts.append("")

    prompt_parts.append(
        "Analyze the files and respond with your next action as a JSON object."
    )

    return "\n".join(prompt_parts)


def parse_action(text: str) -> dict:
    """Parse LLM output into an action dict."""
    # Strip markdown code fences
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Try to find JSON object
    try:
        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            # Validate action_type
            if "action_type" in data:
                return data
    except json.JSONDecodeError:
        pass

    # Fallback: mark_complete to avoid infinite loops
    return {"action_type": "mark_complete"}


def run_episode(task_id: str, scenario_id: str = None) -> float:
    """Run a single episode and return the final score.

    Emits ``[START]``, ``[STEP]``, and ``[END]`` markers on stdout for
    the validator to parse.
    """
    # === [START] marker ===
    print(f"[START] task={task_id}")

    reset_body = {"task_id": task_id}
    if scenario_id:
        reset_body["scenario_id"] = scenario_id

    resp = http_requests.post(f"{ENV_URL}/reset", json=reset_body, timeout=30)
    resp.raise_for_status()
    reset_data = resp.json()
    observation = reset_data["observation"]
    info = reset_data["info"]
    scenario = info.get("scenario_id", "unknown")

    print(f"  Scenario: {scenario}")

    done = False
    final_score = 0.0
    step_count = 0

    # For migration tasks, start by requesting context files
    first_actions = []
    if task_id == "migration_review":
        available = observation["context"]["available_files"]
        for fname in available:
            if fname in ("context.json", "app_context.py", "service_dependencies.txt"):
                first_actions.append(
                    {"action_type": "request_context", "filename": fname}
                )
    elif task_id == "iac_review":
        # Request additional files
        available = observation["context"]["available_files"]
        for fname in available:
            first_actions.append(
                {"action_type": "request_context", "filename": fname}
            )

    # Execute pre-planned context requests
    for pre_action in first_actions:
        resp = http_requests.post(
            f"{ENV_URL}/step", json={"action": pre_action}, timeout=30
        )
        resp.raise_for_status()
        step_data = resp.json()
        observation = step_data["observation"]
        done = step_data["done"]
        step_count += 1
        reward_val = step_data.get("reward", 0.0) or 0.0
        final_score = reward_val
        print(f"[STEP] step={step_count} reward={reward_val}")
        if done:
            break

    # Main agent loop
    while not done:
        prompt = build_prompt(task_id, observation)

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS[task_id]},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            llm_output = response.choices[0].message.content or ""
        except Exception as e:
            print(f"    LLM error: {e}")
            llm_output = '{"action_type": "mark_complete"}'

        action = parse_action(llm_output)

        try:
            resp = http_requests.post(
                f"{ENV_URL}/step", json={"action": action}, timeout=30
            )
            resp.raise_for_status()
            step_data = resp.json()
        except Exception as e:
            print(f"    Step error: {e}")
            # Try mark_complete as fallback
            resp = http_requests.post(
                f"{ENV_URL}/step",
                json={"action": {"action_type": "mark_complete"}},
                timeout=30,
            )
            resp.raise_for_status()
            step_data = resp.json()

        observation = step_data["observation"]
        done = step_data["done"]
        reward_val = step_data.get("reward", 0.0) or 0.0
        final_score = reward_val
        step_count += 1
        print(f"[STEP] step={step_count} reward={reward_val}")

        # Small delay to avoid rate limiting
        time.sleep(0.3)

    # === [END] marker ===
    print(f"[END] task={task_id} score={final_score} steps={step_count}")
    return final_score


def main():
    print("=" * 60)
    print("SecureReview Baseline Inference")
    print("=" * 60)
    print(f"Model: {MODEL_NAME}")
    print(f"API: {API_BASE_URL}")
    print(f"Environment: {ENV_URL}")
    print()

    # Get available tasks and scenarios
    tasks_resp = http_requests.get(f"{ENV_URL}/tasks", timeout=10)
    tasks_resp.raise_for_status()
    tasks = tasks_resp.json()
    print(f"Available tasks: {[t['id'] for t in tasks]}")
    print()

    all_scores = {}

    for task_id in TASKS:
        print(f"\n{'='*40}")
        print(f"Task: {task_id}")
        print(f"{'='*40}")

        scores = []
        # Run one episode per task (random scenario)
        score = run_episode(task_id)
        scores.append(score)

        avg_score = sum(scores) / len(scores)
        all_scores[task_id] = avg_score
        print(f"\n  Average score for {task_id}: {avg_score:.3f}")

    # Summary
    print(f"\n{'='*60}")
    print("BASELINE RESULTS SUMMARY")
    print(f"{'='*60}")
    for task_id, score in all_scores.items():
        difficulty = {"dependency_review": "easy", "iac_review": "medium", "migration_review": "hard"}
        print(f"  {task_id} ({difficulty[task_id]}): {score:.3f}")

    overall = sum(all_scores.values()) / len(all_scores)
    print(f"\n  Overall average: {overall:.3f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
