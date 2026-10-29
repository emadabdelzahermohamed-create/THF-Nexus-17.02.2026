from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"


class InstructionProgressbarAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_visual_track_is_a_named_determinate_progressbar(self):
        match = re.search(r'<div id="instructionProgressTrack"[^>]*>', self.html)
        self.assertIsNotNone(match, "instruction progress track must be exposed")
        tag = match.group(0)
        self.assertIn('role="progressbar"', tag)
        self.assertIn('data-i18n-aria-label="instructionProgress"', tag)
        self.assertIn('aria-valuemin="0"', tag)
        self.assertIn('aria-valuemax="100"', tag)
        self.assertIn('aria-valuenow="0"', tag)
        self.assertNotIn('aria-hidden="true"', tag)

    def test_runtime_updates_numeric_value_and_current_step_text(self):
        start = self.app.index("function instructionProgressPercent(index, total)")
        end = self.app.index("function renderActiveInstructionSteps", start)
        helper = self.app[start:end]
        self.assertIn("if (!count) return 0;", helper)
        self.assertIn("Math.round(((boundedInstructionIndex(index, count) + 1) / count) * 100)", helper)

        render_start = self.app.index("function renderActiveInstructionSteps")
        render_end = self.app.index("function moveActiveInstructionStep", render_start)
        render = self.app[render_start:render_end]
        self.assertIn("const progressTrack = $('instructionProgressTrack');", render)
        self.assertIn("progressTrack.setAttribute('aria-valuenow', String(progressPercent));", render)
        self.assertIn("progressTrack.setAttribute('aria-valuetext', stepStatus);", render)

    def test_progress_math_expected_boundaries(self):
        def progress(index, total):
            count = max(0, int(total or 0))
            if not count:
                return 0
            bounded = min(count - 1, max(0, int(index or 0)))
            return round(((bounded + 1) / count) * 100)

        self.assertEqual([33, 67, 100], [progress(i, 3) for i in range(3)])
        self.assertEqual(33, progress(-5, 3))
        self.assertEqual(100, progress(50, 3))
        self.assertEqual(0, progress(0, 0))

    def test_progressbar_name_remains_bilingual(self):
        self.assertIn("instructionProgress:'تقدم خطوات الأداء'", self.app)
        self.assertIn("instructionProgress:'Technique step progress'", self.app)
        self.assertIn('data-i18n-aria-label="instructionProgress"', self.html)

    def test_current_step_status_remains_separate_from_progressbar(self):
        self.assertIn('id="activeInstructionProgress" class="instruction-stepper-status" role="status"', self.html)
        self.assertIn("progressTrack.setAttribute('aria-valuetext', stepStatus);", self.app)


if __name__ == "__main__":
    unittest.main()
