import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar
from backend.autoscaler import SCALE_OUT_THRESHOLD, SCALE_IN_THRESHOLD

st.set_page_config(page_title="Instance Lifecycle — CloudScale", layout="wide", page_icon="🔄")
user = require_auth()
show_user_sidebar()

state = get_state()

st.markdown("## 🔄 Instance Lifecycle")
st.caption("Visualizes how instances are born and terminated as load changes")

st.divider()

# ──────────────────────────────────────────────
# Row 1 — Fleet Health Cards
# ──────────────────────────────────────────────
fleet = state.get_fleet_summary()

st.markdown("### Current Fleet Status")

if fleet:
    cols = st.columns(min(len(fleet), 5))
    for i, inst in enumerate(fleet):
        col = cols[i % 5]
        health_color = {
            "healthy": "#22c55e",
            "warning": "#f59e0b",
            "critical": "#ef4444",
            "initializing": "#94a3b8"
        }.get(inst["health"], "#94a3b8")

        status_color = {
            "running": "#22c55e",
            "launching": "#f59e0b",
            "terminating": "#ef4444"
        }.get(inst["status"], "#94a3b8")

        status_icon = {
            "running": "▶",
            "launching": "⟳",
            "terminating": "✕"
        }.get(inst["status"], "?")

        with col:
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid {health_color}44;
                border-top:3px solid {health_color};
                border-radius:10px;padding:14px;margin-bottom:10px;text-align:center">
                <div style="color:#94a3b8;font-size:0.7rem;font-family:monospace">{inst['id']}</div>
                <div style="color:#f1f5f9;font-weight:700;font-size:0.85rem;margin:4px 0">{inst['name']}</div>
                <div style="color:{status_color};font-size:0.75rem;margin-bottom:8px">
                    {status_icon} {inst['status'].upper()}
                </div>
                <div style="display:flex;justify-content:space-between;margin-top:6px">
                    <div style="text-align:left">
                        <div style="color:#64748b;font-size:0.65rem">CPU</div>
                        <div style="color:{health_color};font-weight:700;font-size:0.85rem">{inst['cpu']:.1f}%</div>
                    </div>
                    <div style="text-align:right">
                        <div style="color:#64748b;font-size:0.65rem">MEM</div>
                        <div style="color:#a855f7;font-weight:700;font-size:0.85rem">{inst['memory']:.1f}%</div>
                    </div>
                </div>
                <div style="margin-top:8px">
                    <div style="background:#0f1420;border-radius:4px;height:4px;overflow:hidden">
                        <div style="background:{health_color};width:{inst['cpu']}%;height:100%;border-radius:4px"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No instances running. Generate load to start the fleet.")

st.divider()

# ──────────────────────────────────────────────
# Row 2 — Annotated Instance + CPU Timeline
# ──────────────────────────────────────────────
st.markdown("### Instance Count vs CPU — Annotated with Scaling Events")

if len(state.history_instances) > 1:
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("Instance Count Over Time", "CPU % Over Time"),
        vertical_spacing=0.10,
        row_heights=[0.45, 0.55]
    )

    ticks = list(range(len(state.history_instances)))

    # Instance count — step chart
    fig.add_trace(go.Scatter(
        x=ticks,
        y=state.history_instances,
        mode='lines',
        name='Instances',
        line=dict(color='#22c55e', width=2.5, shape='hv'),
        fill='tozeroy',
        fillcolor='rgba(34,197,94,0.08)'
    ), row=1, col=1)

    # CPU line
    fig.add_trace(go.Scatter(
        x=ticks,
        y=state.history_cpu,
        mode='lines',
        name='CPU %',
        line=dict(color='#f59e0b', width=2),
        fill='tozeroy',
        fillcolor='rgba(245,158,11,0.06)'
    ), row=2, col=1)

    # Threshold bands on CPU panel
    fig.add_hline(y=SCALE_OUT_THRESHOLD, line_dash="dash", line_color="rgba(239,68,68,0.5)",
                  row=2, col=1, annotation_text="Scale-Out 70%", annotation_position="right")
    fig.add_hline(y=SCALE_IN_THRESHOLD, line_dash="dash", line_color="rgba(59,130,246,0.5)",
                  row=2, col=1, annotation_text="Scale-In 30%", annotation_position="right")

    # Mark scaling events as vertical lines (approximate tick positions)
    scale_out_ticks = []
    scale_in_ticks = []

    # Walk history to find where instance count changed
    for i in range(1, len(state.history_instances)):
        diff = state.history_instances[i] - state.history_instances[i - 1]
        if diff > 0:
            scale_out_ticks.append(i)
        elif diff < 0:
            scale_in_ticks.append(i)

    for t in scale_out_ticks:
        fig.add_vline(x=t, line_dash="dot", line_color="rgba(239,68,68,0.6)",
                      row=1, col=1)
        fig.add_vline(x=t, line_dash="dot", line_color="rgba(239,68,68,0.6)",
                      row=2, col=1)

    for t in scale_in_ticks:
        fig.add_vline(x=t, line_dash="dot", line_color="rgba(59,130,246,0.6)",
                      row=1, col=1)
        fig.add_vline(x=t, line_dash="dot", line_color="rgba(59,130,246,0.6)",
                      row=2, col=1)

    # Scale-out / scale-in markers on instance chart
    if scale_out_ticks:
        fig.add_trace(go.Scatter(
            x=scale_out_ticks,
            y=[state.history_instances[t] for t in scale_out_ticks],
            mode='markers',
            name='Scale Out',
            marker=dict(color='#ef4444', size=10, symbol='triangle-up')
        ), row=1, col=1)

    if scale_in_ticks:
        fig.add_trace(go.Scatter(
            x=scale_in_ticks,
            y=[state.history_instances[t] for t in scale_in_ticks],
            mode='markers',
            name='Scale In',
            marker=dict(color='#3b82f6', size=10, symbol='triangle-down')
        ), row=1, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=480,
        margin=dict(l=10, r=80, t=40, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_yaxes(title_text="Instances", row=1, col=1, gridcolor="#1e2433", dtick=1)
    fig.update_yaxes(title_text="CPU %", range=[0, 105], row=2, col=1, gridcolor="#1e2433")
    fig.update_xaxes(title_text="Ticks", row=2, col=1, gridcolor="#1e2433")

    st.plotly_chart(fig, use_container_width=True)

    # Legend note
    st.markdown("""
    <div style="display:flex;gap:24px;padding:8px 0">
        <span style="color:#ef4444;font-size:0.82rem">▲ Scale-Out event</span>
        <span style="color:#3b82f6;font-size:0.82rem">▼ Scale-In event</span>
        <span style="color:#94a3b8;font-size:0.82rem">Dotted lines show exact tick when scaling fired</span>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("No history yet. Generate load on the **Load Generator** page to see the instance lifecycle.")

st.divider()

# ──────────────────────────────────────────────
# Row 3 — Scaling Events: CPU Before vs After
# ──────────────────────────────────────────────
st.markdown("### Scaling Effectiveness — CPU Before vs After Each Event")
st.caption("Shows how much the autoscaler reduced CPU pressure on each scale-out, and reclaimed it on scale-in")

events = state.scaling_events
if len(events) >= 2:
    # Pair consecutive events to show before/after CPU
    event_labels = [f"#{i+1} {e['type']} ({e['time']})" for i, e in enumerate(events[-12:])]
    event_cpus = [e["cpu"] for e in events[-12:]]
    event_colors = ["#ef4444" if e["direction"] == "up" else "#3b82f6" for e in events[-12:]]

    fig_cpu = go.Figure()
    fig_cpu.add_trace(go.Bar(
        x=event_labels,
        y=event_cpus,
        marker_color=event_colors,
        text=[f"{c:.1f}%" for c in event_cpus],
        textposition="outside",
        name="CPU at event"
    ))
    fig_cpu.add_hline(y=SCALE_OUT_THRESHOLD, line_dash="dash", line_color="rgba(239,68,68,0.5)",
                      annotation_text="Scale-Out threshold")
    fig_cpu.add_hline(y=SCALE_IN_THRESHOLD, line_dash="dash", line_color="rgba(59,130,246,0.5)",
                      annotation_text="Scale-In threshold")

    fig_cpu.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=320,
        margin=dict(l=10, r=10, t=10, b=60),
        yaxis=dict(range=[0, 110], title="CPU %", gridcolor="#1e2433"),
        xaxis=dict(tickangle=-30, gridcolor="#1e2433"),
        showlegend=False
    )
    st.plotly_chart(fig_cpu, use_container_width=True)

    # Summary table
    st.markdown("**Recent Scaling Events Detail**")
    for e in reversed(events[-8:]):
        direction_icon = "🔺" if e["direction"] == "up" else "🔻"
        color = "#ef4444" if e["direction"] == "up" else "#3b82f6"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:8px 14px;
            background:#1a1f2e;border-radius:8px;margin-bottom:6px;font-size:0.83rem">
            <span style="font-size:1.1rem">{direction_icon}</span>
            <span style="color:{color};font-weight:700;min-width:90px">{e['type']}</span>
            <span style="color:#f1f5f9">{e['from']} → {e['to']} instances</span>
            <span style="color:#f59e0b">CPU: {e['cpu']}%</span>
            <span style="color:#64748b;margin-left:auto">{e['time']}</span>
        </div>
        """, unsafe_allow_html=True)

elif events:
    st.info("Generate more load variations to see before/after CPU comparisons across multiple events.")
else:
    st.info("No scaling events yet. Increase users past 700 to trigger a scale-out.")

st.divider()

# ──────────────────────────────────────────────
# Row 4 — Users per Instance (Load Spread)
# ──────────────────────────────────────────────
st.markdown("### Load Distribution — Users per Instance Over Time")
st.caption("Lower is better — shows how scaling keeps each instance's workload manageable")

if len(state.history_users) > 1 and len(state.history_instances) > 1:
    users_per_inst = [
        round(u / max(i, 1), 1)
        for u, i in zip(state.history_users, state.history_instances)
    ]

    fig_upi = go.Figure()
    fig_upi.add_trace(go.Scatter(
        y=users_per_inst,
        mode='lines',
        name='Users / Instance',
        line=dict(color='#a855f7', width=2),
        fill='tozeroy',
        fillcolor='rgba(168,85,247,0.08)'
    ))
    fig_upi.add_hline(y=100, line_dash="dash", line_color="rgba(239,68,68,0.4)",
                      annotation_text="≈ Scale-out point (100 users/inst)", annotation_position="right")

    fig_upi.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=220,
        margin=dict(l=10, r=80, t=10, b=20),
        yaxis=dict(title="Users / Instance", gridcolor="#1e2433"),
        xaxis=dict(title="Ticks", gridcolor="#1e2433"),
        showlegend=False
    )
    st.plotly_chart(fig_upi, use_container_width=True)
else:
    st.info("No history data yet.")

st.markdown("---")
st.caption("CloudScale Platform • Instance Lifecycle — updates on each page interaction")
