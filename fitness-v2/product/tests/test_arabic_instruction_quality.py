import json
from pathlib import Path
import unittest


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "android/app/src/main/assets/pulse/data/exercises.js"
)

EXPECTED_ARABIC_CUES = {
    "barbell-deadlift": (
        "منتصف القدمين",
        "ادفع الأرض بالقدمين",
        "ادفع الورك للخلف",
    ),
    "romanian-deadlift": (
        "الركبتين مثنيتين قليلًا",
        "ادفع الورك للخلف",
        "دون فرط تقوس أسفل الظهر",
    ),
    "barbell-bench-press---medium-grip": (
        "لوحي الكتف للخلف ولأسفل",
        "منتصف الصدر",
        "حواجز أمان أو مساعدًا",
    ),
    "pullups": (
        "كتفين بعيدين عن الأذنين",
        "اسحب المرفقين لأسفل",
        "انزل ببطء",
    ),
    "handstand-push-ups": (
        "جدار ثابت",
        "وسادة مناسبة",
        "فقدان التوازن",
    ),
    "barbell-shoulder-press": (
        "أمام الكتفين",
        "الأضلاع فوق الحوض",
        "اخفض البار ببطء",
    ),
    "front-box-jump": (
        "صندوقًا ثابتًا منخفضًا",
        "اهبط على الصندوق بركبتين مثنيتين",
        "انزل خطوة خطوة",
    ),
}


class ArabicInstructionQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = DATA_PATH.read_text(encoding="utf-8")
        payload = source.split("=", 1)[1].strip().removesuffix(";")
        cls.exercises = json.loads(payload)
        cls.by_id = {item["id"]: item for item in cls.exercises}

    def test_key_movements_have_specific_arabic_steps(self):
        for exercise_id, phrases in EXPECTED_ARABIC_CUES.items():
            with self.subTest(exercise_id=exercise_id):
                self.assertIn(exercise_id, self.by_id)
                steps = self.by_id[exercise_id]["steps"]["ar"]
                self.assertEqual(len(steps), 3)
                joined = " ".join(steps)
                for phrase in phrases:
                    self.assertIn(phrase, joined)
                self.assertNotIn("اخفض الحمل أو الجسم بتحكم حتى مدى مريح", joined)

    def test_selected_movements_do_not_share_one_generic_step_template(self):
        step_sets = [
            tuple(self.by_id[exercise_id]["steps"]["ar"])
            for exercise_id in EXPECTED_ARABIC_CUES
        ]
        self.assertEqual(len(step_sets), len(set(step_sets)))


if __name__ == "__main__":
    unittest.main()
