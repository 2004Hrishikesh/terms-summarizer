"""SQLite storage for summary history."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

DB_PATH = os.environ.get("SUMMARIZER_DB", "summaries.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    model TEXT NOT NULL,
    original_words INTEGER NOT NULL,
    summary_words INTEGER NOT NULL,
    processing_time REAL NOT NULL,
    summary TEXT NOT NULL
)
"""


def _connect(db_path=None):
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    return conn


def save_summary(source, model, original_words, summary_words, processing_time, summary, db_path=None):
    """Insert one summary record and return its id."""
    with closing(_connect(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO summaries (created_at, source, model, original_words, summary_words, "
            "processing_time, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                source,
                model,
                original_words,
                summary_words,
                processing_time,
                summary,
            ),
        )
        return cur.lastrowid


def recent_summaries(limit=20, db_path=None):
    """Return the most recent summaries, newest first."""
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT * FROM summaries ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def usage_by_model(db_path=None):
    """Count summaries and average processing time for each model."""
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT model, COUNT(*) AS requests, ROUND(AVG(processing_time), 3) AS avg_seconds "
            "FROM summaries GROUP BY model ORDER BY requests DESC"
        ).fetchall()
    return [dict(row) for row in rows]
