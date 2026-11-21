"""Durable attempt metadata; images and file names never enter SQLite."""
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sqlite3
from uuid import uuid4


def json_answer(value):
    def clean(item):
        if isinstance(item, float) and not math.isfinite(item):
            return str(item)
        if isinstance(item, dict):
            return {key: clean(val) for key, val in item.items()}
        if isinstance(item, (list, tuple)):
            return [clean(val) for val in item]
        return item
    return json.dumps(clean(value), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class HistoryEvent:
    event_id: str
    run_id: str
    created_at: str
    image_key: str
    width: int
    height: int
    quadrant: int
    answer_json: str
    outcome: str
    feedback: str
    result_width: int | None
    result_height: int | None
    completed: int

    @classmethod
    def create(cls, run_id, image_key, size, quadrant, answer, outcome,
               feedback, result_size=None, completed=0):
        return cls(str(uuid4()), run_id, datetime.now(timezone.utc).isoformat(),
                   image_key, *size, quadrant, json_answer(answer), outcome,
                   feedback, *(result_size or (None, None)), completed)


class HistoryStore:
    def __init__(self, path=None):
        self.path = Path(path or os.environ.get("HISTORY_DB_PATH") or
                         Path(__file__).parent / "data" / "history.sqlite3")

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("""CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE, run_id TEXT NOT NULL,
                created_at TEXT NOT NULL, image_key TEXT NOT NULL,
                width INTEGER NOT NULL CHECK(width >= 2),
                height INTEGER NOT NULL CHECK(height >= 2),
                quadrant INTEGER NOT NULL CHECK(quadrant BETWEEN 1 AND 4),
                answer_json TEXT NOT NULL,
                outcome TEXT NOT NULL CHECK(outcome IN ('correct', 'incorrect', 'invalid')),
                feedback TEXT NOT NULL, result_width INTEGER, result_height INTEGER,
                completed INTEGER NOT NULL CHECK(completed BETWEEN 0 AND 4)
            )""")
            connection.execute("CREATE INDEX IF NOT EXISTS attempts_image ON attempts(image_key, id)")
            connection.commit()
            return connection
        except Exception:
            connection.close()
            raise

    def save_events(self, events):
        if not events:
            return
        columns = list(HistoryEvent.__dataclass_fields__)
        sql = ("INSERT INTO attempts (" + ",".join(columns) + ") VALUES (" +
               ",".join("?" for _ in columns) + ") ON CONFLICT(event_id) DO NOTHING")
        with closing(self.connect()) as connection, connection:
            connection.executemany(sql, [tuple(asdict(event).values()) for event in events])

    def list_attempts(self, image_key=None, limit=100):
        if not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("O limite deve estar entre 1 e 500.")
        with closing(self.connect()) as connection:
            if image_key is None:
                rows = connection.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT ?", (limit,))
            else:
                rows = connection.execute(
                    "SELECT * FROM attempts WHERE image_key = ? ORDER BY id DESC LIMIT ?",
                    (image_key, limit))
            return [dict(row) for row in rows]
