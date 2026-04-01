import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import init_db
from mock_notifications import generate_mock_notifications

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
generate_mock_notifications()

st.set_page_config(
    page_title="Priorix — Smart Notification Prioritizer",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important;
    color: #e2e8f0 !important;
    min-height: 100vh;
}



/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(124,58,237,0.1) !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important;
}
.stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
.stTabs [aria-selected="true"] {
    background: rgba(124,58,237,0.3) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* Notification card helpers */
.notif-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    transition: all 0.2s ease;
}
.notif-card:hover { background: rgba(255,255,255,0.07); }
.priority-1 { border-left: 4px solid #ffd700 !important; }
.priority-2 { border-left: 4px solid #c0c0c0 !important; }
.priority-3 { border-left: 4px solid #cd7f32 !important; }
.priority-other { border-left: 4px solid #7c3aed !important; }

/* Divider */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Success / info / warning override */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Landing Page ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 60px 20px 30px 20px;">
    <div style="font-size: 80px; margin-bottom: 10px; animation: pulse 2s infinite;">🔔</div>
    <h1 style="font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, #7c3aed, #a78bfa, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">
        PRIORIX
    </h1>
    <p style="font-size: 1.3rem; color: #94a3b8; margin-top: 10px; font-style: italic;">
        Your notifications, your order.
    </p>
</div>

<style>
[data-testid="stSidebarNav"] { display: none !important; }
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}
</style>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)
cards = [
    ("🎯", "Smart Ranking", "Set custom priorities for each app. Your most important notifications always come first."),
    ("🤖", "AI Summarizer", "Google Gemini condenses dozens of noisy alerts into 2-3 crisp, actionable bullet points."),
    ("📊", "Insights Dashboard", "Visual analytics on your notification habits — read rates, engagement scores, and more."),
]
for col, (emoji, title, desc) in zip([col1, col2, col3], cards):
    col.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px; padding: 28px 22px; text-align: center; height: 200px;
        transition: all 0.3s ease; cursor:default;">
        <div style="font-size:40px; margin-bottom:12px;">{emoji}</div>
        <h3 style="color:#e2e8f0; font-size:1.1rem; font-weight:700; margin-bottom:8px;">{title}</h3>
        <p style="color:#64748b; font-size:0.87rem; line-height:1.5;">{desc}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# CTA buttons
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("🚀  Get Started  →", use_container_width=True, key="get_started"):
        st.switch_page("pages/1_Login.py")
    st.markdown("""
    <p style="text-align:center; color:#64748b; font-size:0.85rem; margin-top:12px;">
        Already have an account?
        <a href="/1_Login" target="_self" style="color:#7c3aed; text-decoration:none; font-weight:600;">
            Login here
        </a>
    </p>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# Stats row
s1, s2, s3, s4 = st.columns(4)
for col, (val, label) in zip(
    [s1, s2, s3, s4],
    [("7", "Apps Supported"), ("100%", "Privacy First"), ("∞", "Notifications Ranked"), ("Free", "Gemini AI Tier")],
):
    col.markdown(f"""
    <div style="background: rgba(124,58,237,0.08); border: 1px solid rgba(124,58,237,0.2);
        border-radius: 12px; padding: 20px; text-align:center;">
        <div style="font-size:1.8rem; font-weight:800; color:#a78bfa;">{val}</div>
        <div style="font-size:0.8rem; color:#64748b;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<p style="text-align:center; color:#374151; font-size:0.75rem; margin-top:50px;">
    © 2026 Priorix · Built for Hackathon Demo · By using this app you agree to our Terms &amp; Conditions
</p>
""", unsafe_allow_html=True)

