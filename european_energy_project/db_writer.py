import sqlite3
import json
from datetime import datetime

DB_PATH = "energy.db"


def init_db():
    """Create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS energy_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature_c REAL,
            apparent_temperature_c REAL,
            wind_speed_kmh REAL,
            consumption_kw REAL,
            baseline_kw REAL,
            anomaly INTEGER DEFAULT 0,
            anomaly_reason TEXT,
            ingested_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            detail TEXT,
            logged_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_reading(reading: dict):
    """Insert a single energy reading into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO energy_readings
        (site, timestamp, temperature_c, apparent_temperature_c,
         wind_speed_kmh, consumption_kw, baseline_kw, anomaly, anomaly_reason, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reading.get("site"),
        reading.get("timestamp"),
        reading.get("temperature_c"),
        reading.get("apparent_temperature_c"),
        reading.get("wind_speed_kmh"),
        reading.get("consumption_kw"),
        reading.get("baseline_kw"),
        1 if reading.get("anomaly") else 0,
        reading.get("anomaly_reason"),
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()


def log_pipeline_event(event: str, detail: str = None):
    """Log a pipeline event for monitoring visibility."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO pipeline_logs (event, detail, logged_at)
        VALUES (?, ?, ?)
    """, (event, detail, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_recent_readings(hours: int = 24) -> list[dict]:
    """Fetch recent readings for dashboard and chatbot context."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM energy_readings
        ORDER BY ingested_at DESC
        LIMIT 500
    """)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_anomalies() -> list[dict]:
    """Fetch all flagged anomalies."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM energy_readings
        WHERE anomaly = 1
        ORDER BY ingested_at DESC
        LIMIT 100
    """)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_pipeline_logs() -> list[dict]:
    """Fetch recent pipeline logs for monitoring tab."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM pipeline_logs
        ORDER BY logged_at DESC
        LIMIT 50
    """)
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print(f"[DB] Initialised database at {DB_PATH}")
