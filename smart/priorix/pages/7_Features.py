import streamlit as st
import sys, os, json, io, wave, struct, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import (
    init_db, get_user_priorities, get_features,
    save_features, ensure_user_priorities
)
from gemini_helper import configure_gemini

init_db()

st.set_page_config(page_title="Priorix — Features", page_icon="⚙️", layout="wide")

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
.stSelectbox > div > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 8px !important; }
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

# ── Load saved features ───────────────────────────────────────────────────────
existing = get_features(user_id)
saved_tones = {}
saved_reduce = False
saved_threshold = 5
if existing:
    try:
        saved_tones = json.loads(existing.get("custom_tones", "{}"))
    except Exception:
        saved_tones = {}
    saved_reduce = bool(existing.get("reduce_sound_enabled", 0))
    saved_threshold = int(existing.get("sound_reduction_threshold", 5))

priorities = get_user_priorities(user_id)
enabled_priorities = [p for p in priorities if p.get("is_enabled", 1)]

# ── Page ──────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style="background: linear-gradient(135deg,#7c3aed,#a78bfa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:2rem; font-weight:800;">
    ⚙️ Features
</h1>
<p style="color:#64748b; margin-top:-8px;">Customize tones, smart mute, and AI settings</p>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Audio Generator Setup ────────────────────────────────────────────────────
def generate_tone(tone_name):
    sample_rate = 44100
    def generate_wave(freq, duration, decay=False):
        num_samples = int(sample_rate * duration)
        data = []
        for i in range(num_samples):
            vol = 1.0 - (i / num_samples) if decay else 1.0
            val = int(vol * 20000.0 * math.sin(2 * math.pi * freq * i / sample_rate))
            data.append(struct.pack('<h', val))
        return b''.join(data)

    audio_data = b''
    if "Default" in tone_name:
        audio_data = generate_wave(440.0, 0.15, True) + generate_wave(440.0, 0.15, True)
    elif "Soft Chime" in tone_name:
        audio_data = generate_wave(523.25, 0.2, True) + generate_wave(659.25, 0.4, True)
    elif "Ping" in tone_name:
        audio_data = generate_wave(880.0, 0.15, True)
    else:
        return None

    out_file = io.BytesIO()
    with wave.open(out_file, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data)
        
    out_file.seek(0)
    return out_file.read()

# ── Feature 1: Notification Tones ────────────────────────────────────────────
st.markdown("### 🔔 Feature 1 — Custom Notification Tones")
st.markdown("<p style='color:#64748b; font-size:0.88rem;'>Set a unique sound for each app based on its priority.</p>", unsafe_allow_html=True)

TONE_OPTIONS = ["Default 🔔", "Soft Chime 🎵", "Ping 📍", "Silent 🔕", "Vibrate only 📳"]
TONE_DESCRIPTIONS = {
    "Default 🔔": "Standard notification sound from your device.",
    "Soft Chime 🎵": "A gentle, pleasant chime — great for low-priority apps.",
    "Ping 📍": "Short, sharp ping — ideal for important alerts.",
    "Silent 🔕": "No sound — notification appears silently.",
    "Vibrate only 📳": "Device vibrates without any audio alert.",
}

new_tones = {}
for p in enabled_priorities:
    app_name = p["app_name"]
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        st.markdown(f"""<div style="font-size:1.6rem; padding-top:22px;">{p['app_emoji']}</div>""",
                    unsafe_allow_html=True)
    with c2:
        sel = st.selectbox(
            f"{app_name}",
            TONE_OPTIONS,
            index=TONE_OPTIONS.index(saved_tones.get(app_name, "Default 🔔"))
                  if saved_tones.get(app_name, "Default 🔔") in TONE_OPTIONS else 0,
            key=f"tone_{app_name}",
        )
        new_tones[app_name] = sel
    with c3:
        if st.button("▶️", key=f"preview_{app_name}", help="Preview tone"):
            st.info(f"🎵 **{sel}** — {TONE_DESCRIPTIONS.get(sel, '')}")
            audio_bytes = generate_tone(sel)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav", autoplay=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Feature 2: Smart Sound Reduction ─────────────────────────────────────────
st.markdown("### 🔕 Feature 2 — Smart Sound Reduction")
st.markdown("<p style='color:#64748b; font-size:0.88rem;'>Automatically mute apps that spam too many notifications.</p>", unsafe_allow_html=True)

reduce_enabled = st.toggle("Enable Smart Sound Reduction", value=saved_reduce, key="reduce_toggle")

threshold = saved_threshold
if reduce_enabled:
    threshold = st.slider(
        "🔊 Mute after ___ notifications from same app in 1 hour",
        min_value=1, max_value=20, value=saved_threshold, key="threshold_slider",
    )
    st.markdown(f"""
    <div style="background: rgba(124,58,237,0.08); border: 1px solid rgba(124,58,237,0.2);
        border-radius: 10px; padding: 14px 18px; margin: 8px 0;">
        <p style="color:#a78bfa; font-size:0.87rem; margin:0;">
            💡 When any app sends more than <strong>{threshold}</strong> notifications per hour,
            its sound will automatically reduce to <strong>Silent</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── Save Button ───────────────────────────────────────────────────────────────
if st.button("💾  Save Features", use_container_width=True, key="save_features"):
    save_features(
        user_id,
        json.dumps(new_tones),
        int(reduce_enabled),
        int(threshold),
    )
    st.success("✅ Features saved!")
    st.toast("Features saved successfully!", icon="💾")

