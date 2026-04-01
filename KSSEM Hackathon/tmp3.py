import os, re

# 1. Update gemini_helper.py
gh = "gemini_helper.py"
gh_code = open(gh, "r", encoding="utf-8").read()
gh_code = gh_code.replace("""import google.generativeai as genai

_configured = False

def configure_gemini(api_key: str):
    global _configured
    genai.configure(api_key=api_key)
    _configured = True
""", """import google.generativeai as genai

# Hardcoded Google Gemini API Key
genai.configure(api_key="AIzaSyAD732IwQflfyAL0bPb5rBEzK03eXHRKm4")
""")
open(gh, "w", encoding="utf-8").write(gh_code)

# 2. Update pages/5_AI_Summarizer.py
s_py = "pages/5_AI_Summarizer.py"
s_code = open(s_py, "r", encoding="utf-8").read()
s_code = re.sub(r"# Gemini API key section.*?st\.markdown\(\"---\"\)\n", "", s_code, count=1, flags=re.DOTALL)
s_code = s_code.replace("from gemini_helper import configure_gemini, summarize_notifications", "from gemini_helper import summarize_notifications")
old_run = """if run_summary or regen:
    if not st.session_state.get("gemini_key"):
        st.warning("⚠️ Please enter your Gemini API key above to use AI Summarization.")
    else:
        with st.spinner("🤖 Gemini is thinking..."):
            try:
                configure_gemini(st.session_state.gemini_key)"""
new_run = """if run_summary or regen:
    with st.spinner("🤖 Gemini is thinking..."):
        try:"""
s_code = s_code.replace(old_run, new_run)
open(s_py, "w", encoding="utf-8").write(s_code)

# 3. Update pages/7_Features.py
f_py = "pages/7_Features.py"
f_code = open(f_py, "r", encoding="utf-8").read()
f_code = re.sub(r"# ── Feature 3: Gemini API Key ──.*?(?=# ── Save Button ──)", "", f_code, flags=re.DOTALL)
open(f_py, "w", encoding="utf-8").write(f_code)

# 4. Update pages/4_Home.py
h_py = "pages/4_Home.py"
h_code = open(h_py, "r", encoding="utf-8").read()
h_code = h_code.replace("hcol1, hcol2, hcol3 = st.columns([5, 1, 1])", "hcol1, hcol2 = st.columns([5, 1])")
h_code = re.sub(r"with hcol3:.*?unsafe_allow_html=True\)\n", "", h_code, flags=re.DOTALL)
h_code = re.sub(r"# Gemini key banner\nif not st\.session_state\.get\(\"gemini_key\"\):\n.*?st\.info[^\n]+\n", "", h_code, flags=re.DOTALL)
open(h_py, "w", encoding="utf-8").write(h_code)

# 5. Fix app.py to NOT hide native sidebar toggle
app_py = "app.py"
app_code = open(app_py, "r", encoding="utf-8").read()
app_code = app_code.replace('/* Hide default sidebar toggle on landing */\n[data-testid="collapsedControl"] { display: none; }', "")
open(app_py, "w", encoding="utf-8").write(app_code)
