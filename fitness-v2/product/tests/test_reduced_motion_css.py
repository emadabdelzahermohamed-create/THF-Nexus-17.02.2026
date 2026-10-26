from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"


class ReducedMotionCssTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (PULSE / "styles.css").read_text(encoding="utf-8")
        cls.app = (PULSE / "app.js").read_text(encoding="utf-8")

    def test_saved_app_preference_controls_interface_transition_durations(self):
        self.assertIn("style.setProperty('--motion',enabled?'0':'1')", self.app)
        self.assertIn(':root[style*="--motion: 0"]', self.css)
        self.assertIn("animation-duration:.01ms!important", self.css)
        self.assertIn("transition-duration:.01ms!important", self.css)

    def test_saved_app_preference_removes_hover_and_press_displacement(self):
        self.assertIn(
            ':root[style*="--motion: 0"] .button:active', self.css
        )
        self.assertIn(
            ':root[style*="--motion: 0"] .exercise-card:hover img', self.css
        )
        self.assertIn(
            ':root[style*="--motion: 0"] .program-card:hover .program-cover img',
            self.css,
        )
        self.assertIn("transform:none!important", self.css)


if __name__ == "__main__":
    unittest.main()
