import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_PATH = PULSE / "app.js"
HTML_PATH = PULSE / "index.html"
CSS_PATH = PULSE / "styles.css"
EXERCISES_PATH = PULSE / "data" / "exercises.js"


def load_exercises():
    source = EXERCISES_PATH.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("exercise runtime payload wrapper is invalid")
    return json.loads(source[len(prefix):].strip().rstrip(";"))


class ActiveInstructionStepperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP_PATH.read_text(encoding="utf-8")
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.css = CSS_PATH.read_text(encoding="utf-8")
        cls.exercises = load_exercises()

    def test_stepper_controls_are_present_and_accessible(self):
        for element_id in (
            'id="activeInstructionProgress"',
            'id="instructionProgressFill"',
            'id="previousInstructionStep"',
            'id="nextInstructionStep"',
            'id="activeSteps"',
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(element_id, self.html)
        self.assertIn('role="status" aria-live="polite" aria-atomic="true"', self.html)
        self.assertIn('data-i18n-aria-label="instructionProgress"', self.html)
        self.assertIn('type="button"', self.html)

    def test_step_progress_and_controls_are_localized_in_both_languages(self):
        for phrase in (
            "instructionProgress:'تقدم خطوات الأداء'",
            "instructionStepOf:'الخطوة {current} من {total}'",
            "previousInstructionStep:'الخطوة السابقة'",
            "nextInstructionStep:'الخطوة التالية'",
            "instructionStepsUnavailable:'لا تتوفر خطوات موثقة لهذا التمرين.'",
            "instructionProgress:'Technique step progress'",
            "instructionStepOf:'Step {current} of {total}'",
            "previousInstructionStep:'Previous step'",
            "nextInstructionStep:'Next step'",
            "instructionStepsUnavailable:'No documented steps are available for this exercise.'",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.app)

    def test_navigation_is_clamped_and_progress_controls_follow_current_index(self):
        start = self.app.index("function boundedInstructionIndex(index, total)")
        end = self.app.index("function renderActiveInstructionSteps", start)
        bounded = self.app[start:end]
        self.assertIn("Math.max(0, Number(total) || 0)", bounded)
        self.assertIn("Math.min(count - 1, Math.max(0, Number(index) || 0))", bounded)

        render_start = self.app.index("function renderActiveInstructionSteps")
        render_end = self.app.index("function moveActiveInstructionStep", render_start)
        render = self.app[render_start:render_end]
        self.assertIn("activeInstructionIndex = boundedInstructionIndex(activeInstructionIndex, steps.length)", render)
        self.assertIn("aria-current=\"step\"", render)
        self.assertIn("instructionProgressFill", render)
        self.assertIn("previous.disabled = !steps.length || activeInstructionIndex <= 0", render)
        self.assertIn("next.disabled = !steps.length || activeInstructionIndex >= steps.length - 1", render)

        move_start = self.app.index("function moveActiveInstructionStep(delta)")
        move_end = self.app.index("function renderActiveWorkout()", move_start)
        move = self.app[move_start:move_end]
        self.assertIn("activeInstructionIndex + delta", move)
        self.assertIn("boundedInstructionIndex(activeInstructionIndex + delta, steps.length)", move)
        self.assertIn("renderActiveInstructionSteps(item)", move)

    def test_index_resets_on_session_or_exercise_change_but_language_rerender_keeps_it(self):
        self.assertIn("let activeInstructionIndex = 0;", self.app)
        self.assertIn("let activeInstructionSessionKey = null;", self.app)
        self.assertIn("state.active?.clientRecordId || state.active?.startedAt", self.app)
        self.assertIn("if (activeInstructionSessionKey !== instructionSessionKey)", self.app)
        self.assertIn("activeInstructionIndex = 0;", self.app)
        language_start = self.app.index("function applyLanguage()")
        language_end = self.app.index("\n  function ", language_start + 1)
        self.assertIn("if (state.active) renderActiveWorkout();", self.app[language_start:language_end])

    def test_current_step_highlight_respects_reduced_motion(self):
        self.assertIn('.technique-card #activeSteps li[aria-current="step"]', self.css)
        self.assertIn(".motion-reduced #instructionProgressFill{transition:none!important}", self.css)
        self.assertIn("@media(prefers-reduced-motion:reduce){#instructionProgressFill{transition:none!important}}", self.css)

    def test_all_catalog_steps_remain_nonblank_and_bilingual(self):
        ids = [item["id"] for item in self.exercises]
        self.assertEqual(112, len(self.exercises))
        self.assertEqual(112, len(set(ids)))
        for item in self.exercises:
            with self.subTest(exercise_id=item["id"]):
                en = item["steps"]["en"]
                ar = item["steps"]["ar"]
                self.assertTrue(en and ar)
                self.assertEqual(len(en), len(ar))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in en))
                self.assertTrue(all(isinstance(step, str) and step.strip() for step in ar))


if __name__ == "__main__":
    unittest.main()
