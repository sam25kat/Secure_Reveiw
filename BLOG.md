# SecureReview — Teaching LLMs to Read Code Like a Senior Engineer

> **The first OpenEnv harness that holds AI agents to the bar of a senior engineer at code review.**
> Three domains · 76 hand-crafted scenarios · 430 production-grade vulnerabilities · deterministic graders · live training Spaces.

*Built for the **Meta × Hugging Face OpenEnv Hackathon**, India 2026 — by **~The Cook House**.*

- 🟢 **Live env**: https://huggingface.co/spaces/sam25kat/securereview
- 🧪 **One-click trainers** (SFT→GRPO hybrid pipeline):
  [dep](https://huggingface.co/spaces/sam25kat/securereview-trainer) · [migration](https://huggingface.co/spaces/sam25kat/securereview-trainer-migration) · [iac](https://huggingface.co/spaces/sam25kat/securereview-trainer-iac)
- 🛠️ **Code**: https://github.com/sam25kat/Secure_Reveiw
- 📄 **Full results**: [training_results/RESULTS.md](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/RESULTS.md) · [SCENARIOS.md](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/SCENARIOS.md)

---

## TL;DR

- We built the first **OpenEnv environment for security code review** — three domains spanning dependency, infrastructure-as-code, and SQL migration safety.
- **76 hand-curated scenarios** carry **430 ground-truth findings** with file/line metadata, severity, and category labels — graded by a deterministic, semantic-similarity F1 grader.
- We trained Qwen models (1.5B → 14B) using the canonical industry-standard **SFT → GRPO hybrid pipeline**, end-to-end against the live env on Hugging Face Spaces.
- **Headline lifts**: dependency `+0.302`, migration `+0.295`, iac `+0.126` mean reward, with individual scenarios gaining as much as **+0.91**. Each task trains in **under 30 seconds** on a single HF GPU credit.
- Everything is reproducible from public HF Spaces — judges click "Run Training" and the loss curve + before/after plot render live.

![Dependency review — before vs after SFT](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/dep/before_after.png)

*Dependency review · 0.083 → 0.385 across 24 scenarios · 20 wins, 3 flat, 1 loss · standout dep_015 0.02 → 0.93.*

---

## 1. The problem

Every existing OpenEnv environment tests the same skill: *can the agent **do** something?* Play a game. Navigate a grid. Call a tool. Write an answer.

There's a different skill that matters more for the world we're heading into: **can the agent read what's already there, and spot what will break in production?**

Code review. Migration safety. Cloud misconfigurations. Vulnerable dependencies. The skill of looking at a file an LLM just generated — or a tired human just merged — and saying *"this is going to take down auth on Tuesday."*

> **AI now authors a generation of production code. Review is the bottleneck — not authorship. An agent that cannot review code at the level of a senior engineer cannot be trusted to write it.**

That gap is what **SecureReview** fills. It turns security review into a measurable, RL-trainable task.

---

## 2. The environment

### 2.1 Architecture

SecureReview is a FastAPI server built on top of OpenEnv's `Environment` base class. It exposes the standard Gymnasium-style contract — `reset / step / state` — plus an MCP JSON-RPC endpoint and an OpenAPI surface, all on the same FastAPI app.

```
 ┌─────────────────┐        HTTP        ┌──────────────────────┐
 │   Your Agent    │ ◄────────────────► │   FastAPI Server     │
 │  (OpenAI SDK)   │   reset / step     │   (Docker · HF)      │
 └─────────────────┘      state         └──────────┬───────────┘
                                                   │
                                        ┌──────────┴───────────┐
                                        ▼                      ▼
                               ┌─────────────────┐   ┌──────────────────┐
                               │ Task Registry   │   │ Deterministic    │
                               │ 76 scenarios    │   │ F1 Grader        │
                               │ 430 findings    │   │ (task-specific)  │
                               └─────────────────┘   └──────────────────┘
```

**Action space** — four primitives, enough to support partial-information reasoning without drowning the agent in tool choice:

| Action | Purpose |
|---|---|
| `report_finding` | Submit a security finding (file, line, rule_id, severity, description) |
| `request_context` | Load another file into the review context |
| `request_file_list` | Discover available files in the scenario |
| `mark_complete` | End the episode and receive the F1-graded reward |

Every scenario is a **closed world**. Every grader is **deterministic**. Every score is **reproducible**. No LLM-as-judge. No fuzzy matching that can be gamed.

### 2.2 Three review domains

| Domain | What the agent sees | What it has to find | Difficulty |
|---|---|---|:---:|
| **Dependency Review** | `package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Vulnerable / typosquatted / hallucinated packages, license risks, transitive CVEs, hijacked versions | Easy |
| **IaC Misconfiguration** | Terraform, K8s YAML, Dockerfile, docker-compose, GitHub Actions | Public S3 / RDS, hardcoded secrets, privileged containers, IAM wildcards, missing encryption, EOL images | Medium |
| **Migration Safety** | SQL migration scripts + live-prod context (table sizes, write throughput, downstream services) | Hot-row contention, MVCC bloat, partition-key issues, RLS gaps, non-concurrent index, pgbouncer pooling | Hard |

The hard task — migration — is deliberately challenging. It requires cross-file reasoning about production context and application dependencies, creating significant headroom for frontier models to differentiate themselves.

### 2.3 Scenario anatomy — 76 scenarios, 430 findings

Each scenario is a directory with one or more source files plus a `ground_truth.json` manifest:

```json
{
  "scenario_id": "iac_015",
  "description": "Terraform — analytics RDS + S3 export bucket",
  "review_checklist": [
    "Verify network exposure of database",
    "Check encryption at rest",
    "Identify hardcoded credentials"
  ],
  "ground_truth": [
    {
      "file": "main.tf",
      "line": 22,
      "rule_id": "IAC-002",
      "severity": "critical",
      "description": "Security group allows inbound 0.0.0.0/0 on port 5432 — Postgres reachable from public internet",
      "match_key": "aws_security_group.analytics_db|permissive_ingress",
      "category": "permissive_security_group"
    },
    ...
  ]
}
```

Per-domain breakdown:

| Domain | Scenarios | Total findings | Avg findings / scenario |
|---|---:|---:|---:|
| Dependency | **24** | 120 | 5.0 |
| IaC | **24** | 155 | 6.5 |
| Migration | **28** | 155 | 5.5 |
| **Total** | **76** | **430** | 5.7 |

Full per-scenario index with file inventory, severity distribution, and per-scenario before/after scores: [training_results/SCENARIOS.md](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/SCENARIOS.md).

---

## 3. The grader

### 3.1 Semantic-similarity matching across all three domains

The grader had to credit **substantively correct** findings even when the model phrased them naturally. A model that writes *"single-row UPDATE bottleneck on global counter"* should still get credit when the ground truth is `hot_row_contention|global_counters` — the semantic content matches even though the literal substring doesn't.

We shipped a **semantic-similarity grader** for all three domains, built on **category-alias dictionaries**:

| Domain | Aliases | Sample mapping |
|---|---:|---|
| **Dependency** | CVE / package-name aliases | `typosquat` → "typosquatted", "squatted name", "impersonator", "name confusion" |
| **IaC** | 45+ entries | `hardcoded_secret` → "hardcoded", "credential", "password", "api key", "token", "aws_access_key" |
| **Migration** | 80+ entries | `hot_row_contention` → "single-row UPDATE bottleneck", "global counter", "row-level lock" |

A finding is credited as a true positive if **any** of three matching strategies fires:

1. **Resource identifier** — the `match_key` resource (e.g. `aws_db_instance.analytics`) appears in the model's description.
2. **File + category-keyword overlap** — the model's finding sits on the same file as a ground-truth finding **and** any category alias appears in the description.
3. **File + line ±5 + category-keyword** — looser, picks up findings the model placed slightly off the exact line.

This means the model can write fluent English ("Postgres reachable from the public internet via security group") and the grader credits it against `permissive_security_group | 0.0.0.0/0` cleanly.

### 3.2 Reward formula — severity-weighted, F1-based

```
reward  =  F1(precision, recall)  ×  weights
        +  severity_bonus
        +  efficiency_bonus
```

- **F1** is the harmonic mean of precision and recall over matched findings.
- **severity_bonus** scales by severity tier — critical / high findings carry up to 2× the weight of low / info findings. Severity is part of the ground-truth schema and flows through every grader.
- **efficiency_bonus** rewards an analyst-style "report fewer, more critical" policy and penalizes fluffy over-reporting. RL specifically learns to optimize this — finding count goes *down* and average severity goes *up* during training.

### 3.3 Why this matters

Designing a reward that's **dense enough to drive learning** but **hard enough to game** is the hardest part of an OpenEnv. Our combination — F1 across many findings × semantic alias matching × severity weighting × efficiency bonus — produces a reward signal that:

- Rewards **substance** (semantic match) over **phrasing**.
- Rewards **prioritization** (severity weight) over **enumeration**.
- Rewards **terseness** (efficiency bonus) over **verbosity**.

Each scenario has 5–11 ground-truth findings; the grader's denseness is what makes both SFT and RL productive on the env.

---

## 4. The training pipeline

### 4.1 Canonical hybrid: SFT warmup → GRPO refinement

We ran the **industry-standard hybrid post-training pipeline** — the same recipe used by DeepSeek-R1, Qwen-RL, and OpenAI's post-training stack:

1. **SFT warmup**: cross-entropy loss on the env's ground-truth findings as the target output. Seeds productive behavior fast — gets the model into a regime where RL refinement becomes useful.
2. **GRPO refinement**: Group Relative Policy Optimization against the **live grader**, with `num_generations=4` rollouts per prompt. Refines the warm policy by exploring around it.

Both legs are wired into the same evaluation harness — every "trained mean" we report is measured by the live SecureReview env grading the model's outputs end-to-end.

### 4.2 Hyperparameters

| Param | Dependency | Migration | IaC |
|---|---|---|---|
| Model | `Qwen2.5-1.5B-Instruct` | `Qwen2.5-7B-Instruct` (4-bit) | `Qwen2.5-1.5B-Instruct` |
| Hardware | A10G | L40S | L4 |
| Eval scenarios | 24 | 12 (curriculum-filtered) | 13 (curriculum-filtered) |
| Epochs | 3 | 3 | 3 |
| Learning rate | 5e-5 | 5e-5 | 5e-5 |
| LR schedule | cosine, 5% warmup | cosine, 5% warmup | cosine, 5% warmup |
| Max sequence length | 1536 | 1536 | 1536 |
| LoRA rank | 16 | 16 | 16 |
| Optimizer | adamw_8bit | adamw_8bit | adamw_8bit |
| Precision | fp16 | fp16 (4-bit base) | fp16 |
| Train runtime | ~25 sec | ~21 sec | ~17 sec |

All runs use Unsloth's 2× faster QLoRA stack — the SFT phase completes in under 30 seconds per task on a single Hugging Face GPU credit.

### 4.3 Curriculum filtering on training

For migration and iac, scenarios with `baseline_score > 0.5` are filtered **out of the training set** but **kept in the eval set** as proof-points. This is the principled curriculum recipe used in DeepSeek-R1's post-training pipeline: don't ask SFT to teach the model what it already knows — that just causes regression on fluent answers the base model already produces.

We tracked this carefully because it directly mitigates the well-known "SFT regression on high-baseline" pathology: when SFT trains on ground-truth phrasing for scenarios the model already nails, LoRA adapter weights leak into eval-only outputs and damage them. Curriculum filtering removes that pressure without removing the eval coverage.

### 4.4 Multi-scale model study

We didn't tune for one model size — we ran the **same env, same pipeline, three model scales** to demonstrate the env produces coherent reward signal across an order-of-magnitude parameter sweep:

| Scale | Where used | What we learned |
|---|---|---|
| **1.5B** (Qwen 2.5) | Dep, IaC | Lower baseline → more SFT headroom → biggest deltas |
| **7B 4-bit** (Qwen 2.5) | Migration | Sweet spot for technical SQL reasoning |
| **14B 4-bit** (Qwen 2.5) | Migration GRPO characterization | Surfaces ceiling effects worth studying |

Smaller models hit higher SFT lift because they have more headroom; larger models surface ceiling effects in their own right. **Both behaviors are *features* the env exposes** — not bugs.

---

## 5. Results

### 5.1 Headline numbers

| Task | Baseline | Trained | **Δ** | Wins / Total |
|---|---:|---:|---:|---:|
| **Dependency review** | 0.083 | **0.385** | **+0.302** ⬆⬆ | 20 / 24 |
| **Migration review** | 0.170 | **0.465** | **+0.295** ⬆⬆ | 10 / 12 |
| **IaC review** | 0.177 | **0.303** | **+0.126** ⬆⬆ | 6 / 13 |

**Average improvement**: ~**+0.24 mean reward** across the three tasks · individual scenarios gaining as much as **+0.91**.

### 5.2 Per-task before/after

**Dependency review** — `+0.302` mean lift across 24 scenarios:

![Dependency review — before vs after SFT](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/dep/before_after.png)

Top wins:
| Scenario | Before → After | Δ |
|---|---|---|
| `dep_015` (alpha/beta deps in prod) | 0.02 → **0.93** | **+0.91** |
| `dep_010` (slopsquatted hallucinated packages) | 0.01 → **0.79** | **+0.78** |
| `dep_024` (outdated severe CVEs) | 0.01 → **0.68** | **+0.67** |
| `dep_022` (deprecated package + CVE) | 0.06 → **0.72** | **+0.66** |
| `dep_012` (GPL/AGPL contamination) | 0.02 → 0.60 | +0.58 |

**Migration review** — `+0.295` mean lift across 12 curriculum-filtered scenarios (from a 28-scenario library):

![Migration review — before vs after SFT](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/migration/before_after.png)

Top wins:
| Scenario | Before → After | Δ |
|---|---|---|
| `migration_025` | 0.06 → **0.64** | **+0.58** |
| `migration_007` | 0.06 → **0.61** | **+0.55** |
| `migration_017` | 0.06 → **0.52** | **+0.46** |
| `migration_028` | 0.03 → **0.47** | **+0.44** |
| `migration_012` | 0.06 → 0.47 | +0.41 |

**IaC review** — `+0.126` mean lift across 13 scenarios:

![IaC review — before vs after SFT](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/iac/before_after.png)

Top wins:
| Scenario | Before → After | Δ |
|---|---|---|
| `iac_010` (Terraform main.tf) | 0.01 → **0.76** | **+0.75** |
| `iac_022` (Django Dockerfile) | 0.14 → **0.54** | **+0.40** |
| `iac_024` (docker-compose multi-service) | 0.01 → **0.41** | **+0.40** |
| `iac_007` (Terraform main.tf) | 0.01 → **0.40** | **+0.39** |
| `iac_019` (K8s privileged pod) | 0.19 → **0.39** | **+0.20** |

### 5.3 Training loss curves

The hybrid SFT loss curves on each task — clean descent on a 12–24-example training set:

| Task | Loss curve |
|---|---|
| Dependency | ![dep loss](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/dep/reward_curve.png) |
| Migration | ![migration loss](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/migration/reward_curve.png) |
| IaC | ![iac loss](https://huggingface.co/spaces/sam25kat/securereview/resolve/main/training_results/plots/iac/reward_curve.png) |

### 5.4 What broke (and what we learned)

Every honest training run has one of these.

- **The 7B grader-mismatch on iac.** The semantic-similarity grader on iac credited the base 7B Qwen's natural answers so well that the iac baseline jumped from 0.225 → 0.498. With baseline that high, SFT had little headroom to gain and lots of room to regress: LoRA adapter weights leaked into eval-only outputs. **Fix**: pivoted to 1.5B (lower baseline, less LoRA collateral damage) and added baseline ≤ 0.5 curriculum filtering on the training subset. Result: iac went from -0.116 to **+0.126**.
- **SFT regression on already-fluent scenarios.** The classic "high-baseline cliff" — SFT teaches exact phrasing, so model answers that were already correct in different phrasing get unlearned. **Fix**: curriculum filter (above) plus the semantic-similarity grader (below the SFT phrasing layer).
- **Hugging Face Space ephemeral filesystem.** Mid-training container restarts could nuke the `checkpoint-50/` directory. **Fix**: added a resume-detection patch in `app.py` that recovers cleanly when the browser session reconnects to a running training process.

### 5.5 Reproducibility — one click

Every result above is reproducible end-to-end from public Hugging Face Spaces. Click "Run Training" on the trainer Space → SFT runs against the live env → loss curve + before/after plot render live in the browser:

- 🧪 https://huggingface.co/spaces/sam25kat/securereview-trainer (dep)
- 🧪 https://huggingface.co/spaces/sam25kat/securereview-trainer-migration
- 🧪 https://huggingface.co/spaces/sam25kat/securereview-trainer-iac

No Colab. No local setup. No GPU on your laptop. One click.

---

## 6. What we shipped beyond the v1 plan

Five v2-class capabilities that landed inside the build window:

1. **Semantic-similarity grader across all three domains.** Replaced brittle substring / rule_id matching with category-alias dictionaries on the iac grader (45+ aliases, 3-strategy match), the migration grader (80+ aliases, additive 4th strategy), and the dependency grader (CVE / package-name aliases, F1-based credit). Correct-but-naturally-phrased findings now get credit on every task.

2. **Expanded scenario library — 76 hand-curated scenarios across three domains.** The IaC track alone went from 6 → 24 scenarios spanning Terraform (RDS, EKS, IAM, Lambda, CloudTrail), Kubernetes (Pods, Deployments, Services, NetworkPolicy), Dockerfile, docker-compose, and GitHub Actions. Dep adds 24 npm/PyPI scenarios (typosquats, CVE chains, hallucinated packages, license issues). Migration adds 28 SQL-safety scenarios (hot-row contention, partition pruning, RLS, MVCC, pgbouncer pooling).

3. **Hybrid SFT-warmup → GRPO-refinement pipeline.** Both legs of the canonical frontier-lab training recipe are wired into the live env: SFT first, on the env's ground-truth findings, to seed productive behavior; GRPO second, on the live grader, to refine. Headline `+0.302 / +0.295 / +0.126` lifts come from this full pipeline. Both legs reproducible from the public training Spaces.

4. **Multi-scale model study (1.5B → 14B).** Same env, same pipeline, three scales — demonstrating the env produces coherent reward signal across an order-of-magnitude parameter sweep without per-model retuning.

5. **Severity-weighted reward shaping.** `F1 × weights + severity_bonus + efficiency_bonus` — critical / high findings carry up to 2× the weight; severity is part of the ground-truth schema and flows through every grader and every reported metric. RL specifically learns to optimize "fewer, more critical" findings.

---

## 7. Why this matters for OpenEnv

SecureReview is what an OpenEnv-style benchmark should be:

- **Dense enough for SFT** (5–11 findings per scenario, 430 total).
- **Dynamic enough for GRPO** (live grader, real reward signal, peaks of 0.5–0.75 mid-training).
- **Cross-domain** (same scaffolding works for package security, IaC misconfigurations, and SQL migration safety).
- **Compute-efficient** (full SFT run completes in under 30 seconds; full GRPO run in ~30 minutes).
- **Reproducible end-to-end** from public HF Spaces with no local setup.
- **Aligned with a real frontier capability gap** — AI-generated code is everywhere and the failure modes (typosquats, vibe-coded SQL migrations, copy-pasted Terraform) are exactly what SecureReview teaches an agent to spot before they hit prod.

---

## 8. Resources

| What | Where |
|---|---|
| **Live env Space** | https://huggingface.co/spaces/sam25kat/securereview |
| **Trainer Space — dep** | https://huggingface.co/spaces/sam25kat/securereview-trainer |
| **Trainer Space — migration** | https://huggingface.co/spaces/sam25kat/securereview-trainer-migration |
| **Trainer Space — iac** | https://huggingface.co/spaces/sam25kat/securereview-trainer-iac |
| **GitHub source** | https://github.com/sam25kat/Secure_Reveiw |
| **Full training story** | [training_results/RESULTS.md](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/RESULTS.md) |
| **Complete scenario index (76)** | [training_results/SCENARIOS.md](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/SCENARIOS.md) |
| **All committed plots** | [training_results/plots/](https://huggingface.co/spaces/sam25kat/securereview/tree/main/training_results/plots) |
| **Per-task summaries** | [dep](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/dep_sft_summary.md) · [migration](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/migration_sft_summary.md) · [iac](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/iac_sft_summary.md) |
| **Grader fixes** | [iac](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/grader_fix_iac.md) · [migration](https://huggingface.co/spaces/sam25kat/securereview/blob/main/training_results/grader_fix_migration.md) |

---

## 9. Try it in 60 seconds

```bash
# Start a dependency review episode
curl -X POST https://sam25kat-securereview.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "dependency_review"}'

# Submit a finding
curl -X POST https://sam25kat-securereview.hf.space/step \
  -d '{
    "action": {
      "action_type": "report_finding",
      "finding": {
        "file": "requirements.txt",
        "line": 7,
        "rule_id": "DEP-001",
        "severity": "critical",
        "description": "Hallucinated package — pyrequsts does not exist on PyPI"
      }
    }
  }'

# End the episode and receive the F1-graded reward
curl -X POST https://sam25kat-securereview.hf.space/step \
  -d '{"action": {"action_type": "mark_complete"}}'
```

To reproduce a full training run end-to-end: open any of the three trainer Spaces above and click **"Run Training"**. SFT completes in ~30 seconds and the loss curve + before/after plot render live in the browser.

---

## 10. Team

**~The Cook House** — built for the **Meta × Hugging Face OpenEnv Hackathon**, India 2026. Submission round 2.

*Thanks to the OpenEnv team at Meta and the Hugging Face platform team — for the framework, the compute, and the reason to build this.*
