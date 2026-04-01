import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "priorix.db")

SEED_APPS = [
    ("GPay", "💳"),
    ("WhatsApp", "💬"),
    ("Airtel", "📶"),
    ("Amazon", "📦"),
    ("YouTube", "▶️"),
    ("Zepto", "🛒"),
    ("Instagram", "📸"),
]


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email_id TEXT UNIQUE NOT NULL,
            ph_no TEXT,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Apps (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT UNIQUE NOT NULL,
            app_emoji TEXT,
            is_enabled INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS Priority (
            priority_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            app_id INTEGER,
            priority_order INTEGER,
            notifications_count INTEGER DEFAULT 0,
            bandit_weight REAL DEFAULT 1.0,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (app_id) REFERENCES Apps(app_id)
        );

        CREATE TABLE IF NOT EXISTS Notifications (
            notif_id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER,
            message TEXT,
            timestamp TEXT,
            is_read INTEGER DEFAULT 0,
            is_dismissed INTEGER DEFAULT 0,
            FOREIGN KEY (app_id) REFERENCES Apps(app_id)
        );

        CREATE TABLE IF NOT EXISTS AI_Summarizer (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            notif_id INTEGER,
            summary_text TEXT,
            created_at TEXT,
            FOREIGN KEY (notif_id) REFERENCES Notifications(notif_id)
        );

        CREATE TABLE IF NOT EXISTS Features (
            feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            custom_tones TEXT DEFAULT '{}',
            reduce_sound_enabled INTEGER DEFAULT 0,
            sound_reduction_threshold INTEGER DEFAULT 5,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
    """)

    # Seed apps if not already present
    for app_name, app_emoji in SEED_APPS:
        cur.execute(
            "INSERT OR IGNORE INTO Apps (app_name, app_emoji) VALUES (?, ?)",
            (app_name, app_emoji),
        )

    conn.commit()
    conn.close()


def register_user(name: str, email: str, ph_no: str, password: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Users (name, email_id, ph_no, password) VALUES (?, ?, ?, ?)",
            (name, email, ph_no, password),
        )
        conn.commit()
        user_id = cur.lastrowid
        # Set default priorities for all apps
        apps = get_apps()
        for i, app in enumerate(apps, start=1):
            cur.execute(
                "INSERT OR IGNORE INTO Priority (user_id, app_id, priority_order) VALUES (?, ?, ?)",
                (user_id, app["app_id"], i),
            )
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def login_user(email: str, password: str):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Users WHERE email_id=? AND password=?", (email, password)
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_apps():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Apps ORDER BY app_id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_priorities(user_id: int):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.*, a.app_name, a.app_emoji, a.is_enabled
        FROM Priority p
        JOIN Apps a ON p.app_id = a.app_id
        WHERE p.user_id = ?
        ORDER BY p.priority_order ASC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_priority(user_id: int, app_id: int, priority_order: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT priority_id FROM Priority WHERE user_id=? AND app_id=?",
        (user_id, app_id),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE Priority SET priority_order=? WHERE user_id=? AND app_id=?",
            (priority_order, user_id, app_id),
        )
    else:
        cur.execute(
            "INSERT INTO Priority (user_id, app_id, priority_order) VALUES (?, ?, ?)",
            (user_id, app_id, priority_order),
        )
    conn.commit()
    conn.close()


def ensure_user_priorities(user_id: int):
    """Ensure all apps have a priority row for this user."""
    conn = get_conn()
    cur = conn.cursor()
    apps = get_apps()
    cur.execute("SELECT app_id FROM Priority WHERE user_id=?", (user_id,))
    existing = {r[0] for r in cur.fetchall()}
    for i, app in enumerate(apps, start=1):
        if app["app_id"] not in existing:
            cur.execute(
                "INSERT OR IGNORE INTO Priority (user_id, app_id, priority_order) VALUES (?, ?, ?)",
                (user_id, app["app_id"], i),
            )
    conn.commit()
    conn.close()


def toggle_app(app_id: int, is_enabled: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Apps SET is_enabled=? WHERE app_id=?", (is_enabled, app_id))
    conn.commit()
    conn.close()


def get_notifications(user_id: int):
    """Returns unread, non-dismissed notifications ordered by user priority + bandit weight."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT n.*, a.app_name, a.app_emoji,
               COALESCE(p.priority_order, 99) AS priority_order,
               COALESCE(p.bandit_weight, 1.0) AS bandit_weight
        FROM Notifications n
        JOIN Apps a ON n.app_id = a.app_id
        LEFT JOIN Priority p ON p.app_id = n.app_id AND p.user_id = ?
        WHERE n.is_read = 0 AND n.is_dismissed = 0 AND a.is_enabled = 1
        ORDER BY priority_order ASC, bandit_weight DESC, n.notif_id ASC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_read(notif_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE Notifications SET is_read=1 WHERE notif_id=?", (notif_id,))
    # Get app_id for bandit update
    cur.execute("SELECT app_id FROM Notifications WHERE notif_id=?", (notif_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if row:
        from bandit import update_weight
        update_weight(DB_PATH, user_id, row[0], 1.0)


def mark_dismissed(notif_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Notifications SET is_dismissed=1 WHERE notif_id=?", (notif_id,)
    )
    cur.execute("SELECT app_id FROM Notifications WHERE notif_id=?", (notif_id,))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    if row:
        from bandit import update_weight
        update_weight(DB_PATH, user_id, row[0], -0.3)


def save_summary(notif_id: int, summary_text: str):
    conn = get_conn()
    cur = conn.cursor()
    created_at = datetime.now().isoformat()
    cur.execute(
        "INSERT INTO AI_Summarizer (notif_id, summary_text, created_at) VALUES (?, ?, ?)",
        (notif_id, summary_text, created_at),
    )
    conn.commit()
    conn.close()


def get_summary(notif_id: int):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM AI_Summarizer WHERE notif_id=? ORDER BY summary_id DESC LIMIT 1",
        (notif_id,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_app_summaries(app_id: int, summary_text: str):
    """Save a summary for all notifications of an app (use notif_id=app_id as sentinel -app_id)."""
    conn = get_conn()
    cur = conn.cursor()
    created_at = datetime.now().isoformat()
    # Use negative app_id as a sentinel for app-level summaries
    notif_id_sentinel = -app_id
    cur.execute(
        "DELETE FROM AI_Summarizer WHERE notif_id=?", (notif_id_sentinel,)
    )
    cur.execute(
        "INSERT INTO AI_Summarizer (notif_id, summary_text, created_at) VALUES (?, ?, ?)",
        (notif_id_sentinel, summary_text, created_at),
    )
    conn.commit()
    conn.close()


def get_app_summary(app_id: int):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    notif_id_sentinel = -app_id
    cur.execute(
        "SELECT * FROM AI_Summarizer WHERE notif_id=? ORDER BY summary_id DESC LIMIT 1",
        (notif_id_sentinel,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_features(user_id: int):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Features WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_features(
    user_id: int,
    custom_tones: str,
    reduce_sound_enabled: int,
    threshold: int,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO Features (user_id, custom_tones, reduce_sound_enabled, sound_reduction_threshold)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            custom_tones=excluded.custom_tones,
            reduce_sound_enabled=excluded.reduce_sound_enabled,
            sound_reduction_threshold=excluded.sound_reduction_threshold
        """,
        (user_id, custom_tones, reduce_sound_enabled, threshold),
    )
    conn.commit()
    conn.close()


def get_dashboard_data(user_id: int):
    """Returns per-app notification counts and bandit weights."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT a.app_name, a.app_emoji,
               COUNT(n.notif_id) AS total_notifs,
               SUM(n.is_read) AS read_count,
               SUM(n.is_dismissed) AS dismissed_count,
               COALESCE(p.priority_order, 99) AS priority_order,
               COALESCE(p.bandit_weight, 1.0) AS bandit_weight
        FROM Apps a
        LEFT JOIN Notifications n ON n.app_id = a.app_id
        LEFT JOIN Priority p ON p.app_id = a.app_id AND p.user_id = ?
        WHERE a.is_enabled = 1
        GROUP BY a.app_id
        ORDER BY priority_order ASC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_notifications_by_app(app_id: int):
    """Returns all notifications for an app (for AI summarization)."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Notifications WHERE app_id=? ORDER BY notif_id ASC",
        (app_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
