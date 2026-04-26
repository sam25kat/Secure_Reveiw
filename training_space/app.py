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


st.set_page_config(page_title="SecureReview Trainer", layout="wide")
st.title("SecureReview — GRPO Trainer")
st.markdown(
    "Trains via GRPO on the live SecureReview environment.  \n"
    "Reward comes from a graded environment — no static dataset."
)

done            = os.path.exists(DONE_FILE)
log_present     = os.path.exists(LOG_FILE)
training_alive  = is_training_alive()
mid_run         = log_present and not done and (training_alive or not is_training_alive())
# Resume detection: if log file exists and not marked done, treat as ongoing
ongoing = log_present and not done

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
