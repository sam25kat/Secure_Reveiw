import gradio as gr
import subprocess
import sys
import os
import json
import threading

PLOTS_DIR = "./plots"
RESULTS_FILE = f"{PLOTS_DIR}/results.json"


def run_training():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "train.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    output = []
    for line in proc.stdout:
        output.append(line.rstrip())
        yield "\n".join(output), None, None, None, None

    proc.wait()

    reward_img = f"{PLOTS_DIR}/reward_curve.png" if os.path.exists(f"{PLOTS_DIR}/reward_curve.png") else None
    ba_img = f"{PLOTS_DIR}/before_after.png" if os.path.exists(f"{PLOTS_DIR}/before_after.png") else None

    summary = ""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            r = json.load(f)
        summary = (
            f"**Baseline mean:** {r['baseline_mean']:.3f}\n\n"
            f"**Trained mean:** {r['trained_mean']:.3f}\n\n"
            f"**Improvement:** {r['improvement']:+.3f}"
        )

    yield "\n".join(output), reward_img, ba_img, summary, gr.update(interactive=True)


def start_training(btn_state):
    yield (
        "Starting training... this takes ~20 minutes on T4.\n",
        None,
        None,
        "",
        gr.update(interactive=False, value="Training in progress..."),
    )
    yield from run_training()


with gr.Blocks(title="SecureReview GRPO Trainer", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown(
        """# SecureReview — GRPO Training

Trains `Qwen2.5-1.5B-Instruct` via GRPO on the [SecureReview](https://sam25kat-securereview.hf.space) environment.
The model learns to identify security vulnerabilities in dependency files — reward comes from a live graded environment, not a static dataset.

**Hardware:** T4 GPU · **Time:** ~20 min · **Steps:** 150"""
    )

    with gr.Row():
        run_btn = gr.Button("▶  Run Training", variant="primary", scale=1)

    with gr.Row():
        log_box = gr.Textbox(
            label="Training Log",
            lines=30,
            max_lines=60,
            autoscroll=True,
            interactive=False,
            scale=2,
        )
        with gr.Column(scale=1):
            summary_md = gr.Markdown(label="Results Summary")
            reward_img = gr.Image(label="Reward Curve", type="filepath")
            ba_img = gr.Image(label="Before vs After", type="filepath")

    run_btn.click(
        fn=start_training,
        inputs=[run_btn],
        outputs=[log_box, reward_img, ba_img, summary_md, run_btn],
    )

if __name__ == "__main__":
    demo.launch()
