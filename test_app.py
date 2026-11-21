import importlib.util
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q1InterfaceTests(unittest.TestCase):
    def test_attempts_and_image_source_change(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 4)
        app.button[0].click().run()
        self.assertEqual(len(app.warning), 1)
        self.assertEqual(len(app.success), 0)

        app.number_input[0].set_value(-1.0)
        app.number_input[3].set_value(-1.0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)

        app.number_input[0].set_value(0.0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.success), 0)

        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 0)
        self.assertEqual(len(app.error), 0)


if __name__ == "__main__":
    unittest.main()
