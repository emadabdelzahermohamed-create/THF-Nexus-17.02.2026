from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
APP_PATH = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "assets"
    / "pulse"
    / "app.js"
)


class MotionPreferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_PATH.read_text()

    def test_saved_motion_preference_wins_over_system_default(self):
        self.assertIn("store.getItem('pulse.v2.reduceMotion')", self.source)
        self.assertIn("if(saved!==null)return saved==='1';", self.source)
        self.assertIn("prefers-reduced-motion: reduce", self.source)

    def test_toggle_is_applied_persisted_and_restored_on_boot(self):
        self.assertIn("store.setItem('pulse.v2.reduceMotion',enabled?'1':'0')", self.source)
        self.assertIn("applyMotionPreference(event.target.checked)", self.source)
        self.assertIn("applyMotionPreference(preferredReducedMotion(),false)", self.source)


if __name__ == "__main__":
    unittest.main()
