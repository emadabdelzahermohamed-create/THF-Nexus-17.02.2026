import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "android" / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"

TARGETS = {
    "medicine-ball-full-twist": (4, ("الكرة", "الشريك", "الدوران")),
    "one-arm-medicine-ball-slam": (4, ("بيد واحدة", "فوق الرأس", "الأرض")),
    "pallof-press-with-rotation": (6, ("الكيبل", "ربع دورة", "البكرة")),
    "hanging-leg-raise": (4, ("العارضة", "الساقين", "دون تأرجح")),
    "pallof-press": (6, ("الكيبل", "الذراعان", "يلف جذعك")),
    "mountain-climbers": (2, ("البلانك", "ركبة", "الحوض")),
    "overhead-slam": (4, ("الكرة الطبية", "فوق الرأس", "الأرض")),
    "air-bike": (6, ("أسفل الظهر", "المرفق", "الركبة")),
}
GENERIC_AR = {
    "ابدأ من جذع ثابت وتنفس دون حبس طويل.",
    "نفّذ الحركة ببطء ومن دون شد الرقبة.",
    "توقف قبل فقدان وضع الحوض أو أسفل الظهر.",
}

class CoreArabicInstructionSpecificityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = CATALOG.read_text(encoding="utf-8")
        cls.exercises = {item["id"]: item for item in json.loads(source.split("=", 1)[1].strip().rstrip(";"))}

    def test_core_exercise_cues_are_specific_and_bilingual_steps_align(self):
        for exercise_id, (expected_steps, required_terms) in TARGETS.items():
            with self.subTest(exercise=exercise_id):
                exercise = self.exercises[exercise_id]
                arabic = exercise["steps"]["ar"]
                english = exercise["steps"]["en"]
                joined = " ".join(arabic)
                self.assertEqual(expected_steps, len(arabic))
                self.assertEqual(len(english), len(arabic))
                self.assertTrue(set(arabic).isdisjoint(GENERIC_AR))
                self.assertEqual(len(arabic), len(set(arabic)))
                for term in required_terms:
                    self.assertIn(term, joined)

    def test_overhead_slam_english_equipment_spelling(self):
        first_step = self.exercises["overhead-slam"]["steps"]["en"][0].lower()
        self.assertIn("medicine ball", first_step)
        self.assertNotIn("medine ball", first_step)

if __name__ == "__main__":
    unittest.main()
