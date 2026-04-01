import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, get_apps, get_user_priorities, set_priority, ensure_user_priorities

init_db()

st.set_page_config(page_title="Priorix — Set Priority", page_icon="🎯", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stNumberInput > div > div > input { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; color: #e2e8f0 !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; color: #e2e8f0 !important; }
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

# ── Page Content ──────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="background: linear-gradient(135deg,#7c3aed,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:2rem; font-weight:800;">
    🎯 Set Notification Priority
</h1>
<p style="color:#64748b; margin-top:-8px;">Assign a rank to each app. Lower number = higher priority.</p>
""", unsafe_allow_html=True)
st.markdown("---")

priorities = get_user_priorities(user_id)
enabled_priorities = [p for p in priorities if p.get("is_enabled", 1)]

left, right = st.columns([3, 2])

with left:
    st.markdown("#### 🗂️ Set App Ranks")

    search = st.text_input("🔍 Search apps", placeholder="Type to filter...", key="search_apps")
    filtered = [p for p in enabled_priorities if search.lower() in p["app_name"].lower()] if search else enabled_priorities

    rank_inputs = {}
    for p in filtered:
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; padding: 8px 0;">
                <span style="font-size:1.5rem;">{p['app_emoji']}</span>
                <span style="font-size:1rem; font-weight:600; color:#e2e8f0;">{p['app_name']}</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            rank_inputs[p["app_id"]] = st.number_input(
                f"Rank for {p['app_name']}",
                min_value=1, max_value=10,
                value=int(p["priority_order"]),
                key=f"rank_{p['app_id']}",
                label_visibility="collapsed",
            )

    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("✅  Confirm Priorities", use_container_width=True, key="confirm"):
            for app_id, order in rank_inputs.items():
                set_priority(user_id, app_id, int(order))
            st.success("✅ Priority saved! Notifications will now appear in this order.")
            st.rerun()
    with bc2:
        if st.button("🔤  Sort A→Z", use_container_width=True, key="sort_az"):
            sorted_apps = sorted(enabled_priorities, key=lambda x: x["app_name"])
            for i, p in enumerate(sorted_apps, start=1):
                set_priority(user_id, p["app_id"], i)
            st.toast("Sorted A→Z!", icon="🔤")
            st.rerun()
    with bc3:
        if st.button("🔄  Reset Default", use_container_width=True, key="reset"):
            for i, p in enumerate(enabled_priorities, start=1):
                set_priority(user_id, p["app_id"], i)
            st.toast("Reset to default!", icon="🔄")
            st.rerun()

with right:
    st.markdown("#### 👁️ Priority Preview")

    # Sort by current rank_inputs values
    preview_items = sorted(enabled_priorities, key=lambda p: rank_inputs.get(p["app_id"], p["priority_order"]))
    rank_medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, p in enumerate(preview_items, start=1):
        medal = rank_medals.get(i, f"#{i}")
        border = "#ffd700" if i == 1 else "#c0c0c0" if i == 2 else "#cd7f32" if i == 3 else "#7c3aed"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
            border-left: 4px solid {border}; border-radius: 10px; padding: 12px 16px; margin: 6px 0;
            display:flex; align-items:center; gap:12px;">
            <span style="font-size:1.1rem; font-weight:700; color:{border}; min-width:28px;">{medal}</span>
            <span style="font-size:1.4rem;">{p['app_emoji']}</span>
            <span style="color:#e2e8f0; font-weight:600;">{p['app_name']}</span>
        </div>
        """, unsafe_allow_html=True)

