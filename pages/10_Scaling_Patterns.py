import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statistics
from backend.state import get_state
from backend.auth import require_auth, show_user_sidebar
from backend.autoscaler import SCALE_OUT_THRESHOLD, SCALE_IN_THRESHOLD

st.set_page_config(page_title="Scaling Patterns — CloudScale", layout="wide", page_icon="📐")
user = require_auth()
show_user_sidebar()

state = get_state()

st.markdown("## 📐 Scaling Patterns & Efficiency")
st.caption("Correlation analysis, zone distribution, and efficiency scoring of the autoscaler")

st.divider()

# ──────────────────────────────────────────────
# Row 1 — Efficiency Score Cards
# ──────────────────────────────────────────────
cpu_hist = state.history_cpu
inst_hist = state.history_instances

if len(cpu_hist) >= 5:
    optimal = sum(1 for c in cpu_hist if SCALE_IN_THRESHOLD <= c <= SCALE_OUT_THRESHOLD)
    overloaded = sum(1 for c in cpu_hist if c > SCALE_OUT_THRESHOLD)
    underloaded = sum(1 for c in cpu_hist if c < SCALE_IN_THRESHOLD)
    total = len(cpu_hist)

    efficiency_pct = round((optimal / total) * 100, 1)
    over_pct = round((overloaded / total) * 100, 1)
    under_pct = round((underloaded / total) * 100, 1)

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        color = "#22c55e" if efficiency_pct >= 70 else "#f59e0b" if efficiency_pct >= 40 else "#ef4444"
        st.markdown(f"""
        <div style="background:#1a1f2e;border:1px solid {color}44;border-top:3px solid {color};
            border-radius:10px;padding:18px;text-align:center">
            <div style="color:#94a3b8;font-size:0.75rem">EFFICIENCY SCORE</div>
            <div style="color:{color};font-size:2rem;font-weight:800">{efficiency_pct}%</div>
            <div style="color:#64748b;font-size:0.72rem">Time in optimal zone</div>
        </div>
        """, unsafe_allow_html=True)
    with e2:
        st.markdown(f"""
        <div style="background:#1a1f2e;border:1px solid rgba(239,68,68,0.3);border-top:3px solid #ef4444;
            border-radius:10px;padding:18px;text-align:center">
            <div style="color:#94a3b8;font-size:0.75rem">OVERLOADED</div>
            <div style="color:#ef4444;font-size:2rem;font-weight:800">{over_pct}%</div>
            <div style="color:#64748b;font-size:0.72rem">CPU &gt; {SCALE_OUT_THRESHOLD}%</div>
        </div>
        """, unsafe_allow_html=True)
    with e3:
        st.markdown(f"""
        <div style="background:#1a1f2e;border:1px solid rgba(59,130,246,0.3);border-top:3px solid #3b82f6;
            border-radius:10px;padding:18px;text-align:center">
            <div style="color:#94a3b8;font-size:0.75rem">UNDER-UTILIZED</div>
            <div style="color:#3b82f6;font-size:2rem;font-weight:800">{under_pct}%</div>
            <div style="color:#64748b;font-size:0.72rem">CPU &lt; {SCALE_IN_THRESHOLD}%</div>
        </div>
        """, unsafe_allow_html=True)
    with e4:
        avg_cpu = round(statistics.mean(cpu_hist), 1)
        st.markdown(f"""
        <div style="background:#1a1f2e;border:1px solid rgba(245,158,11,0.3);border-top:3px solid #f59e0b;
            border-radius:10px;padding:18px;text-align:center">
            <div style="color:#94a3b8;font-size:0.75rem">AVG CPU</div>
            <div style="color:#f59e0b;font-size:2rem;font-weight:800">{avg_cpu}%</div>
            <div style="color:#64748b;font-size:0.72rem">Across all ticks</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Generate load for a few seconds to see efficiency metrics.")

st.divider()

# ──────────────────────────────────────────────
# Row 2 — Zone Time Pie + Users vs Instances Scatter
# ──────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.markdown("### Time Spent in Each Zone")
    if len(cpu_hist) >= 5:
        fig_pie = go.Figure(go.Pie(
            labels=["Optimal (30–70%)", "Overloaded (>70%)", "Under-utilized (<30%)"],
            values=[optimal, overloaded, underloaded],
            hole=0.55,
            marker=dict(colors=["#22c55e", "#ef4444", "#3b82f6"]),
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} ticks (%{percent})<extra></extra>"
        ))
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            annotations=[dict(text=f"<b>{efficiency_pct}%</b><br>optimal", x=0.5, y=0.5,
                              font=dict(size=14, color="#22c55e"), showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Not enough data yet.")

with right:
    st.markdown("### Users vs Instances Correlation")
    st.caption("Each point = one recorded tick")
    if len(state.history_users) >= 5:
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=state.history_users,
            y=state.history_instances,
            mode='markers',
            name='Ticks',
            marker=dict(
                color=cpu_hist,
                colorscale=[[0, "#3b82f6"], [0.3, "#22c55e"], [0.7, "#f59e0b"], [1, "#ef4444"]],
                size=7,
                opacity=0.8,
                colorbar=dict(title="CPU %", thickness=12)
            ),
            hovertemplate="Users: %{x}<br>Instances: %{y}<br>CPU: %{marker.color:.1f}%<extra></extra>"
        ))
        fig_scatter.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=10, r=60, t=10, b=30),
            xaxis=dict(title="Active Users", gridcolor="#1e2433"),
            yaxis=dict(title="Instances", gridcolor="#1e2433", dtick=1),
            showlegend=False
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Not enough data yet.")

st.divider()

# ──────────────────────────────────────────────
# Row 3 — CPU Heatmap (zones over time)
# ──────────────────────────────────────────────
st.markdown("### CPU Zone Heatmap Over Time")
st.caption("Shows which zone the system was in at every recorded tick")

if len(cpu_hist) >= 10:
    # Classify each tick into a zone value: 1=underload, 2=optimal, 3=overload
    zone_values = []
    for c in cpu_hist:
        if c < SCALE_IN_THRESHOLD:
            zone_values.append(1)
        elif c <= SCALE_OUT_THRESHOLD:
            zone_values.append(2)
        else:
            zone_values.append(3)

    # Reshape into a 2D grid (10 columns wide) for visual heatmap
    cols_n = 20
    padded = zone_values + [0] * (cols_n - len(zone_values) % cols_n if len(zone_values) % cols_n != 0 else 0)
    rows_n = max(1, len(padded) // cols_n)
    grid = [padded[i * cols_n:(i + 1) * cols_n] for i in range(rows_n)]

    fig_heat = go.Figure(go.Heatmap(
        z=grid,
        colorscale=[
            [0, "#0f1420"],
            [0.01, "#0f1420"],
            [0.33, "#1e3a5f"],   # underload (1) → blue
            [0.66, "#14532d"],   # optimal (2) → green
            [1.0, "#7f1d1d"],    # overload (3) → red
        ],
        zmin=0, zmax=3,
        showscale=False,
        hovertemplate="Tick %{x} of row %{y}<br>Zone: %{z}<extra></extra>"
    ))
    fig_heat.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=160,
        margin=dict(l=10, r=10, t=10, b=20),
        xaxis=dict(title="Tick (within row)", showgrid=False),
        yaxis=dict(title="Row", showgrid=False, autorange="reversed")
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    hm1, hm2, hm3 = st.columns(3)
    with hm1:
        st.markdown('<span style="display:inline-block;width:14px;height:14px;background:#1e3a5f;border-radius:3px;vertical-align:middle"></span> <span style="color:#3b82f6;font-size:0.82rem">Under-utilized (CPU &lt;30%)</span>', unsafe_allow_html=True)
    with hm2:
        st.markdown('<span style="display:inline-block;width:14px;height:14px;background:#14532d;border-radius:3px;vertical-align:middle"></span> <span style="color:#22c55e;font-size:0.82rem">Optimal (30–70%)</span>', unsafe_allow_html=True)
    with hm3:
        st.markdown('<span style="display:inline-block;width:14px;height:14px;background:#7f1d1d;border-radius:3px;vertical-align:middle"></span> <span style="color:#ef4444;font-size:0.82rem">Overloaded (CPU &gt;70%)</span>', unsafe_allow_html=True)
else:
    st.info("Keep generating load to populate the heatmap (needs at least 10 ticks).")

st.divider()

# ──────────────────────────────────────────────
# Row 4 — Scale-Out vs Scale-In Rate Chart
# ──────────────────────────────────────────────
st.markdown("### Scale-Out vs Scale-In Rate")
st.caption("Cumulative count of scale events over time — shows the scaling cadence")

events = state.scaling_events
if len(events) >= 2:
    out_counts = []
    in_counts = []
    outs = 0
    ins = 0
    for e in events:
        if e["direction"] == "up":
            outs += 1
        else:
            ins += 1
        out_counts.append(outs)
        in_counts.append(ins)

    labels = [f"#{i+1}" for i in range(len(events))]

    fig_rate = go.Figure()
    fig_rate.add_trace(go.Scatter(
        x=labels, y=out_counts,
        mode='lines+markers',
        name='Scale Outs (cumulative)',
        line=dict(color='#ef4444', width=2),
        marker=dict(size=6)
    ))
    fig_rate.add_trace(go.Scatter(
        x=labels, y=in_counts,
        mode='lines+markers',
        name='Scale Ins (cumulative)',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6)
    ))
    fig_rate.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=280,
        margin=dict(l=10, r=10, t=10, b=20),
        yaxis=dict(title="Cumulative Count", gridcolor="#1e2433"),
        xaxis=dict(title="Event #", gridcolor="#1e2433"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig_rate, use_container_width=True)

    # Summary stats
    r1, r2, r3 = st.columns(3)
    with r1:
        ratio = round(outs / max(ins, 1), 2)
        st.metric("Scale-Out : Scale-In Ratio", f"{ratio}:1")
    with r2:
        net_change = outs - ins
        st.metric("Net Scaling Direction", f"+{net_change}" if net_change > 0 else str(net_change))
    with r3:
        st.metric("Total Scaling Events", len(events))
else:
    st.info("Not enough scaling events yet. Vary the load between low and high to trigger multiple events.")

st.markdown("---")
st.caption("CloudScale Platform • Scaling Patterns & Efficiency — updates on each page interaction")
