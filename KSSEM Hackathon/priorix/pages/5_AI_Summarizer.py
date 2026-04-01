import streamlit as st  # type: ignore[import-untyped,import-not-found]
import sys, os
from typing import Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import (  # type: ignore[import-not-found]
    init_db, get_apps, get_notifications_by_app,
    save_app_summaries, get_app_summary, ensure_user_priorities
)
from gemini_helper import summarize_notifications  # type: ignore[import-not-found]

init_db()

st.set_page_config(page_title="Priorix — AI Summarizer", page_icon="🤖", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; color: #e2e8f0 !important; }
.stSelectbox > div > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; color: #e2e8f0 !important; }
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
    🤖 AI Summarizer
</h1>
<p style="color:#64748b; margin-top:-8px;">Powered by Google Gemini · Condenses noise into clarity</p>
""", unsafe_allow_html=True)
st.markdown("---")


# App selector: only apps with 2+ notifications
all_apps = get_apps()
apps_with_notifs = []
for app in all_apps:
    notifs = get_notifications_by_app(app["app_id"])
    if len(notifs) >= 2:
        apps_with_notifs.append({**app, "notif_count": len(notifs), "notifs": notifs})

if not apps_with_notifs:
    st.warning("No apps have enough notifications to summarize yet.")
    st.stop()

# Pre-select from Home page if set
default_app_id = st.session_state.pop("summarize_app_id", None)
default_app_name = st.session_state.pop("summarize_app_name", None)
default_idx = 0
if default_app_id:
    for i, a in enumerate(apps_with_notifs):
        if a["app_id"] == default_app_id:
            default_idx = i
            break

app_labels = [f"{a['app_emoji']} {a['app_name']} ({a['notif_count']} notifications)" for a in apps_with_notifs]
selected_label = st.selectbox("📱 Select App to Summarize", app_labels, index=default_idx)
selected_idx = app_labels.index(selected_label)
selected_app: Any = apps_with_notifs[selected_idx]

st.markdown("<br>", unsafe_allow_html=True)

# Show notifications list
st.markdown(f"#### {selected_app['app_emoji']} {selected_app['app_name']} — Notifications")
notif_messages = [n["message"] for n in selected_app["notifs"]]  # type: ignore[union-attr]
for msg in notif_messages:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
        border-radius:8px; padding:10px 14px; margin:4px 0; color:#cbd5e1; font-size:0.88rem;">
        {msg}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Check cached summary
cached = get_app_summary(selected_app["app_id"])
if cached:
    st.markdown(f"""
    <div style="background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.3);
        border-radius: 14px; padding: 20px 24px; margin: 12px 0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <span style="font-size:1.4rem;">🤖</span>
            <span style="font-size:1rem; font-weight:700; color:#a78bfa;">
                AI Summary — {selected_app['app_name']}
            </span>
        </div>
        <div style="color:#e2e8f0; font-size:0.9rem; line-height:1.8; white-space:pre-wrap;">{cached['summary_text']}</div>
        <div style="color:#475569; font-size:0.75rem; margin-top:10px;">📅 Generated: {cached['created_at'][:16]}</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        regen = st.button("🔄 Regenerate", key="regen_btn")
else:
    regen = False

run_summary = st.button("✨  Summarize with Gemini", use_container_width=True, key="run_summary")

if run_summary or regen:
    with st.spinner("🤖 Gemini is thinking..."):
        try:
            summary = summarize_notifications(notif_messages, selected_app["app_name"])
            save_app_summaries(selected_app["app_id"], summary)
            st.markdown(f"""
            <div style="background: rgba(124,58,237,0.12); border: 1px solid rgba(124,58,237,0.4);
                border-radius: 14px; padding: 22px 26px; margin: 14px 0;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                    <span style="font-size:1.5rem;">🤖</span>
                    <span style="font-size:1.05rem; font-weight:700; color:#a78bfa;">
                        AI Summary — {selected_app['app_name']}
                    </span>
                </div>
                <div style="color:#e2e8f0; font-size:0.92rem; line-height:1.9; white-space:pre-wrap;">{summary}</div>
            </div>
            """, unsafe_allow_html=True)
            st.toast("Summary generated and saved!", icon="✨")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Gemini API error: {e}. Please check your API key and try again.")

