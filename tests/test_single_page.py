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
        app.radio(key="curriculum_section").set_value(section).run()
        self.assert_no_error(app)
        self.assertTrue(any(header.value.startswith(f"{section}:") for header in app.header))

    def test_all_sections_and_simulation_actions(self):
        app = self.app()
        self.assertEqual(len(app.radio(key="curriculum_section").options), 7)
        for section in range(1, 8):
            with self.subTest(section=section):
                self.select(app, section)

        self.select(app, 4)
        app.slider(key="lesson_4_ts").set_value(5779.0).run()
        self.assert_no_error(app)
        self.assertEqual(app.slider(key="lesson_4_ts").value, 5779.0)
        app.slider(key="lesson_4_rp").set_value(2.0).run()
        self.assert_no_error(app)
        app.radio(key="lesson_4_component").set_value("行星").run()
        self.assert_no_error(app)

        self.assertTrue(any(h.value == "暗输出里的光子从哪里来" for h in app.header))
        self.assertTrue(any(h.value == "在当前条件下，能找到行星吗？" for h in app.header))
        seed = app.session_state["seed4"]
        app.button(key="action_4_resample").click().run()
        self.assert_no_error(app)
        self.assertEqual(app.session_state["seed4"], seed + 1)
        app.button(key="action_4_simulate").click().run()
        self.assert_no_error(app)
        self.assertTrue(any("/ 100" in metric.value for metric in app.metric))

        self.select(app, 5)
        self.assertFalse(any("不同位置，不同指纹" in h.value for h in app.header))
        self.select(app, 6)
        self.assertFalse(any(h.value == "暗输出里的光子从哪里来" for h in app.header))
        self.select(app, 7)
        seed = app.session_state['matched_seed']
        before = float(app.metric[0].value)
        app.slider(key='lesson_7_separation').set_value(115.).run()
        self.assert_no_error(app)
        self.assertEqual(app.session_state['matched_seed'], seed)
        self.assertGreater(float(app.metric[0].value), before)
        app.button(key='action_7_resample').click().run()
        self.assert_no_error(app)
        self.assertEqual(app.session_state['matched_seed'], seed+1)

    def test_controls_survive_navigation_without_leaking_between_chapters(self):
        app = self.app()
        self.select(app, 1)
        app.slider(key="lesson_1_dphi").set_value(180).run()
        self.assert_no_error(app)

        self.select(app, 2)
        app.slider(key="lesson_2_D").set_value(20.0).run()
        self.assert_no_error(app)
        self.select(app, 3)
        self.assertEqual(app.slider(key="lesson_3_amp").value, 1.0)
        app.slider(key="lesson_3_amp").set_value(1.1).run()
        self.assert_no_error(app)

        self.select(app, 1)
        self.assertEqual(app.slider(key="lesson_1_dphi").value, 180)
        self.assertTrue(any("相位差 **180°**" in text.value for text in app.markdown))
        self.select(app, 2)
        self.assertEqual(app.slider(key="lesson_2_D").value, 20.0)
        self.select(app, 3)
        self.assertEqual(app.slider(key="lesson_3_amp").value, 1.1)

    def test_original_entry_opens_the_same_single_page_app(self):
        app = self.app("首页.py")
        self.assertEqual(len(app.radio(key="curriculum_section").options), 7)
        self.select(app, 1)
        self.assertEqual(app.slider(key="lesson_1_dphi").value, 150)


if __name__ == "__main__":
    unittest.main()
