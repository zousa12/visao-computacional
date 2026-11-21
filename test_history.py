from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from PIL import Image
from answer_validation import AnswerFeedback
from history_store import HistoryEvent, HistoryStore, json_answer
from session_progress import SessionProgress


def sample_event(event_id="example"):
    return replace(HistoryEvent.create("run", "image", (8, 6), 1,
                   {"matrix": [[-1, 0], [0, -1]]}, "correct", "Acertou",
                   (4, 3), 1), event_id=event_id)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = self.enterContext(TemporaryDirectory())
        self.path = Path(self.directory) / "nested" / "history.sqlite3"
        self.store = HistoryStore(self.path)

    def test_save_metadata_and_new_connection(self):
        event = sample_event()
        self.store.save_events([event])
        row = HistoryStore(self.path).list_attempts()[0]
        for key, value in event.__dict__.items():
            self.assertEqual(row[key], value)
        self.assertEqual(json.loads(row["answer_json"])["matrix"][0][0], -1)

    def test_dedup_order_and_parameterized_filter(self):
        first = sample_event("first")
        second = replace(sample_event("second"), image_key="quote' OR 1=1 --")
        self.store.save_events([first, second, first])
        self.assertEqual(len(self.store.list_attempts()), 2)
        self.assertEqual(self.store.list_attempts(limit=1)[0]["event_id"], "second")
        self.assertEqual(len(self.store.list_attempts(second.image_key)), 1)
        self.assertEqual(self.store.list_attempts("unknown"), [])

    def test_batch_rolls_back_on_invalid_row(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.save_events([sample_event(), replace(sample_event("bad"), quadrant=9)])
        self.assertEqual(self.store.list_attempts(), [])

    def test_limits_and_nonfinite_answer(self):
        for limit in (0, 501, 1.2):
            with self.assertRaises(ValueError):
                self.store.list_attempts(limit=limit)
        self.assertEqual(json.loads(json_answer({"a": [float("nan"), float("inf")]})),
                         {"a": ["nan", "inf"]})

    def test_progress_emits_correct_incorrect_and_invalid_events(self):
        progress = SessionProgress("hash", (8, 6))
        image = Image.new("RGB", (4, 3))
        progress.record(1, image, AnswerFeedback(True, "ok"), {"a": 1})
        progress.record(1, image, AnswerFeedback(False, "retry"), {"a": 2})
        progress.record_error(2, "invalid", {"scale_x": 0})
        self.store.save_events(progress.pending_events)
        rows = list(reversed(self.store.list_attempts()))
        self.assertEqual([row["outcome"] for row in rows], ["correct", "incorrect", "invalid"])
        self.assertEqual([row["completed"] for row in rows], [1, 1, 1])
        self.assertEqual(len({row["event_id"] for row in rows}), 3)
        self.assertEqual(len({row["run_id"] for row in rows}), 1)

    def test_survives_process_restart(self):
        code = ("from history_store import HistoryStore; from test_history import sample_event; "
                "import sys; HistoryStore(sys.argv[1]).save_events([sample_event()])")
        subprocess.run([sys.executable, "-c", code, str(self.path)], check=True,
                       cwd=Path(__file__).parent, capture_output=True)
        code = ("from history_store import HistoryStore; import sys; "
                "assert HistoryStore(sys.argv[1]).list_attempts()[0]['event_id']=='example'")
        subprocess.run([sys.executable, "-c", code, str(self.path)], check=True,
                       cwd=Path(__file__).parent, capture_output=True)
