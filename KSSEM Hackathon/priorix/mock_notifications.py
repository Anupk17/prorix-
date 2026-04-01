from datetime import datetime, timedelta
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "priorix.db")

MOCK_NOTIFICATIONS = {
    "GPay": [
        "💳 Payment of ₹1,200 received from Rahul Kumar. UPI Ref: 4521897630.",
        "🎉 Cashback of ₹50 credited! Your GPay balance is now ₹342.",
        "⚠️ Security alert: New login detected from Chrome on Windows.",
        "💸 Send money to 5 friends and earn ₹100 cashback. Offer ends tonight!",
    ],
    "WhatsApp": [
        "📩 Priya: Hey, are you coming to the party tonight?",
        "👥 Study Group: 14 new messages",
        "📞 Missed call from Mom",
        "🔔 You have been added to 'Project Alpha - Team Chat'",
    ],
    "Airtel": [
        "📶 Your data balance is low: 0.3 GB remaining.",
        "💰 Recharge ₹299 and get 2GB/day for 28 days. Tap to recharge.",
        "✅ Recharge of ₹149 successful. Validity: 28 days.",
    ],
    "Amazon": [
        "📦 Your order #408-1234567 has been shipped. Expected: Tomorrow.",
        "⭐ Rate your recent purchase: Boat Airdopes 141.",
        "🛒 Deal of the Day: 60% off on Electronics. Shop now!",
        "🎁 Your wishlist item 'Sony WH-1000XM5' is now 15% off!",
    ],
    "YouTube": [
        "▶️ Fireship just uploaded: '10 AI tools that will replace you in 2025'",
        "🔴 Tech With Tim is LIVE now: Python Full Course",
        "👍 Your comment got 42 likes on Linus Tech Tips.",
    ],
    "Zepto": [
        "🛒 Your Zepto order is out for delivery! Arriving in 8 minutes.",
        "🥦 Fresh vegetables restocked in your area. Order now!",
        "💸 Use code ZEPTO50 for ₹50 off on your next order above ₹199.",
    ],
    "Instagram": [
        "❤️ @tech_guru liked your photo.",
        "💬 @priya_s commented: 'Wow amazing shot!'",
        "👤 3 new followers: @design_daily, @codelife, @bengaluru_eats",
        "🔥 Your reel got 1,200 views in the last hour!",
    ],
}


from typing import Optional
def generate_mock_notifications(db_path: Optional[str] = None):
    """Insert mock notifications into the Notifications table if it is empty."""
    if db_path is None:
        db_path = DB_PATH

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Notifications")
    count = cur.fetchone()[0]
    if count > 0:
        conn.close()
        return  # Already seeded

    # Fetch app name → app_id mapping
    cur.execute("SELECT app_id, app_name FROM Apps")
    app_map = {row["app_name"]: row["app_id"] for row in cur.fetchall()}

    base_time = datetime.now() - timedelta(hours=3)
    inserted: int = 0
    for app_name, messages in MOCK_NOTIFICATIONS.items():
        app_id = app_map.get(app_name)
        if app_id is None:
            continue
        for i, msg in enumerate(messages):
            ts = (base_time + timedelta(minutes=inserted * 7)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            cur.execute(
                "INSERT INTO Notifications (app_id, message, timestamp) VALUES (?, ?, ?)",
                (app_id, msg, ts),
            )
            inserted += 1

    conn.commit()
    conn.close()
