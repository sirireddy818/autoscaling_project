import streamlit as st
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar

# ──────────────────────────────────────────────
# 5_Auto_Scaling_Activity.py
# Shows the full history of scaling events and system logs.
# Two sections:
#   1. Scaling Events Timeline — each scale-out/scale-in as a card
#   2. System Logs — raw text log entries in monospace style
# ──────────────────────────────────────────────

st.set_page_config(page_title="Scaling Activity — CloudScale", layout="wide", page_icon="📜")
user = require_auth()
show_user_sidebar()

state = get_state()

st.markdown("## 📜 Auto Scaling Activity")
st.caption("Timeline of all scaling events and system logs")

st.divider()

# ──────────────────────────────────────────────
# Stats Bar — 4 quick numbers at the top
# ──────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)

with s1:
    st.metric("Total Events", len(state.scaling_events))    # Total scale-out + scale-in count
with s2:
    st.metric("Scale Outs", state.total_scale_outs)         # How many times servers were added
with s3:
    st.metric("Scale Ins", state.total_scale_ins)           # How many times servers were removed
with s4:
    st.metric("Current Instances", state.instances)          # How many servers running right now

st.divider()

# ──────────────────────────────────────────────
# Scaling Events Timeline
# Shows each event as a colored card (newest first)
# Green = scale out (added servers), Blue = scale in (removed servers)
# ──────────────────────────────────────────────
st.markdown("### Scaling Events")

if state.scaling_events:
    # reversed() shows newest events at the top
    for event in reversed(state.scaling_events):
        # Choose color scheme based on direction
        if event["direction"] == "up":
            # Scale OUT → green theme
            icon = "🟢"
            color = "#22c55e"
            border_color = "rgba(34,197,94,0.25)"
            bg = "rgba(34,197,94,0.06)"
        else:
            # Scale IN → blue theme
            icon = "🔵"
            color = "#3b82f6"
            border_color = "rgba(59,130,246,0.25)"
            bg = "rgba(59,130,246,0.06)"

        # Render the event card
        # Left border is thick colored line (like a timeline indicator)
        st.markdown(f"""
        <div style="
            background:{bg};
            border:1px solid {border_color};
            border-left:4px solid {color};
            border-radius:10px;
            padding:16px 20px;
            margin-bottom:10px;
            display:flex;
            align-items:flex-start;
            gap:14px">
            <span style="font-size:1.4rem;margin-top:2px">{icon}</span>
            <div style="flex:1">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <strong style="color:{color};font-size:0.95rem">{event['type']}</strong>
                    <span style="color:#64748b;font-size:0.8rem">{event['time']}</span>
                </div>
                <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px">
                    Instances: {event['from']} → {event['to']} &nbsp;•&nbsp; {event['reason']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # No events yet — prompt user to generate load
    st.info("No scaling events recorded yet. Generate load to trigger auto scaling.")

st.divider()

# ──────────────────────────────────────────────
# System Logs
# Raw text log entries shown in monospace style
# Color-coded by type: green=scale out, blue=scale in, yellow=start, red=stop
# Shows last 20 log entries, newest first
# ──────────────────────────────────────────────
st.markdown("### System Logs")

if state.logs:
    # Show last 20 logs in reverse order (newest at top)
    for i, log in enumerate(reversed(state.logs[-20:])):
        # Color the log text based on what type of event it is
        if "[SCALE OUT]" in log:
            log_color = "#22c55e"   # Green for scale out
        elif "[SCALE IN]" in log:
            log_color = "#3b82f6"   # Blue for scale in
        elif "[START]" in log:
            log_color = "#f59e0b"   # Amber for start events
        elif "[STOP]" in log:
            log_color = "#ef4444"   # Red for stop events
        elif "[UPDATE]" in log:
            log_color = "#a855f7"   # Purple for updates
        else:
            log_color = "#94a3b8"   # Gray for other logs

        st.markdown(f"""
        <div style="
            background:#1a1f2e;
            border:1px solid #2a2f3e;
            border-radius:8px;
            padding:10px 16px;
            margin-bottom:6px;
            font-family:monospace;
            font-size:0.82rem;
            color:{log_color}">
            {log}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No logs yet. System activity will appear here as events occur.")

# ── Clear Logs Button ──
# Only shown if there are logs to clear
if state.logs:
    st.divider()
    if st.button("Clear All Logs", type="secondary"):
        # Wipe all event history and reset counters
        state.logs.clear()
        state.scaling_events.clear()
        state.total_scale_outs = 0
        state.total_scale_ins = 0
        st.rerun()

st.markdown("---")
st.caption("CloudScale Platform • Scaling Activity Log")
