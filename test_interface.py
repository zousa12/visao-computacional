import importlib.util
from pathlib import Path
import unittest


def descendants(node):
    yield node
    for child in getattr(node, "children", {}).values():
        yield from descendants(child)


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit não instalado")
class ChallengeLayoutTests(unittest.TestCase):
    def columns(self, app):
        rows = [
            node for node in app.main.children.values()
            if len(getattr(node, "children", {})) == 2
            and all(child.type == "column" for child in node.children.values())
        ]
        self.assertEqual(len(rows), 2, "A grade deve conter duas linhas com duas colunas.")
        return [column for row in rows for column in row.children.values()]

    def test_each_quadrant_contains_its_form_image_and_attempt_result(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
        self.assertEqual(len(app.exception), 0)
        for index, column in enumerate(self.columns(app)):
            nodes = list(descendants(column))
            titles = [n.value for n in nodes if n.type == "subheader"]
            self.assertEqual(len(titles), 1)
            self.assertTrue(titles[0].startswith(f"Q{index + 1}"))
            self.assertEqual(sum(n.type == "form" for n in nodes), 1)
            self.assertEqual(sum(n.type == "number_input" for n in nodes), (4, 2, 4, 9)[index])
            self.assertEqual(len(column.get("image")), 1)

        for target in range(4):
            if target == 0:
                app.number_input[0].set_value(-1.0)
                app.number_input[3].set_value(-1.0)
            elif target == 1:
                app.number_input(key="q2_sx").set_value(0.5)
                app.number_input(key="q2_sy").set_value(0.333333)
            elif target == 2:
                app.number_input(key="q3_direct_00").set_value(-1.0)
            else:
                inverse = ((1.5, -0.5, 0), (-0.5, 1.5, 0), (0, 0, 1))
                for row in range(3):
                    for column in range(3):
                        app.number_input(key=f"q4_{row}{column}").set_value(float(inverse[row][column]))
            app.button[target].click().run()
            self.assertEqual(len(app.exception), 0)
            for index, column in enumerate(self.columns(app)):
                nodes = list(descendants(column))
                self.assertEqual(sum(n.type == "success" for n in nodes), int(index == target))
                self.assertEqual(len(column.get("image")), 2 if index == target else 1)

    def test_q2_error_is_local_to_its_panel(self):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_string('''
from unittest.mock import patch
from challenge_ui import render_challenges
from image_input import example_image
with patch("challenge_ui.enlarged_q2", side_effect=ValueError("Use uma imagem menor.")):
    render_challenges(example_image())
''').run()
        self.assertEqual(len(app.exception), 0)
        columns = self.columns(app)
        for index, column in enumerate(columns):
            nodes = list(descendants(column))
            self.assertEqual(sum(n.type == "error" for n in nodes), int(index == 1))
            self.assertEqual(len(column.get("image")), 1)
        self.assertEqual(len(app.button), 3)
        app.number_input[0].set_value(-1.0)
        app.number_input[3].set_value(-1.0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.success), 1)
        self.assertEqual(len(app.error), 1)


if __name__ == "__main__":
    unittest.main()
