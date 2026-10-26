from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
PULSE = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "assets" / "pulse"


class MusclePresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (PULSE / "index.html").read_text()
        cls.javascript = (PULSE / "app.js").read_text()

    def test_active_workout_distinguishes_primary_and_supporting_muscles(self):
        self.assertIn('data-i18n="primaryMuscles"', self.html)
        self.assertIn('id="activePrimaryMuscles"', self.html)
        self.assertIn('data-i18n="supportingMuscles"', self.html)
        self.assertIn('id="activeSecondaryMuscles"', self.html)
        self.assertIn("item.muscles.primary[state.lang]", self.javascript)
        self.assertIn("item.muscles.secondary[state.lang]", self.javascript)

    def test_exercise_detail_keeps_primary_and_supporting_muscles_separate(self):
        self.assertIn('id="detailPrimaryMuscles"', self.html)
        self.assertIn('id="detailSecondaryMuscles"', self.html)
        self.assertNotIn('id="detailMuscles"', self.html)

    def test_muscle_group_labels_are_bilingual(self):
        self.assertIn("primaryMuscles:'العضلات الأساسية'", self.javascript)
        self.assertIn("supportingMuscles:'العضلات المساعدة'", self.javascript)
        self.assertIn("primaryMuscles:'Primary muscles'", self.javascript)
        self.assertIn("supportingMuscles:'Supporting muscles'", self.javascript)


if __name__ == "__main__":
    unittest.main()
