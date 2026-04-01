import streamlit as st  # type: ignore[import-untyped,import-not-found]
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import init_db, register_user, login_user  # type: ignore[import-not-found]

init_db()

st.set_page_config(page_title="Priorix — Login", page_icon="🔔", layout="centered")

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important; color: #e2e8f0 !important; }
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; transition: all 0.3s ease !important;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important; border-right: 1px solid rgba(124,58,237,0.2) !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
.stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.05) !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
.stTabs [aria-selected="true"] { background: rgba(124,58,237,0.3) !important; color: #e2e8f0 !important; border-radius: 8px !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# Redirect if already logged in
if st.session_state.get("logged_in"):
    st.switch_page("pages/4_Home.py")

st.markdown("""
<div style="text-align:center; padding: 30px 0 10px 0;">
    <span style="font-size:2.5rem;">🔔</span>
    <h1 style="font-size:2rem; font-weight:800; background: linear-gradient(135deg,#7c3aed,#a78bfa,#60a5fa);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:4px 0;">PRIORIX</h1>
    <p style="color:#64748b; font-size:0.9rem;">Your notifications, your order.</p>
</div>
""", unsafe_allow_html=True)

login_tab, signup_tab = st.tabs(["🔑  Login", "✨  Sign Up"])

# ── Login Tab ─────────────────────────────────────────────────────────────────
with login_tab:
    st.markdown("<br>", unsafe_allow_html=True)
    email = st.text_input("Email Address", placeholder="you@example.com", key="li_email")
    password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔑  Login", use_container_width=True, key="btn_login"):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            user = login_user(email.strip(), password)
            if user:
                st.session_state.user_id = user["user_id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_email = user["email_id"]
                st.session_state.logged_in = True
                st.session_state.gemini_key = ""
                st.success(f"Welcome back, {user['name']}! 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid email or password. Please try again.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔵  Login with Google", use_container_width=True, key="btn_google"):
        with st.spinner("Authenticating with Google..."):
            import time
            time.sleep(1.2)
            # Mock Google Login for Hackathon
            email = "demo@google.com"
            user = login_user(email, "google_mock_pass")
            if not user:
                user_id = register_user("Google User", email, "", "google_mock_pass")
                user = {"user_id": user_id, "name": "Google User", "email_id": email}
            
            st.session_state.user_id = user["user_id"]
            st.session_state.user_name = user["name"]
            st.session_state.user_email = user["email_id"]
            st.session_state.logged_in = True
            st.session_state.gemini_key = ""
            st.success("✅ Logged in via Google!")
            time.sleep(0.5)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: rgba(124,58,237,0.08); border: 1px solid rgba(124,58,237,0.2);
        border-radius: 10px; padding: 14px; margin-top: 8px;">
        <p style="color:#94a3b8; font-size:0.82rem; margin:0;">
            <strong style="color:#a78bfa;">🔒 Priorix needs access to:</strong><br>
            📱 Notifications &nbsp;·&nbsp; 📞 Calls &nbsp;·&nbsp; 💬 SMS &nbsp;·&nbsp; 🖼️ Media
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Allow Access", use_container_width=True, key="btn_allow"):
            st.success("Access granted! Priorix will now prioritize your notifications.")
    with c2:
        if st.button("❌ Deny", use_container_width=True, key="btn_deny"):
            st.warning("Some features may not work without permissions.")

# ── Sign Up Tab ───────────────────────────────────────────────────────────────
with signup_tab:
    st.markdown("<br>", unsafe_allow_html=True)
    full_name = st.text_input("Full Name", placeholder="Navdeep Kabra", key="su_name")
    su_email = st.text_input("Email Address", placeholder="you@example.com", key="su_email")
    su_phone = st.text_input("Phone Number", placeholder="+91 98765 43210", key="su_phone")
    su_pass = st.text_input("Password", type="password", placeholder="Min 6 characters", key="su_pass")
    su_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="su_confirm")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀  Create Account", use_container_width=True, key="btn_signup"):
        if not all([full_name, su_email, su_phone, su_pass, su_confirm]):
            st.error("Please fill in all fields.")
        elif su_pass != su_confirm:
            st.error("❌ Passwords do not match.")
        elif len(su_pass) < 6:
            st.error("❌ Password must be at least 6 characters.")
        else:
            user_id = register_user(full_name.strip(), su_email.strip(), su_phone.strip(), su_pass)
            if user_id:
                st.session_state.user_id = user_id
                st.session_state.user_name = full_name.strip()
                st.session_state.user_email = su_email.strip()
                st.session_state.logged_in = True
                st.session_state.gemini_key = ""
                st.success(f"🎉 Account created! Welcome to Priorix, {full_name.split()[0]}!")
                st.rerun()
            else:
                st.error("❌ An account with this email already exists. Please login.")

    st.markdown("""
    <p style='color:#475569; font-size:0.78rem; text-align:center; margin-top:12px;'>
        By signing up, you agree to Priorix's Terms of Service and Privacy Policy.
    </p>
    """, unsafe_allow_html=True)

