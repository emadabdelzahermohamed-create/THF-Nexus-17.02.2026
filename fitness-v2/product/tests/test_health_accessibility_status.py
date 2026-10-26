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


class HealthAccessibilityStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text()

    def test_health_connection_changes_are_announced_once(self):
        panel = re.search(r'<article class="surface health-connection"[^>]*>', self.html)
        self.assertIsNotNone(panel)
        self.assertIn('role="status"', panel.group())
        self.assertIn('aria-live="polite"', panel.group())
        self.assertIn('aria-atomic="true"', panel.group())

    def test_health_sync_errors_are_alerts(self):
        error = re.search(r'<p id="healthError"[^>]*>', self.html)
        self.assertIsNotNone(error)
        self.assertIn('role="alert"', error.group())
        self.assertIn('aria-atomic="true"', error.group())


if __name__ == "__main__":
    unittest.main()
