import importlib.util
from pathlib import Path
import unittest
from test_support import IsolatedHistoryTestCase


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q1InterfaceTests(IsolatedHistoryTestCase):
    def test_attempts_and_image_source_change(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 19)
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
class Q2InterfaceTests(IsolatedHistoryTestCase):
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


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q3InterfaceTests(IsolatedHistoryTestCase):
    def test_direct_composed_and_invalid_attempts_are_independent(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        app.button[2].click().run()
        self.assertEqual(len(app.warning), 1)
        self.assertEqual(len(app.success), 0)
        app.number_input(key="q3_direct_00").set_value(-1.0)
        app.button[2].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertIn("Q3", app.success[0].value)
        self.assertEqual(app.number_input[0].value, 1.0)
        self.assertEqual(app.number_input(key="q2_sx").value, 1.0)

        app.radio(key="q3_mode").set_value("Composição de duas matrizes").run()
        self.assertEqual(len(app.number_input), 23)
        app.number_input(key="q3_first_00").set_value(-1.0)
        app.number_input(key="q3_first_11").set_value(-1.0)
        app.button[2].click().run()
        self.assertEqual(len(app.success), 0)
        self.assertEqual(len(app.warning), 1)
        app.number_input(key="q3_second_11").set_value(-1.0)
        app.button[2].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertIn("Q3", app.success[0].value)

        app.number_input(key="q3_second_00").set_value(0.0)
        app.button[2].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.success), 0)

        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 0)
        self.assertEqual(len(app.error), 0)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class Q4InterfaceTests(IsolatedHistoryTestCase):
    def test_correct_wrong_and_singular_rgb_matrices(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        app.button[3].click().run()
        self.assertEqual(len(app.warning), 1)
        self.assertIn("Q4", app.warning[0].value)
        self.assertEqual(len(app.success), 0)

        inverse = ((1.5, -0.5, 0.0), (-0.5, 1.5, 0.0), (0.0, 0.0, 1.0))
        for row in range(3):
            for column in range(3):
                app.number_input(key=f"q4_{row}{column}").set_value(inverse[row][column])
        app.button[3].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertIn("Q4", app.success[0].value)
        self.assertEqual(app.number_input[0].value, 1.0)
        self.assertEqual(app.number_input(key="q2_sx").value, 1.0)
        self.assertEqual(app.number_input(key="q3_direct_00").value, 1.0)

        app.number_input(key="q4_22").set_value(0.0)
        app.button[3].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertEqual(len(app.success), 0)

        app.radio[0].set_value("Enviar PNG ou JPEG").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.number_input), 0)
        self.assertEqual(len(app.error), 0)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class FeedbackInterfaceTests(IsolatedHistoryTestCase):
    def test_contextual_guidance_and_extreme_values_do_not_crash(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        app.button[1].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("esperado", app.warning[0].value)

        app.number_input(key="q3_direct_00").set_value(-1.0)
        app.number_input(key="q3_direct_11").set_value(-1.0)
        app.button[2].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("isolada" in warning.value for warning in app.warning))

        app.button[3].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("diferença máxima" in warning.value for warning in app.warning))

        app.number_input[0].set_value(1e-308)
        app.number_input[3].set_value(1e-308)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 1)
        self.assertIn("Q1", app.error[0].value)

        app.number_input[0].set_value(-1.0)
        app.number_input[3].set_value(-1.0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertEqual(len(app.success), 1)


if __name__ == "__main__":
    unittest.main()
