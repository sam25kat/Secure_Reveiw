# SecureReview — The Complete Beginner's Guide

**Written for Sameer S Katte, Team CookHouse**
*Meta PyTorch OpenEnv Hackathon — Finale Prep*

---

> This guide assumes you are smart but brand new to HuggingFace, RL training, and OpenEnv. Every concept is explained from first principles. By the end, you should be able to answer any question a judge or mentor throws at you — confidently and clearly.

---

## Table of Contents

1. [HuggingFace — What Is It?](#section-1-huggingface--what-is-it)
2. [OpenEnv — What Is It?](#section-2-openenv--what-is-it)
3. [SecureReview — Deep Dive](#section-3-securereview--deep-dive)
4. [Adaptive Difficulty — The New Feature](#section-4-adaptive-difficulty--the-new-feature)
5. [Reinforcement Learning — What's Actually Happening](#section-5-reinforcement-learning--whats-actually-happening)
6. [The Full Training Flow (End-to-End)](#section-6-the-full-training-flow-end-to-end)
7. [Pitch Preparation](#section-7-pitch-preparation)
8. [Expected Questions + Prepared Answers](#section-8-expected-questions--prepared-answers)
9. [Glossary](#section-9-glossary)

---

## Section 1: HuggingFace — What Is It?

> **TL;DR:** HuggingFace is GitHub for AI. It hosts models, datasets, and running web apps. SecureReview lives there as a always-on environment that anyone — including hackathon judges — can hit from anywhere in the world.

---

### The Big Picture

Think of HuggingFace (often abbreviated HF) the same way you think about GitHub. GitHub is where developers store and share code. HuggingFace is where AI researchers and developers store and share three things:

- **Models** — the actual trained neural network weights (the "brain file" of an AI)
- **Datasets** — the curated collections of data used to train those models
- **Apps and environments** — running web applications that demonstrate or use those models

It was founded in 2016, started as a chatbot startup, and pivoted to become the central infrastructure layer for the entire open-source AI ecosystem. Today it hosts hundreds of thousands of models and is used by essentially every AI team in the world.

---

### HuggingFace Spaces — The Hosting Platform

A HuggingFace Space is a hosted web application. Think of it like Vercel or Heroku but designed specifically for AI demos and training environments.

When you deploy something as a HF Space:
- It gets a permanent public URL (for example: `https://sam25kat-securereview.hf.space`)
- It runs 24/7 without you having to manage servers
- It's discoverable — anyone browsing HuggingFace can find it
- It scales automatically for traffic spikes
- Free tier is available, paid tiers unlock GPUs

The supported "runtimes" include Python apps (Gradio, Streamlit), static HTML, and Docker containers. SecureReview uses Docker, which gives maximum flexibility — it's just a container that happens to expose a FastAPI web server on port 7860.

**Why port 7860?** That's HuggingFace's default port convention for Docker Spaces. It's just a number they chose and everyone follows.

---

### Why SecureReview Is on HF Spaces

There are three concrete reasons:

1. **Always-on URL.** The hackathon judges don't download and run your code locally — they hit your URL. If your environment isn't publicly accessible, it doesn't count. HF Spaces gives SecureReview a permanent address that is up right now: `https://sam25kat-securereview.hf.space`.

2. **Free hosting.** The alternative is to pay for AWS/GCP/Azure. For a hackathon, free wins.

3. **Discoverability.** HF Spaces are indexed and browsable. Other researchers training RL agents can stumble upon SecureReview just by exploring the platform. This matters for adoption after the hackathon.

---

### The HuggingFace Hub — Where Model Weights Live

When you want to use an AI model — say, Qwen2.5-1.5B-Instruct (the model we're training) — you don't build it from scratch. Someone else trained it, and the resulting weights (billions of floating-point numbers that encode the model's learned knowledge) are stored on the HuggingFace Hub.

Downloading a model from the Hub is a one-liner in Python using the `transformers` library. The Hub acts like a package registry (think npm or PyPI) but instead of JavaScript libraries, it stores model weight files.

When we say "load Qwen2.5-1.5B-Instruct," we mean: download its weights from the Hub and load them into GPU memory so we can run text through it.

---

### HF Token — Your Access Key

A HuggingFace Token (often called `HF_TOKEN`) is like an API key or password. It lets you:

- Download models that require authentication
- Push your own models or Spaces back to HuggingFace
- Use the HuggingFace Inference API (a service that lets you call models hosted on HF without running them yourself)

In `inference.py` — the baseline agent script — you'll see it configured as an environment variable. The OpenAI-compatible client that talks to models is initialized with the `HF_TOKEN` as its API key.

You keep your token secret (never commit it to git). Anyone who has your token can make API calls charged to your account.

---

## Section 2: OpenEnv — What Is It?

> **TL;DR:** OpenEnv is a standard interface for RL training environments. It's like a universal power socket — any training loop that speaks OpenEnv can plug into any OpenEnv environment. SecureReview is one such environment.

---

### The Core Idea: Standardization

Imagine if every charging cable for every phone had a different shape. You'd need a different charger for every device. That was the state of RL training environments before standards emerged.

OpenEnv solves this by defining a minimal, shared contract: every environment must expose the same three operations in the same way. If you write a training loop that speaks OpenEnv, it can train on any environment — a card game, a robotics simulator, a code review environment — without any changes.

For the Meta PyTorch OpenEnv Hackathon, the organizing team built OpenEnv as the framework for the competition. Participants build environments; judges evaluate them.

---

### The Gym Analogy

The closest predecessor to OpenEnv is OpenAI Gym (now called Gymnasium). If you've heard of CartPole (the classic RL "balance a pole" demo) or Atari game playing, those were Gym environments.

OpenAI Gym established the `reset / step / observation` pattern that OpenEnv inherits and extends. The key difference: Gym was designed for toy simulations (pole balancing, video games). OpenEnv is designed for **LLM agent training** — environments where the "agent" is a language model, and the actions and observations are text or structured data.

SecureReview is an OpenEnv environment the way CartPole is a Gym environment. Same concept, different domain: instead of balancing a pole, an agent is reviewing code for security vulnerabilities.

---

### The Three Mandatory Operations

Every OpenEnv environment must implement exactly three things. Everything else is optional.

**1. reset()**

This starts a fresh episode. Think of it as "deal a new hand of cards" or "start a new game level." In SecureReview, calling POST /reset picks a scenario (one of the 16 hand-crafted security reviews), loads the relevant files, resets the step counter, and returns the agent's first observation — what it currently sees.

**2. step(action)**

This is "take one action." The agent looks at its observation, decides what to do, and sends that decision to the environment. The environment processes it and returns: a new observation (what the agent sees now), a reward signal (how well it did on this step), a done flag (whether the episode is finished), and an info dict (extra debugging details). In SecureReview, an action might be "report this finding" or "show me the list of available files."

**3. state (GET /state)**

This is a snapshot of the current episode state — step count, findings so far, which files are loaded, whether the episode is done. It's used by training loops to introspect what's happening without needing to take an action.

These three operations are the "universal power socket." A training loop that calls these endpoints in a loop can train an AI agent on any OpenEnv environment.

---

### openenv.yaml — The Manifest

Every OpenEnv environment has a file called `openenv.yaml` at the root of the project. It's the environment's identity card. SecureReview's `openenv.yaml` declares:

- The environment name (`securereview`)
- The type (`space` — meaning HF Spaces deployment)
- The runtime (`fastapi`)
- The app entry point (`app.main:app`)
- The port (`7860`)
- The version and description
- The list of tasks, each with its ID, name, difficulty, and step budget

This file is what `openenv validate` reads first. If it's missing or malformed, validation fails before a single endpoint is even called.

---

### openenv validate — The Compliance Check

`openenv validate` is a command-line tool provided by the hackathon organizers. It has two modes:

**Local validation** (`openenv validate .`): Checks that the directory structure is correct, `openenv.yaml` is valid, the right files exist.

**Runtime validation** (`openenv validate --url https://sam25kat-securereview.hf.space`): Actually hits the live URL and checks every required endpoint. It calls `/health` and verifies the response says `status: healthy`. It calls `/metadata` and checks the format. It calls `/schema`. It calls `/reset` and then `/step`. It checks that reward scores fall strictly between 0 and 1 (the open interval (0, 1) — not including the endpoints).

SecureReview passes both. The reward clamping (`max(0.01, min(0.99, raw_score))` in `base.py`) was added specifically to satisfy the strict bounds check.

**Why passing validation matters:** Judges pull environments programmatically by URL. An environment that fails validation is effectively invisible to the evaluation pipeline. Passing validation means SecureReview is fully pluggable into any OpenEnv-compatible training loop, which is the whole point of the hackathon.

---

## Section 3: SecureReview — Deep Dive

> **TL;DR:** SecureReview is a training ground for AI code review. An agent reads files, reports security bugs, and gets scored by a deterministic math formula. The 72 vulnerabilities are manually planted, so the score can't be faked.

---

### The Problem

Every major tech company in the world is now using AI to generate code. GitHub Copilot, Cursor, and similar tools write first drafts of functions, modules, and entire features. This is genuinely useful.

But here's the problem no one talks about: **AI-generated code ships security vulnerabilities at scale.** Not because AI is malicious — because it doesn't naturally catch typosquatted package names, doesn't know which SQL migration patterns lock production tables, doesn't think about IAM policies.

And as AI writes more code, the bottleneck shifts from "writing code" to "reviewing code." Human reviewers can't keep up. The logical solution — training AI to review code — requires training environments. SecureReview is one of those environments.

---

### The Three Task Types in Plain English

**Task 1: Dependency and Supply Chain Review (Easy)**

When developers write Python or Node.js code, they list their dependencies in a file (requirements.txt for Python, package.json for Node.js). These files say things like "install the `requests` library, version 2.28."

There are three attack vectors this task tests:

- **Typosquatting**: Someone publishes a package called `reqeusts` (note the misspelling) that looks like `requests`. Developers copy-paste without noticing. The fake package runs malicious code on install. Real attacks: event-stream, ua-parser-js, hundreds of others.

- **Hallucinated packages**: AI code generators sometimes invent package names that don't exist. The code says `import phantomdb` but there is no `phantomdb` package. Either the import silently fails, or worse, someone registers `phantomdb` as a malicious package to catch AI-generated code that references it.

- **Known CVEs at pinned versions**: A specific version of a library (e.g., `Django==3.1.0`) may have a known security vulnerability (CVE). If the requirements file pins to that version, every installation is vulnerable.

The agent's job: read the requirements file, find which entries are suspicious, report them.

**Task 2: Infrastructure-as-Code Security Review (Medium)**

Infrastructure-as-Code means writing your cloud configuration in files instead of clicking around in the AWS console. Terraform (a tool that configures cloud resources) and Kubernetes (a container orchestration system) are the two file formats used here.

The agent reads `.tf` files (Terraform) and `.yaml` files (Kubernetes) and looks for dangerous configurations. Examples:

- An S3 bucket with `public_access = true` — that's your company's data exposed to the internet. (This is how Capital One was breached in 2019.)
- An IAM policy that says `actions: "*"` — that gives unlimited permissions to whoever holds that role. Never appropriate.
- A Kubernetes container running with `privileged: true` — it has root access to the host machine.
- Missing encryption on a database at rest.

This task requires multi-file reasoning — you might need to read both the network config and the S3 config to understand the full risk.

**Task 3: Database Migration Safety Review (Hard)**

This is the one that requires genuine judgment. A database migration is a script that modifies a production database — adding columns, changing types, creating indexes, dropping tables.

The dangerous part: some operations that look innocent in development will lock an entire production table for minutes during deployment, taking down your service. Others will cause application crashes if deployed in the wrong order.

The agent gets not just the SQL migration file, but also context: how big is this table? How much write traffic does it get? What does the deployment strategy look like? It must reason across all of this.

Examples of what it's looking for:
- `ALTER TABLE ADD COLUMN NOT NULL` on a 50-million-row table, with no default value. This forces a full table rewrite under an exclusive lock. Your API goes down for minutes.
- `CREATE INDEX` (instead of `CREATE INDEX CONCURRENTLY`) on a busy table. Regular index creation holds a write lock. Concurrent creation doesn't.
- Dropping a column that the application code still reads. The app code will throw exceptions on every request as soon as the migration runs.

This task is hard because the correct answer depends on context, not just pattern matching.

---

### What an Episode Is

An episode is one complete review session. It follows this lifecycle:

1. **Reset**: The agent calls POST /reset. The environment picks a scenario, loads the files, and gives the agent its first observation.
2. **Steps**: The agent takes actions (report findings, request files) until it decides it's done or runs out of steps.
3. **Grade**: When the agent calls `mark_complete` (or exhausts the step budget), the environment runs the grader, computes the F1 score and bonuses/penalties, and returns the final reward.

The step budget varies by difficulty: 15 steps for dependency review, 25 for IaC, 35 for migration. This forces the agent to be efficient — you can't just enumerate every possible finding infinitely.

---

### What the Agent "Sees"

Every time the agent takes an action, it receives an observation. This observation contains:

- **task_description**: What kind of review is this? What should the agent look for?
- **difficulty**: Easy, medium, or hard.
- **files**: The actual file contents currently in the review context (the agent starts with 1-2 initial files; more can be requested).
- **available_files**: Names of files that exist but haven't been loaded yet.
- **review_checklist**: A list of things the agent should check for.
- **current_step and max_steps**: "You've used 5 of your 15 steps."
- **findings_so_far**: What the agent has already reported.
- **feedback**: The environment's response to the last action.

Think of this like what a human reviewer sees on their screen: the code files open in their editor, a checklist of things to look for, and a note saying "you've spent 30 minutes so far, you have 15 minutes left."

---

### What the Agent Can "Do"

Four actions. No more, no less.

**report_finding**: "I found a security issue." The agent submits a structured finding: which file, which line, a rule ID (like DEP-002 for typosquatting), a severity level (critical/high/medium/low), and a description in plain text. This is the primary action — finding bugs is the whole job.

**request_context**: "Show me this file." The agent asks for a specific file to be loaded into its context. Useful when it sees a filename referenced in another file and wants to inspect it.

**request_file_list**: "What files are available?" The environment returns a list of all files in the scenario. Useful if the agent wants to discover what it's working with before deciding which to request.

**mark_complete**: "I'm done reviewing." This ends the episode and triggers grading. The agent calls this when it believes it has found all the issues (or when it's satisfied with its findings). This is how you choose when to stop — which itself is a skill.

---

### The Reward Formula in Plain English

When an episode ends, the grader runs this calculation:

**Start with F1 score (up to 0.83 points)**

F1 is the harmonic mean of precision and recall (explained in the glossary). Roughly: did you find most of the real bugs (recall) without also flagging a bunch of non-bugs (precision)? F1 balances both. It's multiplied by 0.83, making it the dominant factor.

**Add severity bonus (up to 0.10 points)**

For each true positive (real bug you correctly identified), did you also label its severity correctly? Critical vs. high vs. medium matters. Get the severity right on your correct findings and earn up to 0.10 extra.

**Add efficiency bonus (up to 0.05 points)**

Did you finish faster than your step budget? If you used only half your steps, you get a small bonus. This incentivizes focused, decisive review rather than burning all available moves.

**Add participation bonus (0.01 points, always)**

A tiny floor so that even a completely empty review doesn't score 0.0. This exists because the OpenEnv validator requires scores strictly greater than 0.

**Subtract false positive penalty (up to 0.20 points)**

Every bug you report that doesn't match a real ground-truth vulnerability costs you 0.03 points. Cap at 0.20. This prevents a strategy of "report everything and hope some sticks" — shotgunning findings is actively penalized.

**Clamp to (0.01, 0.99)**

The final score is clamped so it never exactly equals 0 or 1. This is an OpenEnv validator requirement.

A perfect oracle run (submitting exactly the ground truth, nothing more, nothing less) scores approximately 0.98.

---

### Why It Can't Be Gamed

This is a question judges will definitely ask. The answer is clean:

The 72 vulnerabilities were manually planted by Team CookHouse. The grader is pure arithmetic — it doesn't call an LLM to decide if your finding is "good enough." It checks whether your description mentions the exact package name (for dependency review), or whether your resource ID and rule category match (for IaC), or whether your operation and target object match (for migration). These match keys are fixed in `ground_truth.json` files.

There's no judge who can be flattered, no rubric that can be argued about. Either your finding's description contains the word `reqeusts` (the typosquatted package) or it doesn't. Either your finding references `aws_s3_bucket` + `public_access` or it doesn't.

This is called a **deterministic grader**. It's one of SecureReview's strongest claims.

---

## Section 4: Adaptive Difficulty — The New Feature

> **TL;DR:** The environment now tracks how well the agent is doing and automatically adjusts difficulty. Easy scenarios until you're scoring above 0.30, then medium, then hard. This is called RLVE — the E stands for "environment adapts," not just the reward.

---

### The Problem: 16 Fixed Scenarios

SecureReview has 16 hand-crafted scenarios. A model trained on them long enough could theoretically start memorizing the specific bugs in each scenario rather than learning the underlying skill of security review. If it sees `scenario_002` and remembers from training that the answer is "package reqeusts on line 4," that's memorization, not learning.

More practically: if you throw hard scenarios (database migrations) at a model that's only scoring 0.05, it makes no progress. The signal is too noisy. Training on tasks that are too hard is like throwing calculus at a student who doesn't know multiplication — they don't improve, they just thrash.

---

### The Solution: Self-Adjusting Difficulty

The environment now tracks the agent's last 5 episode scores in a rolling window. When you call POST /reset with `adaptive: true`, instead of picking a scenario randomly, it picks one that matches where the agent currently is.

The three tiers:

**Tier 1 (Rolling average below 0.30):** Easy. The environment serves dependency_review scenarios — the ones with requirements.txt and package.json. These have the fearest moving parts. The agent just needs to match package names.

**Tier 2 (Rolling average 0.30 to 0.60):** Medium. The environment switches to iac_review — Terraform and Kubernetes configurations. Multi-file reasoning required, more rules to know.

**Tier 3 (Rolling average above 0.60):** Hard. The environment serves migration_review — SQL migrations with production context. Judgment required. The hardest task, reserved for when the model is genuinely good.

Within each tier, scenarios are also rated by the number of ground-truth findings (1-3 findings = tier 1, 4-5 findings = tier 2, 6+ = tier 3). So even within the same task type, the environment can pick easier or harder specific scenarios.

---

### The /curriculum Endpoint

Hit GET /curriculum at any time and you get a snapshot of the agent's current progress:

- **episodes_completed**: How many episodes have been run.
- **rolling_average**: The average score over the last 5 episodes.
- **current_skill_level**: "easy", "medium", or "hard".
- **recommended_task**: Which task the environment would pick for the next episode.
- **recent_scores**: The actual scores of the last 5 episodes.
- **next_tier_threshold**: What rolling average is needed to advance to the next tier.
- **progress_pct**: How far through the current tier the agent is.

A training loop can call this endpoint to log curriculum progress alongside training metrics. You can literally watch the agent move through tiers as it learns.

---

### Why This Is Impressive: RLVE vs. RLVR

Most RL research for language models uses what's called **RLVR** — Reinforcement Learning with Verifiable Rewards. The key insight in RLVR is that some tasks (math, code execution, factual lookup) have answers you can verify automatically, which means you can compute a real reward without needing a human or another LLM to judge quality.

SecureReview is already RLVR: F1 over ground-truth findings is verifiable and deterministic.

But we went further: **RLVE** — Reinforcement Learning with Verifiable Environments. The "E" means the environment itself adapts. It's not just that the reward is verifiable; it's that the entire curriculum adjusts based on the agent's trajectory.

The difference matters because:
- RLVR: Verifiable reward, fixed task distribution
- RLVE: Verifiable reward + adaptive task distribution

An adaptive environment is a better teacher. It keeps the agent in the "learning zone" — tasks hard enough to generate learning signal, easy enough to not be pure noise. This is the same reason a good human teacher doesn't give a beginner and an expert the same homework.

**Simple pitch line:** "Our environment is a self-adjusting tutor. It gets harder when you're doing well."

---

## Section 5: Reinforcement Learning — What's Actually Happening

> **TL;DR:** We're training a small AI model to get better at security review by having it try scenarios, grading its attempts with the SecureReview environment, and updating its weights toward approaches that scored higher. It's a student that learns from repeated scored attempts.

---

### The Student Analogy

Imagine a student learning to identify security vulnerabilities in code. You don't just hand them a textbook and say "memorize this" (that's fine-tuning on examples). Instead, you:

1. Give them a code review task.
2. Let them try to find the bugs.
3. Grade their work.
4. Give them feedback.
5. Repeat hundreds of times.

Over time, the student gets better — not because they memorized specific answers, but because they developed the underlying skill. That's reinforcement learning.

In our case:
- The "student" is Qwen2.5-1.5B-Instruct, a small language model with 1.5 billion parameters.
- The "task" is a security review scenario served by SecureReview.
- The "grade" is the F1-based reward score from the grader.
- "Getting better" means the model's weights are updated so it's more likely to take actions that led to high scores in the past.

---

### Why RL and Not Just Fine-Tuning on Examples?

Fine-tuning (or supervised learning) works like this: you show the model "here's a requirements.txt, here's the correct list of findings," and you train it to reproduce that output. You need labeled examples for every scenario.

The problem: writing perfect demonstrations for 72 vulnerabilities across 16 scenarios is tractable. But writing perfect demonstrations for every edge case the model might encounter in the real world is not. And fine-tuned models often learn to pattern-match to their training examples rather than reason about novel situations.

RL solves this differently: you don't tell the model the right answer. You let it try, and you score the result. The model discovers strategies that work by exploring the space of possible actions. Because the scoring is deterministic (F1 over ground truth), you can be confident that high-scoring strategies are genuinely good strategies.

The practical advantage: the environment generates its own training signal. You don't need to hand-label everything. You just need a working grader and a lot of episodes.

---

### What GRPO Is

GRPO stands for Group Relative Policy Optimization. It's the specific RL algorithm we're using to train the model. To understand it, start with the core problem: you have a model, you run it on a task, you get a score. How do you update the weights to make it score higher?

The naive approach would be: if the score was high, make the weights more likely to produce that output; if it was low, make them less likely. But this is unstable — you don't know if the score was high because of good reasoning or just luck on a random pick.

GRPO's key insight: **compare multiple attempts on the same task to each other.** Here's the procedure:

1. Take one scenario (say, `dependency_review/scenario_002`).
2. Generate 4 to 8 completions from the same model (the "group").
3. Score all 4-8 completions using the environment.
4. The reward for each completion is computed relative to the group: completions that scored higher than average get a positive signal, those that scored lower get a negative signal.
5. Update the model weights to increase the probability of higher-scoring completions and decrease the probability of lower-scoring ones.

"Group relative" means the reward isn't an absolute score — it's a comparison within the group. This makes training more stable because the signal is always calibrated to what the model is currently capable of, not some external absolute target.

The math: GRPO maximizes the expected reward while including a KL divergence penalty that prevents the model from drifting too far from its starting weights. This stops the model from "forgetting" all its general language ability while learning the security review task.

---

### Why a Small Model (1.5B Parameters)

Qwen2.5-1.5B-Instruct has 1.5 billion parameters. For context: GPT-4 is estimated to have hundreds of billions. DeepSeek-V3-0324 (the baseline agent) is much larger.

We use a small model deliberately. Here's why:

The baseline agent (DeepSeek-V3-0324) already scores 0.34 average across tasks. It's a capable large model. The point of the training experiment isn't to show that a large model can do security review (it can, moderately). The point is to show that **a small model can be made substantially better through training on our environment**.

If a 1.5B model goes from 0.10 (random/poor baseline) to, say, 0.40 through RL training on SecureReview, that's evidence the environment is a good teacher. The environment is providing useful training signal that the model can absorb.

Think of it this way: you could say "a gold medalist can run a 4-minute mile." Not very informative. More impressive: "our training program took a recreational runner from 8 minutes to 5 minutes." The improvement demonstrates the quality of the training, not just the starting capability.

---

### What "Training on the Environment" Means vs. Static Data

When you train on static data, the training set is fixed forever. Every epoch, you see the same examples.

When you train on an environment, the environment generates the training data on the fly. Every episode is a new roll — which scenario gets picked, what the agent does, what score it gets. The model is always interacting with the world (the environment) and learning from the outcomes.

This is the difference between memorizing chess games from a book versus actually playing chess. The book is static data. The game is an environment.

Training on the environment also means you can train on adaptive curriculum — harder scenarios as the model improves. That's not possible with static datasets.

---

## Section 6: The Full Training Flow (End-to-End)

> **TL;DR:** Load a small model, give it 150-200 rounds of "try this security review, see your score, adjust," and watch the reward curve trend upward. Here's every step.

---

### Step 1: Load Qwen2.5-1.5B-Instruct with Unsloth

The training runs in Google Colab (a free cloud notebook environment with a T4 GPU). The T4 has 16GB of GPU memory. A 1.5B parameter model in full 32-bit precision would need roughly 6GB just for weights, plus memory for the activations and gradients during training. It fits, but barely.

Unsloth is a library that loads models in 4-bit quantization (QLoRA), cutting memory usage roughly in half. It also optimizes the training kernels so the whole process runs 2x-3x faster than vanilla HuggingFace training. For a free T4 GPU, this is essential.

Loading the model: one call to `FastLanguageModel.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", load_in_4bit=True)`. Unsloth handles the rest.

---

### Step 2: Pick a Dependency_Review Scenario

For training, we focus on dependency_review (the easy task). Why not all three? Because:
- The training compute budget is limited (free Colab).
- Starting with the task where the baseline score is lowest (the model has the most room to improve) generates the strongest learning signal.
- Once we demonstrate improvement on one task, the methodology generalizes.

At each training step, a scenario is picked from the 6 dependency_review scenarios.

---

### Step 3: Build the Prompt

The prompt is constructed to tell the model everything it needs to know:
- What kind of review this is
- The file content (requirements.txt or package.json)
- The review checklist
- The available rule IDs (DEP-001 through DEP-007)
- How to format its response (JSON actions)

The prompt ends with: "List all security issues as JSON." For the simplified single-turn training format (as opposed to the multi-turn interactive format of the baseline agent), the model sees all files upfront and outputs its full list of findings in one shot.

---

### Step 4: Generate 4 Completions (the GRPO Group)

The model generates 4 different responses to the same prompt. Because language models are probabilistic (there's randomness in which token gets picked at each step), 4 runs of the same model on the same prompt produce 4 different outputs.

These 4 are the "group" in Group Relative Policy Optimization. They might all be different: one might find 3 bugs, one might find 5, one might hallucinate 2 non-existent bugs, one might miss the main typosquat entirely.

---

### Step 5: Score Each Completion

For each of the 4 completions:

1. Parse the JSON findings out of the model's text output.
2. Call POST /reset on the live SecureReview environment to start a fresh episode for that scenario.
3. Submit each finding via POST /step with action_type `report_finding`.
4. Call POST /step with action_type `mark_complete`.
5. Read the reward from the response.

This is the most important step: we're using the live, running SecureReview environment (at `https://sam25kat-securereview.hf.space`) as the reward oracle. The environment's deterministic F1 grader produces the training signal. The environment does the hard work.

---

### Step 6: Compare and Update Weights

Now we have 4 scores, say [0.43, 0.61, 0.28, 0.55]. The group average is 0.47.

GRPO computes a relative advantage for each completion:
- 0.43 is below average → negative signal
- 0.61 is above average → positive signal
- 0.28 is below average → negative signal
- 0.55 is above average → positive signal

The model weights are then updated (via backpropagation) to increase the likelihood of generating completions similar to the 0.61 and 0.55 responses, and decrease the likelihood of generating completions like the 0.28 one.

This is one training step. Repeat 150-200 times.

---

### Step 7: Repeat 150-200 Steps

Each training step uses a fresh scenario (or the same scenario with different random seeds — the details depend on the training loop configuration). After 150-200 steps, the model has "seen" enough episodes to have developed a pattern.

LoRA (Low-Rank Adaptation) means we're not updating all 1.5 billion parameters. We're updating a small set of adapter matrices that get applied on top of the frozen base model. This makes training faster and requires far less memory, while still allowing meaningful behavioral change.

---

### Step 8: Plot the Reward Curve

After training, plot the training reward over steps. A successful run shows an upward trend — early steps scoring 0.15-0.25, later steps scoring 0.35-0.50.

This reward curve is one of the key visuals for the pitch. It's direct evidence that the model improved through training on SecureReview.

---

### Step 9: Before/After Comparison

Run the same evaluation scenarios with:
1. **Untrained Qwen2.5-1.5B-Instruct** — what it scores before any RL training.
2. **Trained Qwen2.5-1.5B-Instruct** — what it scores after 150-200 GRPO steps.

A concrete before/after number is the clearest proof that the environment works as a training signal. If the trained model scores higher on held-out scenarios (scenarios not seen during training), that's generalization, not memorization. That's the strongest result you can show.

---

## Section 7: Pitch Preparation

> **TL;DR:** Lead with the problem. "AI is writing your code — who's reviewing it?" is a stronger opener than "We built an environment." Have a 30-second version and a 2-minute version ready.

---

### The 30-Second Pitch (Non-Technical Audience)

> "We built a training ground for AI code review. AI is generating more code than ever — but who checks it for security bugs? We built SecureReview: the first environment that trains AI to review code the way a senior engineer would. The agent reads real files, spots planted security vulnerabilities, and gets scored. We trained a small AI model on our environment and showed it actually got better."

Practice this until it flows in under 30 seconds. The structure: problem → what we built → how it works → one result. Don't add jargon unless asked.

---

### The 2-Minute Pitch (Technical Judges)

Cover these five points in order — one per 20-25 seconds:

**1. The capability gap.**
No RL training environment exists for security code review. Existing tools like Snyk and Semgrep are static analyzers — they don't train agents. Existing RL environments (CartPole, Atari, word games) don't test the skill that matters in a world of AI-generated code: reading code and spotting what will break production.

**2. What we built.**
Three task domains: dependency review, IaC misconfiguration, database migration safety. 16 hand-crafted scenarios. 72 manually planted vulnerabilities. Deterministic F1 grader — no LLM-as-judge, no human in the loop. Every score is reproducible. Live at sam25kat-securereview.hf.space, right now.

**3. Adaptive difficulty (RLVE).**
We didn't just build an environment — we built a self-adjusting curriculum. The environment tracks the agent's last 5 episode scores and automatically selects scenarios at the right difficulty. Below 0.30 average? Easy tasks. Above 0.60? Hard tasks. This is RLVE — Reinforcement Learning with Verifiable Environments — where the environment adapts, not just the reward. A step beyond standard RLVR.

**4. Training.**
GRPO via HuggingFace TRL. Unsloth for memory efficiency on T4 GPU. Base model: Qwen2.5-1.5B-Instruct. 4 rollouts per prompt, 150-200 steps. We connect the training loop directly to the live environment as the reward oracle.

**5. Results.**
Baseline with DeepSeek-V3-0324: 0.45 on dependency review, 0.52 on IaC, 0.05 on migration. After GRPO training of the 1.5B model on dependency review: [show reward curve trending upward, before/after scores]. The environment produces genuine learning signal.

---

### The "So What" Answer

When a judge asks "okay, but why does this matter?", here's the answer:

> "An AI that can review code for security bugs is worth billions. Every company shipping AI-generated code needs this. Security review is one of the last bottlenecks before code goes to production. We built the training environment that could teach models to do it — and showed it works. The environment is the infrastructure. Future teams can train much larger models on it, add more scenarios, and push the frontier of what automated code review can do."

---

### Energy Tips for the Finale

**Lead with the problem, not the solution.** "AI is writing your code. Who's reviewing it?" hits harder than "We built an RL environment." Start with the thing that makes people lean forward, then explain your solution.

**Say the live URL early.** "It's live right now at sam25kat-securereview.hf.space." Judges can pull it up while you're talking. This is real — not a demo, not a video. That's unusual and impressive.

**When you say "deterministic F1," say what it means in one breath.** "Deterministic F1 — no LLM judge, pure math, can't be gamed." Don't leave the phrase hanging.

**For RLVE vs. RLVR:** "Most environments just have a verifiable reward. Ours adapts — the environment itself is a teacher, not just a scorer."

**If someone asks about migration_review scoring 0.05:** "That's a feature, not a bug. The task requires cross-file reasoning about production context — table sizes, deployment strategy, service dependencies. It's genuinely hard. It creates headroom for frontier models to demonstrate improvement. The baseline being low shows there's a real training problem to solve."

---

## Section 8: Expected Questions + Prepared Answers

---

**Q1: Why not just fine-tune on security CVE datasets?**

Fine-tuning on CVE data trains the model to recognize vulnerability patterns it has seen before. It doesn't train the model to reason about novel code in novel contexts. A fine-tuned model that has seen "log4shell" in training will recognize log4shell. It won't necessarily reason about an unfamiliar typosquatted package name in an unfamiliar requirements file.

RL on SecureReview trains a different skill: the ability to read unfamiliar code, apply general security reasoning principles, and report findings in the right structured format. The reward is on task performance, not pattern memorization. Additionally, the model learns when to stop — how many findings to report, how to avoid false alarms — because the reward explicitly penalizes false positives. Static CVE data can't teach that.

---

**Q2: How do you know the reward isn't being gamed?**

The 72 vulnerabilities were manually planted by our team. Each has a specific match key — a package name, a resource identifier, an operation name — that the agent's description must contain to score a true positive. The grader is pure Python arithmetic: no LLM, no fuzzy matching, no rubric that can be argued with.

An agent can't "game" this by sounding confident or using security jargon. It either names the right package or it doesn't. If it reports 100 findings to carpet-bomb the ground truth, the false positive penalty (0.03 per FP, up to 0.20 total) destroys the score. The formula is explicitly designed to make "report everything" a losing strategy.

---

**Q3: Isn't 1.5B too small to understand code security?**

At baseline — before any training — yes, a 1.5B model is likely to underperform a much larger model on security review. That's expected. But the question isn't whether a 1.5B model starts as a good security reviewer. The question is: can it improve through training? Can the environment provide useful signal that the model can actually absorb?

That's the research question. If a 1.5B model goes from poor scores to decent scores through RL on our environment, we've shown two things: (1) the environment generates real training signal, and (2) even small models can be taught security review skills through RL. The small model proves the environment's value as a teacher.

---

**Q4: What is OpenEnv and why does it matter?**

OpenEnv is the standardized interface for RL training environments in this hackathon. Think of it like USB — a standard plug that means any device (training loop) can connect to any peripheral (RL environment) without custom wiring.

It matters because it makes RL environments composable. A team building a training loop for LLM agents doesn't have to write custom integration code for each environment. They write code that speaks OpenEnv, and they can train on any compliant environment. SecureReview is fully compliant — it passes `openenv validate` both locally and against the live runtime.

For the hackathon specifically, the judges' evaluation pipeline is built on OpenEnv. Environments that aren't compliant aren't discoverable or usable by the evaluation infrastructure.

---

**Q5: How does adaptive difficulty work exactly?**

The environment maintains a rolling window of the agent's last 5 episode scores. When you call POST /reset with `adaptive: true`, it computes the rolling average and selects a task and scenario based on where the agent currently sits.

Rolling average below 0.30: dependency_review (easy). Between 0.30 and 0.60: iac_review (medium). Above 0.60: migration_review (hard). Within each task, scenarios are further tiered by the number of planted findings (1-3 = tier 1, 4-5 = tier 2, 6+ = tier 3), so the difficulty granularity is even finer than just switching tasks.

The /curriculum endpoint exposes this state — current skill level, recommended next task, progress percentage toward the next tier. A training loop can log this alongside loss curves to visualize curriculum progression.

---

**Q6: Can I try it right now?**

Yes. It's live at `https://sam25kat-securereview.hf.space`. The interactive API docs are at `https://sam25kat-securereview.hf.space/docs`.

To run a quick episode right now from a terminal:

Send a POST to `/reset` with body `{"task_id": "dependency_review"}`. Read the requirements.txt in the observation. Report a finding with `report_finding`. Then call `mark_complete`. You'll get a score back immediately.

If you want to just watch it work: open the /docs URL in a browser, expand the /reset endpoint, click "Try it out," send the request, and see the observation returned in real time.

---

**Q7: What was the hardest thing to build?**

The migration_review task. The difficulty isn't writing the SQL — it's writing SQL migration scenarios where the danger is only visible if you understand the production context (table size, deployment strategy, app code that reads specific columns). The grader also had to match findings on operation + target object rather than simple package names, which required more sophisticated matching logic.

Technically, getting `openenv validate` to pass was also non-trivial. The validator checks that reward scores fall in the open interval (0, 1) — strictly between 0 and 1, not including the endpoints. An empty submission was naturally scoring 0.0 (no findings = no F1). We had to add the participation bonus and clamp the score to (0.01, 0.99) to satisfy this requirement.

---

**Q8: How is this different from existing code security tools (Snyk, Semgrep)?**

Snyk and Semgrep are static analyzers. They run pattern-matching rules against code and return a list of known vulnerabilities. They're fast, deterministic, and useful — but they don't use AI, and they can't improve through experience.

SecureReview is a training environment. Its purpose isn't to ship a commercial code security product — it's to teach AI agents to do security review through reinforcement learning. The output is a trained model, not a scan report.

Think of it as the difference between a spell checker (Snyk/Semgrep) and a teacher who gives a student progressively harder proofreading exercises. Both can catch errors. Only the teacher produces a student who gets better.

---

**Q9: What would you do with more compute or time?**

Several things, in priority order:

First, train on all three tasks, not just dependency_review. The migration task is deliberately hard — with more training compute, we'd want to see if GRPO + adaptive curriculum can push a 1.5B model to meaningful improvement there.

Second, use a larger base model — Qwen2.5-7B or 14B. The methodology scales. A larger model with more capacity for reasoning would likely achieve higher final scores.

Third, add more scenarios. 16 is enough to demonstrate the concept, but 100+ scenarios would give stronger generalization guarantees and make the held-out evaluation more meaningful.

Fourth, evaluate on real-world code repositories — not just hand-crafted scenarios. This would test whether the learned skill transfers to genuine production code.

---

**Q10: Why does this matter for the future of AI?**

We're in a period where AI writes a substantial and growing fraction of all production code. The current state: AI generates, humans review. The bottleneck is human review.

The end state we're heading toward — whether we like it or not — is AI generating and AI reviewing. The question isn't whether that happens; it's whether the reviewing AI is any good.

Training environments like SecureReview are the infrastructure that makes the reviewing AI good. You can't have safe AI-generated code at scale without AI code review. You can't have AI code review without training environments. SecureReview is one of the first serious attempts to build that infrastructure as an open, standardized, trainable environment.

The long-term value is in the training environment itself, not just in any single model trained on it. Any team with compute can point their training loop at SecureReview and get a better security reviewer out.

---

## Section 9: Glossary

---

**RL (Reinforcement Learning)**
A training paradigm where an agent learns by taking actions in an environment and receiving reward signals. Unlike supervised learning (where you provide the right answers), RL lets the agent discover what works through trial and error. The core loop is: observe → act → receive reward → update weights → repeat.

---

**GRPO (Group Relative Policy Optimization)**
The specific RL algorithm used to train SecureReview's model. It generates multiple completions (a "group") for the same prompt, scores them all, and updates the model to favor higher-scoring completions relative to the group average. "Group relative" means the reward signal is always calibrated to what the model is currently capable of, making training stable.

---

**F1 Score**
A single number that balances precision and recall. Precision: "of the bugs I reported, what fraction were real?" Recall: "of the real bugs, what fraction did I find?" F1 is the harmonic mean of both. Score of 1.0 means perfect precision and perfect recall. Score of 0 means either everything you reported was wrong, or you missed every real bug. In SecureReview, F1 is the dominant component (83%) of the reward.

---

**Episode**
One complete interaction loop in an RL environment: from reset (start) to mark_complete (end). In SecureReview, one episode is one complete security review session — pick a scenario, take actions up to the step budget, get a final score. Episodes are the unit of experience that generates training data.

---

**Ground Truth**
The manually planted "correct answer" that the grader compares agent findings against. In SecureReview, ground truth is stored in `ground_truth.json` files — one per scenario — and contains the exact list of vulnerabilities Team CookHouse planted. These files are never shown to the agent; only the grader reads them.

---

**Reward Hacking**
When an AI agent finds a way to achieve a high reward score without actually doing the task correctly. For example, if the grader rewarded "number of findings" with no false positive penalty, an agent could spam 1000 findings and score perfectly. SecureReview prevents this: the false positive penalty (0.03 per FP, up to 0.20 total) makes carpet-bombing findings a losing strategy.

---

**RLVE (Reinforcement Learning with Verifiable Environments)**
An extension of RLVR where the environment itself adapts based on the agent's performance. In RLVE, the curriculum adjusts — task difficulty, scenario selection — in addition to providing a verifiable reward. SecureReview implements RLVE via its adaptive difficulty system and /curriculum endpoint.

---

**RLVR (Reinforcement Learning with Verifiable Rewards)**
A training approach for language models where the reward signal is computed by a deterministic function (rather than a human or another LLM). Math correctness (check the answer), code execution (run the code), and F1 over ground truth (SecureReview) are all verifiable rewards. RLVR is the foundation of modern LLM RL training. RLVE is the next step.

---

**HuggingFace Space**
A hosted web application on HuggingFace's platform. Can run any Docker container, Gradio app, or Streamlit app. Gets a permanent public URL. SecureReview is deployed as a Docker Space at `https://sam25kat-securereview.hf.space`. Always-on, free tier available, accessible from anywhere.

---

**OpenEnv**
The standardized framework for RL training environments used in the Meta PyTorch OpenEnv Hackathon. Defines a minimal contract: every environment must expose /reset, /step, /state, /health, /metadata, and /schema endpoints in a specified format. Any training loop that speaks OpenEnv can train on any compliant environment. SecureReview passes full OpenEnv validation.

---

**Pydantic**
A Python library for data validation using type annotations. In SecureReview, Pydantic defines the exact structure of every request and response — `Action`, `Observation`, `Finding`, `Reward`. If an agent sends a malformed action (wrong field names, wrong types), Pydantic rejects it before the environment logic even runs. This is Pydantic v2, the most recent major version.

---

**FastAPI**
A Python web framework for building APIs. FastAPI uses Python type hints to automatically generate API documentation, validate requests, and serialize responses. SecureReview's HTTP server — all the /reset, /step, /state endpoints — is a FastAPI application. Its /docs endpoint provides interactive API documentation generated automatically from the Pydantic models.

---

**Docker**
A containerization tool that packages an application and all its dependencies into a standardized, isolated unit called a container. "Runs on my machine" problems disappear: if it runs in the Docker container, it runs everywhere. SecureReview is deployed as a Docker container on HuggingFace Spaces. The `Dockerfile` at the root of the project defines how to build it.

---

**Unsloth**
A Python library that makes training large language models faster and more memory-efficient. It uses 4-bit quantization (storing weights in 4 bits instead of 16 or 32) and optimized training kernels. For SecureReview's training plan, Unsloth is what makes it possible to train Qwen2.5-1.5B-Instruct on a free T4 GPU in Google Colab. Without Unsloth, the model might not fit in GPU memory at all.

---

**TRL (Transformer Reinforcement Learning)**
HuggingFace's library for training language models with RL. It implements GRPO, PPO, and other RL algorithms as drop-in trainers that work with HuggingFace's model hub and Unsloth. The training loop for SecureReview uses TRL's GRPOTrainer. TRL handles the complexity of computing advantages, updating weights, managing rollouts — the training loop code itself is relatively short.

---

**Instruct Model**
A language model that has been fine-tuned to follow instructions and engage in conversation (as opposed to a "base" model that just predicts the next token in a document). Qwen2.5-1.5B-Instruct is the instruct version — it's been trained to respond to prompts like a helpful assistant. Using an instruct model as the starting point for RL training is standard practice because it already knows how to follow instructions and produce structured output.

---

**Fine-Tuning**
Continuing to train an already-trained model on new data. The base model starts with broad knowledge from its pretraining; fine-tuning specializes it for a specific task or domain. Standard supervised fine-tuning (SFT) requires labeled input-output pairs. RL fine-tuning (what SecureReview does) requires only a reward signal. LoRA/QLoRA (see below) are memory-efficient fine-tuning methods.

---

**LoRA / QLoRA (Low-Rank Adaptation / Quantized LoRA)**
Parameter-efficient fine-tuning techniques. Instead of updating all the model's weights during training (expensive), LoRA adds small adapter matrices to each layer and only trains those. The base model weights stay frozen. QLoRA combines LoRA with 4-bit quantization of the base model. Together they reduce GPU memory requirements by 5-10x, making it possible to fine-tune multi-billion parameter models on consumer or free-tier GPUs. SecureReview's training uses QLoRA via Unsloth.

---

**Adaptive Curriculum**
A training strategy where the difficulty of training tasks adjusts based on learner performance. In education, this is personalized learning — a student who aces 3rd-grade math gets 4th-grade math next, not more 3rd-grade repetition. In SecureReview, the adaptive curriculum adjusts which task and which scenario tier the agent trains on based on its rolling average score. The /curriculum endpoint exposes the current curriculum state.

---

**Baseline Agent**
A reference agent run before any training, used to establish starting performance. In SecureReview, the baseline agent is `inference.py` running DeepSeek-V3-0324 — a large, capable model without any RL training on SecureReview. It scores 0.45 on dependency review, 0.52 on IaC, and 0.05 on migration. These numbers set the benchmark that the trained small model aims to beat (on dependency review) or approach (on the other tasks).

---

*Document version 1.0 — April 2026*
*Team CookHouse: Sai Jadhav + Sameer S Katte*
*SecureReview · Meta PyTorch OpenEnv Hackathon*
