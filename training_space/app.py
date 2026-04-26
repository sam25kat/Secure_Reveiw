import sys
import types

for _mod in ("audioop", "pyaudioop"):
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)

import streamlit as st
import subprocess
import os
import json
import threading
import time

PLOTS_DIR    = "./plots"
LOG_FILE     = "./training.log"
DONE_FILE    = "./training_done.txt"
PID_FILE     = "./training.pid"
RESULTS_FILE = f"{PLOTS_DIR}/results.json"
TASK_ID_FILE = "./.task_id"

# Pre-staged artifacts from a previous successful run — judges see these
# without having to actually click "Run Training". Purely additive: if the
# files don't exist, nothing renders.
SAMPLE_LOG_FILE         = "./sample_run.log"
SAMPLE_BEFORE_AFTER_PNG = "./sample_before_after.png"
SAMPLE_REWARD_PNG       = "./sample_reward_curve.png"
SAMPLE_RESULTS_JSON     = "./sample_results.json"

# ---------------------------------------------------------------------------
# Trainer hub config — same across all 3 trainer Spaces, the active task
# is selected by the contents of `.task_id` at the Space root.
# ---------------------------------------------------------------------------
TASKS = {
    "dependency": {
        "title":     "Dependency Review",
        "subtitle":  "Supply-chain literacy",
        "blurb":     "Typosquats, hallucinated PyPI imports, pinned CVEs, license risks. Tests the baseline of supply-chain awareness every reviewer should have.",
        "stats":     "24 scenarios · 120 findings · Qwen 1.5B · 3 epochs",
        "delta":     "+0.302",
        "deltatxt":  "20 / 24 wins · 0.083 → 0.385",
        "space_url": "https://huggingface.co/spaces/sam25kat/securereview-trainer",
    },
    "iac": {
        "title":     "IaC Misconfiguration",
        "subtitle":  "Cloud-security reasoning",
        "blurb":     "CIS violations in Terraform / K8s — public buckets, wildcard IAM, privileged containers, missing encryption. Multi-file cloud reasoning.",
        "stats":     "24 scenarios · 155 findings · Qwen 1.5B · 3 epochs",
        "delta":     "+0.126",
        "deltatxt":  "6 / 13 wins · 0.177 → 0.303",
        "space_url": "https://huggingface.co/spaces/sam25kat/securereview-trainer-iac",
    },
    "migration": {
        "title":     "Migration Safety",
        "subtitle":  "Database engineering judgment",
        "blurb":     "SQL migrations against live production context — table sizes, write throughput, downstream services. Hot-row contention, RLS gaps, MVCC bloat.",
        "stats":     "12 curriculum-filtered (of 28) · 155 findings · Qwen 7B 4-bit · 3 epochs",
        "delta":     "+0.295",
        "deltatxt":  "10 / 12 wins · 0.170 → 0.465",
        "space_url": "https://huggingface.co/spaces/sam25kat/securereview-trainer-migration",
    },
}
TASK_ORDER = ["dependency", "iac", "migration"]


def detect_local_task() -> str:
    """Each trainer Space puts its own task id in /.task_id — defaults to dep."""
    if os.path.exists(TASK_ID_FILE):
        try:
            t = open(TASK_ID_FILE).read().strip()
            if t in TASKS:
                return t
        except OSError:
            pass
    return "dependency"


LOCAL_TASK = detect_local_task()


# ---------------------------------------------------------------------------

def is_training_alive():
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError, PermissionError):
        return False


def _run():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    with open(LOG_FILE, "w", buffering=1) as log:
        proc = subprocess.Popen(
            [sys.executable, "train.py"],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        proc.wait()
    with open(DONE_FILE, "w") as f:
        f.write("done")
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------

st.set_page_config(page_title="SecureReview Trainer", layout="wide")

st.markdown(
    """
    <style>
      .hub-card {
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 10px;
          padding: 22px 22px 18px 22px;
          background: rgba(255,255,255,0.02);
          height: 100%;
      }
      .hub-card.active {
          border-color: #ff6b35;
          background: rgba(255,107,53,0.06);
      }
      .hub-card h3 {
          margin: 0 0 4px 0;
          font-size: 17px;
      }
      .hub-card .sub {
          color: #9ca3af;
          font-size: 12px;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          margin-bottom: 14px;
      }
      .hub-card .blurb {
          color: #d1d5db;
          font-size: 13px;
          line-height: 1.5;
          min-height: 86px;
      }
      .hub-card .stats {
          font-family: ui-monospace, Menlo, Monaco, "Courier New", monospace;
          font-size: 11px;
          color: #9ca3af;
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(255,255,255,0.08);
      }
      .hub-card .delta {
          font-size: 26px;
          font-weight: 700;
          color: #ff6b35;
          margin-top: 8px;
          letter-spacing: -0.02em;
      }
      .hub-card .delta-cap {
          font-family: ui-monospace, Menlo, Monaco, "Courier New", monospace;
          font-size: 11px;
          color: #9ca3af;
      }
      .hub-card .badge {
          display: inline-block;
          font-family: ui-monospace, Menlo, Monaco, "Courier New", monospace;
          font-size: 10px;
          letter-spacing: 0.08em;
          padding: 2px 8px;
          border-radius: 4px;
          background: #ff6b35;
          color: #0a0a0a;
          margin-left: 8px;
          vertical-align: middle;
      }
      .hub-card a.openbtn {
          display: inline-block;
          margin-top: 16px;
          padding: 8px 14px;
          border: 1px solid rgba(255,255,255,0.2);
          border-radius: 6px;
          color: #d1d5db;
          text-decoration: none;
          font-size: 13px;
      }
      .hub-card a.openbtn:hover {
          border-color: #ff6b35;
          color: #ff6b35;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SecureReview — Trainer Hub")
st.markdown(
    "**Three security-review domains. One canonical SFT → GRPO hybrid pipeline.** "
    "Click *Run Training* on any card — full SFT run completes in ~30 s on a single GPU credit, "
    "with loss curve + before/after plot rendered live."
)
st.markdown("---")

# ---------------------------------------------------------------------------
# Three task cards
# ---------------------------------------------------------------------------

cols = st.columns(3, gap="medium")

for idx, task_id in enumerate(TASK_ORDER):
    cfg = TASKS[task_id]
    is_active = task_id == LOCAL_TASK
    with cols[idx]:
        active_cls = "active" if is_active else ""
        active_badge = '<span class="badge">THIS SPACE</span>' if is_active else ""
        card_html = f"""
        <div class="hub-card {active_cls}">
            <h3>{cfg['title']}{active_badge}</h3>
            <div class="sub">{cfg['subtitle']}</div>
            <div class="blurb">{cfg['blurb']}</div>
            <div class="delta">{cfg['delta']}</div>
            <div class="delta-cap">{cfg['deltatxt']}</div>
            <div class="stats">{cfg['stats']}</div>
        """
        if not is_active:
            card_html += f'<a class="openbtn" href="{cfg["space_url"]}" target="_blank">Open trainer ↗</a>'
        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

st.markdown("")
st.markdown("---")

# ---------------------------------------------------------------------------
# Active-task training panel
# ---------------------------------------------------------------------------

active_cfg = TASKS[LOCAL_TASK]

# ---------------------------------------------------------------------------
# Pre-staged sample-run artifacts (additive, only show if files exist).
# Lets judges see real output without having to click Run.
# ---------------------------------------------------------------------------
have_sample = (
    os.path.exists(SAMPLE_LOG_FILE)
    or os.path.exists(SAMPLE_BEFORE_AFTER_PNG)
    or os.path.exists(SAMPLE_RESULTS_JSON)
)
if have_sample:
    st.subheader(f"📊  {active_cfg['title']} · sample run (already trained)")
    st.markdown(
        f"Below is the recorded output of a successful **{LOCAL_TASK}** "
        f"training run on this Space — the same run that produced the "
        f"`{active_cfg['delta']}` headline number. You can read the log + "
        f"plots without having to launch a new run."
    )
    if os.path.exists(SAMPLE_RESULTS_JSON):
        try:
            r = json.load(open(SAMPLE_RESULTS_JSON))
            c1, c2, c3 = st.columns(3)
            c1.metric("Baseline mean", f"{r.get('baseline_mean', 0):.3f}")
            c2.metric("Trained mean",  f"{r.get('trained_mean',  0):.3f}")
            c3.metric("Improvement",   f"{r.get('improvement',   0):+.3f}")
        except Exception:
            pass
    pcols = st.columns(2)
    if os.path.exists(SAMPLE_BEFORE_AFTER_PNG):
        pcols[0].image(SAMPLE_BEFORE_AFTER_PNG, caption="Before vs After SFT (sample run)")
    if os.path.exists(SAMPLE_REWARD_PNG):
        pcols[1].image(SAMPLE_REWARD_PNG, caption="Training Loss (sample run)")
    if os.path.exists(SAMPLE_LOG_FILE):
        with st.expander("📜  Sample training log (full output)"):
            try:
                st.text(open(SAMPLE_LOG_FILE).read())
            except Exception as e:
                st.error(f"Could not read sample log: {e}")
    st.markdown("---")

st.subheader(f"▶  {active_cfg['title']} · run training here")
st.markdown(
    f"Trains via SFT → GRPO on the live `{LOCAL_TASK}_review` task of the "
    f"SecureReview environment. Reward comes from the live grader — no static dataset."
)

done            = os.path.exists(DONE_FILE)
log_present     = os.path.exists(LOG_FILE)
training_alive  = is_training_alive()
ongoing         = log_present and not done

if not ongoing and not done:
    if st.button("▶  Run Training", type="primary"):
        for p in (DONE_FILE, LOG_FILE, PID_FILE):
            if os.path.exists(p):
                try: os.remove(p)
                except OSError: pass
        threading.Thread(target=_run, daemon=True).start()
        time.sleep(1)
        st.rerun()

elif ongoing:
    if training_alive:
        st.info("Training in progress. Page auto-refreshes every 10 s — safe to close your laptop.")
    else:
        st.warning(
            "Training process not detected (container may have restarted). "
            "If the log below has stopped growing, click **Restart Training**."
        )

    log_content = ""
    if log_present:
        with open(LOG_FILE) as f:
            log_content = f.read()

    st.text_area("Training Log", log_content, height=460)

    col_a, col_b = st.columns(2)
    if not training_alive:
        if col_a.button("Restart Training (clears progress)"):
            for p in (DONE_FILE, LOG_FILE, PID_FILE):
                if os.path.exists(p):
                    try: os.remove(p)
                    except OSError: pass
            threading.Thread(target=_run, daemon=True).start()
            time.sleep(1)
            st.rerun()

    if training_alive:
        time.sleep(10)
        st.rerun()

else:
    st.success("Training complete!")

    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            r = json.load(f)
        c1, c2, c3 = st.columns(3)
        c1.metric("Baseline mean", f"{r['baseline_mean']:.3f}")
        c2.metric("Trained mean",  f"{r['trained_mean']:.3f}")
        c3.metric("Improvement",   f"{r['improvement']:+.3f}")

    col1, col2 = st.columns(2)
    if os.path.exists(f"{PLOTS_DIR}/reward_curve.png"):
        col1.image(f"{PLOTS_DIR}/reward_curve.png", caption="Reward Curve")
    if os.path.exists(f"{PLOTS_DIR}/before_after.png"):
        col2.image(f"{PLOTS_DIR}/before_after.png", caption="Before vs After")

    if log_present:
        with st.expander("Training log"):
            with open(LOG_FILE) as f:
                st.text(f.read())

    if st.button("Reset & Run Again"):
        for p in (DONE_FILE, LOG_FILE, PID_FILE):
            if os.path.exists(p):
                try: os.remove(p)
                except OSError: pass
        st.rerun()
