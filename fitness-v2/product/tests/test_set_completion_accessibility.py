from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "android/app/src/main/assets/pulse/app.js"


class SetCompletionAccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")

    def test_arabic_labels_describe_both_available_actions(self):
        self.assertIn("markSetComplete:'وضع علامة إكمال على المجموعة {set}'", self.app)
        self.assertIn("undoSetCompletion:'إلغاء إكمال المجموعة {set}'", self.app)

    def test_english_labels_describe_both_available_actions(self):
        self.assertIn("markSetComplete:'Mark set {set} complete'", self.app)
        self.assertIn("undoSetCompletion:'Undo completion for set {set}'", self.app)

    def test_button_label_tracks_the_action_and_set_number(self):
        self.assertIn(
            "t(set.complete?'undoSetCompletion':'markSetComplete').replace('{set}',String(index+1))",
            self.app,
        )
        self.assertNotIn('aria-label="${escapeHtml(t(\'completed\'))}"', self.app)

    def test_button_exposes_toggle_state_to_assistive_technology(self):
        self.assertIn('aria-pressed="${String(Boolean(set.complete))}"', self.app)

    def test_button_state_and_visible_glyph_use_the_same_completion_flag(self):
        self.assertIn("${set.complete?'✓':'○'}", self.app)
        self.assertIn('aria-pressed="${String(Boolean(set.complete))}"', self.app)


if __name__ == "__main__":
    unittest.main()
