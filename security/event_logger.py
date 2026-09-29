import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from config.settings import SETTINGS


class SecurityEventLogger:
    def __init__(self):
        self.db_path = Path(SETTINGS["DB_PATH"])
        self.connection: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        try:
            self.connection = sqlite3.connect(
                str(self.db_path), check_same_thread=False
            )
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    categories TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    alert_message TEXT NOT NULL,
                    raw_text_sample TEXT,
                    action_taken TEXT,
                    dismissed INTEGER DEFAULT 0
                )
                """
            )
            self.connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_ts ON security_events(timestamp)"
            )
            self.connection.commit()
            logger.info(f"Database ready: {self.db_path}")
        except Exception as e:
            logger.error(f"Database init error: {e}")

    def log_event(self, event) -> int:
        try:
            cur = self.connection.execute(
                """INSERT INTO security_events
                   (timestamp, severity, categories, confidence,
                    alert_message, raw_text_sample, action_taken)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    event.timestamp.isoformat(),
                    event.severity,
                    json.dumps(event.categories),
                    event.confidence,
                    event.alert_message,
                    (event.raw_text_sample or "")[:500],
                    event.auto_action_taken,
                ),
            )
            self.connection.commit()
            return cur.lastrowid
        except Exception as e:
            logger.error(f"Log event error: {e}")
            return -1

    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        try:
            cur = self.connection.execute(
                "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return []

    def get_statistics(self) -> Dict:
        try:
            total = self.connection.execute(
                "SELECT COUNT(*) FROM security_events"
            ).fetchone()[0]
            by_sev = {}
            for row in self.connection.execute(
                "SELECT severity, COUNT(*) FROM security_events GROUP BY severity"
            ):
                by_sev[row[0]] = row[1]
            return {"total": total, "by_severity": by_sev}
        except Exception:
            return {"total": 0, "by_severity": {}}

    def close(self):
        if self.connection:
            self.connection.close()
