from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
HTML_PATH = PULSE / "index.html"
APP_PATH = PULSE / "app.js"


class ExerciseSearchAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text()
        cls.app = APP_PATH.read_text()

    def test_result_cards_are_not_a_noisy_live_region(self):
        grid = re.search(r'<div id="exerciseGrid"[^>]*>', self.html)
        self.assertIsNotNone(grid)
        self.assertNotIn("aria-live", grid.group())

    def test_dedicated_status_region_announces_only_the_summary(self):
        status = re.search(r'<span id="resultsAnnouncement"[^>]*></span>', self.html)
        self.assertIsNotNone(status)
        self.assertIn('class="sr-only"', status.group())
        self.assertIn('role="status"', status.group())
        self.assertIn('aria-live="polite"', status.group())
        self.assertIn('aria-atomic="true"', status.group())

    def test_summary_is_bilingual_zero_safe_and_debounced(self):
        self.assertIn("function announceExerciseResults(count)", self.app)
        self.assertIn("window.clearTimeout(exerciseResultsAnnouncementTimer)", self.app)
        self.assertIn("}, 350);", self.app)
        self.assertIn("count === 0 ? 'لا توجد تمارين مطابقة'", self.app)
        self.assertIn("count === 0 ? 'No matching exercises'", self.app)
        self.assertIn("announceExerciseResults(results.length)", self.app)

    def test_filter_input_still_updates_the_visible_count_and_cards(self):
        self.assertIn("const results = EXERCISES.filter(matches);", self.app)
        self.assertIn("$('resultsCount').textContent = String(results.length);", self.app)
        self.assertIn("$('exerciseSearch').addEventListener('input',renderExercises)", self.app)
        self.assertIn("results.map(item =>", self.app)


if __name__ == "__main__":
    unittest.main()
