import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP_JS = PULSE / "app.js"
STYLES = PULSE / "styles.css"
PROGRAMS_JS = PULSE / "data" / "programs.js"


def load_programs():
    source = PROGRAMS_JS.read_text(encoding="utf-8")
    payload = source.partition("=")[2].strip()
    if payload.endswith(";"):
        payload = payload[:-1].rstrip()
    return json.loads(payload)


class ProgramWeeklyCommitmentTest(unittest.TestCase):
    def test_all_programs_have_a_coherent_weekly_time_estimate(self):
        programs = load_programs()
        self.assertEqual(26, len(programs))
        for program in programs:
            with self.subTest(program=program["id"]):
                days = program.get("daysPerWeek")
                minutes = program.get("estimatedSessionMinutes")
                self.assertIsInstance(days, int)
                self.assertIsInstance(minutes, int)
                self.assertGreater(days, 0)
                self.assertGreater(minutes, 0)
                self.assertEqual(days, len(program.get("sessions", [])))
                self.assertEqual(days * minutes, round(days * minutes))

    def test_card_and_detail_both_render_the_same_estimate_helper(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("function programWeeklyMinutes(program)", app)
        self.assertIn("function programWeeklyTimeText(program)", app)
        self.assertGreaterEqual(app.count("programWeeklyTimeText(program)"), 3)
        self.assertIn("${escapeHtml(programWeeklyTimeText(program))}", app)
        self.assertIn("return days * sessionMinutes;", app)
        self.assertIn("return minutes === null ? t('noWeeklyEstimate')", app)

    def test_weekly_commitment_copy_is_bilingual_and_explicitly_estimated(self):
        app = APP_JS.read_text(encoding="utf-8")
        self.assertIn("weeklyTrainingTime:'الوقت التدريبي التقديري أسبوعيًا'", app)
        self.assertIn("weeklyTrainingTime:'Estimated weekly training time'", app)
        self.assertIn("minutesPerWeek:'دقيقة'", app)
        self.assertIn("minutesPerWeek:'min'", app)
        self.assertIn("noWeeklyEstimate:'غير متاح'", app)
        self.assertIn("noWeeklyEstimate:'Not available'", app)

    def test_estimate_handles_invalid_program_values_without_fabricating_zero(self):
        app = APP_JS.read_text(encoding="utf-8")
        helper = app.split("function programWeeklyMinutes(program)", 1)[1].split("function programWeeklyTimeText", 1)[0]
        self.assertIn("Number.isInteger(days)", helper)
        self.assertIn("Number.isInteger(sessionMinutes)", helper)
        self.assertIn("days < 1 || sessionMinutes < 1", helper)
        self.assertIn("return null", helper)

    def test_long_localized_labels_wrap_in_cards_and_detail_tags(self):
        app = APP_JS.read_text(encoding="utf-8")
        styles = STYLES.read_text(encoding="utf-8")
        self.assertIn('class="program-weekly-time"', app)
        self.assertIn(".program-weekly-time", styles)
        self.assertIn("overflow-wrap:anywhere", styles)
        self.assertIn("white-space:normal", styles)


if __name__ == "__main__":
    unittest.main()
