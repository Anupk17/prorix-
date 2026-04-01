# 🚀 Prorix — Smart Multi-Platform Notification Prioritizer

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Expo](https://img.shields.io/badge/Expo-000020?style=flat&logo=expo&logoColor=white)](https://expo.dev/)
[![React Native](https://img.shields.io/badge/React_Native-61DAFB?style=flat&logo=react&logoColor=white)](https://reactnative.dev/)
[![Gemini AI](https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat&logo=google-gemini&logoColor=white)](https://ai.google.dev/)

**Prorix** (Priorix) is a comprehensive solution developed for the **KSSEM Hackathon**. It tackles the problem of notification fatigue by intelligently prioritizing, summarizing, and managing alerts across devices using Machine Learning and Generative AI.

---

## 🏗️ Project Architecture

The repository is structured into two core components:

1.  **📊 Priorix Backend & Analytics (Streamlit)**: A powerful dashboard for managing app priorities, viewing engagement analytics, and summarizing notifications using Google Gemini AI.
2.  **📱 Prorix Mobile (Expo/React Native)**: A cross-platform mobile application designed to interface with the prioritization engine and provide a seamless user experience.

---

## ✨ Key Features

### 🧠 Smart Prioritization (Priorix)
- **Epsilon-Greedy Bandit Engine**: An adaptive ML algorithm that learns your habits. It tracks "Read" vs "Dismissed" actions to automatically re-rank notifications from 7+ supported apps.
- **Manual Ranking Override**: Take control by assigning specific weights to critical apps.
- **AI-Powered Summarization**: Uses **Google Gemini 1.5 Flash** to condense hundreds of notifications into concise, actionable bullet points.

### 📉 Real-time Analytics
- Visualize notification distribution across apps.
- Track Bandit Engine engagement scores.
- Monitor read/dismiss rates with interactive Plotly charts.

### 📱 Mobile Experience
- Native interface for managing alerts on the go.
- Built-in permission toggles and custom alert tones.
- **Smart Sound Reduction**: Auto-mutes spammy apps based on hourly frequency thresholds.

---

## 🚀 Quick Start

### 1. Backend & Dashboard (Priorix)
```bash
# Navigate to the priorix directory
cd priorix

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

### 2. Mobile App (Expo)
```bash
# Navigate to the mobile directory
cd mobile

# Install dependencies
npm install

# Start the Expo development server
npx expo start
```

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend (Web)** | Streamlit (Python) |
| **Frontend (Mobile)** | React Native & Expo |
| **Generative AI** | Google Gemini 1.5 Flash |
| **ML Algorithm** | Epsilon-Greedy Multi-Armed Bandit |
| **Database** | SQLite |
| **Visualizations** | Plotly |

---

## 🏆 Hackathon Acknowledgements
This project was built for the **KSSEM Hackathon** to demonstrate the practical application of Reinforcement Learning (Bandit Algorithms) and Large Language Models (Gemini) in improving digital well-being.

---

## 📁 Repository Structure
```
.
├── priorix/             # Streamlit Dashboard & ML Logic
│   ├── app.py           # Main Dashboard Entry point
│   ├── bandit.py        # ML Engine
│   └── database.py      # Persistence Layer
├── mobile/              # Expo Mobile Application
│   ├── app/             # App Router components
│   └── components/      # UI Shared components
├── KSSEM Hackathon/     # (Duplicate) Archived Workspace
└── smart/               # (Duplicate) Archived Workspace
```

---

*Developed with ❤️ for KSSEM Hackathon.*
