from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"


class ActiveInstructionAccessibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_current_step_voice_label_is_bilingual_and_contextual(self):
        self.assertIn("readCurrentInstructionStep:'اقرأ الخطوة الحالية صوتيًا'", self.app)
        self.assertIn("readCurrentInstructionStep:'Read the current step aloud'", self.app)
        self.assertIn("speakCue.setAttribute('aria-label', steps.length", self.app)
        self.assertIn("state.lang === 'ar' ? '، ' : ', '", self.app)
        self.assertIn("t('instructionStepsUnavailable')", self.app)

    def test_current_cue_has_a_polite_atomic_live_region(self):
        self.assertIn(
            '<p id="activeInstructionAnnouncement" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></p>',
            self.html,
        )
        self.assertIn("const announcement = $('activeInstructionAnnouncement');", self.app)
        self.assertIn("`${stepStatus}. ${steps[activeInstructionIndex]}`", self.app)

    def test_live_region_updates_only_when_its_message_changes(self):
        self.assertIn("announcement.textContent !== announcementText", self.app)
        self.assertIn("announcement.textContent = announcementText", self.app)

    def test_current_step_is_escaped_in_visible_instruction_list(self):
        self.assertIn("`${stepStatus}. ${steps[activeInstructionIndex]}`", self.app)
        self.assertIn("escapeHtml(step)", self.app)

    def test_empty_step_list_has_a_truthful_accessible_label(self):
        self.assertIn(
            "? `${t('readCurrentInstructionStep')}${state.lang === 'ar' ? '، ' : ', '}${stepStatus}`",
            self.app,
        )
        self.assertIn(": t('instructionStepsUnavailable'));", self.app)


if __name__ == "__main__":
    unittest.main()
