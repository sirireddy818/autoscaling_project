import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import math
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar
from backend.autoscaler import SCALE_OUT_THRESHOLD, SCALE_IN_THRESHOLD, MAX_INSTANCES, MIN_INSTANCES
from backend.metrics import calculate_cpu, calculate_memory

st.set_page_config(page_title="Scaling Decision Engine — CloudScale", layout="wide", page_icon="⚙️")
user = require_auth()
show_user_sidebar()

state = get_state()

st.markdown("## ⚙️ Scaling Decision Engine")
st.caption("Real-time breakdown of *why* and *how* the autoscaler makes each decision")

st.divider()

# ──────────────────────────────────────────────
# Row 1 — Current State + Decision Status
# ──────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Current CPU", f"{state.cpu_usage:.1f}%")
with c2:
    st.metric("Scale-Out Threshold", f"{SCALE_OUT_THRESHOLD}%")
with c3:
    st.metric("Scale-In Threshold", f"{SCALE_IN_THRESHOLD}%")
with c4:
    st.metric("Active Instances", f"{state.instances} / {MAX_INSTANCES}")

st.divider()

# ──────────────────────────────────────────────
# Row 2 — CPU Zone Meter + Decision Box
# ──────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown("### CPU Position vs Thresholds")

    fig = go.Figure()

    # Zone bands
    fig.add_shape(type="rect", x0=0, x1=100, y0=0, y1=SCALE_IN_THRESHOLD,
                  fillcolor="rgba(59,130,246,0.12)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=100, y0=SCALE_IN_THRESHOLD, y1=SCALE_OUT_THRESHOLD,
                  fillcolor="rgba(34,197,94,0.10)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=100, y0=SCALE_OUT_THRESHOLD, y1=100,
                  fillcolor="rgba(239,68,68,0.12)", line_width=0)

    # Threshold lines
    fig.add_hline(y=SCALE_OUT_THRESHOLD, line_dash="dash", line_color="#ef4444", line_width=2,
                  annotation_text=f"Scale-Out ({SCALE_OUT_THRESHOLD}%)", annotation_position="right")
    fig.add_hline(y=SCALE_IN_THRESHOLD, line_dash="dash", line_color="#3b82f6", line_width=2,
                  annotation_text=f"Scale-In ({SCALE_IN_THRESHOLD}%)", annotation_position="right")

    # CPU history line
    if state.history_cpu:
        fig.add_trace(go.Scatter(
            y=state.history_cpu,
            mode='lines',
            name='CPU %',
            line=dict(color='#f59e0b', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(245,158,11,0.08)'
        ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=320,
        margin=dict(l=10, r=80, t=20, b=20),
        yaxis=dict(range=[0, 105], title="CPU %", gridcolor="#1e2433"),
        xaxis=dict(title="Ticks (history)", gridcolor="#1e2433"),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Zone labels
    z1, z2, z3 = st.columns(3)
    with z1:
        st.markdown("""
        <div style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);
            border-radius:8px;padding:10px;text-align:center">
            <div style="color:#3b82f6;font-weight:700;font-size:0.85rem">🔵 SCALE-IN ZONE</div>
            <div style="color:#94a3b8;font-size:0.78rem">CPU &lt; 30%</div>
            <div style="color:#cbd5e1;font-size:0.8rem">Remove instances</div>
        </div>
        """, unsafe_allow_html=True)
    with z2:
        st.markdown("""
        <div style="background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.3);
            border-radius:8px;padding:10px;text-align:center">
            <div style="color:#22c55e;font-weight:700;font-size:0.85rem">🟢 OPTIMAL ZONE</div>
            <div style="color:#94a3b8;font-size:0.78rem">CPU 30% – 70%</div>
            <div style="color:#cbd5e1;font-size:0.8rem">No action needed</div>
        </div>
        """, unsafe_allow_html=True)
    with z3:
        st.markdown("""
        <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);
            border-radius:8px;padding:10px;text-align:center">
            <div style="color:#ef4444;font-weight:700;font-size:0.85rem">🔴 SCALE-OUT ZONE</div>
            <div style="color:#94a3b8;font-size:0.78rem">CPU &gt; 70%</div>
            <div style="color:#cbd5e1;font-size:0.8rem">Add instances</div>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown("### Current Decision")

    cpu = state.cpu_usage
    users = state.active_users
    instances = state.instances

    if cpu > SCALE_OUT_THRESHOLD and instances < MAX_INSTANCES:
        total_load = (cpu / 100) * instances
        desired = math.ceil(total_load / 0.5)
        new_count = max(instances + 1, desired)
        new_count = min(new_count, MAX_INSTANCES)
        add = new_count - instances

        decision_color = "#ef4444"
        decision_bg = "rgba(239,68,68,0.08)"
        decision_border = "rgba(239,68,68,0.3)"
        decision_icon = "🔴"
        decision_label = "SCALE OUT"
        decision_detail = f"Add {add} instance(s)<br>→ {instances} to {new_count}"
        decision_why = f"CPU {cpu:.1f}% exceeds {SCALE_OUT_THRESHOLD}% threshold"

    elif cpu < SCALE_IN_THRESHOLD and instances > MIN_INSTANCES:
        if cpu < 5 and users == 0:
            new_count = MIN_INSTANCES
        elif cpu < 15:
            new_count = max(MIN_INSTANCES, instances // 2)
        else:
            total_load = (cpu / 100) * instances
            desired = math.ceil(total_load / 0.5)
            new_count = max(MIN_INSTANCES, min(desired, instances - 1))
        remove = instances - new_count

        decision_color = "#3b82f6"
        decision_bg = "rgba(59,130,246,0.08)"
        decision_border = "rgba(59,130,246,0.3)"
        decision_icon = "🔵"
        decision_label = "SCALE IN"
        decision_detail = f"Remove {remove} instance(s)<br>→ {instances} to {new_count}"
        decision_why = f"CPU {cpu:.1f}% below {SCALE_IN_THRESHOLD}% threshold"

    else:
        decision_color = "#22c55e"
        decision_bg = "rgba(34,197,94,0.08)"
        decision_border = "rgba(34,197,94,0.3)"
        decision_icon = "🟢"
        decision_label = "NO ACTION"
        decision_detail = "Fleet size is optimal"
        decision_why = f"CPU {cpu:.1f}% is in the optimal zone"

    st.markdown(f"""
    <div style="background:{decision_bg};border:2px solid {decision_border};
        border-radius:12px;padding:20px;text-align:center;margin-bottom:16px">
        <div style="font-size:2.5rem">{decision_icon}</div>
        <div style="color:{decision_color};font-weight:800;font-size:1.1rem;margin:6px 0">{decision_label}</div>
        <div style="color:#f1f5f9;font-size:0.9rem">{decision_detail}</div>
        <div style="color:#94a3b8;font-size:0.78rem;margin-top:8px">{decision_why}</div>
    </div>
    """, unsafe_allow_html=True)

    # Distance to next threshold
    dist_out = SCALE_OUT_THRESHOLD - cpu
    dist_in = cpu - SCALE_IN_THRESHOLD

    st.markdown(f"""
    <div style="background:#1a1f2e;border:1px solid #2a2f3e;border-radius:10px;padding:14px">
        <div style="color:#94a3b8;font-size:0.78rem;margin-bottom:8px">DISTANCE TO THRESHOLDS</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:#64748b;font-size:0.82rem">→ Scale-Out</span>
            <span style="color:{'#ef4444' if dist_out <= 0 else '#f1f5f9'};font-weight:600;font-size:0.82rem">
                {'AT THRESHOLD' if dist_out <= 0 else f'+{dist_out:.1f}% away'}
            </span>
        </div>
        <div style="display:flex;justify-content:space-between">
            <span style="color:#64748b;font-size:0.82rem">→ Scale-In</span>
            <span style="color:{'#3b82f6' if dist_in <= 0 else '#f1f5f9'};font-weight:600;font-size:0.82rem">
                {'AT THRESHOLD' if dist_in <= 0 else f'{dist_in:.1f}% above'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ──────────────────────────────────────────────
# Row 3 — Capacity Lookup Table
# ──────────────────────────────────────────────
st.markdown("### Capacity Planning Table")
st.caption("Shows how many instances the autoscaler would provision at each user load level")

user_levels = [0, 50, 100, 200, 300, 400, 500, 600, 750, 1000]
rows = []
for u in user_levels:
    # Simulate the full autoscaler loop (up to 10 rounds) for accuracy
    inst = 1
    for _ in range(10):
        cpu_sim = (u / (inst * 100)) * 100  # no jitter for planning table
        cpu_sim = min(cpu_sim, 100.0)
        if cpu_sim > SCALE_OUT_THRESHOLD and inst < MAX_INSTANCES:
            total_load = (cpu_sim / 100) * inst
            inst = min(math.ceil(total_load / 0.5), MAX_INSTANCES)
        elif cpu_sim < SCALE_IN_THRESHOLD and inst > MIN_INSTANCES:
            if cpu_sim < 5 and u == 0:
                inst = MIN_INSTANCES
            elif cpu_sim < 15:
                inst = max(MIN_INSTANCES, inst // 2)
            else:
                total_load = (cpu_sim / 100) * inst
                inst = max(MIN_INSTANCES, math.ceil(total_load / 0.5))
        else:
            break
    final_cpu = round((u / (inst * 100)) * 100, 1) if inst > 0 else 100.0
    final_cpu = min(final_cpu, 100.0)
    final_mem = round(15 + (u / (inst * 120)) * 60, 1) if inst > 0 else 95.0
    final_mem = min(final_mem, 100.0)
    rows.append({"users": u, "instances": inst, "cpu": final_cpu, "memory": final_mem})

x_labels = [str(r["users"]) for r in rows]

fig_cap = go.Figure()
fig_cap.add_trace(go.Bar(
    x=x_labels,
    y=[r["instances"] for r in rows],
    name="Instances",
    marker_color=["#ef4444" if r["instances"] >= MAX_INSTANCES else "#22c55e" for r in rows],
    text=[str(r["instances"]) for r in rows],
    textposition="outside"
))
fig_cap.add_trace(go.Scatter(
    x=x_labels,
    y=[r["cpu"] for r in rows],
    name="Resulting CPU %",
    yaxis="y2",
    mode="lines+markers",
    line=dict(color="#f59e0b", width=2),
    marker=dict(size=7, color="#f59e0b")
))

# Threshold lines on secondary axis using normalized paper coordinates
fig_cap.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=320,
    margin=dict(l=10, r=60, t=20, b=40),
    xaxis=dict(title="Active Users", gridcolor="#1e2433"),
    yaxis=dict(title="Instances", range=[0, MAX_INSTANCES + 1], gridcolor="#1e2433"),
    yaxis2=dict(title="CPU %", overlaying="y", side="right", range=[0, 110],
                showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
    shapes=[
        dict(type="line", xref="paper", x0=0, x1=1,
             yref="y2", y0=SCALE_OUT_THRESHOLD, y1=SCALE_OUT_THRESHOLD,
             line=dict(color="rgba(239,68,68,0.5)", dash="dot", width=1.5)),
        dict(type="line", xref="paper", x0=0, x1=1,
             yref="y2", y0=SCALE_IN_THRESHOLD, y1=SCALE_IN_THRESHOLD,
             line=dict(color="rgba(59,130,246,0.5)", dash="dot", width=1.5)),
    ],
    annotations=[
        dict(xref="paper", x=1.01, yref="y2", y=SCALE_OUT_THRESHOLD,
             text="70%", showarrow=False, font=dict(color="rgba(239,68,68,0.8)", size=11)),
        dict(xref="paper", x=1.01, yref="y2", y=SCALE_IN_THRESHOLD,
             text="30%", showarrow=False, font=dict(color="rgba(59,130,246,0.8)", size=11)),
    ]
)

# Highlight closest user level to current load
if state.active_users > 0:
    closest = min(x_labels, key=lambda x: abs(int(x) - state.active_users))
    closest_idx = x_labels.index(closest)
    fig_cap.add_shape(type="line", xref="x", x0=closest_idx - 0.4, x1=closest_idx + 0.4,
                      yref="paper", y0=0, y1=1,
                      line=dict(color="#a855f7", dash="dash", width=1.5))
    fig_cap.add_annotation(xref="x", x=closest_idx, yref="paper", y=1.05,
                           text="Current", showarrow=False,
                           font=dict(color="#a855f7", size=11))

st.plotly_chart(fig_cap, use_container_width=True)

st.divider()

# ──────────────────────────────────────────────
# Row 4 — Scaling Formula Explained
# ──────────────────────────────────────────────
st.markdown("### How the Scaling Formula Works")

f1, f2 = st.columns(2)

with f1:
    st.markdown("""
    <div style="background:#1a1f2e;border:1px solid #2a2f3e;border-radius:12px;padding:20px">
        <h4 style="color:#ef4444;margin:0 0 12px">Scale-Out Formula</h4>
        <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8">
            When CPU &gt; 70%:<br>
            <code style="color:#f59e0b">total_load = (cpu% / 100) × current_instances</code><br>
            <code style="color:#f59e0b">desired = ceil(total_load / 0.50)</code><br>
            <code style="color:#f59e0b">new_count = max(current+1, desired)</code><br><br>
            <span style="color:#64748b">Target: Keep CPU near <strong style="color:#22c55e">50%</strong> after scaling</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div style="background:#1a1f2e;border:1px solid #2a2f3e;border-radius:12px;padding:20px">
        <h4 style="color:#3b82f6;margin:0 0 12px">Scale-In Formula</h4>
        <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8">
            When CPU &lt; 30%:<br>
            <code style="color:#f59e0b">If CPU &lt; 5% and users = 0 → drop to 1</code><br>
            <code style="color:#f59e0b">If CPU &lt; 15% → halve the fleet</code><br>
            <code style="color:#f59e0b">Else → remove 1 instance at a time</code><br><br>
            <span style="color:#64748b">Cooldown: <strong style="color:#22c55e">2 seconds</strong> between decisions</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("CloudScale Platform • Scaling Decision Engine — updates on each page interaction")
