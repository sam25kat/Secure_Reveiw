---
title: SecureReview GRPO Trainer
emoji: 🔐
colorFrom: red
colorTo: gray
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
hardware: t4-small
---

# SecureReview — GRPO Trainer

Trains `Qwen2.5-1.5B-Instruct` using Group Relative Policy Optimization (GRPO) on the [SecureReview](https://sam25kat-securereview.hf.space) environment.

## What this does

- Loads the model in 4-bit QLoRA (via Unsloth)
- Connects to the live SecureReview environment as a reward oracle
- Runs 150 GRPO training steps — reward = F1-based score from graded vulnerability findings
- Produces `plots/reward_curve.png` and `plots/before_after.png`

## Usage

Click **Run Training** in the Gradio UI. Training takes ~20 minutes on T4.

## Environment

The reward signal comes from [sam25kat/securereview](https://huggingface.co/spaces/sam25kat/securereview) — a live OpenEnv environment that grades security findings against ground-truth scenarios.
