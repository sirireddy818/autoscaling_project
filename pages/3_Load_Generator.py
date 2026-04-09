import streamlit as st
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar

# ──────────────────────────────────────────────
# 3_Load_Generator.py
# Lets the user simulate user traffic (0 to 1000 users).
# Setting users here triggers the autoscaler to add/remove servers.
# Think of this as your "traffic control panel".
# ──────────────────────────────────────────────

# Page config — title and icon shown in browser tab
st.set_page_config(page_title="Load Generator", layout="wide", page_icon="⚡")

# Require login — redirect to login page if not authenticated
user = require_auth()

# Show user info and logout button in the sidebar
show_user_sidebar()

# Get the shared system state object
state = get_state()

st.title("⚡ Load Generator")
st.caption("Simulate user traffic to trigger Auto Scaling behavior")

st.divider()

# ──────────────────────────────────────────────
# Load Slider
# User drags this to set how many simulated users are hitting the site
# ──────────────────────────────────────────────
st.subheader("Simulated User Load")

users = st.slider(
    "Users",
    min_value=0,
    max_value=1000,
    step=50,
    value=state.active_users  # Start at current load level
)

# ── Determine load level label and color based on slider value ──
if users == 0:
    load_label = "🔘 No Load"
    load_color = "gray"
elif users < 300:
    load_label = "🟢 Low Load"     # 1–299 users = low
    load_color = "green"
elif users < 700:
    load_label = "🟡 Medium Load"  # 300–699 users = medium
    load_color = "orange"
else:
    load_label = "🔴 High Load"    # 700–1000 users = high (will trigger scale out)
    load_color = "red"

st.markdown(f"**Load Level:** `{load_label}`")

st.divider()

# ──────────────────────────────────────────────
# Control Buttons
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    # Apply the slider value as the active load
    if st.button("▶️ Apply Load", use_container_width=True, type="primary"):
        state.active_users = users           # Set users to slider value
        state.load_running = users > 0       # Mark load as running if users > 0
        if users > 0:
            state.logs.append(f"[LOAD SET] Load set to {users} users")
        else:
            state.logs.append("[STOP] Load set to 0")
        st.rerun()  # Refresh page to show new state

with col2:
    # Instantly set to maximum load (1000 users)
    if st.button("🚀 Max Load (1000)", use_container_width=True):
        state.active_users = 1000
        state.load_running = True
        state.logs.append("[MAX LOAD] Load set to 1000 users")
        st.rerun()

with col3:
    # Instantly stop all load (0 users)
    if st.button("⛔ Stop Load", use_container_width=True):
        state.active_users = 0
        state.load_running = False
        state.logs.append("[STOP] Load stopped")
        st.rerun()

st.divider()

# ──────────────────────────────────────────────
# Quick Preset Buttons
# One-click shortcuts to common load values
# ──────────────────────────────────────────────
st.subheader("Quick Presets")
p1, p2, p3, p4, p5 = st.columns(5)

with p1:
    if st.button("100 Users", use_container_width=True):
        state.active_users = 100
        state.load_running = True
        state.logs.append("[LOAD SET] Load set to 100 users")
        st.rerun()
with p2:
    if st.button("300 Users", use_container_width=True):
        state.active_users = 300
        state.load_running = True
        state.logs.append("[LOAD SET] Load set to 300 users")
        st.rerun()
with p3:
    if st.button("500 Users", use_container_width=True):
        state.active_users = 500
        state.load_running = True
        state.logs.append("[LOAD SET] Load set to 500 users")
        st.rerun()
with p4:
    if st.button("750 Users", use_container_width=True):
        state.active_users = 750
        state.load_running = True
        state.logs.append("[LOAD SET] Load set to 750 users")
        st.rerun()
with p5:
    if st.button("1000 Users", use_container_width=True):
        state.active_users = 1000
        state.load_running = True
        state.logs.append("[LOAD SET] Load set to 1000 users")
        st.rerun()

st.divider()

# ──────────────────────────────────────────────
# Current Status Display
# Shows whether load is currently running or not
# ──────────────────────────────────────────────
st.subheader("Current Status")

if state.load_running and state.active_users > 0:
    st.success(
        f"Load generator running — **{state.active_users:,}** simulated users active across **{state.instances}** instance(s)"
    )
else:
    st.info(
        "No load is being generated. Use the slider or quick presets above."
    )

st.divider()

# ──────────────────────────────────────────────
# Explanation of how load generation works
# Educational section for the viewer
# ──────────────────────────────────────────────
st.subheader("How Load Generation Works")

st.markdown(
    """
1️⃣ **Simulate Requests**
User traffic is generated using a virtual load slider.

2️⃣ **CPU Utilization Increases**
Each EC2 instance processes requests, raising CPU usage.

3️⃣ **CloudWatch Detection (Simulated)**
Average CPU is monitored continuously.

4️⃣ **Auto Scaling Triggered**
Instances are added or removed based on thresholds.
"""
)

st.markdown("---")
st.caption("AWS Auto Scaling — simulated environment (no real AWS resources)")
