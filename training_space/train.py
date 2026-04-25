import os
import sys
import json
import re
import time
import requests
import functools

print = functools.partial(print, flush=True)

ENV_URL    = os.getenv("ENV_URL", "https://sam25kat-securereview.hf.space")
TASK_ID    = "dependency_review"
MODEL_NAME = "unsloth/Qwen2.5-1.5B-Instruct"
MAX_SEQ_LEN      = 2048
NUM_GENERATIONS  = 4
MAX_NEW_TOKENS   = 600
TRAIN_STEPS      = 150
LEARNING_RATE    = 2e-5
LORA_RANK        = 16
GRAD_ACCUM_STEPS = 4
OUTPUT_DIR       = "./securereview-grpo"
PLOTS_DIR        = "./plots"

os.makedirs(PLOTS_DIR,   exist_ok=True)
os.makedirs(OUTPUT_DIR,  exist_ok=True)

SYSTEM_PROMPT = """You are a senior security engineer reviewing dependency files for vulnerabilities.

Identify ALL security issues including:
- Typosquatted packages (names that misspell popular libraries, e.g. 'reqeusts' instead of 'requests')
- Known CVE-vulnerable versions (e.g. requests<2.20.0 has CVE-2018-18074)
- Hallucinated / non-existent packages that don't exist on PyPI or npm
- Suspicious or malicious packages

Output ONLY a valid JSON array of findings. Each finding must have:
  file, line (integer or null), rule_id (e.g. DEP-001), severity (critical/high/medium/low/info), description

Example output:
[
  {"file": "requirements.txt", "line": 3, "rule_id": "DEP-001", "severity": "critical", "description": "Typosquat: 'reqeusts' misspells 'requests'"}
]

If no issues found, output: []
Output ONLY the JSON array. No explanations, no markdown prose."""


# ── Environment helpers ───────────────────────────────────────────────────────

def env_reset(task_id, scenario_id=None):
    payload = {"task_id": task_id}
    if scenario_id:
        payload["scenario_id"] = scenario_id
    r = requests.post(f"{ENV_URL}/reset", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def env_step(action):
    r = requests.post(f"{ENV_URL}/step", json={"action": action}, timeout=30)
    r.raise_for_status()
    return r.json()


def parse_findings(text):
    patterns = [
        r'```(?:json)?\s*(\[.*?\])\s*```',
        r'(\[\s*\{.*?\}\s*\])',
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
    return []


def run_episode(completion, scenario_id):
    findings = parse_findings(completion)
    try:
        env_reset(TASK_ID, scenario_id)
        valid_sev = {"critical", "high", "medium", "low", "info"}
        for f in findings:
            if not isinstance(f, dict):
                continue
            finding = {
                "file":        str(f.get("file", "requirements.txt")),
                "line":        f.get("line"),
                "rule_id":     str(f.get("rule_id", "DEP-001")),
                "severity":    f.get("severity", "medium") if f.get("severity") in valid_sev else "medium",
                "description": str(f.get("description", ""))[:400],
            }
            env_step({"action_type": "report_finding", "finding": finding})
        result = env_step({"action_type": "mark_complete"})
        return float(result.get("reward", 0.01))
    except Exception as e:
        print(f"  [env error] {e}")
        return 0.01


def build_prompt(obs):
    ctx   = obs["observation"]["context"]
    files = ctx["files"]
    parts = [f"Task: {ctx['task_description']}\n"]
    for f in files:
        parts.append(f"\n--- {f['filename']} ---\n{f['content']}")
    parts.append("\nList all security issues as a JSON array:")
    return "".join(parts)


# ── Main training entry point ─────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SecureReview GRPO Training")
    print(f"  Model : {MODEL_NAME}")
    print(f"  Task  : {TASK_ID}")
    print(f"  Steps : {TRAIN_STEPS}")
    print("=" * 60)

    # Verify environment
    print("\n[1/6] Checking environment connection...")
    r = requests.get(f"{ENV_URL}/health", timeout=15)
    print(f"  Health: {r.json()}")

    # Load model
    print("\n[2/6] Loading model (this takes ~2 min)...")
    from unsloth import FastLanguageModel
    import torch

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name    = MODEL_NAME,
        max_seq_length= MAX_SEQ_LEN,
        dtype         = None,
        load_in_4bit  = True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r                          = LORA_RANK,
        target_modules             = ["q_proj", "k_proj", "v_proj", "o_proj",
                                      "gate_proj", "up_proj", "down_proj"],
        lora_alpha                 = LORA_RANK,
        lora_dropout               = 0,
        bias                       = "none",
        use_gradient_checkpointing = "unsloth",
        random_state               = 42,
    )
    print(f"  Trainable params: ", end="")
    model.print_trainable_parameters()

    # Build dataset
    print("\n[3/6] Building training dataset...")
    from datasets import Dataset

    scenario_ids = [f"dep_{i:03d}" for i in range(1, 7)]
    examples = []
    for sid in scenario_ids:
        try:
            obs    = env_reset(TASK_ID, sid)
            prompt = build_prompt(obs)
            examples.append({
                "prompt": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
                "scenario_id": sid,
            })
            print(f"  Loaded {sid}")
        except Exception as e:
            print(f"  Skipping {sid}: {e}")

    repeats  = max(1, TRAIN_STEPS // (len(examples) * NUM_GENERATIONS) + 1)
    examples = examples * repeats
    dataset  = Dataset.from_list(examples)
    print(f"  Dataset: {len(examples)} examples")

    # Baseline evaluation
    print("\n[4/6] Baseline evaluation (before training)...")
    FastLanguageModel.for_inference(model)

    def evaluate(sids, label):
        scores = {}
        for sid in sids:
            obs         = env_reset(TASK_ID, sid)
            prompt_text = build_prompt(obs)
            messages    = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt_text},
            ]
            inputs = tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
            ).to("cuda")
            with torch.no_grad():
                outputs = model.generate(
                    inputs, max_new_tokens=MAX_NEW_TOKENS,
                    temperature=0.1, do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            completion = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            score      = run_episode(completion, sid)
            scores[sid] = score
            print(f"  [{label}] {sid}: {score:.3f}")
            time.sleep(0.3)
        return scores

    baseline_scores = evaluate(scenario_ids, "before")
    print(f"  Baseline mean: {sum(baseline_scores.values())/len(baseline_scores):.3f}")

    # GRPO training
    print("\n[5/6] GRPO training...")
    FastLanguageModel.for_training(model)

    from trl import GRPOConfig, GRPOTrainer

    reward_log    = []
    step_counter  = [0]

    def reward_fn(completions, prompts=None, **kwargs):
        sids = kwargs.get("scenario_id", [scenario_ids[0]] * len(completions))
        if isinstance(sids, str):
            sids = [sids] * len(completions)
        rewards = []
        for completion, sid in zip(completions, sids):
            text   = completion if isinstance(completion, str) else completion[-1]["content"]
            reward = run_episode(text, sid)
            rewards.append(reward)
        step_counter[0] += 1
        mean_r = sum(rewards) / len(rewards)
        reward_log.append({"step": step_counter[0], "mean_reward": mean_r})
        print(f"  Step {step_counter[0]:>4d} | {[round(r,3) for r in rewards]} | mean {mean_r:.3f}")
        return rewards

    training_args = GRPOConfig(
        num_generations             = NUM_GENERATIONS,
        max_completion_length       = MAX_NEW_TOKENS,
        per_device_train_batch_size = 1,
        gradient_accumulation_steps = GRAD_ACCUM_STEPS,
        learning_rate               = LEARNING_RATE,
        optim                       = "adamw_8bit",
        weight_decay                = 0.01,
        lr_scheduler_type           = "cosine",
        warmup_ratio                = 0.05,
        max_steps                   = TRAIN_STEPS,
        logging_steps               = 5,
        save_steps                  = 50,
        output_dir                  = OUTPUT_DIR,
        fp16                        = not torch.cuda.is_bf16_supported(),
        bf16                        = torch.cuda.is_bf16_supported(),
        seed                        = 42,
        report_to                   = "none",
    )
    trainer = GRPOTrainer(
        model            = model,
        processing_class = tokenizer,
        reward_funcs     = reward_fn,
        args             = training_args,
        train_dataset    = dataset,
    )
    trainer.train()

    # Post-training evaluation
    print("\n[6/6] Post-training evaluation...")
    FastLanguageModel.for_inference(model)
    trained_scores = evaluate(scenario_ids, "after")
    print(f"  Trained mean: {sum(trained_scores.values())/len(trained_scores):.3f}")

    print("\n=== Improvement Summary ===")
    for sid in scenario_ids:
        b     = baseline_scores.get(sid, 0)
        t     = trained_scores.get(sid, 0)
        arrow = "▲" if t > b else ("▼" if t < b else "—")
        print(f"  {sid}: {b:.3f} → {t:.3f}  {arrow} {t-b:+.3f}")

    # Plots
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np

    plt.style.use("dark_background")
    steps   = [e["step"]        for e in reward_log]
    rewards = [e["mean_reward"] for e in reward_log]
    window  = 5
    if len(rewards) >= window:
        smoothed     = np.convolve(rewards, np.ones(window)/window, mode="valid")
        smooth_steps = steps[window-1:]
    else:
        smoothed, smooth_steps = rewards, steps

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(steps, rewards, color="#ff6b35", alpha=0.3, linewidth=1, label="Raw")
    ax.plot(smooth_steps, smoothed, color="#ff6b35", linewidth=2.5, label=f"Smoothed (w={window})")
    ax.set_xlabel("Training Step"); ax.set_ylabel("Episode Reward")
    ax.set_title("SecureReview — GRPO Training Reward Curve", fontweight="bold")
    ax.set_ylim(0, 1); ax.legend(); ax.grid(True, alpha=0.2)
    fig.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/reward_curve.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {PLOTS_DIR}/reward_curve.png")

    b_vals = [baseline_scores.get(s, 0) for s in scenario_ids]
    t_vals = [trained_scores.get(s, 0)  for s in scenario_ids]
    x      = np.arange(len(scenario_ids))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - 0.175, b_vals, 0.35, label="Before", color="#444444")
    ax.bar(x + 0.175, t_vals, 0.35, label="After",  color="#ff6b35")
    for i, (b, t) in enumerate(zip(b_vals, t_vals)):
        ax.text(i+0.175, t+0.02, f"{t-b:+.2f}", ha="center", fontsize=9,
                color="#22d3ee" if t >= b else "#ef4444")
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace("dep_","Dep ") for s in scenario_ids], rotation=15)
    ax.set_ylim(0, 1); ax.legend()
    ax.set_title("SecureReview — Before vs After GRPO", fontweight="bold")
    mb = sum(b_vals)/len(b_vals); mt = sum(t_vals)/len(t_vals)
    ax.text(0.98, 0.92, f"Mean: {mb:.2f} → {mt:.2f}  ({mt-mb:+.2f})",
            transform=ax.transAxes, ha="right", fontsize=10, color="white",
            bbox=dict(boxstyle="round", facecolor="#1a1a1a", alpha=0.8))
    fig.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/before_after.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved {PLOTS_DIR}/before_after.png")

    # Save results JSON for the Gradio app to read
    results = {
        "baseline_mean": sum(b_vals)/len(b_vals),
        "trained_mean":  sum(t_vals)/len(t_vals),
        "improvement":   sum(t_vals)/len(t_vals) - sum(b_vals)/len(b_vals),
        "baseline_scores": baseline_scores,
        "trained_scores":  trained_scores,
    }
    with open(f"{PLOTS_DIR}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print(f"  DONE — Mean {sum(b_vals)/len(b_vals):.3f} → {sum(t_vals)/len(t_vals):.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
