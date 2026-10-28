import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"
APP = PULSE / "app.js"
HTML = PULSE / "index.html"
CSS = PULSE / "styles.css"
EXERCISES = PULSE / "data" / "exercises.js"


def load_exercises():
    source = EXERCISES.read_text(encoding="utf-8")
    prefix = "window.THF_EXERCISES = "
    if not source.startswith(prefix):
        raise AssertionError("exercise data assignment wrapper changed")
    return json.loads(source[len(prefix):].strip().rstrip(";"))


class ActiveWorkoutMuscleGroupsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = APP.read_text(encoding="utf-8")
        cls.html = HTML.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")
        cls.exercises = load_exercises()

    def test_primary_muscles_are_present_in_both_languages_for_all_exercises(self):
        self.assertEqual(112, len(self.exercises))
        ids = [item["id"] for item in self.exercises]
        self.assertEqual(len(ids), len(set(ids)))
        for item in self.exercises:
            with self.subTest(exercise=item["id"]):
                for language in ("en", "ar"):
                    values = item.get("muscles", {}).get("primary", {}).get(language)
                    self.assertIsInstance(values, list)
                    self.assertTrue(values, f"{item['id']} missing primary muscles for {language}")
                    self.assertTrue(all(isinstance(value, str) and value.strip() for value in values))

    def test_secondary_muscle_coverage_is_truthful_and_bilingual(self):
        missing = []
        for item in self.exercises:
            muscles = item.get("muscles", {})
            for language in ("en", "ar"):
                values = muscles.get("secondary", {}).get(language)
                self.assertIsInstance(values, list, item["id"])
                self.assertTrue(all(isinstance(value, str) and value.strip() for value in values))
            en_empty = not muscles["secondary"]["en"]
            ar_empty = not muscles["secondary"]["ar"]
            self.assertEqual(en_empty, ar_empty, item["id"])
            if en_empty:
                missing.append(item["id"])
        self.assertEqual(24, len(missing))

    def test_active_workout_separates_and_hides_empty_muscle_groups(self):
        self.assertIn("const primaryMuscles=item.muscles?.primary?.[state.lang]||[];", self.app)
        self.assertIn("const supportingMuscles=item.muscles?.secondary?.[state.lang]||[];", self.app)
        self.assertIn("primaryMuscles.length?", self.app)
        self.assertIn("supportingMuscles.length?", self.app)
        self.assertIn("t('primaryMuscles')", self.app)
        self.assertIn("t('secondaryMuscles')", self.app)
        self.assertIn("primaryMuscles:'العضلات الأساسية'", self.app)
        self.assertIn("secondaryMuscles:'العضلات المساعدة'", self.app)
        self.assertIn("primaryMuscles:'Primary muscles'", self.app)
        self.assertIn("secondaryMuscles:'Supporting muscles'", self.app)
        self.assertIn('<div id="activeMuscles" class="muscle-groups"></div>', self.html)
        self.assertIn(".muscle-groups{display:grid;gap:9px;", self.css)
        self.assertIn(".muscle-group{display:grid;gap:5px;", self.css)


if __name__ == "__main__":
    unittest.main()
