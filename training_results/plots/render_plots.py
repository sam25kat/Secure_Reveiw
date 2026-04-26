"""Re-render before_after.png + reward_curve.png + results.json for all three
tasks from the per-scenario data captured in *_sft_logs.txt.

The trainer Spaces write plots to ephemeral container disk, so they're not
fetchable via Hub API. This script reproduces them locally with identical
styling, using the authoritative numbers from the training logs.

Run: python3 render_plots.py
"""
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT      = Path(__file__).parent
LOG_DIR   = ROOT.parent
RAW_IAC   = ROOT.parent.parent / "iac_logs.txt"  # iac loss curve only here

TASKS = {
    "dep": {
        "log":   LOG_DIR / "dep_sft_logs.txt",
        "title": "Dependency Review — Before vs After SFT",
        "loss_log": LOG_DIR / "dep_sft_logs.txt",
    },
    "migration": {
        "log":   LOG_DIR / "migration_sft_logs.txt",
        "title": "Migration Review — Before vs After SFT",
        "loss_log": LOG_DIR / "migration_sft_logs.txt",
    },
    "iac": {
        "log":   LOG_DIR / "iac_sft_logs.txt",
        "title": "IaC Review — Before vs After SFT",
        "loss_log": RAW_IAC,
    },
}

SCENARIO_RE = re.compile(r"^\s*([a-z_]+_\d+):\s*([\d.]+)\s*→\s*([\d.]+)")
LOSS_RE     = re.compile(r"'loss':\s*'([\d.]+)'")


def parse_log(path):
    """Returns ordered dict of scenario_id -> (baseline, trained)."""
    out = {}
    with open(path) as f:
        for line in f:
            m = SCENARIO_RE.match(line)
            if m:
                sid, before, after = m.group(1), float(m.group(2)), float(m.group(3))
                out[sid] = (before, after)
    return out


def parse_losses(path):
    if not path.exists():
        return []
    txt = path.read_text()
    return [float(x) for x in LOSS_RE.findall(txt)]


def render_before_after(task, sids_data, title, out_path):
    plt.style.use("dark_background")
    sids   = list(sids_data.keys())
    b_vals = [sids_data[s][0] for s in sids]
    t_vals = [sids_data[s][1] for s in sids]
    x      = np.arange(len(sids))

    fig, ax = plt.subplots(figsize=(max(12, len(sids) * 0.75), 5))
    ax.bar(x - 0.175, b_vals, 0.35, label="Before", color="#444444")
    ax.bar(x + 0.175, t_vals, 0.35, label="After",  color="#ff6b35")

    for i, (b, t) in enumerate(zip(b_vals, t_vals)):
        if abs(t - b) > 0.005:
            ax.text(
                i + 0.175, t + 0.02, f"{t-b:+.2f}",
                ha="center", fontsize=8,
                color="#22d3ee" if t >= b else "#ef4444",
            )

    ax.set_xticks(x)
    ax.set_xticklabels([s.split("_")[-1] for s in sids], rotation=15, fontsize=8)
    ax.set_ylim(0, 1)
    ax.legend(loc="upper left")
    ax.set_title(title, fontweight="bold")

    mb, mt = sum(b_vals) / len(b_vals), sum(t_vals) / len(t_vals)
    ax.text(
        0.98, 0.92, f"Mean: {mb:.3f} → {mt:.3f}  ({mt-mb:+.3f})",
        transform=ax.transAxes, ha="right", fontsize=11, color="white",
        bbox=dict(boxstyle="round", facecolor="#1a1a1a", alpha=0.8),
    )
    fig.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return mb, mt


def render_loss_curve(losses, title, out_path):
    if not losses:
        return
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(range(1, len(losses) + 1), losses, color="#ff6b35", linewidth=2, marker="o", markersize=4)
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Loss")
    ax.set_title(title, fontweight="bold")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    for tag, cfg in TASKS.items():
        out_dir = ROOT / tag
        out_dir.mkdir(exist_ok=True)

        sids_data = parse_log(cfg["log"])
        losses    = parse_losses(cfg["loss_log"])

        mb, mt = render_before_after(tag, sids_data, cfg["title"], out_dir / "before_after.png")
        render_loss_curve(
            losses,
            f"SecureReview {tag} SFT — Training Loss",
            out_dir / "reward_curve.png",
        )

        results = {
            "task":            tag,
            "scenarios":       len(sids_data),
            "baseline_mean":   mb,
            "trained_mean":    mt,
            "improvement":     mt - mb,
            "baseline_scores": {s: v[0] for s, v in sids_data.items()},
            "trained_scores":  {s: v[1] for s, v in sids_data.items()},
        }
        (out_dir / "results.json").write_text(json.dumps(results, indent=2))

        wins   = sum(1 for s in sids_data if sids_data[s][1] - sids_data[s][0] > 0.005)
        losses_ct = sum(1 for s in sids_data if sids_data[s][0] - sids_data[s][1] > 0.005)
        flat   = len(sids_data) - wins - losses_ct
        print(
            f"  {tag:10s}  scenarios={len(sids_data):2d}  "
            f"baseline={mb:.3f}  trained={mt:.3f}  Δ={mt-mb:+.3f}  "
            f"  wins={wins} flat={flat} losses={losses_ct}"
        )


if __name__ == "__main__":
    main()
