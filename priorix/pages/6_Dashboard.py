# pyright: basic
import streamlit as st  # type: ignore[import-untyped]
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import plotly.graph_objects as go  # type: ignore[import-untyped]
import plotly.express as px  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]

from database import init_db, get_dashboard_data, ensure_user_priorities  # type: ignore[import-not-found]

init_db()

st.set_page_config(page_title="Priorix — Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="metric-container"] { background: rgba(124,58,237,0.1) !important; border: 1px solid rgba(124,58,237,0.3) !important; border-radius: 12px !important; padding: 12px !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.switch_page("pages/1_Login.py")

user_id = st.session_state.user_id
ensure_user_priorities(user_id)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔔 PRIORIX")
    st.markdown("---")
    st.page_link("pages/4_Home.py", label="🏠 Home")
    st.page_link("pages/6_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/3_Ranking_Priority.py", label="🎯 Set Priority")
    st.page_link("pages/2_App_Permissions.py", label="📱 App Permissions")
    st.page_link("pages/5_AI_Summarizer.py", label="🤖 AI Summarizer")
    st.page_link("pages/7_Features.py", label="⚙️ Features")
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.get('user_name', 'User')}**")
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app.py")

# ── Page ──────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="background: linear-gradient(135deg,#7c3aed,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:2rem; font-weight:800;">
    📊 Dashboard Analytics
</h1>
<p style="color:#64748b; margin-top:-8px;">Your notification habits at a glance</p>
""", unsafe_allow_html=True)
st.markdown("---")

data = get_dashboard_data(user_id)
if not data:
    st.info("No data available yet. Start interacting with notifications in the Home feed!")
    st.stop()

df = pd.DataFrame(data)
df["label"] = df["app_emoji"] + " " + df["app_name"]
df["total_notifs"] = df["total_notifs"].fillna(0).astype(int)
df["read_count"] = df["read_count"].fillna(0).astype(int)
df["dismissed_count"] = df["dismissed_count"].fillna(0).astype(int)
df["unread_count"] = df["total_notifs"] - df["read_count"] - df["dismissed_count"]
df["unread_count"] = df["unread_count"].clip(lower=0)

total_notifs = int(df["total_notifs"].sum())
total_read = int(df["read_count"].sum())
total_dismissed = int(df["dismissed_count"].sum())
read_rate: float = (int(total_read * 1000 / total_notifs) / 10.0) if total_notifs > 0 else 0.0
most_active = str(df.loc[df["total_notifs"].idxmax(), "app_name"]) if total_notifs > 0 else "N/A"
avg_priority: float = int(float(df["priority_order"].mean()) * 10) / 10.0

# ── Stat cards ────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("📨 Total Notifications", total_notifs)
m2.metric("✅ Read Rate", f"{read_rate}%")
m3.metric("🏆 Most Active App", most_active)
m4.metric("⭐ Avg Priority Score", avg_priority)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Donut + Bar ────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

APP_COLORS: dict[str, str] = {
    "WhatsApp": "#22c55e",
    "Instagram": "#ec4899",
    "GPay": "#3b82f6",
    "YouTube": "#ef4444",
    "Amazon": "#f97316",
    "Zepto": "#a855f7",
    "Airtel": "#14b8a6",
}
colors = [APP_COLORS.get(str(r["app_name"]), "#7c3aed") for _, r in df.iterrows()]

with col1:
    fig_donut = go.Figure(go.Pie(
        labels=df["label"],
        values=df["total_notifs"],
        hole=0.55,
        marker={
            "colors": colors,
            "line": {"color": "#0f0f1a", "width": 2},
        },
        textinfo="label+percent",
        textfont={"color": "#e2e8f0", "size": 11},
        hovertemplate="<b>%{label}</b><br>%{value} notifications<extra></extra>",
    ))
    fig_donut.update_layout(
        title={"text": "Notification Distribution", "font": {"color": "#a78bfa", "size": 15}, "x": 0.5},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        legend={"font": {"color": "#94a3b8"}, "bgcolor": "rgba(0,0,0,0)"},
        annotations=[{
            "text": f"<b>{total_notifs}</b><br>total",
            "x": 0.5, "y": 0.5,
            "font_size": 14, "showarrow": False,
            "font": {"color": "#a78bfa"},
        }],
        margin={"t": 50, "b": 20, "l": 20, "r": 20},
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col2:
    df_sorted = df.sort_values("priority_order")
    fig_bar = go.Figure(go.Bar(
        x=df_sorted["label"],
        y=df_sorted["total_notifs"],
        marker={
            "color": df_sorted["priority_order"],
            "colorscale": [[0, "#7c3aed"], [0.5, "#4f46e5"], [1, "#06b6d4"]],
            "showscale": False,
        },
        text=df_sorted["total_notifs"],
        textposition="outside",
        textfont={"color": "#a78bfa"},
        hovertemplate="<b>%{x}</b><br>%{y} notifications<extra></extra>",
    ))
    fig_bar.update_layout(
        title={"text": "Priority vs Notification Volume", "font": {"color": "#a78bfa", "size": 15}, "x": 0.5},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
        xaxis={"gridcolor": "rgba(255,255,255,0.05)", "tickfont": {"size": 10}},
        yaxis={"gridcolor": "rgba(255,255,255,0.05)"},
        margin={"t": 50, "b": 20, "l": 20, "r": 20},
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Row 2: Bandit weights ─────────────────────────────────────────────────────
st.markdown("#### 🤖 Engagement Scores (Bandit Weights)")
df_w = df.sort_values("bandit_weight", ascending=False)

fig_weights = go.Figure()
fig_weights.add_trace(go.Bar(
    x=df_w["label"],
    y=df_w["bandit_weight"],
    marker={
        "color": df_w["bandit_weight"],
        "colorscale": [[0, "#1e1b4b"], [0.5, "#7c3aed"], [1, "#a78bfa"]],
        "showscale": True,
        "colorbar": {
            "title": "Weight",
            "tickfont": {"color": "#94a3b8"},
            "title_font": {"color": "#94a3b8"},
        },
    },
    text=[f"{w:.2f}" for w in df_w["bandit_weight"]],
    textposition="outside",
    textfont={"color": "#a78bfa"},
    hovertemplate="<b>%{x}</b><br>Bandit Weight: %{y:.3f}<extra></extra>",
))
fig_weights.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#e2e8f0"},
    xaxis={"gridcolor": "rgba(255,255,255,0.05)"},
    yaxis={"gridcolor": "rgba(255,255,255,0.05)", "title": "Engagement Weight"},
    margin={"t": 20, "b": 20, "l": 20, "r": 60},
)
st.plotly_chart(fig_weights, use_container_width=True)

# ── Read vs Dismissed breakdown ───────────────────────────────────────────────
st.markdown("#### 📋 Read vs Dismissed vs Unread")
fig_stack = go.Figure()
fig_stack.add_trace(go.Bar(name="✅ Read", x=df["label"], y=df["read_count"],
                            marker_color="#22c55e"))
fig_stack.add_trace(go.Bar(name="❌ Dismissed", x=df["label"], y=df["dismissed_count"],
                            marker_color="#ef4444"))
fig_stack.add_trace(go.Bar(name="📩 Unread", x=df["label"], y=df["unread_count"],
                            marker_color="#7c3aed"))
fig_stack.update_layout(
    barmode="stack",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#e2e8f0"},
    legend={"bgcolor": "rgba(0,0,0,0)", "font": {"color": "#94a3b8"}},
    xaxis={"gridcolor": "rgba(255,255,255,0.05)"},
    yaxis={"gridcolor": "rgba(255,255,255,0.05)"},
    margin={"t": 20, "b": 20, "l": 20, "r": 20},
)
st.plotly_chart(fig_stack, use_container_width=True)
