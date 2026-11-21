import importlib.util
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch
from history_store import HistoryStore
from test_support import IsolatedHistoryTestCase


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit nao instalado")
class HistoryInterfaceTests(IsolatedHistoryTestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()

    def test_rerun_new_session_and_filter(self):
        app = self.app()
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(HistoryStore().list_attempts()), 1)
        app.run()
        self.assertEqual(len(HistoryStore().list_attempts()), 1)
        restarted = self.app()
        self.assertEqual(len(restarted.exception), 0)
        self.assertEqual(len(restarted.dataframe[0].value), 1)
        self.assertEqual(len(restarted.session_state["challenge_progress"].attempts), 0)
        restarted.selectbox(key="history_scope").set_value("Imagem atual").run()
        self.assertEqual(len(restarted.dataframe[0].value), 1)
        restarted.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(restarted.dataframe[0].value), 1)

    def test_failure_retry_survives_image_change(self):
        app = self.app()
        with patch("history_store.HistoryStore.save_events", side_effect=sqlite3.OperationalError("locked")):
            app.button[0].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.session_state["history_pending"]), 1)
            app.radio[0].set_value("Enviar PNG ou JPEG").run()
            self.assertEqual(len(app.session_state["history_pending"]), 1)
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.session_state["history_pending"]), 0)
        self.assertEqual(len(HistoryStore().list_attempts()), 1)
        app.run()
        self.assertEqual(len(HistoryStore().list_attempts()), 1)
