# 🔔 Priorix — Smart Notification Prioritizer

> *Your notifications, your order.*

Priorix is a hackathon-ready Streamlit app that lets you rank which apps' notifications appear first, adaptively re-ranks them using a Multi-Armed Bandit ML engine based on your interactions, and summarizes noisy notification bundles using Google Gemini AI.

---

## ✨ Features

- 🎯 **Smart Manual Ranking** — Assign priority ranks to any of 7 supported apps
- 🤖 **Epsilon-Greedy Bandit Engine** — Automatically learns your engagement patterns and adjusts ranking weights over time
- 🧠 **AI Summarizer** — Powered by Google Gemini 1.5 Flash; condenses many notifications into 2–3 bullet points
- 📊 **Analytics Dashboard** — 4 Plotly charts showing notification distribution, priority vs volume, bandit engagement scores, and read/dismiss rates
- 📱 **App Permissions** — Toggle which apps are tracked
- 🔕 **Smart Sound Reduction** — Auto-mutes apps that send too many notifications in an hour
- 🎵 **Custom Tones per App** — Assign different alert sounds by priority

---

## 🚀 Setup Instructions

```bash
# 1. Clone the repository
git clone <repo-url>
cd priorix

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The SQLite database (`priorix.db`) and mock notifications are auto-created on first run.

---

## 🤖 Gemini AI Setup

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** → copy your key
4. In Priorix, go to **⚙️ Features** or **🤖 AI Summarizer**
5. Paste your key in the "Gemini API Key" field

> The key is stored only in your session — never persisted to disk.

---

## 📁 Project Structure

```
priorix/
├── app.py                  # Landing page + global CSS
├── priorix.db              # SQLite DB (auto-created)
├── database.py             # All DB init and CRUD functions
├── bandit.py               # Epsilon-Greedy Multi-Armed Bandit engine
├── gemini_helper.py        # Google Gemini API wrapper
├── mock_notifications.py   # Mock data seeder (7 apps, 24 notifications)
├── requirements.txt
├── README.md
└── pages/
    ├── 1_Login.py          # Login + Sign Up (two tabs)
    ├── 2_App_Permissions.py # Toggle which apps to track
    ├── 3_Ranking_Priority.py# Set numeric ranks + live preview
    ├── 4_Home.py           # Main notification feed (CORE)
    ├── 5_AI_Summarizer.py  # Gemini-powered summarization
    ├── 6_Dashboard.py      # Plotly analytics dashboard
    └── 7_Features.py       # Tones, smart mute, Gemini key
```

---

## 🧠 How the Bandit Algorithm Works

Priorix uses an **Epsilon-Greedy Multi-Armed Bandit** to learn which apps you engage with most:

| Event | Reward Signal |
|-------|--------------|
| ✅ User reads a notification | +1.0 |
| ❌ User dismisses without reading | −0.3 |

The weight for each app is updated using **exponential smoothing**:

```
new_weight = old_weight + α × (reward − old_weight)
```
Where `α = 0.1` (learning rate). Weights are clamped between 0.1 and 5.0.

With **15% probability (ε = 0.15)**, the ranking is shuffled for exploration — preventing the algorithm from getting stuck on early preferences.

---

## 📊 Supported Apps

| App | Emoji |
|-----|-------|
| GPay | 💳 |
| WhatsApp | 💬 |
| Airtel | 📶 |
| Amazon | 📦 |
| YouTube | ▶️ |
| Zepto | 🛒 |
| Instagram | 📸 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI / Frontend | Python + Streamlit |
| Backend Logic | Python (in-process) |
| Database | SQLite (`priorix.db`) |
| AI Summarization | Google Gemini 1.5 Flash |
| ML Engine | Epsilon-Greedy Multi-Armed Bandit |
| Charts | Plotly |

---

## 🏆 Hackathon Context

Built for a hackathon demo showcasing real-world ML (bandit algorithms), generative AI (Gemini), and practical UX (notification prioritization). Fully local — no external servers needed.

---

## 📸 Screenshots

> *(Add screenshots of Landing Page, Home Feed, Dashboard, and AI Summarizer here)*
