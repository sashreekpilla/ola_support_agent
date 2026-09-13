import json
import sqlite3
from pathlib import Path
from app.config import SQLITE_PATH, DATA


def connect():
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    conn.execute("CREATE TABLE IF NOT EXISTS support_tickets(record_id TEXT PRIMARY KEY, category TEXT, status TEXT, resolution_time_hours INTEGER, days_since_created INTEGER, escalated INTEGER)")
    conn.commit(); conn.close()


def seed_from_json():
    path = DATA / "support_tickets.json"
    if not path.exists():
        return
    rows = json.loads(path.read_text(encoding="utf-8"))
    conn = connect()
    for r in rows:
        conn.execute("INSERT OR REPLACE INTO support_tickets VALUES (?, ?, ?, ?, ?, ?)", (r["record_id"], r["category"], r["status"], r["resolution_time_hours"], r["days_since_created"], int(r["escalated"])))
    conn.commit(); conn.close()


def get_ticket(record_id: str):
    conn = connect(); row = conn.execute("SELECT * FROM support_tickets WHERE record_id = ?", (record_id,)).fetchone(); conn.close()
    return dict(row) if row else None
