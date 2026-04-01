import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, get_apps, toggle_app

init_db()

st.set_page_config(page_title="Priorix — App Permissions", page_icon="📱", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("Please login first.")
    st.switch_page("pages/1_Login.py")

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

# ── Page Content ──────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="background: linear-gradient(135deg,#7c3aed,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:2rem; font-weight:800;">
    📱 App Permissions
</h1>
<p style="color:#64748b; margin-top:-8px;">Choose which apps Priorix should track and compare.</p>
""", unsafe_allow_html=True)
st.markdown("---")

apps = get_apps()
toggle_changes = {}

cols = st.columns(2)
for i, app in enumerate(apps):
    col = cols[i % 2]
    with col:
        enabled = bool(app["is_enabled"])
        card_border = "rgba(124,58,237,0.5)" if enabled else "rgba(255,255,255,0.08)"
        badge_color = "#22c55e" if enabled else "#ef4444"
        badge_text = "Enabled" if enabled else "Disabled"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.04); border: 1px solid {card_border};
            border-radius: 14px; padding: 20px; margin: 8px 0;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <span style="font-size:2rem;">{app['app_emoji']}</span>
                    <span style="font-size:1.1rem; font-weight:600; color:#e2e8f0; margin-left:10px;">{app['app_name']}</span>
                </div>
                <span style="background:{badge_color}22; color:{badge_color}; border:1px solid {badge_color}44;
                    padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600;">{badge_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        new_val = st.toggle(
            f"Enable {app['app_name']}",
            value=enabled,
            key=f"toggle_{app['app_id']}",
            label_visibility="collapsed",
        )
        if new_val != enabled:
            toggle_changes[app["app_id"]] = int(new_val)

st.markdown("<br>", unsafe_allow_html=True)
if st.button("💾  Save Permissions", use_container_width=True, key="save_perms"):
    for app_id, val in toggle_changes.items():
        toggle_app(app_id, val)
    st.toast("✅ Permissions saved!", icon="✅")
    st.rerun()

st.markdown("""
<p style="color:#475569; font-size:0.83rem; text-align:center; margin-top:16px;">
    ⚠️ Only enabled apps will appear in your notification feed and priority ranking.
</p>
""", unsafe_allow_html=True)

