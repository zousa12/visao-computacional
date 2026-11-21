import importlib.util
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q1InterfaceTests(unittest.TestCase):
    def test_attempts_and_image_source_change(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 6)
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


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q2InterfaceTests(unittest.TestCase):
    def test_q2_attempts_validation_and_q1_regression(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("240 × 160" in item.value and "480 × 480" in item.value for item in app.markdown))
        app.button[1].click().run()
        self.assertEqual(len(app.warning), 1)
        app.number_input(key="q2_sx").set_value(0.5)
        app.number_input(key="q2_sy").set_value(0.333333)
        app.button[1].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertIn("Q2", app.success[0].value)

        for invalid in (0.0, -1.0, 1e9):
            app.number_input(key="q2_sx").set_value(invalid)
            app.button[1].click().run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.error), 1)
            self.assertEqual(len(app.success), 0)

        app.number_input[0].set_value(-1.0)
        app.number_input[3].set_value(-1.0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertIn("Q1", app.success[0].value)

        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 0)
        self.assertEqual(len(app.success), 0)


if __name__ == "__main__":
    unittest.main()
