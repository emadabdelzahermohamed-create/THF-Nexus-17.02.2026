from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
HTML_PATH = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "assets"
    / "pulse"
    / "index.html"
)


class WorkoutAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text()

    def test_set_progress_is_announced_and_labels_the_set_logger(self):
        progress = re.search(r'<h2 id="setProgressTitle"[^>]*>', self.html)
        self.assertIsNotNone(progress)
        self.assertIn('aria-live="polite"', progress.group())
        self.assertIn('aria-atomic="true"', progress.group())

        logger = re.search(r'<div id="setRows"[^>]*>', self.html)
        self.assertIsNotNone(logger)
        self.assertIn('role="region"', logger.group())
        self.assertIn('aria-labelledby="setProgressTitle"', logger.group())

    def test_rest_timer_has_a_stable_accessible_name(self):
        panel = re.search(r'<article id="restPanel"[^>]*>', self.html)
        self.assertIsNotNone(panel)
        self.assertIn('role="timer"', panel.group())
        self.assertIn('aria-labelledby="restLabel restTimer"', panel.group())
        self.assertIn('id="restLabel"', self.html)


if __name__ == "__main__":
    unittest.main()
