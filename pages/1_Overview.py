import streamlit as st
import plotly.graph_objects as go
from backend.metrics import calculate_cpu, calculate_memory
from backend.autoscaler import apply_autoscaling
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar

# ──────────────────────────────────────────────
# 1_Overview.py
# Shows a high-level summary of the system's health.
# Contains 3 gauge charts (CPU, Memory, Instance count)
# and 4 key stat numbers below them.
# ──────────────────────────────────────────────

# Page config — title shown in browser tab
st.set_page_config(page_title="Overview — CloudScale", layout="wide", page_icon="📊")

# Require login — stops page if not logged in
user = require_auth()

# Show user info + logout in sidebar
show_user_sidebar()

# Get the shared system state
state = get_state()

# ── Recalculate metrics for this page visit ──
# Pages don't auto-refresh, so we recalculate when user navigates here
state.cpu_usage = calculate_cpu(state.active_users, state.instances)
state.memory_usage = calculate_memory(state.active_users, state.instances)
apply_autoscaling(state)  # Run the autoscaler to check if scaling is needed
# Recalculate again after potential scaling (instance count may have changed)
state.cpu_usage = calculate_cpu(state.active_users, state.instances)
state.memory_usage = calculate_memory(state.active_users, state.instances)
state.record_snapshot()   # Save this reading to history arrays for charts

st.markdown("## 📊 System Overview")
st.caption("Real-time view of your infrastructure health and scaling status")

st.divider()

# ──────────────────────────────────────────────
# Gauge Charts Row
# Three side-by-side Plotly gauge charts
# ──────────────────────────────────────────────
g1, g2, g3 = st.columns(3)

with g1:
    # ── CPU Gauge ──
    # Color zones: green (0-30%), yellow (30-70%), red (70-100%)
    # Red threshold line at 70% (scale-out trigger)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=state.cpu_usage,
        number={"suffix": "%", "font": {"size": 36, "color": "#f1f5f9"}},
        title={"text": "CPU Utilization", "font": {"size": 14, "color": "#94a3b8"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569"},
            "bar": {"color": "#3b82f6"},         # Blue fill bar
            "bgcolor": "#1a1f2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "rgba(34,197,94,0.15)"},    # Green zone (safe)
                {"range": [30, 70], "color": "rgba(245,158,11,0.15)"},  # Yellow zone (moderate)
                {"range": [70, 100], "color": "rgba(239,68,68,0.15)"}, # Red zone (scale out)
            ],
            "threshold": {
                "line": {"color": "#ef4444", "width": 3},  # Red line at 70% (scale-out point)
                "thickness": 0.8,
                "value": 70
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with g2:
    # ── Memory Gauge ──
    # Similar to CPU but no threshold line (memory doesn't trigger scaling)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=state.memory_usage,
        number={"suffix": "%", "font": {"size": 36, "color": "#f1f5f9"}},
        title={"text": "Memory Utilization", "font": {"size": 14, "color": "#94a3b8"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569"},
            "bar": {"color": "#a855f7"},          # Purple fill bar
            "bgcolor": "#1a1f2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(34,197,94,0.15)"},    # Green zone
                {"range": [40, 75], "color": "rgba(245,158,11,0.15)"},  # Yellow zone
                {"range": [75, 100], "color": "rgba(239,68,68,0.15)"}, # Red zone
            ],
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

with g3:
    # ── Instance Count with Delta ──
    # Shows current instance count + arrow showing if it went up or down
    # delta = difference from the previous recorded value
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=state.instances,
        number={"font": {"size": 52, "color": "#22c55e"}},
        title={"text": "Active Instances", "font": {"size": 14, "color": "#94a3b8"}},
        # Compare to the second-to-last history value to show the delta arrow
        delta={"reference": state.history_instances[-2] if len(state.history_instances) > 1 else state.instances, "relative": False}
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        margin=dict(l=20, r=20, t=30, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────
# Key Stats Row
# 4 simple metric boxes below the gauges
# ──────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)

with s1:
    st.metric("👥 Active Users", f"{state.active_users:,}")
with s2:
    st.metric("📈 Scale Outs", state.total_scale_outs)   # How many times we added servers
with s3:
    st.metric("📉 Scale Ins", state.total_scale_ins)     # How many times we removed servers
with s4:
    st.metric("📋 Total Requests", f"{state.total_requests:,}")  # Cumulative request count

# ──────────────────────────────────────────────
# System Status Banner
# Shows a contextual message about current system state
# ──────────────────────────────────────────────
st.divider()

if state.cpu_usage > 70:
    # CPU above scale-out threshold → red alert
    st.error("🔴 **System Under High Load** — Scaling out to handle demand. New instances being provisioned.")
elif state.cpu_usage < 30 and state.instances > 1:
    # CPU below scale-in threshold and we have extra instances → blue info
    st.info("🔵 **Low Load Detected** — Scaling in to reduce costs. Excess instances being terminated.")
elif state.load_running:
    # Load is running but CPU is in normal range → green success
    st.success("🟢 **System Stable** — All instances healthy. Load within normal parameters.")
else:
    # No load running at all → warning to go generate some load
    st.warning("⚠️ **Idle** — No active load. Go to Load Generator to simulate traffic.")
