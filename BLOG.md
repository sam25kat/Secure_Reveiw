# SecureReview: Teaching LLMs to Read Code Like a Senior Engineer

*Draft for HuggingFace blog · OpenEnv Hackathon submission, India 2026*

---

## The problem

Every existing OpenEnv environment tests the same skill — *can the agent **do** something?* Play a game, navigate a grid, call a tool, write an answer.

But there's a different skill that matters more for the world we're heading into: **can the agent read what's already there, and spot what will break in production?**

Code review. Migration safety. Infrastructure misconfigurations. Vulnerable dependencies. The skill of looking at a file an LLM (or a tired human) just generated and saying *"this is going to take down auth on Tuesday"*.

That's what **SecureReview** is — an OpenEnv environment that turns security review into a measurable RL task.

## The environment

Three review domains, all wired into the same FastAPI / Gym-style harness:

| Task | What the agent sees | What it has to find |
|---|---|---|
| `dependency_review` | `package.json`, `requirements.txt` | Vulnerable / typosquatted / hallucinated packages |
| `migration_review` | SQL migration scripts | Hot-row contention, RLS gaps, partition pruning, MVCC bloat |
| `iac_review` | Terraform, K8s YAML, Dockerfile, docker-compose, GitHub Actions | Public S3, hardcoded secrets, privileged containers, IAM wildcards |

**60+ hand-curated scenarios** across the three domains. Each scenario carries ground-truth findings with file/line metadata and severity, all consumed by a **semantic-similarity grader** that credits correct findings whether the model phrases them as `"hardcoded_secret"` or `"AWS_ACCESS_KEY_ID baked into image layer"`.

## The training

We ran the **canonical industry-standard hybrid pipeline**: SFT warmup on the env's ground-truth findings, then GRPO refinement against the live grader. Same recipe DeepSeek-R1, Qwen-RL, and OpenAI's post-training stack use.

| Task | Baseline | Trained | Δ | Wins |
|---|---|---|---|---|
| Dependency | `0.083` | `0.385` | **+0.302** | 20/24 |
| Migration | `0.170` | `0.465` | **+0.295** | 10/12 |
| IaC | `0.177` | `0.303` | **+0.126** | 6/13 |

Average **+0.24 mean reward lift**, individual scenarios gaining as much as **+0.91**. Each task trains in **under 30 seconds** on a single Hugging Face GPU credit.

## Why this is interesting

**The reward signal is dense by design.** Each scenario has 5–11 ground-truth findings; the grader uses category-alias dictionaries (45+ for IaC, 80+ for migration, plus CVE/package-name aliases for dep) so naturally-phrased findings get credit. F1-based scoring with severity weighting means an analyst-style "report fewer, more critical" policy is what RL learns to optimize.

**The same env scales from 1.5B to 14B.** Smaller models hit higher SFT lift because of more SFT headroom; larger models surface ceiling effects worth studying. Both are *features* the env exposes. Multi-scale runs are a one-click reproduce.

**It's a real benchmark, not a toy.** AI-generated code is everywhere now and the failure modes — typosquats, vibe-coded SQL migrations, copy-pasted Terraform — are exactly what SecureReview teaches an agent to spot before they hit prod.

## Try it

- **Env**: [huggingface.co/spaces/sam25kat/securereview](https://huggingface.co/spaces/sam25kat/securereview)
- **Trainers** (one-click reproduce):
  - [securereview-trainer](https://huggingface.co/spaces/sam25kat/securereview-trainer) (dep)
  - [securereview-trainer-migration](https://huggingface.co/spaces/sam25kat/securereview-trainer-migration)
  - [securereview-trainer-iac](https://huggingface.co/spaces/sam25kat/securereview-trainer-iac)
- **Code**: [github.com/sam25kat/Secure_Reveiw](https://github.com/sam25kat/Secure_Reveiw)

Click "Run Training" on any trainer Space — full SFT→GRPO hybrid pipeline, training Loss + Before/After plots, **all in one click**.

---

*Built for the **Meta × Hugging Face OpenEnv Hackathon**, India 2026 — by **~The Cook House**. Submission round 2.*
