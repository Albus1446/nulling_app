"""Exercise the single-page navigation and its chapter-specific widget state."""
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class SinglePageTests(unittest.TestCase):
    def app(self, entry="app.py"):
        app = AppTest.from_file(str(ROOT / entry), default_timeout=120).run()
        self.assert_no_error(app)
        return app

    def assert_no_error(self, app):
        self.assertEqual([error.message for error in app.exception], [])
        self.assertEqual([warning.value for warning in app.warning], [])

    def select(self, app, section):
        app.radio(key="selected_section").set_value(section).run()
        self.assert_no_error(app)
        self.assertTrue(any(header.value.startswith(f"{section}:") for header in app.header))

    def test_all_sections_and_simulation_actions(self):
        app = self.app()
        self.assertEqual(len(app.radio(key="selected_section").options), 9)
        for section in range(1, 9):
            with self.subTest(section=section):
                self.select(app, section)

        self.select(app, 4)
        app.toggle(key="lesson_4_ring").set_value(False).run()
        self.assert_no_error(app)
        self.assertTrue(app.slider(key="lesson_4_ring_r").disabled)

        self.select(app, 7)
        seed = app.session_state["seed7"]
        app.button(key="action_7_resample").click().run()
        self.assert_no_error(app)
        self.assertEqual(app.session_state["seed7"], seed + 1)
        app.button(key="action_7_simulate").click().run()
        self.assert_no_error(app)
        self.assertTrue(any("/ 100" in metric.value for metric in app.metric))

    def test_controls_survive_navigation_without_leaking_between_chapters(self):
        app = self.app()
        self.select(app, 1)
        app.slider(key="lesson_1_dphi").set_value(180).run()
        self.assert_no_error(app)

        self.select(app, 2)
        app.slider(key="lesson_2_b").set_value(20.0).run()
        self.assert_no_error(app)
        self.select(app, 3)
        self.assertEqual(app.slider(key="lesson_3_b3").value, 14.5)
        app.slider(key="lesson_3_b3").set_value(8.0).run()
        self.assert_no_error(app)

        self.select(app, 1)
        self.assertEqual(app.slider(key="lesson_1_dphi").value, 180)
        self.assertTrue(any("相位差 **180°**" in text.value for text in app.markdown))
        self.select(app, 2)
        self.assertEqual(app.slider(key="lesson_2_b").value, 20.0)
        self.select(app, 3)
        self.assertEqual(app.slider(key="lesson_3_b3").value, 8.0)

    def test_original_entry_opens_the_same_single_page_app(self):
        app = self.app("首页.py")
        self.assertEqual(len(app.radio(key="selected_section").options), 9)
        self.select(app, 1)
        self.assertEqual(app.slider(key="lesson_1_dphi").value, 150)


if __name__ == "__main__":
    unittest.main()
