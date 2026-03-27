import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import (
    init_db, get_notifications, mark_read, mark_dismissed,
    ensure_user_priorities, get_user_priorities
)
from bandit import get_ranked_notifications
from mock_notifications import generate_mock_notifications

init_db()
generate_mock_notifications()

st.set_page_config(page_title="Priorix — Home", page_icon="🔔", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button { background: linear-gradient(135deg, #7c3aed, #4f46e5) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(124,58,237,0.35) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
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

# ── Header ────────────────────────────────────────────────────────────────────
user_name = st.session_state.get("user_name", "User")
initials = "".join([w[0].upper() for w in user_name.split()[:2]])

hcol1, hcol2 = st.columns([5, 1])
with hcol1:
    st.markdown("""
    <h1 style="font-size:1.8rem; font-weight:800; background: linear-gradient(135deg,#7c3aed,#a78bfa);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;">
        🔔 Priorix Feed
    </h1>
    """, unsafe_allow_html=True)
with hcol2:
    st.markdown(f"""
    <div style="width:42px; height:42px; border-radius:50%; background: linear-gradient(135deg,#7c3aed,#4f46e5);
        display:flex; align-items:center; justify-content:center; font-weight:700; font-size:15px;
        color:white; margin-top:6px;">{initials}</div>
    """, unsafe_allow_html=True)


st.markdown("---")

# ── Load notifs ───────────────────────────────────────────────────────────────
all_notifs = get_notifications(user_id)
priorities_raw = get_user_priorities(user_id)
priorities_map = {p["app_id"]: {"priority_order": p["priority_order"], "bandit_weight": p["bandit_weight"]}
                  for p in priorities_raw}

sorted_notifs = get_ranked_notifications(all_notifs, priorities_map)

# Group by app
from collections import defaultdict
grouped = defaultdict(list)
for n in sorted_notifs:
    grouped[n["app_name"]].append(n)

if not sorted_notifs:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:4rem;">🎉</div>
        <h3 style="color:#64748b;">All caught up!</h3>
        <p style="color:#475569;">No pending notifications. You're all clear.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render grouped notifications
    for app_name, notifs in grouped.items():
        if not notifs:
            continue
        sample = notifs[0]
        emoji = sample.get("app_emoji", "📱")
        priority = sample.get("priority_order", 99)
        border_color = "#ffd700" if priority == 1 else "#c0c0c0" if priority == 2 else "#cd7f32" if priority == 3 else "#7c3aed"

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin: 18px 0 8px 0;">
            <span style="font-size:1.5rem;">{emoji}</span>
            <span style="font-size:1.05rem; font-weight:700; color:#e2e8f0;">{app_name}</span>
            <span style="background:rgba(124,58,237,0.15); color:#a78bfa; border:1px solid rgba(124,58,237,0.3);
                padding:2px 8px; border-radius:12px; font-size:0.75rem;">
                Priority #{priority}
            </span>
            <span style="background:rgba(255,255,255,0.07); color:#64748b; padding:2px 8px;
                border-radius:12px; font-size:0.75rem;">{len(notifs)} notifications</span>
        </div>
        """, unsafe_allow_html=True)

        for notif in notifs:
            nid = notif["notif_id"]
            ts = notif.get("timestamp", "")[:16] if notif.get("timestamp") else ""

            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
                border-left: 4px solid {border_color}; border-radius: 12px; padding: 14px 18px; margin: 6px 0 2px 0;">
                <p style="color:#e2e8f0; font-size:0.9rem; margin:0 0 6px 0;">{notif['message']}</p>
                <span style="color:#475569; font-size:0.75rem;">🕐 {ts}</span>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
            with btn_col1:
                if st.button("✅ Read", key=f"read_{nid}"):
                    mark_read(nid, user_id)
                    st.toast(f"Marked as read!", icon="✅")
                    st.rerun()
            with btn_col2:
                if st.button("❌ Dismiss", key=f"dismiss_{nid}"):
                    mark_dismissed(nid, user_id)
                    st.toast(f"Dismissed.", icon="❌")
                    st.rerun()

        # Summarize button if 3+ notifications in this app group
        if len(notifs) >= 3:
            app_id = notifs[0]["app_id"]
            if st.button(f"🤖 Summarize {app_name} ({len(notifs)} notifications)", key=f"summarize_{app_id}"):
                st.session_state["summarize_app_id"] = app_id
                st.session_state["summarize_app_name"] = app_name
                st.switch_page("pages/5_AI_Summarizer.py")

        st.markdown("---")

# ── Bottom nav ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
nb1, nb2, nb3 = st.columns(3)
with nb1:
    st.markdown("<div style='text-align:center; color:#64748b; font-size:1.3rem;'>🔍<br><span style='font-size:0.7rem;'>Search</span></div>", unsafe_allow_html=True)
with nb2:
    st.markdown("<div style='text-align:center; color:#a78bfa; font-size:1.3rem;'>🏠<br><span style='font-size:0.7rem;'>Home</span></div>", unsafe_allow_html=True)
with nb3:
    if st.button("⚙️ Settings", use_container_width=True, key="nav_settings"):
        st.switch_page("pages/7_Features.py")

