import sqlite3
import random

EPSILON = 0.15  # 15% exploration rate
ALPHA = 0.1     # Learning rate
WEIGHT_MIN = 0.1
WEIGHT_MAX = 5.0


def update_weight(db_path: str, user_id: int, app_id: int, reward: float):
    """
    Updates bandit weight using incremental mean (exponential smoothing).
    reward: +1.0 = read, -0.3 = dismissed, +0.5 = opened app
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT bandit_weight FROM Priority WHERE user_id=? AND app_id=?",
        (user_id, app_id),
    )
    row = cur.fetchone()
    if row:
        old_weight = row[0]
        new_weight = old_weight + ALPHA * (reward - old_weight)
        new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, new_weight))
        cur.execute(
            "UPDATE Priority SET bandit_weight=? WHERE user_id=? AND app_id=?",
            (new_weight, user_id, app_id),
        )
        conn.commit()
    conn.close()


def get_ranked_notifications(notifications: list, priorities: dict) -> list:
    """
    Rank notifications by score:
    Score = (1 / priority_order) * bandit_weight
    With EPSILON chance of random exploration.

    priorities: dict mapping app_id -> {priority_order, bandit_weight}
    """

    def score(notif):
        app_id = notif["app_id"]
        p = priorities.get(app_id, {})
        priority_order = p.get("priority_order", 99)
        bandit_weight = p.get("bandit_weight", 1.0)

        if random.random() < EPSILON:
            return random.random()  # exploration

        return (1.0 / max(priority_order, 1)) * bandit_weight

    return sorted(notifications, key=score, reverse=True)


def get_ranked_apps(db_path: str, user_id: int) -> list:
    """
    Returns apps sorted by (priority_order ASC, bandit_weight DESC).
    With EPSILON explore: occasionally shuffles top 3.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.app_id, p.priority_order, p.bandit_weight, a.app_name, a.app_emoji
        FROM Priority p
        JOIN Apps a ON a.app_id = p.app_id
        WHERE p.user_id = ? AND a.is_enabled = 1
        ORDER BY p.priority_order ASC, p.bandit_weight DESC
        """,
        (user_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    if random.random() < EPSILON and len(rows) > 2:
        top = rows[:3]  # type: ignore
        random.shuffle(top)
        rows = top + rows[3:]  # type: ignore

    return rows
