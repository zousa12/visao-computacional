from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from unittest.mock import patch


class IsolatedHistoryTestCase(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory())
        self.history_path = Path(directory) / "history.sqlite3"
        self.enterContext(patch.dict(os.environ, {"HISTORY_DB_PATH": str(self.history_path)}))
